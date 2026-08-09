#!/usr/bin/env python3
"""
Test Suite - Security Validator Unpublished Findings & CVE Year Validation
Tests Recommendations A, B, and C for handling unpublished/zeroday findings
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


def test_validate_unpublished_finding_comprehensive():
    """Test A: validate_unpublished_finding handles all scenarios correctly"""
    validator = SecurityValidator()
    
    print("\n" + "=" * 80)
    print("Test A: validate_unpublished_finding - All Scenarios")
    print("=" * 80)
    
    all_passed = True
    
    # Test 1: Unpublished finding without CVE -> should be valid
    print("\n  1. Unpublished finding without CVE (zero-day)...")
    finding1 = {
        'type': 'sqli',
        'severity': 'critical',
        'detector': 'advanced_sqli_scanner',
        'url': 'https://target.com/api',
        'parameter': 'id',
        'is_unpublished': True,
        'cve_id': None,
        'cwe_id': 'CWE-89',
        'description': 'Novel SQL injection with bypass technique...',
        'disclosure_timeline': '90_days',
        'proof_of_concept': 'SELECT * FROM users WHERE 1=1',
        'context': {
            'severity': 'critical',
            'exploitability_score': 0.9,
            'attack_complexity': 'low'
        }
    }
    result1 = validator.validate_unpublished_finding(finding1)
    assert result1['is_valid'] == True, "FAIL: Unpublished finding should be valid"
    assert result1['is_unpublished'] == True, "FAIL: Should be marked unpublished"
    assert result1['is_zero_day'] == True, "FAIL: Should be marked as zero-day"
    assert result1['status'] == 'pending_cve_assignment', "FAIL: Status should be pending_cve_assignment"
    assert result1['severity'] == 'info', "FAIL: Severity should be info (no warnings when complete)"
    print("      PASSED: Valid, zero-day, pending CVE assignment")
    
    # Test 2: Unpublished finding missing disclosure_timeline -> should have warnings
    print("\n  2. Unpublished finding missing disclosure_timeline...")
    finding2 = finding1.copy()
    finding2['disclosure_timeline'] = None
    finding2['proof_of_concept'] = None
    result2 = validator.validate_unpublished_finding(finding2)
    assert result2['is_valid'] == True, "FAIL: Should still be valid"
    assert result2['is_unpublished'] == True, "FAIL: Should be marked unpublished"
    assert 'warnings' in result2, "FAIL: Should have warnings"
    assert 'add_disclosure_timeline' in result2.get('sub_recommendations', []), \
        "FAIL: Should recommend adding disclosure timeline"
    assert result2['severity'] == 'warning', "FAIL: Should downgrade to warning when incomplete"
    print("      PASSED: Valid but with warnings for missing fields")
    
    # Test 3: Published finding with CVE -> should be valid
    print("\n  3. Published finding with CVE...")
    finding3 = {
        'type': 'sqli',
        'severity': 'critical',
        'detector': 'sqli_scanner',
        'url': 'https://target.com/search',
        'cve_id': 'CVE-2023-1234',
        'cwe_id': 'CWE-89'
    }
    result3 = validator.validate_unpublished_finding(finding3)
    assert result3['is_valid'] == True, "FAIL: Published finding with CVE should be valid"
    assert result3['is_unpublished'] == False, "FAIL: Should NOT be marked unpublished"
    assert result3['has_cve'] == True, "FAIL: Should have CVE"
    print("      PASSED: Valid published finding with CVE")
    
    # Test 4: Finding without CVE and not unpublished -> should be invalid
    print("\n  4. Finding without CVE and not unpublished...")
    finding4 = {
        'type': 'xss',
        'severity': 'high',
        'detector': 'xss_detector',
        'cwe_id': 'CWE-79'
    }
    result4 = validator.validate_unpublished_finding(finding4)
    assert result4['is_valid'] == False, "FAIL: Should be invalid without CVE and not unpublished"
    assert result4['is_unpublished'] == False, "FAIL: Should not be unpublished"
    assert 'error' in result4, "FAIL: Should have error message"
    assert result4['recommendation'] == 'mark_unpublished_or_add_cve'
    print("      PASSED: Invalid, needs CVE or unpublished flag")
    
    # Test 5: Unpublished finding WITH CVE -> should be valid (CVE takes priority)
    print("\n  5. Unpublished finding but has CVE (priority test)...")
    finding5 = {
        'type': 'sqli',
        'severity': 'critical',
        'detector': 'scanner',
        'is_unpublished': True,
        'cve_id': 'CVE-2024-1234',
        'cwe_id': 'CWE-89'
    }
    result5 = validator.validate_unpublished_finding(finding5)
    assert result5['is_valid'] == True, "FAIL: Should be valid with CVE"
    assert result5['is_unpublished'] == False, "FAIL: Should not be unpublished when CVE present"
    print("      PASSED: CVE takes priority over unpublished flag")
    
    print("\n  ✅ All validate_unpublished_finding tests PASSED!")
    return all_passed and True


def test_validate_finding_completeness_unpublished():
    """Test C: validate_finding_completeness accounts for is_unpublished flag"""
    validator = SecurityValidator()
    
    print("\n" + "=" * 80)
    print("Test C: validate_finding_completeness with is_unpublished flag")
    print("=" * 80)
    
    # Test 1: Published finding completeness (cve_id is recommended)
    print("\n  1. Published finding completeness (CVE recommended)...")
    finding1 = {
        'type': 'sqli',
        'severity': 'critical',
        'detector': 'scanner',
        'url': 'https://example.com',
        'parameter': 'id',
        'cwe_id': 'CWE-89',
        'description': 'SQL injection found',
        'payload': "' OR 1=1--",
        'impact': 'Data exfiltration',
        'remediation': 'Use parameterized queries',
        # cve_id missing - should be in missing_recommended
    }
    result1 = validator.validate_finding_completeness(finding1)
    assert result1['is_complete'] == True, "FAIL: Required fields present"
    cve_missing = any(m['field'] == 'cve_id' for m in result1['missing_recommended'])
    assert cve_missing, "FAIL: cve_id should be in missing_recommended for published findings"
    assert result1.get('is_unpublished') == False
    print("      PASSED: CVE in missing_recommended for published findings")
    
    # Test 2: Unpublished finding completeness (cve_id NOT recommended, disclosure_timeline IS)
    print("\n  2. Unpublished finding completeness (CVE NOT recommended)...")
    finding2 = {
        'type': 'sqli',
        'severity': 'critical',
        'detector': 'scanner',
        'url': 'https://example.com',
        'parameter': 'id',
        'is_unpublished': True,
        'cwe_id': 'CWE-89',
        'description': 'Zero-day SQL injection with bypass',
        'payload': "' OR 1=1--",
        'proof_of_concept': 'Detailed PoC steps here',
        'impact': 'Data exfiltration',
        'remediation': 'Use parameterized queries',
        'disclosure_timeline': '90_days',
        # cve_id missing - should NOT be in missing_recommended
    }
    result2 = validator.validate_finding_completeness(finding2)
    assert result2['is_complete'] == True, "FAIL: Should be complete"
    assert result2.get('is_unpublished') == True, "FAIL: Should track is_unpublished"
    cve_missing2 = any(m['field'] == 'cve_id' for m in result2['missing_recommended'])
    assert not cve_missing2, "FAIL: cve_id should NOT be in missing_recommended for unpublished findings"
    print("      PASSED: CVE NOT in missing_recommended for unpublished findings")
    
    # Test 3: Unpublished finding missing disclosure_timeline
    print("\n  3. Unpublished finding missing disclosure_timeline...")
    finding3 = finding2.copy()
    finding3['disclosure_timeline'] = None
    finding3['proof_of_concept'] = None
    result3 = validator.validate_finding_completeness(finding3)
    assert result3['is_complete'] == False, "FAIL: Should be incomplete (missing recommended fields)"
    timeline_missing = any(m['field'] == 'disclosure_timeline' for m in result3['missing_recommended'])
    assert timeline_missing, "FAIL: disclosure_timeline should be in missing_recommended"
    poc_missing = any(m['field'] == 'proof_of_concept' for m in result3['missing_recommended'])
    assert poc_missing, "FAIL: proof_of_concept should be in missing_recommended"
    print("      PASSED: disclosure_timeline and proof_of_concept in missing_recommended")
    
    print("\n  ✅ All validate_finding_completeness tests PASSED!")
    return True


def test_cve_year_validation():
    """Test CVE year validation handles future years for unpublished findings"""
    validator = SecurityValidator()
    
    print("\n" "Test: CVE Year Validation")
    print("=" * 80)
    
    all_passed = True
    
    # Test 1: Normal CVE year (valid)
    print("\n  1. Normal CVE year (2023)...")
    result = validator.validate_cve_id('CVE-2023-1234')
    assert result['valid'] == True, "FAIL: CVE-2023-1234 should be valid"
    assert result['year'] == 2023
    print("      PASSED")
    
    # Test 2: Future CVE year (current_year + 1) - should be valid with warning
    print("\n  2. CVE year = current_year + 1 (pre-assigned)...")
    from datetime import datetime
    future_year = datetime.now().year + 1
    result2 = validator.validate_cve_id(f'CVE-{future_year}-9999')
    assert result2['valid'] == True, "FAIL: Future CVE year should be valid (pre-assigned)"
    assert result2.get('warning') == True, "FAIL: Should have warning flag"
    print("      PASSED: Future year valid with warning")
    
    # Test 3: Too far future CVE year (> current_year + 1)
    print("\n  3. CVE year = current_year + 2 (too far future)...")
    far_future = datetime.now().year + 2
    result3 = validator.validate_cve_id(f'CVE-{far_future}-9999')
    assert result3['valid'] == False, "FAIL: Too far future should be invalid"
    assert 'error' in result3
    print("      PASSED: Too far future is invalid")
    
    # Test 4: CVE year before 1999
    print("\n  4. CVE year = 1998 (before CVE started)...")
    result4 = validator.validate_cve_id('CVE-1998-0001')
    assert result4['valid'] == False, "FAIL: Pre-1999 should be invalid"
    assert 'error' in result4
    print("      PASSED: Pre-1999 is invalid")
    
    print("\n  ✅ All CVE year validation tests PASSED!")
    return all_passed


def test_severity_consistency_unpublished():
    """Test B: Severity consistency check for unpublished findings"""
    validator = SecurityValidator()
    
    print("\n" + "=" * 80)
    print("Test B: Severity Consistency for Unpublished Findings")
    print("=" * 80)
    
    # Test 1: Critical without CVE, NOT unpublished -> should have issue
    print("\n  1. Critical without CVE, not unpublished...")
    finding1 = {
        'severity': 'critical',
        'cve_id': '',
        'exploitability_score': 0.9,
        'attack_complexity': 'low'
    }
    result1 = validator.validate_severity_consistency(finding1)
    assert not result1['is_consistent'], "FAIL: Should be inconsistent"
    has_cve_issue = any(
        i['rule'] == 'severity_cve_consistency' for i in result1['issues']
    )
    assert has_cve_issue, "FAIL: Should flag severity_cve_consistency"
    # Check severity is 'info' (downgraded from warning)
    cve_issue = [i for i in result1['issues'] if i['rule'] == 'severity_cve_consistency'][0]
    assert cve_issue['severity'] == 'info', "FAIL: Should be downgraded to info"
    print("      PASSED: Critical without CVE flagged at info level")
    
    # Test 2: Critical without CVE, BUT unpublished -> should be consistent
    print("\n  2. Critical without CVE, but unpublished...")
    finding2 = {
        'severity': 'critical',
        'cve_id': '',
        'cwe_id': 'CWE-89',
        'is_unpublished': True,
        'exploitability_score': 0.9,
        'attack_complexity': 'low'
    }
    result2 = validator.validate_severity_consistency(finding2)
    assert result2['is_consistent'], "FAIL: Should be consistent (unpublished)"
    assert len(result2['issues']) == 0, "FAIL: Should have no issues for unpublished"
    print("      PASSED: Unpublished zero-day is consistent (no false positive)")
    
    # Test 3: Critical with CWE, not unpublished -> should be consistent
    print("\n  3. Critical with CWE, not unpublished...")
    finding3 = {
        'severity': 'critical',
        'cwe_id': 'CWE-89',
        'exploitability_score': 0.9,
        'attack_complexity': 'low'
    }
    result3 = validator.validate_severity_consistency(finding3)
    assert result3['is_consistent'], "FAIL: Should be consistent (has CWE)"
    print("      PASSED: Critical with CWE is consistent")
    
    print("\n  ✅ All severity consistency tests PASSED!")
    return True


def test_comprehensive_validation_unpublished():
    """Test comprehensive_validation with unpublished findings"""
    validator = SecurityValidator()
    
    print("\n" + "=" * 80)
    print("Test: Comprehensive Validation - Unpublished Finding")
    print("=" * 80)
    
    # Test: Complete unpublished finding
    print("\n  1. Complete unpublished zero-day finding...")
    finding1 = {
        'id': 'ZERO-DAY-001',
        'type': 'sqli',
        'severity': 'critical',
        'detector': 'advanced_sqli_scanner',
        'url': 'https://target.com/api',
        'parameter': 'id',
        'is_unpublished': True,
        'cve_id': None,
        'cwe_id': 'CWE-89',
        'description': 'Novel SQL injection with bypass technique...',
        'payload': "' OR 1=1--",
        'proof_of_concept': 'Detailed PoC: SELECT * FROM users WHERE 1=1',
        'impact': 'Full database access',
        'remediation': 'Apply parameterized queries and WAF rules',
        'disclosure_timeline': '90_days',
        'exploitability_score': 0.9,
        'attack_complexity': 'low',
        'user_interaction': 'none',
        'context': {
            'severity': 'critical',
            'cwe_id': 'CWE-89',
            'exploitability_score': 0.9,
            'attack_complexity': 'low',
            'required_privileges': 'none',
            'detection_difficulty': 'medium'
        }
    }
    result1 = validator.comprehensive_validation(finding1)
    assert result1['overall_valid'] == True, "FAIL: Unpublished finding should be valid"
    assert result1['recommendation'] == 'accept', "FAIL: Should recommend accept"
    assert result1['action'] == 'proceed', "FAIL: Should recommend proceed"
    assert result1['message'] == 'Valid unpublished finding - pending CVE assignment'
    print("      PASSED: Unpublished finding accepted with accept/proceed")
    
    # Test: Unpublished finding with false positive indicators
    print("\n  2. Unpublished finding with test indicators (FP check)...")
    finding2 = {
        'id': 'ZERO-DAY-002',
        'type': 'sqli',
        'severity': 'critical',
        'detector': 'test_scanner',
        'url': 'https://target.com/api',
        'parameter': 'id',
        'is_unpublished': True,
        'cve_id': None,
        'cwe_id': 'CWE-89',
        'description': 'test vulnerability',
        'payload': 'test',
        'proof_of_concept': 'test PoC',
        'disclosure_timeline': '90_days',
        'context': {
            'severity': 'critical',
            'exploitability_score': 0.9,
        }
    }
    result2 = validator.comprehensive_validation(finding2)
    # Should be rejected due to false positive indicators
    assert result2['overall_valid'] == False, "FAIL: Test-indicated finding should be invalid"
    fp_check = result2['checks']['false_positive']
    assert fp_check['is_likely_false_positive'] == True, "FAIL: Should detect as false positive"
    print("      PASSED: Test-indicated unpublished finding correctly flagged as FP")
    
    # Test: Non-unpublished finding without CVE
    print("\n  3. Non-unpublished finding without CVE (should be rejected)...")
    finding3 = {
        'id': 'BAD-001',
        'type': 'sqli',
        'severity': 'critical',
        'detector': 'scanner',
        'url': 'https://target.com/api',
        'parameter': 'id',
        'cwe_id': 'CWE-89',
        'exploitability_score': 0.9,
        'attack_complexity': 'low',
        'context': {
            'severity': 'critical',
            'exploitability_score': 0.9,
            'attack_complexity': 'low',
        }
    }
    result3 = validator.comprehensive_validation(finding3)
    assert result3['overall_valid'] == False, "FAIL: Should be invalid without CVE and not unpublished"
    print("      PASSED: Non-unpublished without CVE rejected")
    
    print("\n  ✅ All comprehensive validation tests PASSED!")
    return True


def test_has_cve_or_cwe_helper():
    """Test the has_cve_or_cwe_check helper function"""
    print("\n" + "=" * 80)
    print("Test: has_cve_or_cwe_check Helper Function")
    print("=" * 80)
    
    assert has_cve_or_cwe_check({'cve_id': 'CVE-2023-1234'}) == True
    assert has_cve_or_cwe_check({'cwe_id': 'CWE-89'}) == True
    assert has_cve_or_cwe_check({'cve_id': '', 'cwe_id': 'CWE-89'}) == True
    assert has_cve_or_cwe_check({'cve_id': None, 'cwe_id': None}) == False
    assert has_cve_or_cwe_check({}) == False
    print("  ✅ All helper function tests PASSED!")
    return True


def test_disclosure_timeline_validation():
    """Test validate_disclosure_timeline method"""
    validator = SecurityValidator()
    
    print("\n" + "=" * 80)
    print("Test: Disclosure Timeline Validation")
    print("=" * 80)
    
    # Valid timeline
    assert validator.validate_disclosure_timeline('90_days')['valid'] == True
    assert validator.validate_disclosure_timeline('48_hours')['valid'] == True
    assert validator.validate_disclosure_timeline('coordinated')['valid'] == True
    assert validator.validate_disclosure_timeline('30_days')['valid'] == True
    
    # Invalid timeline
    assert validator.validate_disclosure_timeline('invalid')['valid'] == False
    assert validator.validate_disclosure_timeline('')['valid'] == False
    
    print("  ✅ All disclosure timeline tests PASSED!")
    return True


def test_backward_compatibility():
    """Verify existing demo findings still work correctly"""
    validator = SecurityValidator()
    
    print("\n" + "=" * 80)
    print("Test: Backward Compatibility (Existing Findings)")
    print("=" * 80)
    
    # Test finding from demo_basic_validation (FIND-001)
    print("\n  1. Published finding with CVE (FIND-001)...")
    finding1 = {
        'id': 'FIND-001',
        'type': 'sqli',
        'severity': 'critical',
        'detector': 'sqli_scanner',
        'url': 'https://example.com/search',
        'parameter': 'q',
        'cve_id': 'CVE-2023-1234',
        'cwe_id': 'CWE-89',
        'payload': "' OR 1=1 --",
        'context': {
            'severity': 'critical',
            'cve_id': 'CVE-2023-1234',
            'cwe_id': 'CWE-89',
            'exploitability_score': 0.9,
            'attack_complexity': 'low',
            'required_privileges': 'none',
            'detection_difficulty': 'easy'
        }
    }
    result1 = validator.comprehensive_validation(finding1)
    # Should be valid with high score
    assert result1['validation_score'] >= 0.7, "FAIL: Should have good score"
    print(f"      Score: {result1['validation_score']:.2%}, Valid: {result1['overall_valid']}")
    print("      PASSED")
    
    # Test false positive finding (FIND-003)
    print("\n  2. Test/dummy data (FIND-003 - false positive)...")
    finding3 = {
        'id': 'FIND-003',
        'type': 'test_vuln',
        'severity': 'test',
        'detector': 'test_scanner',
        'payload': 'test',
        'context': {
            'severity': 'test'
        }
    }
    result3 = validator.comprehensive_validation(finding3)
    assert result3['checks']['false_positive']['is_likely_false_positive'] == True
    print(f"      FP Score: {result3['checks']['false_positive']['fp_score']:.2%}")
    print("      PASSED")
    
    print("\n  ✅ All backward compatibility tests PASSED!")
    return True


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + "  SECURITY VALIDATOR - UNPUBLISHED FINDINGS TEST SUITE".center(78) + "║")
    print("╚" + "=" * 78 + "╝")
    
    tests = [
        ("validate_unpublished_finding", test_validate_unpublished_finding_comprehensive),
        ("validate_finding_completeness (unpublished)", test_validate_finding_completeness_unpublished),
        ("CVE Year Validation", test_cve_year_validation),
        ("Severity Consistency (unpublished)", test_severity_consistency_unpublished),
        ("Comprehensive Validation (unpublished)", test_comprehensive_validation_unpublished),
        ("has_cve_or_cwe_check Helper", test_has_cve_or_cwe_helper),
        ("Disclosure Timeline Validation", test_disclosure_timeline_validation),
        ("Backward Compatibility", test_backward_compatibility),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, 'PASS', None))
        except (AssertionError, Exception) as e:
            results.append((name, 'FAIL', str(e)))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    passed = sum(1 for _, status, _ in results if status == 'PASS')
    failed = sum(1 for _, status, _ in results if status == 'FAIL')
    
    for name, status, error in results:
        icon = "✅" if status == "PASS" else "❌"
        print(f"  {icon} {name}: {status}")
        if error:
            print(f"      Error: {error}")
    
    print(f"\n  Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    print("=" * 80)
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
