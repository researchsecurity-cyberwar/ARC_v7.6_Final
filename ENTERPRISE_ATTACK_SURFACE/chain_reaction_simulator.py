class ChainReactionSimulator:
    """
    “What if I SSRF here? → Can I reach metadata?”
    Mensimulasikan rantai eksploitasi multi-langkah.
    """
    
    def __init__(self):
        self.attack_chains = {
            'ssrf_to_cloud_takeover': [
                'ssrf_internal_discovery',
                'cloud_metadata_access', 
                'iam_privilege_escalation',
                'data_exfiltration'
            ],
            'idor_to_account_takeover': [
                'idor_parameter_tampering',
                'session_token_leak',
                'account_impersonation'
            ],
            'xss_to_rce': [
                'dom_xss_execution',
                'client_side_prototype_pollution',
                'browser_rce_chain'
            ]
        }
    
    def simulate_chain(self, initial_vulnerability, target_info):
        """
        Simulasikan rantai eksploitasi dari kerentanan awal.
        """
        possible_chains = self._find_relevant_chains(initial_vulnerability)
        simulation_results = []
        
        for chain_name, steps in possible_chains.items():
            chain_result = {
                'chain_name': chain_name,
                'steps': [],
                'blast_radius': 0,
                'feasibility_score': 0
            }
            
            current_context = target_info.copy()
            step_success = True
            
            for step in steps:
                if not step_success:
                    break
                
                step_result = self._simulate_step(step, current_context)
                chain_result['steps'].append(step_result)
                
                if step_result['success']:
                    # Update konteks untuk langkah berikutnya
                    current_context.update(step_result.get('new_context', {}))
                    chain_result['blast_radius'] += step_result.get('impact_score', 0)
                else:
                    step_success = False
                
                chain_result['feasibility_score'] = self._calculate_feasibility(chain_result['steps'])
            
            simulation_results.append(chain_result)
        
        return simulation_results
    
    def _find_relevant_chains(self, vuln_type):
        """Temukan rantai yang relevan dengan tipe kerentanan."""
        relevant = {}
        vuln_lower = vuln_type.lower()
        
        if 'ssrf' in vuln_lower:
            relevant['ssrf_to_cloud_takeover'] = self.attack_chains['ssrf_to_cloud_takeover']
        if 'idor' in vuln_lower or 'bola' in vuln_lower:
            relevant['idor_to_account_takeover'] = self.attack_chains['idor_to_account_takeover']
        if 'xss' in vuln_lower:
            relevant['xss_to_rce'] = self.attack_chains['xss_to_rce']
        
        return relevant if relevant else self.attack_chains  # Return all if no match
    
    def _simulate_step(self, step_name, context):
        """Simulasikan satu langkah dalam rantai eksploitasi."""
        # Ini akan terintegrasi dengan modul exploitasi sebenarnya nanti
        # Untuk sekarang, simulasi berbasis aturan
        
        step_templates = {
            'ssrf_internal_discovery': {
                'description': 'Discover internal services via SSRF',
                'success_probability': 0.8,
                'impact_score': 3,
                'required_context': ['ssrf_endpoint']
            },
            'cloud_metadata_access': {
                'description': 'Access cloud metadata service',
                'success_probability': 0.7,
                'impact_score': 5,
                'required_context': ['cloud_provider']
            },
            'iam_privilege_escalation': {
                'description': 'Escalate IAM privileges',
                'success_probability': 0.6,
                'impact_score': 8,
                'required_context': ['metadata_access']
            },
            'data_exfiltration': {
                'description': 'Exfiltrate sensitive data',
                'success_probability': 0.9,
                'impact_score': 10,
                'required_context': ['privilege_escalation']
            }
        }
        
        template = step_templates.get(step_name, {})
        required_context = template.get('required_context', [])
        
        # Cek apakah konteks yang dibutuhkan tersedia
        context_available = all(req in context for req in required_context)
        success = context_available and (random.random() < template.get('success_probability', 0.5))
        
        return {
            'step_name': step_name,
            'description': template.get('description', 'Unknown step'),
            'success': success,
            'impact_score': template.get('impact_score', 1) if success else 0,
            'new_context': {f'{step_name}_success': True} if success else {}
        }
    
    def _calculate_feasibility(self, steps):
        """Hitung skor kelayakan rantai eksploitasi."""
        if not steps:
            return 0
        
        success_steps = sum(1 for step in steps if step['success'])
        total_steps = len(steps)
        avg_impact = sum(step['impact_score'] for step in steps) / total_steps
        
        feasibility = (success_steps / total_steps) * (avg_impact / 10)
        return round(feasibility, 2)