# -*- coding: utf-8 -*-
"""
Verifikasi end-to-end integrasi ARC Chat:

    ArcChatEngine + ConversationEngine(hook brief) + program_brief + Google VRP
    + REPL (chat terminal)

Menjalankan semua tanpa jaringan (Google VRP pakai konfigurasi lokal ARC).
"""
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(ROOT)
sys.path.insert(0, PROJECT)

from DIALOGIC_COPILLOT.arc_chat_engine import ArcChatEngine  # noqa: E402
from DIALOGIC_COPILLOT.program_brief import ProgramBriefStore  # noqa: E402

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS]  {name}")
    else:
        FAIL += 1
        print(f"  [FAIL]  {name}  {detail}")


def contains_all(haystack, needles):
    return all(n.lower() in haystack.lower() for n in needles)


# =====================================================================
# Setup engine dengan direktori temp (tidak menyentuh ~/.arc)
# =====================================================================
tmp = tempfile.mkdtemp(prefix="arc_chat_test_")
mem_dir = os.path.join(tmp, "conv")
brief_dir = os.path.join(tmp, "briefs")

engine = ArcChatEngine(memory_dir=mem_dir, briefs_dir=brief_dir)

print("=== 1. Hook ConversationEngine -> program_brief ===")
check("brief_engine ter-inject ke ConversationEngine",
      engine.conversation.brief_engine is engine)
check("ProgramBriefStore aktif", isinstance(engine.brief_store, ProgramBriefStore))

# =====================================================================
# 2. Target bebas apa saja
# =====================================================================
print("\n=== 2. Dialog target bebas (domain/IP/nama program) ===")
for t in ("shop.example.id", "10.0.0.5", "hackerone.com/program/nasa", "bank.xyz"):
    r = engine.start_conversation(t)
    check(f"mulai target '{t}'", "Dialog dimulai" in r, r[:80])
    r2 = engine.handle("/target")
    check(f"target aktif = '{t}'", t in r2, r2)

check("mulai lewat pesan '/mulai api.abc.com'",
      "api.abc.com" in engine.handle("/mulai api.abc.com"))

# =====================================================================
# 3. Paste brief bounty utuh (auto-parse)
# =====================================================================
print("\n=== 3. Paste brief bounty utuh -> auto parse & simpan ===")
brief_text = """Target: shop.example.id
Program: Shop Indonesia Bounty
Platform: BugCrowd
Deskripsi: Bug bounty untuk toko online utama. Fokus pada IDOR, XSS, dan auth bypass.
Scope: shop.example.id, *.shop.example.id, api.shop.example.id
Out of scope: staging.shop.example.id, aplikasi internal
Rules: severity critical: $5000; severity high: $2000; response time: 72 jam
Requirements: repro steps wajib, PoC atau video, laporan dalam bahasa Inggris
"""
r = engine.handle(brief_text)
check("brief terparse & tersimpan", "tersimpan" in r, r[:120])
check("jumlah scope disebutkan", "3 item" in r, r)
check("rules disebutkan", "3 entri" in r, r)

brief = engine.brief_store.get_brief("shop.example.id")
check("scope tersimpan benar",
      brief.get("scope") == ["shop.example.id", "*.shop.example.id", "api.shop.example.id"],
      str(brief.get("scope")))
check("out_of_scope tersimpan",
      "staging.shop.example.id" in brief.get("out_of_scope", []),
      str(brief.get("out_of_scope")))
check("wildcard dipertahankan", "*.shop.example.id" in brief.get("scope", []))
check("rules severity critical", brief.get("rules", {}).get("severity critical") == "$5000",
      str(brief.get("rules"))[:100])
check("requirements terisi", len(brief.get("requirements", [])) >= 3)
check("program name diekstrak", brief.get("program_name") == "Shop Indonesia Bounty")

# =====================================================================
# 4. Perintah bertahap: tambah scope / oos / requirement / rules
# =====================================================================
print("\n=== 4. Perintah bertahap (dialog natural) ===")
engine.handle("/mulai shop.example.id")
r = engine.handle("tambah scope admin.shop.example.id; cdn.shop.example.id")
check("tambah scope bertahap", "admin.shop.example.id" in r and "cdn.shop.example.id" in r, r)
r = engine.handle("tambah out of scope dev.shop.example.id")
check("tambah out of scope", "dev.shop.example.id" in r, r)
r = engine.handle("tambah requirement validasi ulang sebelum submit")
check("tambah requirement", "validasi ulang sebelum submit" in r, r)
r = engine.handle("set rules max_report_per_day: 5; dup_check: wajib")
check("set rules", contains_all(r, ["max_report_per_day", "5", "dup_check"]), r)

# =====================================================================
# 5. Lihat brief & manifest
# =====================================================================
print("\n=== 5. Lihat brief & manifest ===")
r = engine.handle("lihat brief")
check("lihat brief menampilkan scope", contains_all(r, ["shop.example.id", "Scope", "Rules"]), r[:200])
r = engine.handle("manifest")
check("manifest generate", contains_all(r, ["scope", "domains", "allowed_operations"]), r[:200])
try:
    manifest = json.loads(r.split("\n", 1)[1])
    check("manifest adalah JSON valid", manifest["target_domain"] == "shop.example.id")
    check("manifest scope.domains ada", "shop.example.id" in manifest["scope"]["domains"],
          str(manifest["scope"]["domains"]))
except Exception as e:
    check("manifest adalah JSON valid", False, str(e))

# =====================================================================
# 5b. BAHASA NATURAL: "target X, scope Y, rules Z" (paham sendiri)
# =====================================================================
print("\n=== 5b. Bahasa natural (tanpa perintah formal) ===")
engine.handle("/mulai bank.xyz")
natural = ("target bank.xyz, scope *.bank.xyz dan api.bank.xyz, "
           "out of scope staging.bank.xyz, "
           "rules xss: allowed; sqli: out, "
           "requirements repro wajib dan bukti PoC")
