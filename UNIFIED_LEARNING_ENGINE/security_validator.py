"""
Security Validator - Framework untuk validasi temuan keamanan
Memastikan temuan vulnerability valid dan tidak false positive
"""
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class SecurityValidator:
    """
    Validator untuk temuan keamanan
    - Validasi CVE/CWE format
    - Check untuk false positives
    - Validasi severity dan exploitability
    - Consistency checks
    """
    
    def __init__(self):
        # CVE format: CVE-YYYY-NNNN+
        self.cve_pattern = re.compile(r'^CVE-\d{4}-\d{4,}$')
        
        # CWE format: CWE-NNN
        self.cwe_pattern = re.compile(r'^CWE-\d+$')
        
        # Known false positive indicators
        self.fp_indicators = [
            'test',
            'dummy',
            'example',
            'placeholder',
            'fake',
            'mock',
            'sample',
            'debug',
            'dev',
            'staging'
        ]
        
        # Severity validation rules
        self.valid_severities = ['critical', 'high', 'medium', 'low', 'info']
        
        # Valid attack complexities
        self.valid_complexities = ['low', 'medium', 'high']
        
        # Valid privilege levels
        self.valid_privileges = ['none', 'low', 'high']
        
        # Valid difficulty levels
        self.valid_difficulties = ['easy', 'medium', 'hard']
        
        # Valid disclosure timeline values for unpublished findings
        self.valid_disclosure_timelines = [
            '24_hours', '48_hours', '7_days', '14_days', '30_days',
            '45_days', '60_days', '90_days', '120_days', '180_days',
            'coordinated', 'full_disclosure', 'no_coordination'
        ]
    
    def validate_unpublished_finding(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate unpublished/zero-day findings yang belum memiliki CVE
        
        Handles three scenarios:
        1. Legitimate unpublished finding (is_unpublished=True, no CVE) -> valid, pending CVE
        2. Published finding with CVE -> valid, normal
        3. Finding without CVE and not marked unpublished -> invalid, needs action
        
        For unpublished findings, also validates disclosure_timeline and proof_of_concept
        to ensure responsible handling of zero-day vulnerabilities.
        
        Args:
            finding: Vulnerability finding dict
            
        Returns:
            Validation result with unpublished status
        """
        has_cve = bool(finding.get('cve_id'))
        has_cwe = bool(finding.get('cwe_id'))
        is_unpublished = finding.get('is_unpublished', False)
        has_disclosure_timeline = bool(finding.get('disclosure_timeline'))
        has_proof_of_concept = bool(finding.get('proof_of_concept'))
        has_payload = bool(finding.get('payload'))
        
        # Scenario 1: Explicit unpublished flag without CVE - legitimate zero-day
        if is_unpublished and not has_cve:
            warnings = []
            recommendations = []
            
            # Check for disclosure timeline (responsible disclosure)
            if not has_disclosure_timeline:
                warnings.append('Missing disclosure_timeline for unpublished finding')
                recommendations.append('add_disclosure_timeline')
            
            # Check for proof of concept or payload
            if not has_proof_of_concept and not has_payload:
                warnings.append('Missing proof_of_concept/payload for unpublished finding')
                recommendations.append('add_proof_of_concept')
            
            # Check for CWE (recommended but not required)
            if not has_cwe:
                warnings.append('No CWE specified for unpublished finding')
            
            result = {
                'is_valid': True,
                'is_unpublished': True,
                'status': 'pending_cve_assignment',
                'severity': 'info',
                'recommendation': 'accept_pending_cve',
                'message': 'Unpublished finding - CVE assignment pending',
                'has_cwe': has_cwe,
                'is_zero_day': True
            }
            
            if warnings:
                result['warnings'] = warnings
                result['sub_recommendations'] = recommendations
                result['severity'] = 'warning'
            
            return result
        
        # Scenario 2: Has CVE - normal published validation
        if has_cve:
            cve_validation = self.validate_cve_id(finding.get('cve_id', ''))
            return {
                'is_valid': cve_validation.get('valid', False),
                'is_unpublished': False,
                'has_cve': True,
                'has_cwe': has_cwe,
                'severity': 'info' if cve_validation.get('valid', False) else 'warning',
                'message': 'Published finding with CVE'
            }
        
        # Scenario 3: No CVE and not marked unpublished - needs action
        if not has_cve and not is_unpublished:
            return {
                'is_valid': False,
                'is_unpublished': False,
                'error': 'Missing CVE/CWE and not marked as unpublished',
                'severity': 'warning',
                'recommendation': 'mark_unpublished_or_add_cve'
            }
        
        # Fallback for any other combination
        return {
            'is_valid': True,
            'is_unpublished': is_unpublished,
            'has_cve': has_cve,
            'has_cwe': has_cwe,
            'severity': 'info'
        }
    
    def validate_cve_id(self, cve_id: str) -> Dict[str, Any]:
        """
        Validate CVE ID format
        
        Args:
            cve_id: CVE ID string
            
        Returns:
            Validation result
        """
        if not cve_id:
            return {
                'valid': False,
                'error': 'CVE ID is empty',
                'severity': 'error'
            }
        
        cve_id = cve_id.strip().upper()
        
        if not self.cve_pattern.match(cve_id):
            return {
                'valid': False,
                'error': f'Invalid CVE format: {cve_id}. Expected: CVE-YYYY-NNNN',
                'severity': 'error',
                'cve_id': cve_id
            }
        
        # Extract year and number
        parts = cve_id.split('-')
        year = int(parts[1])
        number = int(parts[2])
        
        # Validate year range
        current_year = datetime.now().year
        if year < 1999 or year > current_year + 1:  # CVE started in 1999
            return {
                'valid': False,
                'error': f'Invalid CVE year: {year}. CVE years must be between 1999 and {current_year + 1}.',
                'severity': 'warning',
                'cve_id': cve_id
            }
        
        # Validate number range
        if number < 1 or number > 99999:
            return {
                'valid': False,
                'error': f'Invalid CVE number: {number}',
                'severity': 'warning',
                'cve_id': cve_id
            }
        
        # Future year warning (e.g., current_year + 1 for pre-assigned CVEs/unpublished findings)
        if year > current_year:
            return {
                'valid': True,
                'cve_id': cve_id,
                'year': year,
                'number': number,
                'severity': 'info',
                'warning': True,
                'message': f'CVE year {year} is in the future. This may be valid for pre-assigned CVEs or unpublished findings.'
            }
        
        return {
            'valid': True,
            'cve_id': cve_id,
            'year': year,
            'number': number,
            'severity': 'info'
        }
    
    def validate_cwe_id(self, cwe_id: str) -> Dict[str, Any]:
        """
        Validate CWE ID format
        
        Args:
            cwe_id: CWE ID string
            
        Returns:
            Validation result
        """
        if not cwe_id:
            return {
                'valid': False,
                'error': 'CWE ID is empty',
                'severity': 'error'
            }
        
        cwe_id = cwe_id.strip().upper()
        
        if not self.cwe_pattern.match(cwe_id):
            return {
                'valid': False,
                'error': f'Invalid CWE format: {cwe_id}. Expected: CWE-NNN',
                'severity': 'error',
                'cwe_id': cwe_id
            }
        
        # Extract number
        number = int(cwe_id.split('-')[1])
        
        # Validate range (CWE has ~1200 entries)
        if number < 1 or number > 9999:
            return {
                'valid': False,
                'error': f'Invalid CWE number: {number}',
                'severity': 'warning',
                'cwe_id': cwe_id
            }
        
        return {
            'valid': True,
            'cwe_id': cwe_id,
            'number': number,
            'severity': 'info'
        }
    
    def validate_disclosure_timeline(self, disclosure_timeline: str) -> Dict[str, Any]:
        """
        Validate disclosure timeline for unpublished/zero-day findings
        
        Args:
            disclosure_timeline: Timeline string (e.g., '90_days', '48_hours')
            
        Returns:
            Validation result
        """
        if not disclosure_timeline:
            return {
                'valid': False,
                'error': 'Disclosure timeline is empty',
                'severity': 'warning'
            }
        
        timeline = disclosure_timeline.strip().lower()
        
        if timeline in self.valid_disclosure_timelines:
            return {
                'valid': True,
                'disclosure_timeline': timeline,
                'severity': 'info'
            }
        
        return {
            'valid': False,
            'error': f'Invalid disclosure timeline: {disclosure_timeline}. '
                     f'Valid values: {", ".join(self.valid_disclosure_timelines)}',
            'severity': 'warning',
            'disclosure_timeline': disclosure_timeline
        }
    
    def check_false_positive(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if finding is likely a false positive
        
        Args:
            finding: Vulnerability finding dict
            
        Returns:
            False positive check result
        """
        fp_score = 0.0
        fp_reasons = []
        
        # Check 1: Test/dummy indicators in description or context
        context_str = json.dumps(finding.get('context', {}))
        finding_str = json.dumps(finding)
        
        for indicator in self.fp_indicators:
            if indicator in finding_str.lower():
                fp_score += 0.3
                fp_reasons.append(f"Contains '{indicator}' indicator")
        
        # Check 2: Missing critical fields
        required_fields = ['type', 'severity', 'detector']
        missing_fields = [f for f in required_fields if not finding.get(f)]
        
        if missing_fields:
            fp_score += 0.2
            fp_reasons.append(f"Missing required fields: {missing_fields}")
        
        # Check 3: Invalid severity
        severity = finding.get('severity', '').lower()
        if severity and severity not in self.valid_severities:
            fp_score += 0.3
            fp_reasons.append(f"Invalid severity: {severity}")
        
        # Check 4: Suspicious payload patterns
        payload = finding.get('payload', '')
        if payload:
            # Check for test payloads
            test_payloads = ['<script>alert(1)</script>', 'test', 'abc', '123']
            if payload in test_payloads:
                fp_score += 0.4
                fp_reasons.append("Suspicious test payload")
        
        # Check 5: Confidence score validation
        confidence = finding.get('confidence', 1.0)
        if confidence < 0.3:
            fp_score += 0.2
            fp_reasons.append(f"Low confidence score: {confidence}")
        
        # Determine if likely false positive
        is_likely_fp = fp_score >= 0.5
        
        return {
            'is_likely_false_positive': is_likely_fp,
            'fp_score': min(fp_score, 1.0),
            'fp_reasons': fp_reasons,
            'recommendation': 'reject' if is_likely_fp else 'accept',
            'severity': 'warning' if is_likely_fp else 'info'
        }
    
    def validate_severity_consistency(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate severity is consistent with other attributes
        
        Args:
            finding: Vulnerability finding dict
            
        Returns:
            Consistency check result
        """
        issues = []
        severity = finding.get('severity', 'medium').lower()
        
        # Extract attributes
        has_cve = bool(finding.get('cve_id'))
        has_cwe = bool(finding.get('cwe_id'))
        is_unpublished = finding.get('is_unpublished', False)
        exploitability = finding.get('exploitability_score', 0.5)
        attack_complexity = finding.get('attack_complexity', 'medium').lower()
        user_interaction = finding.get('user_interaction', 'none')
        
        # Rule 1: Critical/High severity should have CVE/CWE
        if severity in ['critical', 'high'] and not (has_cve or has_cwe):
            # Check if this is explicitly marked as unpublished
            if is_unpublished:
                # This is acceptable - unpublished zero-day
                pass  # No issue - legitimate unpublished finding
            else:
                # Flag as unusual - might need CVE or should be marked unpublished
                issues.append({
                    'rule': 'severity_cve_consistency',
                    'message': f'{severity.upper()} severity without CVE/CWE. Consider marking as unpublished or assigning CVE.',
                    'severity': 'info'  # Downgrade from warning to info
                })
        
        # Rule 2: Low exploitability + high severity = inconsistent
        if exploitability < 0.3 and severity in ['critical', 'high']:
            issues.append({
                'rule': 'exploitability_severity_match',
                'message': 'High severity with low exploitability score',
                'severity': 'warning'
            })
        
        # Rule 3: Complex attack + critical severity = unusual
        if attack_complexity == 'high' and severity == 'critical':
            issues.append({
                'rule': 'complexity_severity_match',
                'message': 'Critical severity with high attack complexity is rare',
                'severity': 'info'
            })
        
        # Rule 4: User interaction required + critical = check
        if user_interaction == 'required' and severity == 'critical':
            issues.append({
                'rule': 'user_interaction_severity',
                'message': 'Critical severity requiring user interaction needs review',
                'severity': 'info'
            })
        
        is_consistent = len(issues) == 0
        
        return {
            'is_consistent': is_consistent,
            'issues': issues,
            'severity': 'warning' if not is_consistent else 'info',
            'recommendation': 'review' if not is_consistent else 'accept'
        }
    
    def validate_exploitability_score(self, score: float) -> Dict[str, Any]:
        """
        Validate exploitability score is in valid range
        
        Args:
            score: Exploitability score (0.0-1.0)
            
        Returns:
            Validation result
        """
        if not isinstance(score, (int, float)):
            return {
                'valid': False,
                'error': 'Exploitability score must be numeric',
                'severity': 'error'
            }
        
        if score < 0.0 or score > 1.0:
            return {
                'valid': False,
                'error': f'Exploitability score {score} out of range [0.0-1.0]',
                'severity': 'error'
            }
        
        # Check for suspicious values
        if score == 0.0 or score == 1.0:
            return {
                'valid': True,
                'warning': True,
                'message': f'Extreme exploitability score: {score}',
                'severity': 'warning'
            }
        
        return {
            'valid': True,
            'score': float(score),
            'severity': 'info'
        }
    
    def validate_finding_completeness(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate finding has all required fields
        
        For unpublished findings (is_unpublished=True), cve_id is not required
        since the CVE hasn't been assigned yet. Instead, disclosure_timeline
        and proof_of_concept are recommended.
        
        Args:
            finding: Vulnerability finding dict
            
        Returns:
            Completeness check result
        """
        # Required fields (always required regardless of unpublished status)
        required_fields = {
            'type': 'Vulnerability type (e.g., sqli, xss)',
            'severity': 'Severity level (critical/high/medium/low/info)',
            'detector': 'Detector name that found this',
            'url': 'Target URL',
            'parameter': 'Affected parameter (if applicable)'
        }
        
        # Base recommended fields for all findings
        recommended_fields = {
            'cve_id': 'CVE identifier',
            'cwe_id': 'CWE identifier',
            'description': 'Detailed description',
            'payload': 'Proof of concept payload',
            'impact': 'Impact assessment',
            'remediation': 'Remediation recommendation'
        }
        
        # Check if this is an unpublished finding
        is_unpublished = finding.get('is_unpublished', False)
        
        if is_unpublished:
            # For unpublished findings:
            # - cve_id is NOT recommended (expected to be missing, pending assignment)
            # - disclosure_timeline IS recommended (required for responsible disclosure)
            # - proof_of_concept IS recommended (required as evidence)
            recommended_fields = {
                'cwe_id': 'CWE identifier',
                'description': 'Detailed description',
                'payload': 'Proof of concept payload',
                'proof_of_concept': 'Proof of concept details',
                'impact': 'Impact assessment',
                'remediation': 'Remediation recommendation',
                'disclosure_timeline': 'Responsible disclosure timeline'
            }
        
        missing_required = []
        missing_recommended = []
        
        for field, description in required_fields.items():
            if field not in finding or not finding[field]:
                missing_required.append({
                    'field': field,
                    'description': description
                })
        
        for field, description in recommended_fields.items():
            if field not in finding or not finding[field]:
                missing_recommended.append({
                    'field': field,
                    'description': description
                })
        
        # Calculate completeness score
        total_required = len(required_fields)
        total_recommended = len(recommended_fields)
        
        required_score = (total_required - len(missing_required)) / total_required
        recommended_score = (total_recommended - len(missing_recommended)) / total_recommended
        
        overall_score = (required_score * 0.7) + (recommended_score * 0.3)
        
        # For unpublished findings, recommended fields (disclosure_timeline,
        # proof_of_concept) are effectively required for a complete submission
        if is_unpublished:
            is_complete = len(missing_required) == 0 and len(missing_recommended) == 0
        else:
            is_complete = len(missing_required) == 0
        
        return {
            'is_complete': is_complete,
            'completeness_score': overall_score,
            'missing_required': missing_required,
            'missing_recommended': missing_recommended,
            'is_unpublished': is_unpublished,
            'severity': 'error' if missing_required else ('warning' if missing_recommended else 'info'),
            'recommendation': 'complete' if is_complete else 'incomplete'
        }
    
    def validate_vulnerability_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate vulnerability context data
        
        Args:
            context: Vulnerability context dict
            
        Returns:
            Validation result
        """
        issues = []
        
        # Validate severity
        severity = context.get('severity', 'medium')
        if severity.lower() not in self.valid_severities:
            issues.append({
                'field': 'severity',
                'value': severity,
                'error': f"Invalid severity: {severity}",
                'severity': 'error'
            })
        
        # Validate attack complexity
        complexity = context.get('attack_complexity', 'medium')
        if complexity.lower() not in self.valid_complexities:
            issues.append({
                'field': 'attack_complexity',
                'value': complexity,
                'error': f"Invalid attack complexity: {complexity}",
                'severity': 'error'
            })
        
        # Validate required privileges
        privileges = context.get('required_privileges', 'none')
        if privileges.lower() not in self.valid_privileges:
            issues.append({
                'field': 'required_privileges',
                'value': privileges,
                'error': f"Invalid privilege level: {privileges}",
                'severity': 'error'
            })
        
        # Validate detection difficulty
        difficulty = context.get('detection_difficulty', 'medium')
        if difficulty.lower() not in self.valid_difficulties:
            issues.append({
                'field': 'detection_difficulty',
                'value': difficulty,
                'error': f"Invalid detection difficulty: {difficulty}",
                'severity': 'error'
            })
        
        # Validate exploitability score
        exploitability = context.get('exploitation_score', 0.5)
        exp_validation = self.validate_exploitability_score(exploitability)
        if not exp_validation['valid']:
            issues.append({
                'field': 'exploitability_score',
                'value': exploitability,
                'error': exp_validation['error'],
                'severity': 'error'
            })
        
        # Validate CVE if present
        cve_id = context.get('cve_id')
        if cve_id:
            cve_validation = self.validate_cve_id(cve_id)
            if not cve_validation['valid']:
                issues.append({
                    'field': 'cve_id',
                    'value': cve_id,
                    'error': cve_validation['error'],
                    'severity': 'warning'
                })
        
        # Validate CWE if present
        cwe_id = context.get('cwe_id')
        if cwe_id:
            cwe_validation = self.validate_cwe_id(cwe_id)
            if not cwe_validation['valid']:
                issues.append({
                    'field': 'cwe_id',
                    'value': cwe_id,
                    'error': cwe_validation['error'],
                    'severity': 'warning'
                })
        
        # Validate disclosure timeline if present (for unpublished findings)
        disclosure_timeline = context.get('disclosure_timeline')
        if disclosure_timeline:
            timeline_validation = self.validate_disclosure_timeline(disclosure_timeline)
            if not timeline_validation['valid']:
                issues.append({
                    'field': 'disclosure_timeline',
                    'value': disclosure_timeline,
                    'error': timeline_validation['error'],
                    'severity': 'warning'
                })
        
        is_valid = len([i for i in issues if i['severity'] == 'error']) == 0
        
        return {
            'is_valid': is_valid,
            'issues': issues,
            'error_count': len([i for i in issues if i['severity'] == 'error']),
            'warning_count': len([i for i in issues if i['severity'] == 'warning']),
            'severity': 'error' if not is_valid else ('warning' if issues else 'info'),
            'recommendation': 'fix_errors' if not is_valid else ('review_warnings' if issues else 'accept')
        }
    
    def comprehensive_validation(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run comprehensive validation on a finding
        
        Includes special handling for unpublished findings (zero-day vulnerabilities):
        - Unpublished findings without CVE are accepted as valid
        - Completeness check accounts for the is_unpublished flag
        - Severity consistency is relaxed for published (unmarked) findings
        
        Args:
            finding: Complete vulnerability finding dict
            
        Returns:
            Comprehensive validation report
        """
        report = {
            'finding_id': finding.get('id', 'unknown'),
            'timestamp': datetime.now().isoformat(),
            'overall_valid': True,
            'validation_score': 0.0,
            'checks': {}
        }
        
        # Check 0: Unpublished finding validation
        unpublished_check = self.validate_unpublished_finding(finding)
        report['checks']['unpublished_status'] = unpublished_check
        
        # Check 1: False positive likelihood
        fp_check = self.check_false_positive(finding)
        report['checks']['false_positive'] = fp_check
        
        # Check 2: Finding completeness
        completeness = self.validate_finding_completeness(finding)
        report['checks']['completeness'] = completeness
        
        # Check 3: Severity consistency
        context = finding.get('context', {})
        severity_consistency = self.validate_severity_consistency(finding)
        report['checks']['severity_consistency'] = severity_consistency
        
        # Check 4: Context validation
        if context:
            context_validation = self.validate_vulnerability_context(context)
            report['checks']['context_validation'] = context_validation
        else:
            report['checks']['context_validation'] = {
                'is_valid': False,
                'error': 'Missing context',
                'severity': 'warning'
            }
        
        # Calculate overall validation score
        scores = []
        
        # Check 0: Unpublished status (if unpublished, this is neutral/positive)
        if unpublished_check.get('is_unpublished', False):
            # Unpublished findings get a base score boost (they're legitimate zero-days)
            scores.append(0.8 * 0.1)  # 10% weight, base score 0.8
        elif not unpublished_check.get('is_valid', False):
            # Not unpublished and invalid - penalty
            scores.append(0.2 * 0.1)
        else:
            # Published and valid
            scores.append(1.0 * 0.1)
        
        # False positive check (lower is better)
        fp_score = 1.0 - fp_check.get('fp_score', 0.0)
        scores.append(fp_score * 0.3)
        
        # Completeness (higher is better)
        completeness_score = completeness.get('completeness_score', 0.0)
        scores.append(completeness_score * 0.3)
        
        # Severity consistency
        severity_score = 1.0 if severity_consistency.get('is_consistent', False) else 0.5
        scores.append(severity_score * 0.2)
        
        # Context validation
        context_score = 1.0 if report['checks']['context_validation'].get('is_valid', False) else 0.0
        scores.append(context_score * 0.2)
        
        report['validation_score'] = sum(scores)
        
        # Determine overall validity
        # Fixed: the original logic had a confusing double-negation.
        # has_errors is True if any check fails:
        #   - False positive check: True if likely false positive
        #   - Completeness: True if not complete
        #   - Severity consistency: True if inconsistent
        #   - Context validation: True if invalid
        has_errors = any([
            fp_check.get('is_likely_false_positive', False),  # True = likely false positive (error)
            not completeness.get('is_complete', True),
            not severity_consistency.get('is_consistent', True),
            not report['checks']['context_validation'].get('is_valid', True)
        ])
        
        # Special handling for unpublished findings
        is_unpublished_valid = unpublished_check.get('is_valid', False)
        is_unpublished = unpublished_check.get('is_unpublished', False)
        has_cve = bool(finding.get('cve_id'))
        
        # If any check has errors (false positive, incomplete, invalid context), reject immediately
        if has_errors:
            report['overall_valid'] = False
            report['recommendation'] = 'reject' if fp_check.get('is_likely_false_positive', False) else 'review'
            report['action'] = 'discard' if fp_check.get('is_likely_false_positive', False) else 'additional_verification'
            report['message'] = 'Finding failed one or more validation checks'
        elif is_unpublished and is_unpublished_valid:
            # Unpublished findings with no errors are accepted
            report['overall_valid'] = True
            report['recommendation'] = 'accept'
            report['action'] = 'proceed'
            report['message'] = 'Valid unpublished finding - pending CVE assignment'
        elif not is_unpublished_valid and not has_cve:
            # Not unpublished and missing CVE without unpublished flag
            report['overall_valid'] = False
            report['recommendation'] = 'reject'
            report['action'] = 'discard'
            report['message'] = 'Finding lacks CVE and is not marked as unpublished'
        else:
            # Normal threshold for published findings
            report['overall_valid'] = report['validation_score'] >= 0.7
            
            if report['validation_score'] >= 0.9:
                report['recommendation'] = 'accept'
                report['action'] = 'proceed'
            elif report['validation_score'] >= 0.7:
                report['recommendation'] = 'review'
                report['action'] = 'manual_review'
            elif report['validation_score'] >= 0.5:
                report['recommendation'] = 'caution'
                report['action'] = 'additional_verification'
            else:
                report['recommendation'] = 'reject'
                report['action'] = 'discard'
        
        return report
    
    def batch_validate_findings(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate multiple findings
        
        Args:
            findings: List of vulnerability findings
            
        Returns:
            Batch validation report
        """
        results = []
        
        for finding in findings:
            validation = self.comprehensive_validation(finding)
            results.append(validation)
        
        # Aggregate statistics
        total = len(results)
        valid_count = sum(1 for r in results if r['overall_valid'])
        invalid_count = total - valid_count
        
        avg_score = sum(r['validation_score'] for r in results) / total if total > 0 else 0.0
        
        recommendations = {}
        for r in results:
            rec = r.get('recommendation', 'unknown')
            recommendations[rec] = recommendations.get(rec, 0) + 1
        
        return {
            'total_findings': total,
            'valid_findings': valid_count,
            'invalid_findings': invalid_count,
            'average_validation_score': avg_score,
            'validation_distribution': recommendations,
            'detailed_results': results,
            'summary': self._generate_summary(results)
        }
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> str:
        """Generate human-readable summary"""
        if not results:
            return "No findings to validate"
        
        total = len(results)
        valid = sum(1 for r in results if r['overall_valid'])
        avg_score = sum(r['validation_score'] for r in results) / total
        
        summary = f"Validated {total} findings: {valid} valid ({avg_score:.1%} avg score). "
        
        if avg_score >= 0.8:
            summary += "High quality findings."
        elif avg_score >= 0.6:
            summary += "Moderate quality, some may need review."
        else:
            summary += "Low quality findings, recommend manual review."
        
        return summary


def has_cve_or_cwe_check(finding: Dict[str, Any]) -> bool:
    """
    Helper to check if finding has CVE or CWE
    
    Args:
        finding: Vulnerability finding dict
        
    Returns:
        True if finding has CVE or CWE, False otherwise
    """
    return bool(finding.get('cve_id')) or bool(finding.get('cwe_id'))


class VulnerabilityPatternValidator:
    """
    Validator untuk pola vulnerability
    Memastikan pattern sesuai dengan known vulnerability databases
    """
    
    def __init__(self):
        # Known vulnerability patterns
        self.sql_injection_patterns = [
            r"(?i)(union.*select|select.*from|insert.*into|delete.*from|drop.*table)",
            r"(?i)(or\s+1\s*=\s*1|and\s+1\s*=\s*1)",
            r"(?i)(--|#|/\*|\*/|xp_|sp_)",
        ]
        
        self.xss_patterns = [
            r"(?i)(<script|</script>|javascript:|onload=|onerror=)",
            r"(?i)(alert\(|confirm\(|prompt\(|document\.cookie)",
            r"(?i)(<img.*onerror|<svg.*onload|<body.*onload)",
        ]
        
        self.ssrf_patterns = [
            r"(?i)(localhost|127\.0\.0\.1|0\.0\.0\.0|::1)",
            r"(?i)(file://|gopher://|dict://|sftp://)",
            r"(?i)(169\.254\.|10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)",
        ]
    
    def validate_sqli_pattern(self, payload: str) -> Dict[str, Any]:
        """Validate SQL injection pattern"""
        if not payload:
            return {'valid': False, 'error': 'Empty payload'}
        
        matches = []
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, payload):
                matches.append(pattern)
        
        return {
            'valid': len(matches) > 0,
            'matches': matches,
            'confidence': min(len(matches) / len(self.sql_injection_patterns), 1.0)
        }
    
    def validate_xss_pattern(self, payload: str) -> Dict[str, Any]:
        """Validate XSS pattern"""
        if not payload:
            return {'valid': False, 'error': 'Empty payload'}
        
        matches = []
        for pattern in self.xss_patterns:
            if re.search(pattern, payload):
                matches.append(pattern)
        
        return {
            'valid': len(matches) > 0,
            'matches': matches,
            'confidence': min(len(matches) / len(self.xss_patterns), 1.0)
        }
    
    def validate_ssrf_pattern(self, payload: str) -> Dict[str, Any]:
        """Validate SSRF pattern"""
        if not payload:
            return {'valid': False, 'error': 'Empty payload'}
        
        matches = []
        for pattern in self.ssrf_patterns:
            if re.search(pattern, payload):
                matches.append(pattern)
        
        return {
            'valid': len(matches) > 0,
            'matches': matches,
            'confidence': min(len(matches) / len(self.ssrf_patterns), 1.0)
        }
    
    def validate_vulnerability_type(self, vuln_type: str, payload: str = '') -> Dict[str, Any]:
        """
        Validate vulnerability type matches payload pattern
        
        Args:
            vuln_type: Vulnerability type (sqli, xss, ssrf, etc.)
            payload: Payload to check
            
        Returns:
            Validation result
        """
        vuln_type = vuln_type.lower().strip()
        
        validators = {
            'sqli': self.validate_sqli_pattern,
            'xss': self.validate_xss_pattern,
            'ssrf': self.validate_ssrf_pattern
        }
        
        validator = validators.get(vuln_type)
        if not validator:
            return {
                'valid': True,
                'message': f'No pattern validator for type: {vuln_type}',
                'severity': 'info'
            }
        
        result = validator(payload)
        result['vuln_type'] = vuln_type
        
        return result
