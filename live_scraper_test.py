#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ARC Live Scraper Test - uji nyata semua scraper bug bounty & CTF
menggunakan kredensial asli dari confiq.yaml (~/.arc/config.yaml).

Setiap scraper diuji: import, init, validate_session, dan get_all_programs.
HTTP timeout pendek (8 detik) agar cepat selesai.
"""
import sys, os, io, time, importlib.util, traceback

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = os.path.dirname(os.path.abspath(__file__))

# --- Lokasi config: prioritas ~/.arc/config.yaml, fallback confiq.yaml di repo ---
CONFIG_CANDIDATES = [
    os.path.expanduser("~/.arc/config.yaml"),
    os.path.join(BASE, "confiq.yaml"),
]
config_path = next((p for p in CONFIG_CANDIDATES if os.path.exists(p)), None)
if not config_path:
    print("❌ Tidak ada config ditemukan (cari ~/.arc/config.yaml atau confiq.yaml)")
    sys.exit(1)

import yaml
with open(config_path, encoding='utf-8') as f:
    CONFIG = yaml.safe_load(f) or {}
BB = CONFIG.get('credentials', {}).get('bug_bounty', {}) or {}
CTF = CONFIG.get('credentials', {}).get('ctf', {}) or {}
print(f"📄 Config: {config_path}")
print(f"   Bug bounty entries: {list(BB.keys())}")
print(f"   CTF entries: {list(CTF.keys())}")

results = []

def report(name, ok, detail=""):
    results.append(ok)
    mark = "✅" if ok else "❌"
    print(f"  {mark} {name}" + (f" — {detail}" if detail else ""))

def import_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def cred_for(platform, section):
    """Cari kredensial platform di section (bug_bounty/ctf), dengan prefix match."""
    if platform in section and isinstance(section[platform], dict):
        return section[platform]
    for k, v in section.items():
        if platform in k and isinstance(v, dict):
            return v
    return {}
# ============================================================
# 1. HACKERONE (API token)
# ============================================================
print("\n" + "=" * 70)
print("1. HACKERONE — API token")
print("=" * 70)
try:
    h1_path = os.path.join(BASE, "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/hackerone_scraper.py")
    h1_mod = import_module("hackerone_scraper", h1_path)
    h1_creds = cred_for("hackerone", BB)
    tok = h1_creds.get('api_token')
    if not tok:
        report("HackerOne: api_token di config", False, "key 'hackerone_main' atau prefix 'hackerone'")
    else:
        report("HackerOne: api_token ditemukan", True, "len=%d" % len(tok))
        scr = h1_mod.HackerOneScraper(tok)
        t0 = time.time()
        ok_sess = scr.validate_session()
        report("HackerOne: validate_session (/me)", ok_sess, f"{time.time()-t0:.1f}s")
        t0 = time.time()
        progs = scr.get_all_programs()
        report("HackerOne: get_all_programs()", isinstance(progs, list) and len(progs) > 0,
               f"{len(progs)} program, {time.time()-t0:.1f}s")
        if progs:
            print(f"      contoh: {progs[0].get('name', '?')} — {progs[0].get('state', '?')}")
except Exception as e:
    report("HackerOne: import/exec", False, str(e)[:200])
    traceback.print_exc()

# ============================================================
# 2. INTRIGITI (Personal Access Token)
# ============================================================
print("\n" + "=" * 70)
print("2. INTRIGITI — Personal Access Token")
print("=" * 70)
try:
    intg_path = os.path.join(BASE, "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/intigriti_scraper.py")
    intg_mod = import_module("intigriti_scraper", intg_path)
    intg_creds = cred_for("intigriti", BB)
    tok = intg_creds.get('personal_access_token')
    if not tok:
        report("Intigriti: personal_access_token di config", False, "key 'intigriti_personal'")
    else:
        report("Intigriti: token ditemukan", True, "len=%d" % len(tok))
        scr = intg_mod.IntigritiScraper(tok)
        t0 = time.time()
        ok_sess = scr.validate_session()
        report("Intigriti: validate_session (/profile)", ok_sess, f"{time.time()-t0:.1f}s")
        t0 = time.time()
        progs = scr.get_all_programs()
        report("Intigriti: get_all_programs()", isinstance(progs, list) and len(progs) > 0,
               f"{len(progs)} program, {time.time()-t0:.1f}s")
        if progs:
            print(f"      contoh: {progs[0].get('name', '?')} — {progs[0].get('state', '?')}")
except Exception as e:
    report("Intigriti: import/exec", False, str(e)[:200])
    traceback.print_exc()
# ============================================================
# 3. BUGGROWD (session cookie)
# ============================================================
print("\n" + "=" * 70)
print("3. BUGGROWD — session cookie")
print("=" * 70)
try:
    bc_path = os.path.join(BASE, "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/bugcrowd_scraper.py")
    bc_mod = import_module("bugcrowd_scraper", bc_path)
    bc_creds = cred_for("bugcrowd", BB)
    ck = bc_creds.get('session_cookie')
    if not ck:
        report("BugCrowd: session_cookie di config", False, "key 'bugcrowd_corp'")
    else:
        report("BugCrowd: session_cookie ditemukan", True, "len=%d" % len(ck))
        scr = bc_mod.BugCrowdScraper(ck)
        t0 = time.time()
        ok_sess = scr.validate_session()
        report("BugCrowd: validate_session (/dashboard)", ok_sess, f"{time.time()-t0:.1f}s")
        t0 = time.time()
        progs = scr.get_all_programs()
        report("BugCrowd: get_all_programs()", isinstance(progs, list) and len(progs) > 0,
               f"{len(progs)} program, {time.time()-t0:.1f}s")
        if progs:
            print(f"      contoh: {progs[0].get('name', '?')} — {progs[0].get('status', '?')}")
except Exception as e:
    report("BugCrowd: import/exec", False, str(e)[:200])
    traceback.print_exc()

# ============================================================
# 4. YESWEHACK (session cookie)
# ============================================================
print("\n" + "=" * 70)
print("4. YESWEHACK — session cookie")
print("=" * 70)
try:
    ywh_path = os.path.join(BASE, "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/yeswehack_scraper.py")
    ywh_mod = import_module("yeswehack_scraper", ywh_path)
    ywh_creds = cred_for("yeswehack", BB)
    ck = ywh_creds.get('session_cookie')
    if not ck:
        report("YesWeHack: session_cookie di config", False, "key 'yeswehack_researcher'")
    else:
        report("YesWeHack: session_cookie ditemukan", True, "len=%d" % len(ck))
        scr = ywh_mod.YesWeHackScraper(ck)
        t0 = time.time()
        ok_sess = scr.validate_session()
        report("YesWeHack: validate_session (/dashboard)", ok_sess, f"{time.time()-t0:.1f}s")
        t0 = time.time()
        progs = scr.get_all_programs()
        report("YesWeHack: get_all_programs()", isinstance(progs, list) and len(progs) > 0,
               f"{len(progs)} program, {time.time()-t0:.1f}s")
        if progs:
            print(f"      contoh: {progs[0].get('name', '?')} — {progs[0].get('status', '?')}")
except Exception as e:
    report("YesWeHack: import/exec", False, str(e)[:200])
    traceback.print_exc()

# ============================================================
# 5. IMMUNEFI (session cookie)
# ============================================================
print("\n" + "=" * 70)
print("5. IMMUNEFI — session cookie")
print("=" * 70)
try:
    imm_path = os.path.join(BASE, "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/immunefi_scraper.py")
    imm_mod = import_module("immunefi_scraper", imm_path)
    imm_creds = cred_for("immunefi", BB)
    ck = imm_creds.get('session_cookie')
    if not ck:
        report("Immunefi: session_cookie di config", False, "key 'immunefi_bounty'")
    else:
        report("Immunefi: session_cookie ditemukan", True, "len=%d" % len(ck))
        scr = imm_mod.ImmunefiScraper(ck)
        t0 = time.time()
        ok_sess = scr.validate_session()
        report("Immunefi: validate_session (/bounties)", ok_sess, f"{time.time()-t0:.1f}s")
        t0 = time.time()
        progs = scr.get_all_programs()
        report("Immunefi: get_all_programs()", isinstance(progs, list) and len(progs) > 0,
               f"{len(progs)} program, {time.time()-t0:.1f}s")
        if progs:
            print(f"      contoh: {progs[0].get('name', '?')} — {progs[0].get('url', '?')}")
except Exception as e:
    report("Immunefi: import/exec", False, str(e)[:200])
    traceback.print_exc()
# ============================================================
# 6. HACKTHEBOX (session cookie, CTF)
# ============================================================
print("\n" + "=" * 70)
print("6. HACKTHEBOX — session cookie (CTF)")
print("=" * 70)
try:
    htb_path = os.path.join(BASE, "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/ctf_monitor/hackthebox_scraper.py")
    htb_mod = import_module("hackthebox_scraper", htb_path)
    htb_creds = cred_for("hackthebox", CTF)
    ck = htb_creds.get('session_cookie')
    if not ck:
        report("HackTheBox: session_cookie di config", False, "key 'hackthebox_pro' di ctf")
    else:
        report("HackTheBox: session_cookie ditemukan", True, "len=%d" % len(ck))
        scr = htb_mod.HackTheBoxScraper(ck)
        t0 = time.time()
        ok_sess = scr.validate_session()
        report("HackTheBox: validate_session (/machines)", ok_sess, f"{time.time()-t0:.1f}s")
        t0 = time.time()
        progs = scr.get_all_programs()
        report("HackTheBox: get_all_programs() -> dict", isinstance(progs, dict) and len(progs) > 0,
               f"{len(progs)} entri, {time.time()-t0:.1f}s")
        if progs:
            k = list(progs.keys())[0]
            print(f"      contoh: {k} — {progs[k].get('type', '?')}")
except Exception as e:
    report("HackTheBox: import/exec", False, str(e)[:200])
    traceback.print_exc()

# ============================================================
# 7. TRYHACKME (session cookie, CTF)
# ============================================================
print("\n" + "=" * 70)
print("7. TRYHACKME — session cookie (CTF)")
print("=" * 70)
try:
    thm_path = os.path.join(BASE, "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/ctf_monitor/tryhackme_scraper.py")
    thm_mod = import_module("tryhackme_scraper", thm_path)
    thm_creds = cred_for("tryhackme", CTF)
    ck = thm_creds.get('session_cookie')
    if not ck:
        report("TryHackMe: session_cookie di config", False, "key 'tryhackme_student' di ctf")
    else:
        report("TryHackMe: session_cookie ditemukan", True, "len=%d" % len(ck))
        scr = thm_mod.TryHackMeScraper(ck)
        t0 = time.time()
        ok_sess = scr.validate_session()
        report("TryHackMe: validate_session (/rooms)", ok_sess, f"{time.time()-t0:.1f}s")
        t0 = time.time()
        progs = scr.get_all_programs()
        report("TryHackMe: get_all_programs() -> dict", isinstance(progs, dict) and len(progs) > 0,
               f"{len(progs)} entri, {time.time()-t0:.1f}s")
        if progs:
            k = list(progs.keys())[0]
            print(f"      contoh: {k} — {progs[k].get('title', '?')}")
except Exception as e:
    report("TryHackMe: import/exec", False, str(e)[:200])
    traceback.print_exc()
# ============================================================
# 8. GOOGLE VRP (integrator, publik tanpa cookie juga jalan)
# ============================================================
print("\n" + "=" * 70)
print("8. GOOGLE VRP — bughunters.google.com")
print("=" * 70)
try:
    gvrp_path = os.path.join(BASE, "BROWSER_SECURITY_RESEARCH/google_vrp_integrator.py")
    gvrp_mod = import_module("google_vrp_integrator", gvrp_path)
    gvrp_creds = cred_for("bughunters_google", BB)
    try:
        scr = gvrp_mod.GoogleVRPIntegrator()
        report("GoogleVRP: init tanpa cookie", True)
    except TypeError as e:
        scr = gvrp_mod.GoogleVRPIntegrator(gvrp_creds.get('session_cookie') or None)
        report("GoogleVRP: init dengan cookie", True)
    t0 = time.time()
    progs = scr.get_all_google_programs()
    report("GoogleVRP: get_all_google_programs()", isinstance(progs, dict) and len(progs) > 0,
           f"{len(progs)} program, {time.time()-t0:.1f}s")
    if isinstance(progs, dict) and progs:
        k = list(progs.keys())[0]
        print(f"      contoh: {k} — {progs[k].get('status', '?')}")
    t0 = time.time()
    progs2 = scr.get_all_programs()
    report("GoogleVRP: get_all_programs() (alias compat)", isinstance(progs2, dict),
           f"{time.time()-t0:.1f}s")
except Exception as e:
    report("GoogleVRP: import/exec", False, str(e)[:200])
    traceback.print_exc()

# ============================================================
# HASIL AKHIR
# ============================================================
passed = sum(1 for r in results if r)
total = len(results)
print("\n" + "=" * 70)
print(f"HASIL AKHIR: {passed}/{total} CHECK PASS")
print("=" * 70)
print("CATATAN: 'Session expired' pada platform cookie = kredensial kedaluwarsa,")
print("bukan bug kode. Update session_cookie di config lalu jalankan ulang.")
sys.exit(0 if passed == total else 1)
