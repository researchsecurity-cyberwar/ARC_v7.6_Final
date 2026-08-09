#!/usr/bin/env python3
"""
Test Runner - bypasses broken __init__.py in UNIFIED_LEARNING_ENGINE
Run from project root: python -m UNIFIED_LEARNING_ENGINE.run_tests
"""
import sys
import os
import importlib.util

# Import security_validator directly, bypassing __init__.py
this_dir = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("security_validator", os.path.join(this_dir, "security_validator.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

SecurityValidator = mod.SecurityValidator
has_cve_or_cwe_check = mod.has_cve_or_cwe_check
VulnerabilityPatternValidator = mod.VulnerabilityPatternValidator


from datetime import datetime


def test_validate_unpublished_finding_comprehensive():
    validator = SecurityValidator()
    print("\n" + "=" * 80)
    print("Test A: validate_unpublished_finding - All Scenarios")
    print("=" * 80)

    # Test 1: Unpublished finding without CVE -> valid
    print("\n  1. Unpublished finding without CVE (zero-day)...")
    finding1 = {
        'type': 'sqli', 'severity': 'critical', 'detector': 'advanced_sqli_scanner',
        'url': 'https://target.com/api', 'parameter': 'id',
        'is_unpublished': True, 'cve_id': None, 'cwe_id': 'CWE-89',
        'description': 'Novel SQL injection with bypass technique...',
        'disclosure_timeline': '90_days',
        'proof_of_concept': 'SELECT * FROM users WHERE 1=1',
        'context': {'severity': 'critical', 'exploitation_score': 0.9, 'attack_complexity': 'low'}
    }
    r = validator.validate_unpublished_finding(finding1)
    assert r['is_valid'] == True, "FAIL: should be valid"
    assert r['is_unpublished'] == True, "FAIL: should be unpublished"
    assert r['is_zero_day'] == True, "FAIL: should be zero-day"
    assert r['status'] == 'pending_cve_assignment', "FAIL: wrong status"
    assert r['severity'] == 'info', "FAIL: should be info"
    print("      PASSED")

    # Test 2: Missing disclosure_timeline -> warnings
    print("\n  2. Unpublished finding missing disclosure_timeline...")
    finding2 = finding1.copy()
    finding2['disclosure_timeline'] = None
    finding2['proof_of_concept'] = None
    r2 = validator.validate_unpublished_finding(finding2)
    assert r2['is_valid'] == True, "FAIL: should still be valid"
    assert 'warnings' in r2, "FAIL: should have warnings"
    assert 'add_disclosure_timeline' in r2.get('sub_recommendations', []), "FAIL"
    assert r2['severity'] == 'warning', "FAIL: should downgrade to warning"
    print("      PASSED")

    # Test 3: Published with CVE -> valid
    print("\n  3. Published finding with CVE...")
    finding3 = {'type': 'sqli', 'severity': 'critical', 'detector': 'scanner',
                'url': 'https://x.com', 'cve_id': 'CVE-2023-1234', 'cwe_id': 'CWE-89'}
    r3 = validator.validate_unpublished_finding(finding3)
    assert r3['is_valid'] == True and r3['is_unpublished'] == False and r3['has_cve'] == True
    print("      PASSED")

    # Test 4: No CVE, not unpublished -> invalid
    print("\n  4. Finding without CVE and not unpublished...")
    finding4 = {'type': 'xss', 'severity': 'high', 'detector': 'xss_detector', 'cwe_id': 'CWE-79'}
    r4 = validator.validate_unpublished_finding(finding4)
    assert r4['is_valid'] == False and 'error' in r4
    assert r4['recommendation'] == 'mark_unpublished_or_add_cve'
    print("      PASSED")

    # Test 5: Unpublished but has CVE -> CVE priority
    print("\n  5. Unpublished finding but has CVE...")
    finding5 = {'type': 'sqli', 'severity': 'critical', 'detector': 's',
                'is_unpublished': True, 'cve_id': 'CVE-2024-1234', 'cwe_id': 'CWE-89'}
    r5 = validator.validate_unpublished_finding(finding5)
    assert r5['is_valid'] == True and r5['is_unpublished'] == False
    print("      PASSED")

    print("\n  All validate_unpublished_finding tests PASSED!")
    return True


def test_finding_completeness_unpublished():
    validator = SecurityValidator()
    print("\n" + "=" * 80)
    print("Test C: validate_finding_completeness with is_unpublished flag")
    print("=" * 80)

    # Published: cve_id in recommended
    print("\n  1. Published finding (CVE recommended)...")
    f1 = {'type': 'sqli', 'severity': 'critical', 'detector': 's', 'url': 'https://e.com',
          'parameter': 'id', 'cwe_id': 'CWE-89', 'description': 'd', 'payload': 'p',
          'impact': 'i', 'remediation': 'r'}
    r1 = validator.validate_finding_completeness(f1)
    assert r1['is_complete'] == True
    assert any(m['field'] == 'cve_id' for m in r1['missing_recommended']), "FAIL: cve should be missing for published"
    assert r1.get('is_unpublished') == False
    print("      PASSED")

    # Unpublished: cve_id NOT in recommended
    print("\n  2. Unpublished finding (CVE NOT recommended)...")
    f2 = {'type': 'sqli', 'severity': 'critical', 'detector': 's', 'url': 'https://e.com',
          'parameter': 'id', 'is_unpublished': True, 'cwe_id': 'CWE-89',
          'description': 'd', 'payload': 'p', 'proof_of_concept': 'poc',
          'impact': 'i', 'remediation': 'r', 'disclosure_timeline': '90_days'}
    r2 = validator.validate_finding_completeness(f2)
    assert r2['is_complete'] == True
    assert r2.get('is_unpublished') == True
    assert not any(m['field'] == 'cve_id' for m in r2['missing_recommended']), "FAIL: cve should NOT be missing for unpublished"
    print("      PASSED")

    # Unpublished missing disclosure_timeline
    print("\n  3. Unpublished finding missing disclosure_timeline...")
    f3 = f2.copy()
    f3['disclosure_timeline'] = None
    f3['proof_of_concept'] = None
    r3 = validator.validate_finding_completeness(f3)
    assert r3['is_complete'] == False
    assert any(m['field'] == 'disclosure_timeline' for m in r3['missing_recommended'])
    assert any(m['field'] == 'proof_of_concept' for m in r3['missing_recommended'])
    print("      PASSED")

    print("\n  All validate_finding_completeness tests PASSED!")
    return True


def test_cve_year_validation():
    validator = SecurityValidator()
    print("\n" + "=" * 80)
    print("Test: CVE Year Validation")
    print("=" * 80)

    print("\n  1. Normal CVE year (2023)...")
    r = validator.validate_cve_id('CVE-2023-1234')
    assert r['valid'] == True and r['year'] == 2023
    print("      PASSED")

    print("\n  2. CVE year = current_year + 1 (pre-assigned)...")
    fy = datetime.now().year + 1
    r2 = validator.validate_cve_id('CVE-{}-9999'.format(fy))
    assert r2['valid'] == True and r2.get('warning') == True
    print("      PASSED: Future year valid with warning")

    print("\n  3. CVE year = current_year + 2 (too far)...")
    ff = datetime.now().year + 2
    r3 = validator.validate_cve_id('CVE-{}-9999'.format(ff))
    assert r3['valid'] == False and 'error' in r3
    print("      PASSED: Too far future is invalid")

    print("\n  4. CVE year = 1998 (before CVE started)...")
    r4 = validator.validate_cve_id('CVE-1998-0001')
    assert r4['valid'] == False
    print("      PASSED: Pre-1999 is invalid")

    print("\n  All CVE year validation tests PASSED!")
    return True


def test_severity_consistency_unpublished():
    validator = SecurityValidator()
    print("\n" + "=" * 80)
    print("Test B: Severity Consistency for Unpublished Findings")
    print("=" * 80)

    print("\n  1. Critical without CVE, not unpublished...")
    f1 = {'severity': 'critical', 'cve_id': '', 'exploitation_score': 0.9, 'attack_complexity': 'low'}
    r1 = validator.validate_severity_consistency(f1)
    assert not r1['is_consistent']
    assert any(i['rule'] == 'severity_cve_consistency' for i in r1['issues'])
    cve_issue = [i for i in r1['issues'] if i['rule'] == 'severity_cve_consistency'][0]
    assert cve_issue['severity'] == 'info', "FAIL: should be downgraded to info"
    print("      PASSED: Flagged at info level")

    print("\n  2. Critical without CVE, but unpublished...")
    f2 = {'severity': 'critical', 'cve_id': '', 'cwe_id': 'CWE-89',
          'is_unpublished': True, 'exploitation_score': 0.9, 'attack_complexity': 'low'}
    r2 = validator.validate_severity_consistency(f2)
    assert r2['is_consistent'], "FAIL: should be consistent"
    assert len(r2['issues']) == 0, "FAIL: should have no issues"
    print("      PASSED: Unpublished zero-day is consistent")

    print("\n  3. Critical with CWE, not unpublished...")
    f3 = {'severity': 'critical', 'cwe_id': 'CWE-89', 'exploitation_score': 0.9, 'attack_complexity': 'low'}
    r3 = validator.validate_severity_consistency(f3)
    assert r3['is_consistent']
    print("      PASSED")

    print("\n  All severity consistency tests PASSED!")
    return True


def test_comprehensive_validation_unpublished():
    validator = SecurityValidator()
    print("\n" + "=" * 80)
    print("Test: Comprehensive Validation - Unpublished Finding")
    print("=" * 80)

    print("\n  1. Complete unpublished zero-day finding...")
    f1 = {
        'id': 'ZERO-DAY-001', 'type': 'sqli', 'severity': 'critical',
        'detector': 'advanced_sqli_scanner', 'url': 'https://target.com/api', 'parameter': 'id',
        'is_unpublished': True, 'cve_id': None, 'cwe_id': 'CWE-89',
        'description': 'Novel SQL injection with bypass technique...',
        'payload': "' OR 1=1--",
        'proof_of_concept': 'Detailed PoC: SELECT * FROM users WHERE 1=1',
        'impact': 'Full database access', 'remediation': 'Apply parameterized queries',
        'disclosure_timeline': '90_days', 'exploitation_score': 0.9,
        'attack_complexity': 'low', 'user_interaction': 'none',
        'context': {'severity': 'critical', 'cwe_id': 'CWE-89',
                     'exploitation_score': 0.9, 'attack_complexity': 'low',
                     'required_privileges': 'none', 'detection_difficulty': 'medium'}
    }
    r1 = validator.comprehensive_validation(f1)
    assert r1['overall_valid'] == True, "FAIL: should be valid"
    assert r1['recommendation'] == 'accept'
    assert r1['action'] == 'proceed'
    assert r1['message'] == 'Valid unpublished finding - pending CVE assignment'
    print("      PASSED: Accepted with accept/proceed")

    print("\n  2. Unpublished finding with test indicators (FP)...")
    f2 = {
        'id': 'ZERO-DAY-002', 'type': 'sqli', 'severity': 'critical',
        'detector': 'test_scanner', 'url': 'https://target.com/api', 'parameter': 'id',
        'is_unpublished': True, 'cve_id': None, 'cwe_id': 'CWE-89',
        'description': 'test vulnerability', 'payload': 'test',
        'proof_of_concept': 'test PoC', 'disclosure_timeline': '90_days',
        'context': {'severity': 'critical', 'exploitation_score': 0.9}
    }
    r2 = validator.comprehensive_validation(f2)
    assert r2['overall_valid'] == False, "FAIL: should be invalid (FP)"
    assert r2['checks']['false_positive']['is_likely_false_positive'] == True
    print("      PASSED: Test-indicated FP correctly flagged")

    print("\n  3. Non-unpublished finding without CVE (rejected)...")
    f3 = {
        'id': 'BAD-001', 'type': 'sqli', 'severity': 'critical',
        'detector': 'scanner', 'url': 'https://target.com/api', 'parameter': 'id',
        'cwe_id': 'CWE-89', 'exploitation_score': 0.9, 'attack_complexity': 'low',
        'context': {'severity': 'critical', 'exploitation_score': 0.9, 'attack_complexity': 'low'}
    }
    r3 = validator.comprehensive_validation(f3)
    assert r3['overall_valid'] == False, "FAIL: should be rejected"
    print("      PASSED: Non-unpublished without CVE rejected")

    print("\n  All comprehensive validation tests PASSED!")
    return True


def test_helpers_and_backward():
    validator = SecurityValidator()
    print("\n" + "=" * 80)
    print("Test: Helpers & Backward Compatibility")
    print("=" * 80)

    print("\n  1. has_cve_or_cwe_check helper...")
    assert has_cve_or_cwe_check({'cve_id': 'CVE-2023-1234'}) == True
    assert has_cve_or_cwe_check({'cwe_id': 'CWE-89'}) == True
    assert has_cve_or_cwe_check({'cve_id': None, 'cwe_id': None}) == False
    assert has_cve_or_cwe_check({}) == False
    print("      PASSED")

    print("\n  2. Disclosure timeline validation...")
    assert validator.validate_disclosure_timeline('90_days')['valid'] == True
    assert validator.validate_disclosure_timeline('48_hours')['valid'] == True
    assert validator.validate_disclosure_timeline('coordinated')['valid'] == True
    assert validator.validate_disclosure_timeline('invalid')['valid'] == False
    print("      PASSED")

    print("\n  3. Published finding with CVE (backward compat)...")
    f1 = {
        'id': 'FIND-001', 'type': 'sqli', 'severity': 'critical',
        'detector': 'sqli_scanner', 'url': 'https://example.com/search', 'parameter': 'q',
        'cve_id': 'CVE-2023-1234', 'cwe_id': 'CWE-89', 'payload': "' OR 1=1 --",
        'context': {'severity': 'critical', 'cve_id': 'CVE-2023-1234', 'cwe_id': 'CWE-89',
                     'exploitation_score': 0.9, 'attack_complexity': 'low',
                     'required_privileges': 'none', 'detection_difficulty': 'easy'}
    }
    r1 = validator.comprehensive_validation(f1)
    assert r1['validation_score'] >= 0.7, "FAIL: should have good score"
    print("      Score: {:.2%}, Valid: {}".format(r1['validation_score'], r1['overall_valid']))
    print("      PASSED")

    print("\n  4. False positive finding (backward compat)...")
    f3 = {'id': 'FIND-003', 'type': 'test_vuln', 'severity': 'test',
          'detector': 'test_scanner', 'payload': 'test',
          'context': {'severity': 'test'}}
    r3 = validator.comprehensive_validation(f3)
    assert r3['checks']['false_positive']['is_likely_false_positive'] == True
    print("      FP Score: {:.0%}".format(r3['checks']['false_positive']['fp_score']))
    print("      PASSED")

    print("\n  All helper and backward compatibility tests PASSED!")
    return True


def main():
    print("\n+========================================================================+")
    print("|  SECURITY VALIDATOR - UNPUBLISHED FINDINGS TEST SUITE                  |")
    print("+========================================================================+")

    tests = [
        ("validate_unpublished_finding", test_validate_unpublished_finding_comprehensive),
        ("validate_finding_completeness (unpublished)", test_finding_completeness_unpublished),
        ("CVE Year Validation", test_cve_year_validation),
        ("Severity Consistency (unpublished)", test_severity_consistency_unpublished),
        ("Comprehensive Validation (unpublished)", test_comprehensive_validation_unpublished),
        ("Helpers & Backward Compatibility", test_helpers_and_backward),
    ]

    results = []
    for name, test_func in tests:
        try:
            test_func()
            results.append((name, 'PASS', None))
        except (AssertionError, Exception) as e:
            results.append((name, 'FAIL', str(e)))

    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    passed = sum(1 for _, status, _ in results if status == 'PASS')
    failed = sum(1 for _, status, _ in results if status == 'FAIL')

    for name, status, error in results:
        icon = "[PASS]" if status == "PASS" else "[FAIL]"
        print("  {} {}".format(icon, name))
        if error:
            print("      Error: {}".format(error))

    print("\n  Total: {} | Passed: {} | Failed: {}".format(len(results), passed, failed))
    print("=" * 80)
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
