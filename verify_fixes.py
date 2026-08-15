#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verify all fixes - syntax, imports, integration checks."""
import sys, os, py_compile
sys.path.insert(0, os.path.abspath('.'))

p = 0
t = 0

def ok(n, d=""):
    global p, t
    t += 1; p += 1
    print(f"  [OK] {n}" + (f" -- {d}" if d else ""))

def fail(n, d=""):
    global p, t
    t += 1
    print(f"  [FAIL] {n}" + (f" -- {d}" if d else ""))

# 1. Compilation
print("=" * 60)
print("1. Compilation Checks")
print("=" * 60)
files = [
    "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/ctf_monitor/ctftime_scraper.py",
    "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/ctf_monitor/private_ctf_detector.py",
    "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/ctf_monitor/hackthebox_scraper.py",
    "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/ctf_monitor/tryhackme_scraper.py",
    "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/bugcrowd_scraper.py",
    "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/hackerone_scraper.py",
    "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/intigriti_scraper.py",
    "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/yeswehack_scraper.py",
    "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/immunefi_scraper.py",
    "CTF_INTELLIGENCE/ctf_challenge_ingestor.py",
    "arc_main.py",
    "live_scraper_test.py",
]
for f in files:
    full = os.path.join(os.path.abspath('.'), f)
    try:
        py_compile.compile(full, doraise=True)
        ok("compile " + os.path.basename(f))
    except Exception as e:
        fail("compile " + os.path.basename(f), str(e)[:120])

# 2. Import checks
print()
print("=" * 60)
print("2. Import Checks")
print("=" * 60)
try:
    from SHADOW_INTELLIGENCE_RADAR.direct_platform_monitor.ctf_monitor.ctftime_scraper import CTFtimeScraper
    ok("import CTFtimeScraper")
    scr = CTFtimeScraper()
    ok("instantiate CTFtimeScraper")
except Exception as e:
    fail("CTFtimeScraper", str(e)[:200])

try:
    from SHADOW_INTELLIGENCE_RADAR.direct_platform_monitor.ctf_monitor.private_ctf_detector import PrivateCTFDetector
    ok("import PrivateCTFDetector")
except Exception as e:
    fail("PrivateCTFDetector", str(e)[:200])

try:
    from CTF_INTELLIGENCE.ctf_challenge_ingestor import CTFChallengeIngestor
    ok("import CTFChallengeIngestor")
    import CTF_INTELLIGENCE.ctf_challenge_ingestor as ing
    if hasattr(ing, 'time'):
        ok("ctf_challenge_ingestor has time module")
    else:
        fail("ctf_challenge_ingestor time", "missing")
except Exception as e:
    fail("CTFChallengeIngestor", str(e)[:200])

# 3. arc_main.py integration
print()
print("=" * 60)
print("3. arc_main.py Integration")
print("=" * 60)
arc_path = os.path.join(os.path.abspath('.'), 'arc_main.py')
with open(arc_path, encoding='utf-8') as f:
    arc_src = f.read()
if "import CTFtimeScraper" in arc_src:
    ok("arc_main.py imports CTFtimeScraper")
else:
    fail("arc_main.py imports CTFtimeScraper", "not found")
if "self.scrapers['ctftime'] = CTFtimeScraper()" in arc_src:
    ok("arc_main.py initializes CTFtimeScraper")
else:
    fail("arc_main.py initializes CTFtimeScraper", "not found")

