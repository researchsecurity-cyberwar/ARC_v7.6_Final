#!/usr/bin/env python3
"""
Security Validator Demo - Demonstrasi penggunaan SecurityValidator
Untuk validasi temuan keamanan yang benar-benar valid
"""
import sys
import os
import importlib.util
from typing import Dict, List, Any

# Import security_validator directly, bypassing __init__.py
this_dir = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("security_validator", os.path.join(this_dir, "security_validator.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

SecurityValidator = mod.SecurityValidator
has_cve_or_cwe_check = mod.has_cve_or_cwe_check
VulnerabilityPatternValidator = mod.VulnerabilityPatternValidator


def demo_basic_validation():
    """Demo 1: Basic validation of individual findings"""
    print("=" * 80)
    print("DEMO 1: Basic Finding Validation")
    print("=" * 80)
    
    validator = SecurityValidator()
    
    validator = SecurityValidator()
    
    # Test finding 1: Valid SQL injection
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
    
    print("\n1. Validating FIND-001 (SQL Injection with CVE):")
    result1 = validator.comprehensive_validation(finding1)
    print(f"   Valid: {result1['overall_valid']}")
    print(f"   Score: {result1['validation_score']:.2%}")
    print(f"   Recommendation: {result1['recommendation']}")
    print(f"   Action: {result1['action']}")
    
    # Test finding 2: Invalid CVE format
    finding2 = {
        'id': 'FIND-002',
        'type': 'xss',
        'severity': 'high',
        'detector': 'xss_detector',
        'url': 'https://example.com/page',
        'parameter': 'name',
        'cve_id': 'INVALID-CVE',
        'payload': '<script>alert(1)</script>',
        'context': {
            'severity': 'high',
            'exploitability_score': 0.8
        }
    }
    
    print("\n2. Validating FIND-002 (XSS with invalid CVE):")
    result2 = validator.comprehensive_validation(finding2)
    print(f"   Valid: {result2['overall_valid']}")
    print(f"   Score: {result2['validation_score']:.2%}")
    print(f"   Recommendation: {result2['recommendation']}")
    print(f"   Issues found:")
    for check_name, check_result in result2['checks'].items():
        if isinstance(check_result, dict) and not check_result.get('is_valid', True):
            print(f"     - {check_name}: {check_result.get('error', 'Invalid')}")
    
    # Test finding 3: Likely false positive (test/dummy data)
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
    
    print("\n3. Validating FIND-003 (Test/dummy data - likely false positive):")
    result3 = validator.comprehensive_validation(finding3)
    print(f"   Valid: {result3['overall_valid']}")
    print(f"   Score: {result3['validation_score']:.2%}")
    print(f"   Recommendation: {result3['recommendation']}")
    print(f"   False Positive Score: {result3['checks']['false_positive']['fp_score']:.2%}")
    print(f"   FP Reasons: {result3['checks']['false_positive']['fp_reasons']}")


def demo_batch_validation():
    """Demo 2: Batch validation of multiple findings"""
    print("\n" + "=" * 80)
    print("DEMO 2: Batch Validation")
    print("=" * 80)
    
    validator = SecurityValidator()
    
    # Sample findings
    findings = [
        {
            'id': 'FIND-001',
            'type': 'sqli',
            'severity': 'critical',
            'detector': 'sqli_scanner',
            'url': 'https://example.com/search',
            'parameter': 'q',
            'cve_id': 'CVE-2023-1234',
            'payload': "' OR 1=1 --",
            'context': {
                'severity': 'critical',
                'exploitability_score': 0.9
            }
        },
        {
            'id': 'FIND-002',
            'type': 'xss',
            'severity': 'high',
            'detector': 'xss_detector',
            'url': 'https://example.com/page',
            'parameter': 'name',
            'payload': '<script>alert(1)</script>',
            'context': {
                'severity': 'high',
                'exploitability_score': 0.7
            }
        },
        {
            'id': 'FIND-003',
            'type': 'ssrf',
            'severity': 'critical',
            'detector': 'ssrf_hunter',
            'url': 'http://example.com/proxy',
            'parameter': 'url',
            'payload': 'http://localhost:8080/admin',
            'context': {
                'severity': 'critical',
                'exploitability_score': 0.8,
                'attack_complexity': 'low'
            }
        },
        {
            'id': 'FIND-004',
            'type': 'info',
            'severity': 'info',
            'detector': 'scanner',
            'payload': 'test'
        }
    ]
    
    print(f"\nValidating {len(findings)} findings...")
    report = validator.batch_validate_findings(findings)
    
    print(f"\n📊 Batch Validation Report:")
    print(f"   Total Findings: {report['total_findings']}")
    print(f"   Valid: {report['valid_findings']}")
    print(f"   Invalid: {report['invalid_findings']}")
    print(f"   Average Score: {report['average_validation_score']:.2%}")
    print(f"   Distribution: {report['validation_distribution']}")
    print(f"   Summary: {report['summary']}")


def demo_cve_cwe_validation():
    """Demo 3: CVE/CWE validation"""
    print("\n" + "=" * 80)
    print("DEMO 3: CVE/CWE Format Validation")
    print("=" * 80)
    
    # validator already imported at module level
    
    validator = SecurityValidator()
    
    test_cves = [
        'CVE-2023-1234',
        'CVE-2023-12345',
        'CVE-1999-0001',
        'CVE-2030-9999',
        'INVALID',
        'CVE-23-1234',
        'CVE-2023-abc'
    ]
    
    print("\nValidating CVE IDs:")
    for cve in test_cves:
        result = validator.validate_cve_id(cve)
        status = "✓" if result['valid'] else "✗"
        print(f"   {status} {cve}: {result.get('error', 'Valid')}")
    
    test_cwes = [
        'CWE-89',
        'CWE-79',
        'CWE-787',
        'INVALID',
        'CWE-99999'
    ]
    
    print("\nValidating CWE IDs:")
    for cwe in test_cwes:
        result = validator.validate_cwe_id(cwe)
        status = "✓" if result['valid'] else "✗"
        print(f"   {status} {cwe}: {result.get('error', 'Valid')}")


def demo_pattern_validation():
    """Demo 4: Vulnerability pattern validation"""
    print("\n" + "=" * 80)
    print("DEMO 4: Vulnerability Pattern Validation")
    print("=" * 80)
    
    pattern_validator = VulnerabilityPatternValidator()
    
    # SQL Injection patterns
    sqli_payloads = [
        "' OR 1=1 --",
        "UNION SELECT * FROM users",
        "admin' --",
        "normal_search_query"
    ]
    
    print("\nValidating SQL Injection patterns:")
    for payload in sqli_payloads:
        result = pattern_validator.validate_sqli_pattern(payload)
        status = "✓" if result['valid'] else "✗"
        print(f"   {status} '{payload}': confidence={result.get('confidence', 0):.2%}")
    
    # XSS patterns
    xss_payloads = [
        '<script>alert(1)</script>',
        '<img src=x onerror=alert(1)>',
        'javascript:alert(1)',
        'normal_text'
    ]
    
    print("\nValidating XSS patterns:")
    for payload in xss_payloads:
        result = pattern_validator.validate_xss_pattern(payload)
        status = "✓" if result['valid'] else "✗"
        print(f"   {status} '{payload}': confidence={result.get('confidence', 0):.2%}")
    
    # SSRF patterns
    ssrf_payloads = [
        'http://localhost:8080/admin',
        'http://127.0.0.1/',
        'file:///etc/passwd',
        'http://example.com'
    ]
    
    print("\nValidating SSRF patterns:")
    for payload in ssrf_payloads:
        result = pattern_validator.validate_ssrf_pattern(payload)
        status = "✓" if result['valid'] else "✗"
        print(f"   {status} '{payload}': confidence={result.get('confidence', 0):.2%}")


def demo_severity_consistency():
    """Demo 5: Severity consistency checks"""
    print("\n" + "=" * 80)
    print("DEMO 5: Severity Consistency Validation")
    print("=" * 80)
    
    # validator already imported at module level
    
    validator = SecurityValidator()
    
    test_cases = [
        {
            'name': 'Critical with CVE - Consistent',
            'finding': {
                'severity': 'critical',
                'cve_id': 'CVE-2023-1234',
                'exploitability_score': 0.9,
                'attack_complexity': 'low',
                'user_interaction': 'none'
            }
        },
        {
            'name': 'Critical without CVE - Inconsistent',
            'finding': {
                'severity': 'critical',
                'cve_id': '',
                'exploitability_score': 0.9,
                'attack_complexity': 'low'
            }
        },
        {
            'name': 'High severity with low exploitability - Inconsistent',
            'finding': {
                'severity': 'high',
                'exploitability_score': 0.2,
                'attack_complexity': 'high'
            }
        },
        {
            'name': 'Critical with user interaction - Needs review',
            'finding': {
                'severity': 'critical',
                'user_interaction': 'required',
                'exploitability_score': 0.8
            }
        }
    ]
    
    print("\nSeverity Consistency Checks:")
    for test_case in test_cases:
        result = validator.validate_severity_consistency(test_case['finding'])
        status = "✓" if result['is_consistent'] else "⚠️"
        print(f"\n   {status} {test_case['name']}")
        print(f"      Consistent: {result['is_consistent']}")
        if result['issues']:
            print(f"      Issues:")
            for issue in result['issues']:
                print(f"        - {issue['message']}")


def demo_false_positive_detection():
    """Demo 6: False positive detection"""
    print("\n" + "=" * 80)
    print("DEMO 6: False Positive Detection")
    print("=" * 80)
    
    # validator already imported at module level
    
    validator = SecurityValidator()
    
    test_cases = [
        {
            'name': 'Production vulnerability - Likely real',
            'finding': {
                'type': 'sqli',
                'severity': 'critical',
                'detector': 'sqli_scanner',
                'url': 'https://api.example.com/users',
                'parameter': 'id',
                'cve_id': 'CVE-2023-1234',
                'payload': "' UNION SELECT * FROM users--",
                'confidence': 0.95
            }
        },
        {
            'name': 'Test/dummy data - Likely false positive',
            'finding': {
                'type': 'test_vuln',
                'severity': 'test',
                'detector': 'test_scanner',
                'payload': 'test',
                'confidence': 0.1
            }
        },
        {
            'name': 'Missing fields - Possibly incomplete',
            'finding': {
                'type': 'xss',
                'payload': '<script>alert(1)</script>'
            }
        }
    ]
    
    print("\nFalse Positive Detection:")
    for test_case in test_cases:
        result = validator.check_false_positive(test_case['finding'])
        status = "✓ REAL" if not result['is_likely_false_positive'] else "⚠️ FP"
        print(f"\n   {status} {test_case['name']}")
        print(f"      FP Score: {result['fp_score']:.2%}")
        print(f"      Recommendation: {result['recommendation']}")
        if result['fp_reasons']:
            print(f"      Reasons:")
            for reason in result['fp_reasons']:
                print(f"        - {reason}")


def main():
    """Run all demonstrations"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  SECURITY VALIDATOR - COMPREHENSIVE DEMONSTRATION".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    try:
        demo_basic_validation()
        demo_batch_validation()
        demo_cve_cwe_validation()
        demo_pattern_validation()
        demo_severity_consistency()
        demo_false_positive_detection()
        
        print("\n" + "=" * 80)
        print("✅ All demonstrations completed successfully!")
        print("=" * 80)
        print("\n💡 Usage in your code:")
        print("   # Direct import (recommended for this demo):")
        print("   import importlib.util")
        print("   spec = importlib.util.spec_from_file_location('security_validator', 'path/to/security_validator.py')")
        print("   mod = importlib.util.module_from_spec(spec)")
        print("   spec.loader.exec_module(mod)")
        print("   SecurityValidator = mod.SecurityValidator")
        print("   validator = SecurityValidator()")
        print("   result = validator.comprehensive_validation(finding)")
        print("   if result['overall_valid']:")
        print("       # Proceed with finding")
        print("   else:")
        print("       # Review or discard")
        print()
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()