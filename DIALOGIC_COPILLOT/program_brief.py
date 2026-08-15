# -*- coding: utf-8 -*-
"""
Program Brief — memahami target/bounty secara mendalam via dialog ARC.

Tujuan: ketika integrasi API platform belum bekerja (fallback publik tetap jalan),
researcher memasukkan sendiri detail bounty (deskripsi, scopes, out-of-scopes,
rules, persyaratan) lewat dialog ARC. ARC mem-parse, menyimpan per-target, dan
men-generate manifest otorisasi (ScopeSovereigntyGuard) supaya semua operasi
berikutnya otomatis dibatasi ke in-scope.
"""
import json
import os
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

BRIEFS_DIR_DEFAULT = "~/.arc/briefs"

# Marker section -> label alternatif (Indonesia + Inggris).
SECTION_LABELS: Dict[str, List[str]] = {
    "description": ["description", "deskripsi", "deskripsi bounty", "tentang", "about"],
    "scope": ["scope", "in scope", "in-scope", "in_scope", "aspek", "daftar target", "target"],
    "out_of_scope": ["out of scope", "out-of-scope", "out_of_scope", "outside of scope",
                     "diluar scope", "di luar scope", "tidak termasuk", "excluded", "not in scope"],
    "rules": ["rules", "rule", "peraturan", "ketentuan", "aturan"],
    "requirements": ["requirements", "requirement", "persyaratan", "syarat", "kebutuhan"],
}

_SECTION_HEADER_WORDS = {
    "description": {"description", "deskripsi", "tentang"},
    "scope": {"scope", "in scope", "aspek", "target"},
    "out_of_scope": {"out of scope", "outside of scope", "diluar scope", "excluded", "not in scope"},
    "rules": {"rules", "peraturan", "ketentuan", "aturan"},
    "requirements": {"requirements", "persyaratan", "syarat"},
}


def _clean(value: str) -> str:
    """Bersihkan & ratakan whitespace."""
    return re.sub(r'\s+', ' ', (value or '')).strip()


def _split_items(text: str) -> List[str]:
    """Pecah teks menjadi daftar item (per baris, lalu koma/titik-koma)."""
    items: List[str] = []
    if not text:
        return items
    for line in text.splitlines():
        for part in re.split(r'[;,]', line):
            part = (_clean(part) or '')
            part = re.sub(r'^[-*•]\s+|\d+[\.\)]\s+', '', part).strip()
            part = _clean(part)
            if part and part not in items:
                items.append(part)
    return items


def parse_program_brief(text: str, platform: Optional[str] = None,
                        program_name: Optional[str] = None,
                        target_domain: Optional[str] = None) -> Dict[str, Any]:
    """Parse teks bounty (hasil paste dari dashboard platform) menjadi skema
    ProgramBrief dengan heuristik berbasis marker section.

    Contoh input yang dikenali:
        Deskripsi: Perekrutan kerentanan pada ...
        Scope: app.example.com, *.example.com
        Out of scope: staging.example.com
        Rules: accepted vuln types: xss, sqli
        Requirements: repro wajib, bukti PoC
    """
    brief: Dict[str, Any] = {
        "program_name": program_name or "",
        "platform": platform or "",
        "target_domain": target_domain or "",
        "description": "",
        "scope": [],
        "out_of_scope": [],
        "rules": {},
        "requirements": [],
        "allowed_operations": ["recon", "scan", "exploit"],
        "source": "manual_dialog",
        "updated_at": datetime.now().isoformat(),
    }

    section_buf: Dict[str, List[str]] = {k: [] for k in SECTION_LABELS}
    current = "description"
    text = (text or "").strip()
    if not text:
        return brief

    for raw_line in text.splitlines():
        line = _clean(raw_line)
        if not line:
            continue
        lower = line.lower()

        matched = None
        rest = ""
        # 1) header dengan ':' atau '=' diikuti konten -> "Scope: ..."
        for key, labels in SECTION_LABELS.items():
            for lab in labels:
                if re.match(rf'^{re.escape(lab)}\s*[:=]', lower):
                    matched = key
                    tail = re.split(r'[:=]', line, 1)[1].strip()
                    rest = _clean(tail)
                    break
            if matched:
                break
        if not matched:
            # 2) baris sendirian yang persis kata header (tanpa ':')
            for key, words in _SECTION_HEADER_WORDS.items():
                if lower in words:
                    matched = key
                    break
        if matched:
            current = matched
            if rest:
                section_buf[current].append(rest)
            continue

        # baris non-header -> masuk ke section aktif
        if line:
            # metadata (program/platform/target) tidak masuk ke section scope
            if re.match(r'^(?:program|platform|target|program_name|target_domain)\s*[:=]',
                        line, re.IGNORECASE):
                continue
            section_buf[current].append(line)

    brief["description"] = _clean(" ".join(section_buf["description"]))
    brief["scope"] = _split_items("\n".join(section_buf["scope"]))
    brief["out_of_scope"] = _split_items("\n".join(section_buf["out_of_scope"]))

    # rules: baris berisi ':' jadi dict {label: value}, selain itu ke _notes.
    # Satu baris boleh berisi banyak 'k: v' dipisah ';'.
    rules: Dict[str, Any] = {}
    notes: List[str] = []
    for line in section_buf["rules"]:
        if ':' in line:
            for pair in re.split(r';', line):
                if ':' in pair:
                    k, _, v = pair.partition(':')
                    k = _clean(k)
                    v = _clean(v)
                    if k:
                        rules[k] = v
                elif _clean(pair):
                    notes.append(_clean(pair))
        elif line:
            notes.append(line)
    if notes:
        rules["_notes"] = notes
    brief["rules"] = rules

    brief["requirements"] = _split_items("\n".join(section_buf["requirements"]))
    return brief


