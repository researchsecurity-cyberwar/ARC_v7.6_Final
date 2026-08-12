#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ARC module verification - checks structure and compatibility of each scraper."""
import sys, os, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE = os.path.dirname(os.path.abspath(__file__))
results = []

def check(name, condition, detail=""):
    status = "✅" if condition else "❌"
    results.append((name, condition))
    print(f"  {status} {name} {('— ' + detail) if detail else ''}")

print("=" * 80)
print("ARC v7.6 FINAL - VERIFIKASI TOTAL MODULE BUG BOUNTY & CTF")
print("=" * 80)

print(f"\n[1] INISIALISASI SCRAPER DI arc_main.py")
print("-" * 60)
with open(os.path.join(BASE, 'arc_main.py'), encoding='utf-8') as f:
    main_code = f.read()

check("HackerOne scraper oleh api_token", 
      "self.scrapers['hackerone'] = HackerOneScraper(h1_creds['api_token'])" in main_code)
check("Intigriti scraper oleh personal_access_token",
      "self.scrapers['intigriti'] = IntigritiScraper(intigriti_creds['personal_access_token'])" in main_code)
check("BugCrowd scraper oleh session_cookie",
      "self.scrapers['bugcrowd'] = BugCrowdScraper(creds['session_cookie'])" in main_code)
check("YesWeHack scraper oleh session_cookie",
      "self.scrapers['yeswehack'] = YesWeHackScraper(creds['session_cookie'])" in main_code)
check("Immunefi scraper oleh session_cookie",
      "self.scrapers['immunefi'] = ImmunefiScraper(creds['session_cookie'])" in main_code)
check("HackTheBox scraper (CTF) dari config",
      "get_platform_credentials('hackthebox')" in main_code)
check("TryHackMe scraper (CTF) dari config",
      "get_platform_credentials('tryhackme')" in main_code)
check("Google VRP terdaftar sebagai scraper",
      "self.scrapers['google_vrp'] = self.google_vrp_integrator" in main_code)

print(f"\n[2] LOOP INTELIJEN (_update_intelligence_feed)")
print("-" * 60)
check("Loop memanggil scraper.get_all_programs()",
      "programs = scraper.get_all_programs()" in main_code)
check("Loop print jumlah program per platform",
      "OK Found {len(programs)} programs on {platform}" in main_code)
check("Loop menangkap exception per platform",
      "except Exception as e:" in main_code)
check("Google VRP feed terpisah", "get_all_google_programs()" in main_code)
check("Cache program intelligence", "_cache_program_intelligence" in main_code)
print(f"\n[3] MODULE-LEVEL SCRAPER VERIFICATION")
print("-" * 60)

def read_m(path):
    with open(os.path.join(BASE, path), encoding='utf-8') as f:
        return f.read()

print("\n[3a] HackerOneScraper")
h1 = read_m('SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/hackerone_scraper.py')
check("get_all_programs(include_inactive)", "def get_all_programs(self, include_inactive=False)" in h1)
check("API /hackers/programs", "/hackers/programs" in h1)
check("Pagination", "page[size]" in h1 and "page[number]" in h1)
check("Filter open programs", "program_info['state'] == 'open'" in h1)
check("Check reports via /hackers/reports", "/hackers/reports" in h1)
check("Get scope via APIs", "/structured_scopes" in h1)
check("Validate session via /me", "/me" in h1)
check("Fallback public programs", "_get_public_programs_only" in h1)

print("\n[3b] IntigritiScraper")
intg = read_m('SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/intigriti_scraper.py')
check("get_all_programs(include_inactive)", "def get_all_programs(self, include_inactive=False)" in intg)
check("API /companies", "self.base_url}/companies" in intg)
check("Header X-API-KEY", "X-API-KEY" in intg)
check("Pagination", "'size': 100" in intg and "'page': page" in intg)
check("Filter isOpen", "isOpen" in intg)
check("Get scope via /domains", "/domains" in intg)
check("Check reports via /reports", "/reports" in intg)
check("Handles 401 & 403", "response.status_code == 401" in intg and "response.status_code == 403" in intg)
bc = read_m('SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/bugcrowd_scraper.py')
check("get_all_programs()", "def get_all_programs(self):" in bc)
check("Endpoint /dashboard", "/dashboard" in bc)
check("Cookie _bugcrowd_session", "_bugcrowd_session" in bc)
check("Reject 'Sign in'", "'Sign in'" in bc)
check("Handles 401", "== 401" in bc or "status_code == 401" in bc)
check("Get program details (scope)", "def get_program_details" in bc)
check("Extract rules", "_extract_bugcrowd_rules" in bc)
check("Limit 20 programs", "[:20]" in bc)
print("\n[3d] YesWeHackScraper")
ywh = read_m('SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/yeswehack_scraper.py')
check("get_all_programs()", "def get_all_programs(self):" in ywh)
check("Endpoint /dashboard", "/dashboard" in ywh)
check("Cookie 'session'", "cookies.set('session'" in ywh)
check("Reject 'Login'", "'Login'" in ywh)
check("Get program details", "def get_program_details" in ywh)
check("Parse scope", "_parse_scope_from_text" in ywh)
check("Extract rules", "_extract_yeswehack_rules" in ywh)
check("Limit 15 programs", "[:15]" in ywh)

