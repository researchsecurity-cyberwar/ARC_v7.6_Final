#!/bin/bash
# ============================================================
# deploy_kali.sh — Deploy & verifikasi ARC v7.6 Final di Kali Linux
# Menjalankan: bash deploy_kali.sh
# ============================================================
set -e

ARC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📂 ARC directory: $ARC_DIR"

# 1. Deploy config ke ~/.arc/config.yaml
echo ""
echo "[1] Deploy config..."
mkdir -p ~/.arc
if [ -f "$ARC_DIR/confiq.yaml" ]; then
    cp "$ARC_DIR/confiq.yaml" ~/.arc/config.yaml
    echo "   ✅ config.yaml tersalin dari confiq.yaml"
else
    echo "   ⚠️ confiq.yaml tidak ditemukan — pakai ~/.arc/config.yaml yang ada"
fi

# 2. Verifikasi fix kritis ada di file
echo ""
echo "[2] Verifikasi fix kritis..."
if grep -q "if isinstance(success_prob, dict)" "$ARC_DIR/arc_main.py"; then
    echo "   ✅ Fix dict*int di arc_main.py"
else
    echo "   ❌ Fix dict*int TIDAK ada di arc_main.py! File versi lama."
fi
if grep -q "_normalize_probability" "$ARC_DIR/UNIFIED_LEARNING_ENGINE/self_learning_orchestrator.py"; then
    echo "   ✅ Fix _normalize_probability di orchestrator"
else
    echo "   ❌ Fix _normalize_probability TIDAK ada! File versi lama."
fi
if grep -q "/star" "$ARC_DIR/DIALOGIC_COPILLOT/PLATFORM_COMMUNICATOR/telegram_notifier.py"; then
    echo "   ✅ Alias /star di telegram_notifier"
else
    echo "   ❌ Alias /star TIDAK ada! File versi lama."
fi

# 3. Jalankan verifikasi struktural
echo ""
echo "[3] Jalankan final_verify.py..."
cd "$ARC_DIR"
python final_verify.py

# 4. Cek kesehatan session (opsional, butuh jaringan)
echo ""
echo "[4] Cek kesehatan session platform..."
python - <<'PYEOF'
import os, sys, yaml, importlib.util, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.dirname(os.path.abspath(__file__))

def import_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

cfg_path = os.path.expanduser("~/.arc/config.yaml")
if not os.path.exists(cfg_path):
    cfg_path = os.path.join(BASE, "confiq.yaml")
with open(cfg_path, encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f) or {}
BB = CONFIG.get("credentials", {}).get("bug_bounty", {}) or {}
CTF = CONFIG.get("credentials", {}).get("ctf", {}) or {}

def cred_for(platform, section):
    if platform in section and isinstance(section[platform], dict):
        return section[platform]
    for k, v in section.items():
        if platform in k and isinstance(v, dict):
            return v
    return {}

checks = [
    ("hackerone", "hackerone_scraper.py", "HackerOneScraper",
     "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/", BB, "api_token"),
    ("intigriti", "intigriti_scraper.py", "IntigritiScraper",
     "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/", BB, "personal_access_token"),
    ("bugcrowd", "bugcrowd_scraper.py", "BugCrowdScraper",
     "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/", BB, "session_cookie"),
    ("yeswehack", "yeswehack_scraper.py", "YesWeHackScraper",
     "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/", BB, "session_cookie"),
    ("immunefi", "immunefi_scraper.py", "ImmunefiScraper",
     "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/", BB, "session_cookie"),
    ("hackthebox", "hackthebox_scraper.py", "HackTheBoxScraper",
     "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/ctf_monitor/", CTF, "session_cookie"),
    ("tryhackme", "tryhackme_scraper.py", "TryHackMeScraper",
     "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/ctf_monitor/", CTF, "session_cookie"),
]

for platform, fname, cls, sub, section, key in checks:
    creds = cred_for(platform, section)
    val = creds.get(key)
    if not val:
        print(f"  ⚠️ {platform}: tidak ada {key} di config")
        continue
    try:
        mod = import_module(fname, os.path.join(BASE, sub, fname))
        scraper = getattr(mod, cls)(val)
        ok = scraper.validate_session()
        progs = scraper.get_all_programs()
        n = len(progs) if hasattr(progs, "__len__") else 0
        print(f"  {'✅' if ok else '❌'} {platform}: session={'valid' if ok else 'EXPIRED/INVALID'}, {n} program")
    except Exception as e:
        print(f"  ❌ {platform}: error {e}")

# Google VRP selalu publik
try:
    gvrp = import_module("google_vrp_integrator",
                         os.path.join(BASE, "BROWSER_SECURITY_RESEARCH/google_vrp_integrator.py"))
    gi = gvrp.GoogleVRPIntegrator()
    progs = gi.get_all_google_programs()
    print(f"  ✅ google_vrp: {len(progs)} program (publik, tanpa cookie)")
except Exception as e:
    print(f"  ❌ google_vrp: error {e}")
PYEOF

echo ""
echo "✅ Deploy selesai. Jalankan: python arc_main.py"