def merge_brief(base: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
    """Gabungkan patch ke brief dasar (hasil pemanggilan bertahap)."""
    merged = dict(base or {})
    for key in ("program_name", "platform", "target_domain", "description", "source"):
        if patch.get(key):
            merged[key] = patch[key]
    for key in ("scope", "out_of_scope", "requirements", "allowed_operations"):
        items = list(merged.get(key, []) or [])
        for it in patch.get(key, []) or []:
            if it and it not in items:
                items.append(it)
        merged[key] = items
    merged["rules"] = {**(merged.get("rules") or {}), **(patch.get("rules") or {})}
    merged["updated_at"] = datetime.now().isoformat()
    return merged


def extract_domains(assets: List[str], out_scope: List[str]) -> List[str]:
    """Ekstrak daftar domain (apex) dari asset in-scope, minus out-of-scope."""
    domain_set: List[str] = []

    def normalize(asset: str) -> Optional[str]:
        asset = _clean(asset).strip('*.')
        if not asset:
            return None
        if asset.startswith(('http://', 'https://')):
            host = urlparse(asset).netloc
        else:
            host = asset.split('/')[0].split(':')[0]
        host = host.lower().replace('www.', '').strip('.')
        return host or None

    for asset in assets:
        host = normalize(asset)
        if host and host not in domain_set:
            domain_set.append(host)
    for oos in out_scope:
        host = normalize(oos)
        if host:
            domain_set = [d for d in domain_set if d != host]
    return domain_set


def brief_to_manifest(brief: Dict[str, Any], expiry_days: int = 30,
                      legal_contact: str = "authorized_security_researcher@example.com") -> Dict[str, Any]:
    """Konversi ProgramBrief menjadi dict manifest untuk ScopeSovereigntyGuard."""
    domains = extract_domains(brief.get("scope", []), brief.get("out_of_scope", []))
    program_name = (_clean(brief.get("program_name") or "") or
                    (_clean(brief.get("target_domain") or "") or "program"))
    manifest = {
        "program_name": program_name,
        "platform": brief.get("platform", ""),
        "target_domain": brief.get("target_domain", ""),
        "description": brief.get("description", ""),
        "created_at": datetime.now().isoformat(),
        "expiry_date": (datetime.now() + timedelta(days=expiry_days)).isoformat(),
        "status": "active",
        "scope": {
            "domains": domains,
            "assets": brief.get("scope", []),
            "out_of_scope": brief.get("out_of_scope", []),
            "technologies": [],
        },
        "rules": brief.get("rules", {}),
        "requirements": brief.get("requirements", []),
        "allowed_operations": brief.get("allowed_operations", ["recon", "scan", "exploit"]),
        "bounty_tier": "manual_brief",
        "source": brief.get("source", "manual_dialog"),
        "legal_contact": legal_contact,
    }
    return manifest


class ProgramBriefStore:
    """Penyimpanan ProgramBrief per-target (JSON) di ~/.arc/briefs."""

    def __init__(self, briefs_dir: Optional[str] = None):
        self.briefs_dir = os.path.expanduser(briefs_dir or BRIEFS_DIR_DEFAULT)
        os.makedirs(self.briefs_dir, exist_ok=True)

    def _key(self, target_domain: str) -> str:
        key = re.sub(r'[^\w\-.]', '_', _clean(target_domain).lower())
        return key or "unknown"

    def _path(self, target_domain: str) -> str:
        return os.path.join(self.briefs_dir, f"{self._key(target_domain)}.json")

    def get_brief(self, target_domain: str) -> Dict[str, Any]:
        path = self._path(target_domain)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_brief(self, brief: Dict[str, Any]) -> str:
        target = brief.get("target_domain") or brief.get("program_name") or "program"
        path = self._path(target)
        brief["updated_at"] = datetime.now().isoformat()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(brief, f, indent=2, ensure_ascii=False)
        return path

    def upsert(self, target_domain: str, patch: Dict[str, Any]) -> Dict[str, Any]:
        base = self.get_brief(target_domain)
        if not base.get("target_domain"):
            base["target_domain"] = target_domain
        merged = merge_brief(base, patch)
        merged["target_domain"] = merged.get("target_domain") or target_domain
        self.save_brief(merged)
        return merged

    def add_item(self, target_domain: str, field: str, item: str) -> Dict[str, Any]:
        """Tambahkan satu item ke field list (scope/out_of_scope/requirements)."""
        base = self.get_brief(target_domain)
        if not base.get("target_domain"):
            base["target_domain"] = target_domain
        items = list(base.get(field, []) or [])
        parsed = _split_items(item)
        for it in parsed:
            if it and it not in items:
                items.append(it)
        base[field] = items
        self.save_brief(base)
        return base

    def clear_brief(self, target_domain: str) -> bool:
        path = self._path(target_domain)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    def list_briefs(self) -> List[str]:
        return sorted(
            os.path.splitext(f)[0] for f in os.listdir(self.briefs_dir) if f.endswith(".json")
        )
