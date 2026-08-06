import os, sys, importlib, inspect, traceback
sys.path.insert(0, os.path.abspath('.'))

issues = []

# 1. Check _initialize_scrapers vs __init__ in arc_main
print('=== 1. _initialize_scrapers NOT called in __init__ ===')
with open('arc_main.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

init_end = content.index('def _initialize_sovereign_reasoner')
init_section = content[:init_end]
has_init_call = '_initialize_scrapers' in init_section
print(f'  _initialize_scrapers called in __init__: {has_init_call}')
call_count = content.count('_initialize_scrapers()')
print(f'  Total calls to _initialize_scrapers(): {call_count}')
if call_count == 1:
    issues.append('BUG: _initialize_scrapers() only called in _update_intelligence_feed(), not in __init__. self.scrapers stays empty {} until first loop iteration.')

# 2. Check auto_integration_engine location
print()
print('=== 2. auto_integration_engine location ===')
old_path = 'INFRASTRUCTURE/auto_integration_engine.py'
new_path = 'TOOL_ORCHESTRATION/INTELLIGENT_TOOL_MANAGER/auto_integration_engine'
print(f'  Old location exists: {os.path.exists(old_path)}')
print(f'  New location exists: {os.path.isdir(new_path)}')

# 3. Check for files referencing auto_integration_engine imports
print()
print('=== 3. Files importing/auto_integration_engine ===')
for root, dirs, files in os.walk('.'):
    if '__pycache__' in root:
        continue
    for f in files:
        if f.endswith('.py'):
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as fh:
                content2 = fh.read()
            if 'auto_integration_engine' in content2:
                rel = os.path.relpath(filepath, '.')
                # Check if it's an import or just a comment
                lines = content2.split('\n')
                for i, line in enumerate(lines):
                    if 'auto_integration_engine' in line and 'import' in line.lower():
                        print(f'  {rel} line {i+1}: {line.strip()[:120]}')

# 4. Check __init__.py content - non-empty ones
print()
print('=== 4. Non-empty __init__.py files ===')
found_nonempty = False
for root, dirs, files in os.walk('.'):
    if '__pycache__' in root:
        continue
    for f in files:
        if f == '__init__.py':
            filepath = os.path.join(root, f)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as fh:
                    file_content = fh.read().strip()
                if file_content:
                    found_nonempty = True
                    rel = os.path.relpath(filepath, '.')
                    print(f'  {rel}: {repr(file_content[:200])}')
            except:
                pass
if not found_nonempty:
    print('  All __init__.py files are empty (standard, OK)')

# 5. Check VULNERABILITY_DETECTORS subdirs
print()
print('=== 5. VULNERABILITY_DETECTORS subdirs __init__.py ===')
vd_subdirs = ['web_security', 'api_security', 'cloud_security', 'mobile_security', 'crypto_web3_security', 'ai_security', 'mfa_security', 'spa_security', 'realtime_security', 'mobile_hybrid_security']
for subdir in vd_subdirs:
    init_file = f'VULNERABILITY_DETECTORS/{subdir}/__init__.py'
    has_init = os.path.exists(init_file)
    exists_dir = os.path.isdir(f'VULNERABILITY_DETECTORS/{subdir}')
    if exists_dir:
        status = 'OK' if has_init else 'MISSING!'
        print(f'  {subdir}/ dir exists, __init__.py: {status}')
        if not has_init:
            issues.append(f'Missing __init__.py in VULNERABILITY_DETECTORS/{subdir}/')
    else:
        print(f'  {subdir}/ dir does NOT exist on disk (in tree but missing)')

# 6. Check pre_fingerprinted_chains
print()
print('=== 6. pre_fingerprinted_chains directory ===')
dir_path = 'CHAIN_INTELLIGENCE_ENGINE/pre_fingerprinted_chains'
if os.path.isdir(dir_path):
    files = os.listdir(dir_path)
    print(f'  Contents: {files}')
    has_init = os.path.exists(os.path.join(dir_path, '__init__.py'))
    print(f'  Has __init__.py: {has_init}')
    if not has_init:
        issues.append('CHAIN_INTELLIGENCE_ENGINE/pre_fingerprinted_chains/ has no __init__.py')
else:
    print('  Directory does not exist')

# 7. Check for imports referencing missing directories
print()
print('=== 7. Imports of missing directories ===')
missing_patterns = ['CTF_INTELLIGENCE.CTF_LOGIN_MANAGER', 'CTF_INTELLIGENCE.DIRECT_CTF_MONITOR', 'VULNERABILITY_DETECTORS.mobile_hybrid_security']
for root, dirs, files in os.walk('.'):
    if '__pycache__' in root:
        continue
    for f in files:
        if f.endswith('.py'):
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as fh:
                content2 = fh.read()
            for missing in missing_patterns:
                if missing in content2:
                    rel = os.path.relpath(filepath, '.')
                    print(f'  {rel} references {missing}')
                    issues.append(f'{rel} imports missing module {missing}')

# 8. Check if any module has a method called get_platform_session or similar that's called but missing
print()
print('=== 8. Check BugBountySession & CTFSession methods ===')
from SOVEREIGN_SESSION_MANAGER.bug_bounty_session import BugBountySession
bb_methods = [m for m in dir(BugBountySession) if not m.startswith('_')]
print(f'  BugBountySession methods: {bb_methods}')

from SOVEREIGN_SESSION_MANAGER.ctf_session import CTFSession
ctf_methods = [m for m in dir(CTFSession) if not m.startswith('_')]
print(f'  CTFSession methods: {ctf_methods}')

from SOVEREIGN_SESSION_MANAGER.vdp_session import VDPSession
vdp_methods = [m for m in dir(VDPSession) if not m.startswith('_')]
print(f'  VDPSession methods: {vdp_methods}')

# 9. Check for hardcoded OS-specific paths
print()
print('=== 9. OS-specific path issues ===')
path_issues = []
for root, dirs, files in os.walk('.'):
    if '__pycache__' in root:
        continue
    for f in files:
        if f.endswith('.py'):
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as fh:
                content2 = fh.read()
            # Check for Windows-specific paths (excluding this script itself)
            if 'deep_analysis.py' not in filepath and ('C:\\' in content2 or 'C:\\Users' in content2):
                rel = os.path.relpath(filepath, '.')
                path_issues.append(rel)
                print(f'  WARNING: Hardcoded Windows path in {rel}')
            # Check for forward-slash paths that might break on Linux
            if '/home/' in content2 and sys.platform == 'win32':
                pass  # Linux paths are fine for Kali Linux deployment
if not path_issues:
    print('  No hardcoded Windows paths found')

# 10. Check the submitters called with wrong arguments
print()
print('=== 10. Submitter constructor args vs arc_main usage ===')
# arc_main: HackerOneSubmitter(h1_creds['api_token']) -> expects session_token
# arc_main: IntigritiSubmitter(intigriti_creds['personal_access_token']) -> expects personal_access_token
# arc_main: BugCrowdSubmitter(creds['session_cookie']) -> expects session_cookie
# Check if submit_report method signature
from SOVEREIGN_REPORTING.PLATFORM_SPECIFIC_SUBMITTER.hackerone_submitter import HackerOneSubmitter
sig = inspect.signature(HackerOneSubmitter.submit_report)
print(f'  HackerOneSubmitter.submit_report{sig}')

from SOVEREIGN_REPORTING.PLATFORM_SPECIFIC_SUBMITTER.immunefi_submitter import ImmunefiSubmitter
sig = inspect.signature(ImmunefiSubmitter.submit_report)
print(f'  ImmunefiSubmitter.submit_report{sig}')

from SOVEREIGN_REPORTING.PLATFORM_SPECIFIC_SUBMITTER.bugcrowd_submitter import BugCrowdSubmitter
sig = inspect.signature(BugCrowdSubmitter.submit_report)
print(f'  BugCrowdSubmitter.submit_report{sig}')

# Check what arc_main calls submit_report with
# Line 375: self.submitters[platform].submit_report(finding.get('program_handle'), finding, finding.get('evidence_files', []))
print()
print('  arc_main calls: submit_report(program_handle, finding, evidence_files)')
print('  Checking if submit_report signatures match...')

# 11. Check telegram_notifier for methods used elsewhere
print()
print('=== 11. TelegramNotifier - methods referenced externally ===')
from DIALOGIC_COPILLOT.PLATFORM_COMMUNICATOR.telegram_notifier import TelegramNotifier
ext_methods = ['set_sovereign_reasoner', 'set_command_interpreter', 'set_conversation_engine', 'set_platform_communicator']
for m in ext_methods:
    has = hasattr(TelegramNotifier, m)
    print(f'  {m}: {"exists" if has else "MISSING"}')

# 12. Check for the _initialize_scrapers method body - does it work?
print()
print('=== 12. _update_intelligence_feed logic check ===')
print('  In arc_main: _update_intelligence_feed() calls self._initialize_scrapers() if not self.scrapers')
print('  But _initialize_scrapers requires credentials - if none, scrapers stay empty')
print('  Then it calls scraper.get_all_programs() for each - this should work if scrapers are initialized')

# 13. Check for missing submitter for immunefi_scraper
print()
print('=== 13. ImmunefiScraper constructor check ===')
from SHADOW_INTELLIGENCE_RADAR.direct_platform_monitor.bug_bounty_monitor.immunefi_scraper import ImmunefiScraper
sig = inspect.signature(ImmunefiScraper.__init__)
print(f'  ImmunefiScraper.__init__{sig}')

# Summary
print()
print(f'=== SUMMARY: {len(issues)} issues found ===')
for i, issue in enumerate(issues, 1):
    print(f'  {i}. {issue}')
