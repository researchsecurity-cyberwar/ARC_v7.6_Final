#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Functional test for CTFtimeScraper - verifies live API connectivity
and all methods return correct data structures.
"""
import sys, os, json, time

sys.path.insert(0, os.path.abspath('.'))

passed = 0
total = 0

def check(name, ok, detail=""):
    global passed, total
    total += 1
    if ok:
        passed += 1
    mark = "OK" if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" -- {detail}" if detail else ""))

print("=" * 70)
print("1. CTFtimeScraper - import & instantiate")
print("=" * 70)
try:
    from SHADOW_INTELLIGENCE_RADAR.direct_platform_monitor.ctf_monitor.ctftime_scraper import CTFtimeScraper
    scr = CTFtimeScraper()
    check("import & init (no credentials needed)", True, "CTFtimeScraper created")
except Exception as e:
    check("import & init", False, str(e)[:200])
    sys.exit(1)

t0 = time.time()
ok = scr.validate_session()
check(f"validate_session (public API)", ok, f"{time.time()-t0:.1f}s")

t0 = time.time()
upcoming = scr.get_upcoming_events(limit=20)
check("get_upcoming_events() returns list", isinstance(upcoming, list), f"{len(upcoming)} events, {time.time()-t0:.1f}s")
if upcoming:
    ev = upcoming[0]
    ev_keys = sorted(ev.keys())
    expected_keys = {'id', 'title', 'start', 'finish', 'duration_hours', 'format', 'onsite', 'participants', 'organizers', 'url', 'ctf_url'}
    check("event has expected keys", expected_keys.issubset(set(ev_keys)), f"missing: {expected_keys - set(ev_keys)}")
    print(f"  Sample: {ev.get('title', '?')} | format={ev.get('format', '?')} | onsite={ev.get('onsite', '?')} | participants={ev.get('participants', 0)}")

t0 = time.time()


t0 = time.time()
programs = scr.get_all_programs()
check("get_all_programs() returns dict", isinstance(programs, dict), f"{len(programs)} programs, {time.time()-t0:.1f}s")
if programs:
    k = list(programs.keys())[0]
    v = programs[k]
    print(f"  Sample: {k} -> name={v.get('name', '?')} | platform={v.get('platform', '?')} | status={v.get('status', '?')}")
    prog_keys = set(v.keys())
    expected_prog_keys = {'name', 'url', 'platform', 'status', 'start', 'finish', 'format', 'duration_hours'}
    check("program entry has expected keys", expected_prog_keys.issubset(prog_keys), f"missing: {expected_prog_keys - prog_keys}")

t0 = time.time()
intel = scr.get_intelligence()
check("get_intelligence() returns dict", isinstance(intel, dict), f"source={intel.get('source')}")
if intel:
    check("intelligence has upcoming_events", 'upcoming_events' in intel, f"{len(intel.get('upcoming_events', []))} events")
    check("intelligence has top_teams", 'top_teams' in intel, f"{len(intel.get('top_teams', []))} teams")
    check("intelligence has past_events", 'past_events' in intel, f"{len(intel.get('past_events', []))} events")
    check("intelligence has timestamp", 'timestamp' in intel, str(intel.get('timestamp')))

if upcoming and upcoming[0].get('id'):
    ev_id = upcoming[0]['id']
    t0 = time.time()
    detail = scr.get_event_by_id(ev_id)
    check(f"get_event_by_id({ev_id})", isinstance(detail, dict) and len(detail) > 0, f"{len(detail)} fields, {time.time()-t0:.1f}s")
    if detail:
        print(f"  title={detail.get('title', '?')} | format={detail.get('format', '?')}")
        print(f"  organizers={detail.get('organizers', [])[:3]} | participants={detail.get('participants', 0)}")
        print(f"  duration_hours={detail.get('duration_hours', 0)} | prizes={detail.get('prizes', '?')[:50]}")

print()
print("=" * 70)
print("2. arc_main.py integration check")
print("=" * 70)
try:
    from SHADOW_INTELLIGENCE_RADAR.direct_platform_monitor.ctf_monitor.ctftime_scraper import CTFtimeScraper
    check("CTFtimeScraper accessible from arc_main import path", True)
    arc_main_path = os.path.join(os.path.abspath('.'), 'arc_main.py')
    with open(arc_main_path, encoding='utf-8') as f:
        arc_src = f.read()
    check("arc_main.py imports CTFtimeScraper", 'from SHADOW_INTELLIGENCE_RADAR.direct_platform_monitor.ctf_monitor.ctftime_scraper import CTFtimeScraper' in arc_src)
    check("arc_main.py initializes CTFtimeScraper in _initialize_scrapers", "self.scrapers['ctftime'] = CTFtimeScraper()" in arc_src)
except Exception as e:
    check("arc_main integration", False, str(e)[:200])

print()
print("=" * 70)
print(f"RESULT: {passed}/{total} checks PASSED")
print("=" * 70)
sys.exit(0 if passed == total else 1)

teams = scr.get_top_teams(limit=10)
check("get_top_teams() returns list", isinstance(teams, list), f"{len(teams)} teams, {time.time()-t0:.1f}s")
if teams:
    for t in teams[:3]:
        print(f"  Rank {t.get('rank')}: {t.get('name')} -- score={t.get('score')} -- country={t.get('country')}")
    team_keys = sorted(teams[0].keys())
    expected_team_keys = {'rank', 'name', 'score', 'country', 'organization', 'team_id'}
    check("team entry has expected keys", expected_team_keys.issubset(set(team_keys)), f"missing: {expected_team_keys - set(team_keys)}")