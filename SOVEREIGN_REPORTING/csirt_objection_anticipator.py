class CSIRTObjectionAnticipator:
    """
    Pre-empt 5 likely rejections + counter-evidence.
    Mengantisipasi 5 penolakan umum CSIRT dan menyediakan bukti balasan.
    """
    
    def __init__(self):
        self.common_objections = {
            'not_reproducible': {
                'objection': 'We cannot reproduce this vulnerability',
                'counter_evidence': [
                    'Video PoC demonstrating step-by-step exploitation',
                    'HAR file showing exact HTTP requests/responses',
                    'Automated reproduction script with success verification',
                    'Multiple environment validation (Chrome, Firefox, Safari)'
                ],
                'response_strategy': 'Provide additional reproduction environments and detailed network captures'
            },
            'out_of_scope': {
                'objection': 'This finding is out of scope for our program',
                'counter_evidence': [
                    'Program scope documentation showing inclusion',
                    'Similar vulnerabilities previously accepted',
                    'Business impact analysis demonstrating relevance',
                    'Regulatory compliance implications'
                ],
                'response_strategy': 'Emphasize business impact and regulatory pressure even for out-of-scope findings'
            },
            'duplicate': {
                'objection': 'This is a duplicate of an existing report',
                'counter_evidence': [
                    'Unique attack vector or exploitation chain',
                    'Different affected components or versions',
                    'Enhanced impact assessment or business logic abuse',
                    'Additional affected endpoints or parameters'
                ],
                'response_strategy': 'Highlight unique angle and enhanced impact that differentiates from existing reports'
            },
            'low_severity': {
                'objection': 'This finding is low severity and not eligible for bounty',
                'counter_evidence': [
                    'Chain reaction potential leading to critical impact',
                    'Business logic abuse with financial implications',
                    'Regulatory compliance violations increasing severity',
                    'Real-world exploitation scenarios demonstrating impact'
                ],
                'response_strategy': 'Demonstrate blast radius and business impact to justify higher severity rating'
            },
            'wont_fix': {
                'objection': 'We do not plan to fix this issue',
                'counter_evidence': [
                    'Regulatory requirements mandating remediation',
                    'Industry best practices requiring fix',
                    'Competitor implementations showing secure patterns',
                    'Simple and low-risk remediation options provided'
                ],
                'response_strategy': 'Provide specific, simple patch recommendations and emphasize regulatory obligations'
            }
        }
    
    def anticipate_objections(self, vulnerability_data: dict) -> dict:
        """
        Antisipasi keberatan CSIRT dan siapkan bukti balasan.
        """
        results = {
            'vulnerability_data': vulnerability_data,
            'anticipated_objections': [],
            'counter_strategies': []
        }
        
        # Antisipasi semua keberatan umum
        for objection_key, objection_data in self.common_objections.items():
            objection_entry = {
                'objection_type': objection_key,
                'objection_text': objection_data['objection'],
                'counter_evidence': objection_data['counter_evidence'],
                'response_strategy': objection_data['response_strategy'],
                'confidence_score': self._calculate_objection_confidence(objection_key, vulnerability_data)
            }
            results['anticipated_objections'].append(objection_entry)
            results['counter_strategies'].append({
                'objection_type': objection_key,
                'strategy': objection_data['response_strategy'],
                'evidence_to_provide': objection_data['counter_evidence']
            })
        
        return results
    
    def _calculate_objection_confidence(self, objection_type: str, vuln_data: dict) -> float:
        """Hitung kepercayaan bahwa keberatan akan diajukan."""
        vuln_type = vuln_data.get('type', '').lower()
        severity = vuln_data.get('severity', 'medium').lower()
        
        # Aturan heuristik untuk memprediksi keberatan
        if objection_type == 'not_reproducible':
            # XSS dan client-side lebih sering tidak bisa direproduksi
            if vuln_type in ['xss', 'csrf', 'clickjacking']:
                return 0.8
            else:
                return 0.4
        
        elif objection_type == 'out_of_scope':
            # Logic flaw sering dianggap out of scope
            if 'logic' in vuln_type or 'business' in vuln_type:
                return 0.7
            else:
                return 0.3
        
        elif objection_type == 'duplicate':
            # Kerentanan umum seperti SQLi sering diduplikasi
            if vuln_type in ['sqli', 'xss', 'idor']:
                return 0.6
            else:
                return 0.2
        
        elif objection_type == 'low_severity':
            if severity in ['low', 'medium']:
                return 0.9
            else:
                return 0.3
        
        elif objection_type == 'wont_fix':
            if vuln_type in ['information_disclosure', 'missing_security_headers']:
                return 0.8
            else:
                return 0.4
        
        return 0.5