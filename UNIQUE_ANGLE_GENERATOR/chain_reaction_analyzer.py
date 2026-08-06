class ChainReactionAnalyzer:
    """
    Find additional exploitation paths.
    Menemukan jalur eksploitasi tambahan dari temuan awal.
    """
    
    def __init__(self):
        self.exploitation_chains = {
            'xss': ['session_theft', 'account_takeover', 'csrf_chaining'],
            'ssrf': ['internal_recon', 'aws_metadata_access', 'database_access'],
            'idor': ['privilege_escalation', 'data_exfiltration', 'account_impersonation'],
            'sqli': ['authentication_bypass', 'admin_panel_access', 'rce_via_udf'],
            'rce': ['persistence', 'lateral_movement', 'credential_dumping']
        }
    
    def analyze_chain_reactions(self, initial_finding: dict):
        """
        Analisis reaksi berantai dari temuan awal.
        """
        results = {
            'initial_finding': initial_finding,
            'additional_paths': [],
            'blast_radius': 'limited',
            'chaining_opportunities': [],
            'analysis_complete': False
        }
        
        try:
            vuln_type = initial_finding.get('type', '').lower()
            
            # Temukan jalur eksploitasi tambahan
            additional_paths = self._find_additional_exploitation_paths(vuln_type)
            results['additional_paths'] = additional_paths
            
            # Tentukan blast radius
            blast_radius = self._assess_blast_radius(vuln_type, initial_finding)
            results['blast_radius'] = blast_radius
            
            # Identifikasi peluang chaining
            chaining_opportunities = self._identify_chaining_opportunities(vuln_type)
            results['chaining_opportunities'] = chaining_opportunities
            
            results['analysis_complete'] = True
        
        except Exception as e:
            results['error'] = f'Chain reaction analysis failed: {str(e)}'
        
        return results
    
    def _find_additional_exploitation_paths(self, vuln_type: str) -> list:
        """Temukan jalur eksploitasi tambahan."""
        base_paths = self.exploitation_chains.get(vuln_type, [])
        
        # Tambahkan jalur umum
        common_paths = ['data_exfiltration', 'persistence', 'impact_amplification']
        all_paths = base_paths + common_paths
        
        return list(set(all_paths))
    
    def _assess_blast_radius(self, vuln_type: str, finding: dict) -> str:
        """Nilai blast radius."""
        target_scope = finding.get('scope', 'single_endpoint')
        
        if vuln_type in ['rce', 'sqli']:
            if target_scope == 'entire_application':
                return 'critical'
            else:
                return 'high'
        elif vuln_type in ['xss', 'ssrf', 'idor']:
            if target_scope == 'entire_application':
                return 'high'
            else:
                return 'medium'
        else:
            return 'limited'
    
    def _identify_chaining_opportunities(self, vuln_type: str) -> list:
        """Identifikasi peluang chaining."""
        opportunities = []
        
        if vuln_type == 'xss':
            opportunities.extend([
                'Combine with CSRF to perform state-changing actions',
                'Chain with IDOR to access other users data',
                'Use for session hijacking leading to account takeover'
            ])
        elif vuln_type == 'ssrf':
            opportunities.extend([
                'Access cloud metadata services for credential theft',
                'Scan internal network for additional vulnerabilities',
                'Chain with file inclusion to read local files'
            ])
        elif vuln_type == 'idor':
            opportunities.extend([
                'Escalate privileges by accessing admin endpoints',
                'Chain with XSS to steal sessions of other users',
                'Access sensitive data leading to business impact'
            ])
        elif vuln_type == 'sqli':
            opportunities.extend([
                'Bypass authentication to access admin panels',
                'Extract database credentials for lateral movement',
                'Achieve RCE through UDF or file write primitives'
            ])
        elif vuln_type == 'rce':
            opportunities.extend([
                'Establish persistence through backdoor installation',
                'Dump credentials from memory or configuration files',
                'Move laterally to other systems in the network'
            ])
        
        return opportunities