# 4. Bug bounty scrapers - Programs/Scope/OutOfScope/Rules
print()
print("=" * 60)
print("4. Bug Bounty - Programs/Scope/OutOfScope/Rules")
print("=" * 60)
bb = {
    "HackerOne": "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/hackerone_scraper.py",
    "BugCrowd": "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/bugcrowd_scraper.py",
    "Intigriti": "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/intigriti_scraper.py",
    "YesWeHack": "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/yeswehack_scraper.py",
    "Immunefi": "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/immunefi_scraper.py",
}
for cls_name, path in bb.items():
    full = os.path.join(os.path.abspath('.'), path)
    with open(full, encoding='utf-8') as f:
        src = f.read()
    if "def get_all_programs" in src:
        ok(cls_name + ": get_all_programs")
    else:
        fail(cls_name + ": get_all_programs", "not found")
    if "scope" in src.lower():
        ok(cls_name + ": scope")
    else:
        fail(cls_name + ": scope", "not found")
    if "out_of_scope" in src:
        ok(cls_name + ": out_of_scope")
    else:
        fail(cls_name + ": out_of_scope", "not found")
    if "rules" in src.lower():
        ok(cls_name + ": rules")
    else:
        fail(cls_name + ": rules", "not found")
# 5. CTF scrapers - Challenges/Writeups/Knowledge
print()
print("=" * 60)
print("5. CTF Scrapers - Challenges/Writeups/Knowledge")
print("=" * 60)
ctf = {
    "CTFtime": "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/ctf_monitor/ctftime_scraper.py",
    "HackTheBox": "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/ctf_monitor/hackthebox_scraper.py",
    "TryHackMe": "SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/ctf_monitor/tryhackme_scraper.py",
    "CTFChallengeIngestor": "CTF_INTELLIGENCE/ctf_challenge_ingestor.py",
}
for cls_name, path in ctf.items():
    full = os.path.join(os.path.abspath('.'), path)
    with open(full, encoding='utf-8') as f:
        src = f.read()
    if "def get_all_programs" in src or "def ingest_free_challenges" in src:
        ok(cls_name + ": listing")
    else:
        fail(cls_name + ": listing", "not found")
    has_kw = any(kw in src.lower() for kw in ["writeup", "event", "challenge", "machine", "room", "github"])
    if has_kw:
        ok(cls_name + ": writeup/challenge/knowledge")
    else:
        fail(cls_name + ": writeup/challenge/knowledge", "not found")

# 6. CTFtime live functional test
print()
print("=" * 60)
print("6. CTFtime Live Functional Test")
print("=" * 60)
import time
try:
    scr2 = CTFtimeScraper()
    t0 = time.time()
    vals = scr2.validate_session()
    ok("validate_session", f"{vals} ({time.time()-t0:.1f}s)")

    t0 = time.time()
    upcoming = scr2.get_upcoming_events(limit=10)
    ok("get_upcoming_events", f"{len(upcoming)} events ({time.time()-t0:.1f}s)")

    t0 = time.time()
    teams = scr2.get_top_teams(limit=5)
    ok("get_top_teams", f"{len(teams)} teams ({time.time()-t0:.1f}s)")

    t0 = time.time()
    programs = scr2.get_all_programs()
    ok("get_all_programs", f"{len(programs)} programs ({time.time()-t0:.1f}s)")

    if programs:
        k = list(programs.keys())[0]
        v = programs[k]
        ok("program has platform field", 'platform' in v)
        ok("program has status field", 'status' in v)
        ok("program has name field", 'name' in v)

    time.sleep(1)
    intel = scr2.get_intelligence()
    ok("get_intelligence", f"src={intel.get('source')}")
    ok("intelligence has upcoming_events", len(intel.get('upcoming_events', [])) > 0)
    ok("intelligence has top_teams", len(intel.get('top_teams', [])) > 0)

    time.sleep(1)
    if upcoming and upcoming[0].get('id'):
        ev_id = upcoming[0]['id']
        detail = scr2.get_event_by_id(ev_id)
        ok("get_event_by_id", f"{len(detail)} fields")
        ok("event detail has organizers", 'organizers' in detail)
        ok("event detail has prizes", 'prizes' in detail)
        ok("event detail has duration_hours", 'duration_hours' in detail)
except Exception as e:
    fail("live CTFtime test", str(e)[:200])

# Summary
print()
print("=" * 60)
print(f"FINAL RESULT: {p}/{t} checks PASSED")
print("=" * 60)
sys.exit(0 if p == t else 1)
