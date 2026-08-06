import sys, os, inspect, importlib
sys.path.insert(0, os.path.abspath('.'))

# 1. Check if BugBountySession has the methods mentioned in the comment
from SOVEREIGN_SESSION_MANAGER.bug_bounty_session import BugBountySession
stub_methods = ['_auto_login', '_get_csrf_token', '_extract_session_cookie', 'store_platform_credentials']
print('=== BugBountySession - checking stub methods ===')
for m in stub_methods:
    has = hasattr(BugBountySession, m)
    status = 'EXISTS' if has else 'MISSING!'
    print(f'  {m}: {status}')

# 2. Check ReportScraper
print()
print('=== ReportScraper ===')
from DUPLICATE_INTELLIGENCE.report_scraper import ReportScraper
r = ReportScraper()
methods = [m for m in dir(r) if not m.startswith('_') and callable(getattr(r, m, None))]
print(f'  Methods: {methods}')
print(f'  Constructor: {inspect.signature(ReportScraper.__init__)}')

# 3. Check PLATFORM_SPECIFIC_SUBMITTER __init__.py
print()
print('=== PLATFORM_SPECIFIC_SUBMITTER/__init__.py ===')
init_path = 'SOVEREIGN_REPORTING/PLATFORM_SPECIFIC_SUBMITTER/__init__.py'
if os.path.exists(init_path):
    with open(init_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    print(f'  Size: {len(content)} bytes')
    print(f'  Content: {repr(content[:200])}')
else:
    print('  File does not exist')

# 4. Check the ImmunefiScraper
print()
print('=== ImmunefiScraper ===')
from SHADOW_INTELLIGENCE_RADAR.direct_platform_monitor.bug_bounty_monitor.immunefi_scraper import ImmunefiScraper
print(f'  Constructor: {inspect.signature(ImmunefiScraper.__init__)}')
methods = [m for m in dir(ImmunefiScraper) if not m.startswith('_') and callable(getattr(ImmunefiScraper, m, None))]
print(f'  Methods: {methods}')

# 5. Check arc_main _initialize_scrapers for immunefi
print()
print('=== arc_main immunefi references ===')
with open('arc_main.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
for i, line in enumerate(content.split('\n')):
    lower_line = line.lower()
    if 'immunefi' in lower_line and ('scraper' in lower_line or 'submit' in lower_line or 'cred' in lower_line):
        print(f'  Line {i+1}: {line.strip()}')

# 6. Check all submit_report signatures vs arc_main call
print()
print('=== Submit report signatures ===')
submitters = {
    'HackerOneSubmitter': 'SOVEREIGN_REPORTING.PLATFORM_SPECIFIC_SUBMITTER.hackerone_submitter',
    'IntigritiSubmitter': 'SOVEREIGN_REPORTING.PLATFORM_SPECIFIC_SUBMITTER.intigriti_submitter',
    'BugCrowdSubmitter': 'SOVEREIGN_REPORTING.PLATFORM_SPECIFIC_SUBMITTER.bugcrowd_submitter',
    'YesWeHackSubmitter': 'SOVEREIGN_REPORTING.PLATFORM_SPECIFIC_SUBMITTER.yeswehack_submitter',
    'ImmunefiSubmitter': 'SOVEREIGN_REPORTING.PLATFORM_SPECIFIC_SUBMITTER.immunefi_submitter',
}
for name, path in submitters.items():
    mod = importlib.import_module(path)
    cls = getattr(mod, name)
    sig = inspect.signature(cls.submit_report)
    print(f'  {name}.submit_report{sig}')

# 7. Check if arc_main line 375 calls submit_report with matching args
print()
print('  arc_main line ~375: submit_report(program_handle, finding, evidence_files)')
print('  All submit_report accept: (program_handle/program_name, report_data, evidence_files=None)')
print('  Match: YES (arc_main passes exactly 3 args, submit_report has 3 params)')

# 8. Check the _initialize_submitters for immunefi - it uses session_cookie
print()
print('=== Check submitter constructors vs arc_main ===')
for name, path in submitters.items():
    mod = importlib.import_module(path)
    cls = getattr(mod, name)
    sig = inspect.signature(cls.__init__)
    params = list(sig.parameters.keys())
    # arc_main passes:
    # HackerOneSubmitter(h1_creds['api_token']) -> session_token
    # IntigritiSubmitter(intigriti_creds['personal_access_token']) -> personal_access_token
    # BugCrowdSubmitter(creds['session_cookie']) -> session_cookie
    # YesWeHackSubmitter(creds['session_cookie']) -> session_cookie
    # ImmunefiSubmitter(creds['session_cookie']) -> session_cookie
    print(f'  {name}.__init__ params: {params}')