print("\n[3e] ImmunefiScraper")
imm = read_m('SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/immunefi_scraper.py')
check("get_all_programs()", "def get_all_programs(self):" in imm)
check("Endpoint /bounties", "/bounties" in imm)
check("Cookie parsing split ;", "split('; ')" in imm)
check("Get program details", "def get_program_details" in imm)
check("Parse DeFi scope (address)", "0x[a-fA-F0-9]{40}" in imm)
check("Extract economic rules", "_extract_immunefi_rules" in imm)
check("Reentrancy/flashloan detect", "reentrancy" in imm and "flash loan" in imm)
check("Limit 10 programs", "[:10]" in imm)

print("\n[3f] HackTheBoxScraper (CTF)")
htb = read_m('SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/ctf_monitor/hackthebox_scraper.py')
check("get_all_programs() -> dict", "def get_all_programs(self) -> dict" in htb)
check("Cookie PHPSESSID", "PHPSESSID" in htb)
check("Get active machines", "def get_active_machines" in htb)
check("Check new challenges", "def check_new_challenges" in htb)
check("Kombinasi machines+challenges dict", "'type': 'machine'" in htb and "programs = {}" in htb)
check("Validate session", "def validate_session" in htb)

print("\n[3g] TryHackMeScraper (CTF)")
thm = read_m('SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/ctf_monitor/tryhackme_scraper.py')
check("get_all_programs() -> dict", "def get_all_programs(self) -> dict" in thm)
check("Cookie connect.sid", "connect.sid" in thm)
check("Get available rooms", "def get_available_rooms" in thm)
check("Get room details", "def get_room_details" in thm)
check("Rooms as programs dict", "room.get('code'" in thm and "programs = {}" in thm)
check("Validate session", "def validate_session" in thm)

print("\n[3g2] Fix Parsing Terbaru (BugCrowd /engagements, HTB/THM link HTML)")
bc2 = read_m('SHADOW_INTELLIGENCE_RADAR/direct_platform_monitor/bug_bounty_monitor/bugcrowd_scraper.py')
check("BugCrowd: parse /engagements juga",
      "/(?:programs|engagements)/" in bc2)
check("BugCrowd: deteksi redirect login Okta",
      "redirected_to_login" in bc2)
check("BugCrowd: fallback publik saat session expired",
      "_get_public_programs_only()" in bc2)
check("HTB: parse link /machines/<slug>",
      "re.findall(r'href=" in htb and "/machines/" in htb)
check("HTB: parse link /challenges/<slug>",
      "re.findall(r'href=" in htb and "/challenges/" in htb)
check("THM: parse link /room/<code>",
      "re.findall(r'href=" in thm and "/room/" in thm)

print("\n[3h] GoogleVRPIntegrator")
gvrp = read_m('BROWSER_SECURITY_RESEARCH/google_vrp_integrator.py')
check("get_all_programs() alias compat", "def get_all_programs(self) -> Dict[str, dict]" in gvrp)
check("get_all_google_programs() -> dict", "def get_all_google_programs(self" in gvrp)
check("Cache <1 jam", "cache_fresh" in gvrp)
check("Fallback config staus", "'status': 'fallback'" in gvrp)
check("Simpan cache ke disk", "_save_cache" in gvrp)
print(f"\n[4] CONFIG CREDENTIAL MAPPING")
print("-" * 60)
with open(os.path.join(BASE, 'confiq.yaml'), encoding='utf-8') as f:
    cfgf = f.read()

expected_creds = {
    'hackerone': 'hackerone_main', 'intigriti': 'intigriti_personal',
    'bugcrowd': 'bugcrowd_corp', 'yeswehack': 'yeswehack_researcher',
    'immunefi': 'immunefi_bounty', 'bughunters_google': 'bughunters_google',
    'hackthebox': 'hackthebox_pro', 'tryhackme': 'tryhackme_student'
}
for platform, cfg_key in expected_creds.items():
    hint = "harus di credentials.bug_bounty atau credentials.ctf"
    check(f"config.yaml punya key '{cfg_key}' (untuk {platform})",
          cfg_key in cfgf,
          hint)
