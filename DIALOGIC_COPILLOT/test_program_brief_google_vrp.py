# -*- coding: utf-8 -*-
"""
Real-life test: program_brief.py + data nyata program Google VRP.

Test ini memakai data asli 13 program Google Vulnerability Reward Program
yang dibundel di BROWSER_SECURITY_RESEARCH/google_vrp_integrator.py
(nama program asli, URL rules asli, rentang bounty asli, pola scope asli),
lalu menjalankan pipeline ProgramBrief lengkap:

    teks bounty (seperti hasil paste dialog ARC)
        -> parse_program_brief
        -> ProgramBriefStore (simpan/load/upsert/add_item)
        -> brief_to_manifest  (manifest untuk ScopeSovereigntyGuard)

Catatan jujur: halaman bughunters.google.com adalah SPA (JS-rendered),
HTML mentah tidak berisi isi rules tanpa browser session. Karena itu
"real data" diambil dari konfigurasi integrasi ARC yang sudah berisi
data resmi program Google.
"""
import json
import os
import sys
import tempfile

# Supaya emoji/unicode tidak rusak di console Windows
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(ROOT)
sys.path.insert(0, PROJECT)

from DIALOGIC_COPILLOT.program_brief import (  # noqa: E402
    _clean,
    _split_items,
    parse_program_brief,
    merge_brief,
    extract_domains,
    brief_to_manifest,
    ProgramBriefStore,
)


PASS = 0
FAIL = 0


def check(name: str, cond: bool, detail: str = ""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS]  {name}")
    else:
        FAIL += 1
        print(f"  [FAIL]  {name}  {detail}")


# =====================================================================
# 1) Unit test _split_items (fungsi yang tadinya rusak)
# =====================================================================
print("\n=== 1. _split_items (fungsi yang di-fix) ===")
r = _split_items("app.example.com, *.example.com\n  - api.example.com;\n\n- api.example.com")
check("split + dedup + strip bullet (wildcard *. tetap utuh)",
      r == ["app.example.com", "*.example.com", "api.example.com"], str(r))
r = _split_items("a,,b\n\n")
check("skip string kosong dari delimiter ganda", r == ["a", "b"], str(r))
r = _split_items("• satu\n1. dua\n- tiga\n* empat")
check("strip bullet/angka awalan", r == ["satu", "dua", "tiga", "empat"], str(r))
r = _split_items("   ")
check("text hanya whitespace -> []", r == [], str(r))
check("_clean collapse whitespace", _clean("  app\n  example.com ") == "app example.com")

# =====================================================================
# 2) Ambil data nyata Google VRP dari integrator ARC
# =====================================================================
print("\n=== 2. Ambil data nyata Google VRP (konfigurasi integrator ARC) ===")
from BROWSER_SECURITY_RESEARCH.google_vrp_integrator import GoogleVRPIntegrator  # noqa: E402

integrator = GoogleVRPIntegrator()
programs = dict(integrator.google_programs)
check("ada 13 program Google VRP", len(programs) >= 13, f"hanya {len(programs)}")
for key in ("chrome_vrp", "cloud_vrp", "ai_vrp", "google_vrp", "oss_vrp"):
    prog = programs.get(key, {})
    check(f"data program '{key}' punya scope_patterns & bounty",
          bool(prog.get("scope_patterns")) and bool(prog.get("bounty_range")),
          str(prog)[:120])

# =====================================================================
# 3) Pipeline nyata: teks bounty -> parse -> store -> manifest
# =====================================================================
print("\n=== 3. Pipeline ProgramBrief dari data Google VRP ===")


def build_brief_text(key: str, prog: dict) -> str:
    """Bangun teks bounty seperti hasil paste/dialog researcher ke ARC."""
    scope_items = prog.get("scope_patterns", []) or []
    return "\n".join([
        f"Program: {prog.get('name', key)}",
        f"Platform: Google VRP",
        f"Deskripsi: Program bug bounty resmi Google untuk {prog.get('name', key)}. "
        f"Rentang bounty {prog.get('bounty_range', 'N/A')}. "
        f"Tipe program {prog.get('program_type', 'N/A')}. "
        f"Aturan resmi di {prog.get('rules_url', 'N/A')}.",
        f"Scope: {', '.join(scope_items)}",
        "Out of scope: lingkungan staging/testing, aplikasi pihak ketiga tanpa kontrak Google",
        f"Rules: bounty_range: {prog.get('bounty_range', 'N/A')}; "
        f"report_url: {prog.get('report_url', 'N/A')}; official_rules_url: {prog.get('rules_url', 'N/A')}",
        "Requirements: repro steps wajib, PoC atau video, laporan dalam bahasa Inggris",
    ])


tmpdir = tempfile.mkdtemp(prefix="arc_brief_test_")
store = ProgramBriefStore(briefs_dir=tmpdir)
check("ProgramBriefStore buat direktori", os.path.isdir(tmpdir), tmpdir)

