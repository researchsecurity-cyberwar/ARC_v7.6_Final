class FindingFusionEngine:
    """
    Merge partial findings into full exploitation paths.
    Menggabungkan temuan parsial menjadi jalur eksploitasi lengkap.
    """
    
    def __init__(self):
        self.fusion_rules = {
            'ssrf_to_cloud_takeover': {
                'prerequisites': ['ssrf_vulnerability', 'cloud_environment'],
                'fusion_logic': self._fuse_ssrf_cloud_path
            },
            'idor_to_account_takeover': {
                'prerequisites': ['idor_vulnerability', 'session_management'],
                'fusion_logic': self._fuse_idor_account_path
            },
            'xss_to_rce': {
                'prerequisites': ['dom_xss', 'client_side_prototype_pollution'],
                'fusion_logic': self._fuse_xss_rce_path
            }
        }
    
    def fuse_partial_findings(self, findings: List[dict], target_context: dict) -> List[dict]:
        """
        Gabungkan temuan parsial menjadi jalur eksploitasi lengkap.
        """
        fused_findings = []
        
        # Kelompokkan temuan berdasarkan tipe
        finding_types = {}
        for finding in findings:
            ftype = finding.get('type', 'unknown')
            if ftype not in finding_types:
                finding_types[ftype] = []
            finding_types[ftype].append(finding)
        
        # Terapkan aturan fusi
        for fusion_name, rule in self.fusion_rules.items():
            prerequisites_met = all(
                prereq in finding_types for prereq in rule['prerequisites']
            )
            
            if prerequisites_met:
                fused_path = rule['fusion_logic'](
                    finding_types, target_context, fusion_name
                )
                if fused_path:
                    fused_findings.append(fused_path)
        
        return fused_findings
    
    def _fuse_ssrf_cloud_path(self, findings: dict, context: dict, fusion_name: str) -> dict:
        """Gabungkan SSRF dengan lingkungan cloud menjadi jalur takeover."""
        ssrf_finding = findings['ssrf_vulnerability'][0]
        cloud_context = context.get('cloud_environment', {})
        
        return {
            'fusion_type': fusion_name,
            'attack_path': [
                'Exploit SSRF vulnerability',
                'Access cloud metadata service',
                'Extract IAM credentials',
                'Escalate privileges',
                'Takeover cloud resources'
            ],
            'prerequisites': findings['ssrf_vulnerability'] + [cloud_context],
            'blast_radius': 'CRITICAL',
            'confidence_score': 0.85
        }
    
    def _fuse_idor_account_path(self, findings: dict, context: dict, fusion_name: str) -> dict:
        """Gabungkan IDOR dengan manajemen sesi menjadi takeover akun."""
        idor_finding = findings['idor_vulnerability'][0]
        session_context = context.get('session_management', {})
        
        return {
            'fusion_type': fusion_name,
            'attack_path': [
                'Exploit IDOR vulnerability',
                'Access other user\'s data',
                'Extract session tokens',
                'Impersonate target user',
                'Achieve account takeover'
            ],
            'prerequisites': findings['idor_vulnerability'] + [session_context],
            'blast_radius': 'HIGH',
            'confidence_score': 0.75
        }
    
    def _fuse_xss_rce_path(self, findings: dict, context: dict, fusion_name: str) -> dict:
        """Gabungkan XSS dengan prototype pollution menjadi RCE."""
        xss_finding = findings['dom_xss'][0]
        pollution_context = context.get('client_side_prototype_pollution', {})
        
        return {
            'fusion_type': fusion_name,
            'attack_path': [
                'Trigger DOM-based XSS',
                'Exploit prototype pollution',
                'Execute arbitrary JavaScript',
                'Achieve client-side RCE',
                'Exfiltrate sensitive data'
            ],
            'prerequisites': findings['dom_xss'] + [pollution_context],
            'blast_radius': 'MEDIUM',
            'confidence_score': 0.65
        }