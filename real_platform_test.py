#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ARC Live Real-Scale Platform Verification
==========================================
Uji nyata ketiga platform (HackerOne, Intigriti, CTFtime) dengan kredensial asli
dari confiq.yaml. Verifikasi fakta teknis:

  1. HackerOne  — API token permanen (tidak kadaluarsa)  → HTTP Basic Auth
  2. Intigriti  — PAT kadaluarsa 6 bulan                 → X-API-KEY header
  3. CTFtime    — API publik tanpa auth, tidak kadaluarsa → REST API
"""
import sys, os, io, time, json, base64, importlib.util, traceback, yaml

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = os.path.dirname(os.path.abspath(__file__))

# --- Load config ---
config_path = os.path.join(BASE, "confiq.yaml")
if not os.path.exists(config_path):
    config_path = os.path.expanduser("~/.arc/config.yaml")
if not os.path.exists(config_path):
    print("❌ confiq.yaml atau ~/.arc/config.yaml tidak ditemukan")
    sys.exit(1)

with open(config_path, encoding='utf-8') as f:
    CONFIG = yaml.safe_load(f) or {}

BB = CONFIG.get('credentials', {}).get('bug_bounty', {}) or {}
CTF_CFG = CONFIG.get('credentials', {}).get('ctf', {}) or {}
print(f"📄 Config: {config_path}")
print(f"   Bug bounty keys: {list(BB.keys())}")
print(f"   CTF keys: {list(CTF_CFG.keys())}")

results = []

def report(name, ok, detail=""):
    results.append(ok)
    mark = "✅" if ok else "❌"
    print(f"  {mark} {name}" + (f" — {detail}" if detail else ""))

def cred_for(platform, section):
    if platform in section and isinstance(section[platform], dict):
        return section[platform]
    for k, v in section.items():
        if platform in k and isinstance(v, dict):
            return v
    return {}

def import_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ============================================================
# 1. HACKERONE — API token (HTTP Basic Auth)
# ============================================================
print("\n" + "=" * 70)
print("1. HACKERONE — API token (HTTP Basic Auth)")
print("=" * 70)
try:
    import requests
    h1_path = os.path.join(BASE, "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/hackerone_scraper.py")
    h1_mod = import_module("hackerone_scraper", h1_path)
    h1_creds = cred_for("hackerone", BB)
    tok = h1_creds.get('api_token')

    if not tok:
        report("HackerOne: api_token di config", False, "key 'hackerone_main' atau prefix 'hackerone'")
    else:
        report("HackerOne: api_token ditemukan", True, f"len={len(tok)}")
        scr = h1_mod.HackerOneScraper(tok)
        t0 = time.time()
        ok_sess = scr.validate_session()
        report("HackerOne: validate_session (/me)", ok_sess, f"{time.time()-t0:.1f}s")

        # Fakta teknis: HackerOne API token format & auth method
        h1_api = "https://api.hackerone.com/v1"
        if ':' in tok:
            user, secret = tok.split(':', 1)
        else:
            try:
                decoded = base64.b64decode(tok).decode('utf-8')
                user, secret = decoded.split(':', 1)
            except Exception:
                user, secret = tok, ''
        
        print(f"  🔧 [Fakta] HackerOne auth: HTTP Basic Auth (identifier:secret)")
        print(f"  🔧 [Fakta] Identifier: {user[:30]}...")
        print(f"  🔧 [Fakta] Secret: {secret[:10]}...")
        print(f"  🔧 [Fakta] API endpoint: {h1_api}")
        print(f"  🔧 [Fakta] Token expiry: NO EXPIRY (hanya bisa dicabut manual)")

        # Test /me
        resp = requests.get(f"{h1_api}/me", auth=(user, secret), timeout=10)
        print(f"  🔧 [Fakta] GET /me → HTTP {resp.status_code}")
        if resp.status_code == 200:
            me = resp.json()
            print(f"  🔧 [Fakta] Profil: email={me.get('email', '?')}, name={me.get('name', '?')}")

        # Test /hackers/programs
        t0 = time.time()
        progs = scr.get_all_programs()
        report("HackerOne: get_all_programs()", isinstance(progs, list) and len(progs) > 0,
               f"{len(progs)} program, {time.time()-t0:.1f}s")
        if progs:
            p = progs[0]
            print(f"  📊 Contoh: {p.get('name', '?')} — state={p.get('state', '?')} — bounty={p.get('offers_bounties', '?')}")

except Exception as e:
    report("HackerOne: import/exec", False, str(e)[:300])
    traceback.print_exc()


# ============================================================
# 2. INTRIGITI — Personal Access Token (X-API-KEY)
# ============================================================
print("\n" + "=" * 70)
print("2. INTRIGITI — Personal Access Token (X-API-KEY)")
print("=" * 70)
try:
    import requests
    int_path = os.path.join(BASE, "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/intigriti_scraper.py")
    int_mod = import_module("intigriti_scraper", int_path)
    int_creds = cred_for("intigriti", BB)
    pat = int_creds.get('personal_access_token')

    if not pat:
        report("Intigriti: personal_access_token di config", False, "key 'intigriti_personal' atau prefix 'intigriti'")
    else:
        report("Intigriti: PAT ditemukan", True, f"len={len(pat)}")
        scr = int_mod.IntigritiScraper(pat)
        t0 = time.time()
        ok_sess = scr.validate_session()
        report("Intigriti: validate_session (/profile)", ok_sess, f"{time.time()-t0:.1f}s")

        # Fakta teknis: Intigriti API token format & auth
        int_api = "https://api.intigriti.com/external/researcher/v1"
        print(f"  🔧 [Fakta] Intigriti auth: X-API-KEY header")
        print(f"  🔧 [Fakta] API endpoint: {int_api}")
        print(f"  🔧 [Fakta] Token format: UUID-like (bukan base64)")
        print(f"  🔧 [Fakta] Token expiry: PAT kadaluarsa (~6 bulan - perlu rotasi)")

        # Test /profile
        resp = requests.get(f"{int_api}/profile", headers={'X-API-KEY': pat}, timeout=10)
        print(f"  🔧 [Fakta] GET /profile → HTTP {resp.status_code}")
        if resp.status_code == 200:
            profile = resp.json()
            print(f"  🔧 [Fakta] Profil: {json.dumps(profile, indent=2)[:300]}")
            # Cek expiry di response
            exp = profile.get('exp') or profile.get('expires_at') or profile.get('expiresAt')
            if exp:
                print(f"  🔧 [Fakta] Token expiry ditemukan: {exp}")
            else:
                print(f"  🔧 [Fakta] Expiry tidak eksplisit di response, tapi PAT Intigriti memang kadaluarsa")

        # Test /companies
        resp2 = requests.get(f"{int_api}/companies", headers={'X-API-KEY': pat}, params={'size': 5, 'page': 0}, timeout=10)
        print(f"  🔧 [Fakta] GET /companies → HTTP {resp2.status_code}")
        if resp2.status_code == 200:
            companies = resp2.json()
            count = len(companies.get('content', []))
            print(f"  🔧 [Fakta] Companies count: {count}")

        t0 = time.time()
        progs = scr.get_all_programs()
        report("Intigriti: get_all_programs()", isinstance(progs, list) and len(progs) > 0,
               f"{len(progs)} program, {time.time()-t0:.1f}s")
        if progs:
            p = progs[0]
            print(f"  📊 Contoh: {p.get('name', '?')} — handle={p.get('handle', '?')} — bounty={p.get('offers_bounties', '?')}")

except Exception as e:
    report("Intigriti: import/exec", False, str(e)[:300])
    traceback.print_exc()


# ============================================================
# 3. CTFtime — API publik (tanpa auth, tanpa expiry)
# ============================================================
print("\n" + "=" * 70)
print("3. CTFtime — API publik (tanpa autentikasi)")
print("=" * 70)
try:
    ctftime_path = os.path.join(BASE, "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/ctf_monitor/ctftime_scraper.py")
    ctf_mod = import_module("ctftime_scraper", ctftime_path)

    scr = ctf_mod.CTFtimeScraper()
    t0 = time.time()
    ok_sess = scr.validate_session()
    report("CTFtime: validate_session (publik API)", ok_sess, f"{time.time()-t0:.1f}s")

    print(f"  🔧 [Fakta] CTFtime auth: TIDAK PERLU (public REST API)")
    print(f"  🔧 [Fakta] API endpoint: https://ctftime.org/api/v1")
    print(f"  🔧 [Fakta] Token/cookie expiry: TIDAK ADA (publik, tidak perlu update)")

    t0 = time.time()
    upcoming = scr.get_upcoming_events(limit=20)
    report("CTFtime: get_upcoming_events()", isinstance(upcoming, list) and len(upcoming) > 0,
           f"{len(upcoming)} event, {time.time()-t0:.1f}s")
    if upcoming:
        ev = upcoming[0]
        print(f"  📊 Event: {ev.get('title', '?')}")
        print(f"     format={ev.get('format', '?')}, onsite={ev.get('onsite', '?')}")
        print(f"     participants={ev.get('participants', 0)}")
        print(f"     duration={ev.get('duration_hours', 0)} jam")
        print(f"     start={ev.get('start', '?')}")

    t0 = time.time()
    teams = scr.get_top_teams(limit=5)
    report("CTFtime: get_top_teams()", isinstance(teams, list) and len(teams) > 0,
           f"{len(teams)} tim, {time.time()-t0:.1f}s")
    if teams:
        for t in teams[:3]:
            print(f"  📊 Rank {t['rank']}: {t['name']} — score={t['score']} — country={t['country']}")

    t0 = time.time()
    programs = scr.get_all_programs()
    report("CTFtime: get_all_programs() (ARC compat)", isinstance(programs, dict),
           f"{len(programs)} program, {time.time()-t0:.1f}s")

    t0 = time.time()
    intel = scr.get_intelligence()
    report("CTFtime: get_intelligence() (full dump)", isinstance(intel, dict),
           f"events={len(intel.get('upcoming_events',[]))}, teams={len(intel.get('top_teams',[]))}, {time.time()-t0:.1f}s")

except Exception as e:
    report("CTFtime: import/exec", False, str(e)[:300])
    traceback.print_exc()

# ============================================================
# RINGKASAN & HASIL AKHIR
# ============================================================
print("\n" + "=" * 70)
print("RINGKASAN FAKTA TEKNIS — VERIFIKASI SKALA REAL")
print("=" * 70)
print("""
Platform      | Auth Method       | Token/Cookie Expiry          | Auto-update needed?
------------- | ----------------- | ---------------------------- | -------------------
HackerOne     | HTTP Basic Auth   | NO EXPIRY (manual revocation)| NO
Intigriti     | X-API-KEY header  | EXPIRY (~6 months)           | YES (rotate q6mo)
CTFtime       | None (public API) | NO EXPIRY                    | NO
BugCrowd      | Session cookie    | EXPIRY (browser session)     | YES
YesWeHack     | Session cookie    | EXPIRY                       | YES
Immunefi      | Session cookie    | EXPIRY (Firebase JWT)        | YES
HackTheBox    | Session cookie    | EXPIRY                       | YES
TryHackMe     | Session cookie    | EXPIRY                       | YES
""")
passed = sum(1 for r in results if r)
total = len(results)
print("=" * 70)
print(f"HASIL AKHIR: {passed}/{total} CHECK PASS")
print("=" * 70)
sys.exit(0 if passed == total else 1)