r = engine.handle(natural)
check("brief natural diterima & disimpan", "tersimpan" in r, r[:160])
nb = engine.brief_store.get_brief("bank.xyz")
check("natural: scope terpecah", "*.bank.xyz" in nb.get("scope", [])
      and "api.bank.xyz" in nb.get("scope", []), str(nb.get("scope")))
check("natural: out of scope", "staging.bank.xyz" in nb.get("out_of_scope", []),
      str(nb.get("out_of_scope")))
check("natural: rules", nb.get("rules", {}).get("xss") == "allowed", str(nb.get("rules")))
check("natural: requirements", "repro wajib" in nb.get("requirements", [])
      and "bukti PoC" in nb.get("requirements", []), str(nb.get("requirements")))
check("natural: target diekstrak", nb.get("target_domain") == "bank.xyz",
      str(nb.get("target_domain")))

# intent eksplisit "buat brief untuk X, scope ..."
r = engine.handle("buat brief untuk fintech.abc, scope web.fintech.abc, rules auth: wajib")
check("intent 'buat brief' dibuat", "tersimpan" in r, r[:120])
nb2 = engine.brief_store.get_brief("fintech.abc")
check("intent 'buat brief' scope", "web.fintech.abc" in nb2.get("scope", []),
      str(nb2.get("scope")))

# =====================================================================
# 5c. Pertanyaan: "apa scope target X?" / "rules untuk X?"
# =====================================================================
print("\n=== 5c. Pertanyaan (ARC paham konteks) ===")
r = engine.handle("apa scope target bank.xyz")
check("tanya scope", "*.bank.xyz" in r and "api.bank.xyz" in r, r[:150])
r = engine.handle("rules untuk bank.xyz")
check("tanya rules", "xss" in r and "allowed" in r, r[:150])
r = engine.handle("apa out of scope bank.xyz")
check("tanya out of scope", "staging.bank.xyz" in r, r[:150])
r = engine.handle("sebutkan requirements fintech.abc")
check("tanya requirements", bool(r), r[:120])
r = engine.handle("target bank.xyz")
check("perintah 'target X' pindah target", "Target diganti: bank.xyz" in r, r[:100])
r2 = engine.handle("/target")
check("target benar-benar berganti", "bank.xyz" in r2, r2)

# =====================================================================
# 6. Intel Google VRP terintegrasi
# =====================================================================
print("\n=== 6. Integrasi Google VRP ===")
r = engine.handle("program google")
check("daftar program Google VRP", "Google Vulnerability Reward Programs" in r, r[:150])
check("ada cloud_vrp", "cloud_vrp" in r)
r = engine.handle("cek scope https://cloud.google.com")
check("cek scope URL", "cloud.google.com" in r and ("IN SCOPE" in r or "NOT IN SCOPE" in r), r[:150])
r = engine.handle("cek scope https://shop.example.id")
check("cek scope target non-google (tidak crash)", bool(r), r[:120])

# =====================================================================
# 7. Perintah operasional fallback (tidak crash, minta approval)
# =====================================================================
print("\n=== 7. Fallback perintah operasional ===")
r = engine.handle("scan shop.example.id for vulnerabilities")
check("scan -> fallback approval", "human-in-the-loop" in r or "sesi ARC" in r, r[:150])
r = engine.handle("hallo apa kabar")
check("pesan bebas -> balasan membantu (tidak crash)", bool(r) and "ARC" in r, r[:150])
r = engine.handle("")
check("pesan kosong -> balasan sapa", bool(r), r[:80])
r = engine.handle("x" * 5000)
check("pesan raksasa -> tidak crash", bool(r), r[:100])

# =====================================================================
# 8. Persistensi file (brief & percakapan tersimpan di disk)
# =====================================================================
print("\n=== 8. Persistensi ===")
brief_files = os.listdir(brief_dir)
check("file brief tersimpan di disk", any("shop.example.id" in f for f in brief_files), str(brief_files))
conv_files = os.listdir(mem_dir)
check("file percakapan tersimpan di disk", len(conv_files) >= 1, str(conv_files))
check("riwayat percakapan tercatat", len(engine.get_history()) >= 5,
      f"{len(engine.get_history())} pesan")

# Engine baru membaca data yang sama (simulasi restart)
engine2 = ArcChatEngine(memory_dir=mem_dir, briefs_dir=brief_dir)
check("engine baru lihat brief yang sama", "shop.example.id" in engine2.list_briefs(),
      str(engine2.list_briefs()))

# =====================================================================
# 9. REPL engine (tanpa interaksi; simulasi via engine)
# =====================================================================
print("\n=== 9. REPL/CLI ===")
r = engine.handle("/bantuan")
check("/bantuan menampilkan panduan", contains_all(r, ["TARGET", "BRIEF", "MANIFEST", "GOOGLE"]), r[:200])
r = engine.handle("daftar brief")
check("daftar brief memuat semua target",
      contains_all(r, ["shop.example.id", "bank.xyz", "fintech.abc"]), r)
r = engine.handle("hapus brief shop.example.id")
check("hapus brief", "dihapus" in r, r)
check("brief benar-benar hilang", "shop.example.id" not in engine.list_briefs(),
      str(engine.list_briefs()))

# Bersihkan temp
shutil.rmtree(tmp, ignore_errors=True)

print("\n" + "=" * 60)
print(f"RESULT: {PASS} PASS, {FAIL} FAIL")
print("=" * 60)
sys.exit(1 if FAIL else 0)