check("NVD API key di config", "nvd:" in cfgf)
check("Shodan API key di config", "shodan:" in cfgf)
check("GitHub token di config", "github:" in cfgf)
check("Telegram bot_token di config", "bot_token:" in cfgf)
check("Telegram chat_id di config", "chat_id:" in cfgf)

print(f"\n[5] FIX ERROR success_probability (dict * int)")
print("-" * 60)
check("sukses_probiability guard (isinstance dict) di arc_main.py",
      "if isinstance(success_prob, dict)" in main_code)
check("Konversi ke float", "success_prob = float(success_prob)" in main_code)

# Fix baru: normalisasi probabilitas di SUMBER (orchestrator) -- defense-in-depth
# agar success_probability SELALU float di semua konsumen (arc_main, closed_loop_feedback,
# learning_mixin, xss_detector, dst). Cegah 'TypeError: dict * int' yg bukan dari arc_main.
orch_path = os.path.join(BASE, "UNIFIED_LEARNING_ENGINE", "self_learning_orchestrator.py")
orch_code = ""
if os.path.exists(orch_path):
    try:
        with open(orch_path, encoding="utf-8") as f:
            orch_code = f.read()
    except Exception:
        orch_code = ""
check("self_learning_orchestrator.py terbaca", bool(orch_code))
check("Helper _normalize_probability ada",
      "_normalize_probability" in orch_code)
check("get_learning_recommendations pakai _normalize_probability",
      "self._normalize_probability(" in orch_code)
check("Alias /star -> /start di telegram_notifier",
      "('/start', '/star')" in open(
          os.path.join(BASE, "DIALOGIC_COPILLOT", "PLATFORM_COMMUNICATOR", "telegram_notifier.py"),
              encoding="utf-8").read())




print("\n[6] BRIDGE: Telegram command + human-in-the-loop (human_in-the-loop_gate)")
print("-" * 60)
notifier_code = read_m("DIALOGIC_COPILLOT/PLATFORM_COMMUNICATOR/telegram_notifier.py")
check("TelegramNotifier punya handle_telegram_command", "def handle_telegram_command" in notifier_code)
check("TelegramNotifier.handle_telegram_command route /approve_op_<id> ke gate",
      "/approve_" in notifier_code and "handle_telegram_approval" in notifier_code)
check("TelegramNotifier punya set_human_in_the_loop_gate", "set_human_in_the_loop_gate" in notifier_code)
check("TelegramNotifier punya set_session_manager", "set_session_manager" in notifier_code)
check("TelegramNotifier punya _start_autonomous_ops / /stop / /help",
      "_start_autonomous_ops" in notifier_code and "stop" in notifier_code and "help" in notifier_code)

sac_code = read_m("TOOL_ORCHERATION/INTELLIGENT_TOOL_MANAGER/session_approval_controller.py".replace("ORCHERATION", "ORCHESTRATION"))
check("SessionApprovalController punya parse_command (dukung /approve<spasi><id>)",
      "def parse_command" in sac_code and "rid = tokens" in sac_code)
check("SessionApprovalController punya handle_text", "def handle_text" in sac_code)
check("SessionApprovalController.handle_text bridge ke gate (/approve_op_)",
      "pending_approvals" in sac_code and "/approve_op_" in sac_code)

hitl_code = read_m("COGNITIVE_CORE/human_in_the_loop_gate.py")
check("HumanInTheLoopGate punya requires_approval", "def requires_approval" in hitl_code)
check("HumanInTheLoopGate punya request_approval (blocking sampai approved/rejected)",
      "def request_approval" in hitl_code)
check("HumanInTheLoopGate punya handle_telegram_approval", "def handle_telegram_approval" in hitl_code)
check("HumanInTheLoopGate.handle_telegram_approval ubah pending_approvals[].approved",
      "approved" in hitl_code and "pending_approvals" in hitl_code)
check("HumanInTheLoopGate.request_approval return True/False setelah keputusan & clean up",
      "del self.pending_approvals" in hitl_code)

passed = sum(1 for _, c in results if c)
failed = len(results) - passed
print("\n" + "=" * 80)
print(f"RESULT: {passed} passed   |  {failed} failed")
print("=" * 80)
if failed == 0:
    print("SEMUA MODULE BUG BOUNTY & CTF TERVERIFIKASI!")
else:
    print("Sebagian gagal. Daftar yang gagal:")
    for nn, cc in results:
        if not cc:
            print(f"   X {nn}")
print("=" * 80)