saved_manifests = []
for key, prog in list(programs.items()):
    text = build_brief_text(key, prog)
    brief = parse_program_brief(
        text,
        platform="Google VRP",
        program_name=prog.get("name", key),
        target_domain=f"{key}.program.google",
    )
    expected = prog.get("scope_patterns", [])
    check(f"parse '{key}' scope terisi ({len(brief['scope'])} item)",
          len(brief["scope"]) == len(expected), str(brief["scope"])[:200])
    check(f"parse '{key}' rules mendeteksi bounty_range",
          str(brief["rules"].get("bounty_range", "")).startswith(prog.get("bounty_range", "X_X")),
          str(brief["rules"])[:140])

    path = store.save_brief(brief)
    check(f"simpan brief '{key}' ke file", os.path.exists(path), path)

    loaded = store.get_brief(brief["target_domain"])
    check(f"load brief '{key}' kembali", loaded.get("scope") == brief["scope"])

    manifest = brief_to_manifest(brief, expiry_days=30)
    saved_manifests.append((key, manifest))
    check(f"manifest '{key}' punya scope.domains",
          isinstance(manifest["scope"]["domains"], list), str(manifest["scope"]["domains"])[:150])

print(f"  Briefs tersimpan di: {tmpdir}")
check("list_briefs memuat semua target", len(store.list_briefs()) == len(programs),
      f"{len(store.list_briefs())} != {len(programs)}")

# =====================================================================
# 4) Flow dialog ARC: tambah scope bertahap (add_item / upsert)
# =====================================================================
print("\n=== 4. Simulasi dialog ARC: tambah scope bertahap ===")
target = "simulasi.dialog.arc"
b1 = store.add_item(target, "scope", "api.google.com, *.gstatic.com")
check("add_item pertama (wildcard dipertahankan)",
      b1["scope"] == ["api.google.com", "*.gstatic.com"], str(b1.get("scope")))
b2 = store.add_item(target, "scope", "*.gstatic.com; admin.google.com")
check("add_item kedua dedup + tambah baru (wildcard dipertahankan)",
      b2["scope"] == ["api.google.com", "*.gstatic.com", "admin.google.com"], str(b2.get("scope")))
b3 = store.upsert(target, {"rules": {"bounty_range": "$500 - $31,337"},
                          "requirements": ["repro wajib", "PoC atau video"]})
check("upsert menambah rules & requirements", b3["rules"].get("bounty_range") == "$500 - $31,337"
      and "repro wajib" in b3["requirements"], str(b3)[:300])
b4 = store.upsert(target, {"description": "Simulasi target dialog ARC."})
check("upsert memperbarui deskripsi", b4["description"] == "Simulasi target dialog ARC.")
check("upsert tidak menduplikasi scope", len(b4["scope"]) == 3, str(b4.get("scope")))

# =====================================================================
# 5) extract_domains + out-of-scope removal (bagian manifest)
# =====================================================================
print("\n=== 5. extract_domains (in-scope minus out-of-scope) ===")
doms = extract_domains(["https://www.google.com", "*.google.com", "cloud.google.com"],
                       ["cloud.google.com", "staging.google.com"])
check("out-of-scope terhapus dari domain", doms == ["google.com"], str(doms))
doms2 = extract_domains(["https://maps.google.com/route", "https://www.gstatic.com/"],
                        ["www.google.com"])
check("normalisasi URL & www.", doms2 == ["maps.google.com", "gstatic.com"], str(doms2))

# =====================================================================
# 6) merge_brief (pemanggilan bertahap)
# =====================================================================
print("\n=== 6. merge_brief ===")
base = {"program_name": "Google VRP", "scope": ["a.com"], "rules": {"x": "1"}, "description": "old"}
merged = merge_brief(base, {"scope": ["a.com", "b.com"], "rules": {"y": "2"}, "description": "new"})
check("merge scope dedup", merged["scope"] == ["a.com", "b.com"], str(merged["scope"]))
check("merge rules gabung", merged["rules"] == {"x": "1", "y": "2"}, str(merged["rules"]))
check("merge deskripsi baru menang", merged["description"] == "new")

# =====================================================================
# 7) Contoh manifest akhir yang akan dipakai ScopeSovereigntyGuard
# =====================================================================
print("\n=== 7. Contoh manifest (untuk ScopeSovereigntyGuard) ===")
print(json.dumps(saved_manifests[0][1], indent=2, ensure_ascii=False)[:1600])

# Bersihkan direktori temp
import shutil  # noqa: E402
shutil.rmtree(tmpdir, ignore_errors=True)

print("\n" + "=" * 60)
print(f"RESULT: {PASS} PASS, {FAIL} FAIL")
print("=" * 60)
sys.exit(1 if FAIL else 0)
