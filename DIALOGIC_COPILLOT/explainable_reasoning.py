class ExplainableReasoning:
    """
    “Why I think this is vulnerable” + MITRE mapping.
    Memberikan penalaran yang dapat dijelaskan dengan pemetaan MITRE.
    """
    
    def __init__(self):
        self.mitre_mappings = {
            'xss': 'T1059 - Command and Scripting Interpreter',
            'sqli': 'T1189 - Drive-by Compromise',
            'ssrf': 'T1071.001 - Application Layer Protocol: Web Protocols',
            'idor': 'T1068 - Exploitation for Privilege Escalation',
            'rce': 'T1059 - Command and Scripting Interpreter',
            'lfi': 'T1059 - Command and Scripting Interpreter',
            'csrf': 'T1071.001 - Application Layer Protocol: Web Protocols'
        }
        
        self.confidence_factors = {
            'high': ['multiple_indicators', 'reproducible', 'severe_impact'],
            'medium': ['single_indicator', 'theoretical', 'moderate_impact'],
            'low': ['speculative', 'unverified', 'minimal_impact']
        }
    
    def generate_explanation(self, vulnerability: dict) -> dict:
        """
        Hasilkan penjelasan yang dapat dipahami untuk kerentanan.
        """
        vuln_type = vulnerability.get('type', '').lower()
        confidence = vulnerability.get('confidence', 'medium')
        
        explanation = {
            'vulnerability_type': vuln_type,
            'mitre_technique': self.mitre_mappings.get(vuln_type, 'Unknown'),
            'reasoning_steps': self._generate_reasoning_steps(vulnerability),
            'confidence_level': confidence,
            'confidence_factors': self.confidence_factors.get(confidence, []),
            'business_impact': self._assess_business_impact(vulnerability),
            'remediation_guidance': self._generate_remediation_guidance(vuln_type)
        }
        
        return explanation
    
    def _generate_reasoning_steps(self, vulnerability: dict) -> list:
        """Hasilkan langkah-langkah penalaran."""
        steps = []
        vuln_type = vulnerability.get('type', '')
        
        if vuln_type == 'xss':
            steps = [
                'Detected user input reflected in HTML context without proper encoding',
                'Input can be controlled by attacker via URL parameters',
                'Execution context allows JavaScript injection',
                'Potential for session hijacking and credential theft'
            ]
        elif vuln_type == 'sqli':
            steps = [
                'User input concatenated directly into SQL query',
                'Error messages reveal database structure',
                'Time-based blind injection confirmed',
                'Potential for full database compromise'
            ]
        elif vuln_type == 'ssrf':
            steps = [
                'URL parameter used to fetch external resources',
                'Internal network addresses accessible',
                'Cloud metadata service reachable',
                'Potential for IAM credential theft'
            ]
        else:
            steps = [
                f'Detected {vuln_type} vulnerability through automated scanning',
                'Vulnerability confirmed through validation tests',
                'Impact assessed based on target context'
            ]
        
        return steps
    
    def _assess_business_impact(self, vulnerability: dict) -> str:
        """Nilai dampak bisnis."""
        severity = vulnerability.get('severity', 'medium')
        target_type = vulnerability.get('target_type', 'web_application')
        
        impact_descriptions = {
            'critical': {
                'web_application': 'Full system compromise, data breach, financial loss',
                'api': 'Unauthorized access to all user data, account takeover',
                'cloud': 'Complete infrastructure takeover, data exfiltration'
            },
            'high': {
                'web_application': 'Significant data exposure, service disruption',
                'api': 'Access to sensitive user information',
                'cloud': 'Privilege escalation, resource abuse'
            },
            'medium': {
                'web_application': 'Limited information disclosure',
                'api': 'Partial data access',
                'cloud': 'Limited privilege escalation'
            }
        }
        
        return impact_descriptions.get(severity, {}).get(target_type, 'General security risk')
    
    def _generate_remediation_guidance(self, vuln_type: str) -> str:
        """Hasilkan panduan remediasi."""
        guidance = {
            'xss': 'Implement proper output encoding based on context (HTML, JavaScript, URL). Use Content Security Policy (CSP) with strict directives.',
            'sqli': 'Use parameterized queries or prepared statements. Never concatenate user input directly into SQL queries.',
            'ssrf': 'Implement allowlist for URL schemes and domains. Disable unnecessary URL protocols (file://, gopher://).',
            'idor': 'Implement proper authorization checks for every object access. Use unpredictable identifiers.',
            'rce': 'Never execute user-controlled input as system commands. Use allowlist for command parameters.',
            'lfi': 'Avoid including files based on user input. Use allowlist for file paths.',
            'csrf': 'Implement anti-CSRF tokens for state-changing operations. Use SameSite cookies.'
        }
        
        return guidance.get(vuln_type, 'Apply secure coding practices and validate all user input.')