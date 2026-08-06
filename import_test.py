import os, sys, importlib, traceback

# Add root to path
sys.path.insert(0, os.path.abspath('.'))

# All modules referenced in arc_main.py
arc_main_imports = [
    'SOVEREIGN_SESSION_MANAGER.credential_vault',
    'SOVEREIGN_SESSION_MANAGER.config_loader',
    'SOVEREIGN_SESSION_MANAGER.platform_session_manager',
    'COGNITIVE_CORE.human_in_the_loop_gate',
    'ETHICAL_ARMOR.scope_sovereignty_guard',
    'DIALOGIC_COPILLOT.PLATFORM_COMMUNICATOR.telegram_notifier',
    'SOVEREIGN_SESSION_MANAGER.bug_bounty_session',
    'SOVEREIGN_SESSION_MANAGER.ctf_session',
    'DUPLICATE_INTELLIGENCE.report_scraper',
    'UNIQUE_ANGLE_GENERATOR.uniqueness_validator',
    'SOVEREIGN_REPORTING.multi_document_generator',
    'VERIFIABLE_EVIDENCE_ARTIFACT.behavioral_proof_recorder',
    'SOVEREIGN_REPORTING.PATCH_GENERATOR.web_patch_factory',
    'SOVEREIGN_REPORTING.PLATFORM_SPECIFIC_SUBMITTER.hackerone_submitter',
    'SOVEREIGN_REPORTING.PLATFORM_SPECIFIC_SUBMITTER.intigriti_submitter',
    'SOVEREIGN_REPORTING.PLATFORM_SPECIFIC_SUBMITTER.bugcrowd_submitter',
    'SOVEREIGN_REPORTING.PLATFORM_SPECIFIC_SUBMITTER.yeswehack_submitter',
    'SOVEREIGN_REPORTING.PLATFORM_SPECIFIC_SUBMITTER.immunefi_submitter',
    'SHADOW_INTELLIGENCE_RADAR.direct_platform_monitor.bug_bounty_monitor.hackerone_scraper',
    'SHADOW_INTELLIGENCE_RADAR.direct_platform_monitor.bug_bounty_monitor.intigriti_scraper',
    'SHADOW_INTELLIGENCE_RADAR.direct_platform_monitor.bug_bounty_monitor.bugcrowd_scraper',
    'SHADOW_INTELLIGENCE_RADAR.direct_platform_monitor.bug_bounty_monitor.yeswehack_scraper',
    'SHADOW_INTELLIGENCE_RADAR.direct_platform_monitor.bug_bounty_monitor.immunefi_scraper',
    'UNIFIED_LEARNING_ENGINE.self_learning_orchestrator',
    'UNIFIED_LEARNING_ENGINE.learning_bridge',
    'UNIFIED_LEARNING_ENGINE.ctf_challenge_analyzer',
    'UNIFIED_LEARNING_ENGINE.platform_writeup_scraper',
    'VULNERABILITY_DETECTORS.web_security.xss_detector',
    'VULNERABILITY_DETECTORS.web_security.sqli_scanner',
    'VULNERABILITY_DETECTORS.web_security.ssrf_hunter',
    'VULNERABILITY_DETECTORS.web_security.idor_analyzer',
    'VULNERABILITY_DETECTORS.web_security.csrf_validator',
    'VULNERABILITY_DETECTORS.web_security.lfi_scanner',
    'VULNERABILITY_DETECTORS.web_security.rfi_scanner',
    'VULNERABILITY_DETECTORS.web_security.command_injection_scanner',
    'VULNERABILITY_DETECTORS.web_security.modern_web_analyzer',
    'VULNERABILITY_DETECTORS.web_security.backdoor_hunter',
    'VULNERABILITY_DETECTORS.api_security.bola_scanner',
    'VULNERABILITY_DETECTORS.api_security.mass_assignment_tester',
    'VULNERABILITY_DETECTORS.api_security.jwt_validator',
    'ETHICAL_ARMOR.audit_trail_logger',
    'ETHICAL_ARMOR.zero_trust_execution',
    'ETHICAL_ARMOR.data_minimization_enforcer',
    'ETHICAL_ARMOR.chain_ethics_lock',
    'COGNITIVE_CORE.sovereign_reasoner',
]

print("=" * 60)
print("IMPORT TEST RESULTS")
print("=" * 60)

passed = 0
failed = 0
errors = []

for module_path in arc_main_imports:
    try:
        importlib.import_module(module_path)
        passed += 1
    except ImportError as e:
        failed += 1
        errors.append((module_path, str(e)))
    except Exception as e:
        failed += 1
        errors.append((module_path, f"Non-import error: {e}"))

print(f"\nArc Main Imports: {passed} passed, {failed} failed")

if errors:
    print("\n--- FAILED IMPORTS ---")
    for mod, err in errors:
        print(f"  FAIL: {mod}")
        print(f"    Error: {err}")
        # Show last 3 lines of traceback
        try:
            importlib.import_module(mod)
        except Exception as e:
            tb_lines = traceback.format_exc().strip().split('\n')
            for line in tb_lines[-5:]:
                print(f"    {line}")
        print()

# Now try importing ALL .py files in the project
print("\n" + "=" * 60)
print("FULL PROJECT IMPORT TEST")
print("=" * 60)

all_modules = []
for root, dirs, files in os.walk('.'):
    if '__pycache__' in root:
        continue
    for f in files:
        if f.endswith('.py') and f != '__init__.py' and not f.startswith('audit_') and not f.startswith('test_'):
            filepath = os.path.join(root, f)
            rel_path = os.path.relpath(filepath, '.')
            module_path = rel_path.replace('\\', '.').replace('/', '.')
            module_path = module_path[:-3]  # Remove .py
            all_modules.append(module_path)

all_passed = 0
all_failed = 0
all_errors = []

for module_path in sorted(all_modules):
    try:
        importlib.import_module(module_path)
        all_passed += 1
    except Exception as e:
        all_failed += 1
        all_errors.append((module_path, str(e)))

print(f"\nFull Import Test: {all_passed} passed, {all_failed} failed")

if all_errors:
    print("\n--- FAILED IMPORTS (all modules) ---")
    for mod, err in sorted(all_errors):
        print(f"  FAIL: {mod}: {err}")

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"arc_main imports: {passed}/{len(arc_main_imports)} passed")
print(f"All modules: {all_passed}/{len(all_modules)} passed")
print(f"Total failures: {failed + all_failed}")
