class RoleAssigner:
    """
    Assign roles: Recon Specialist / Chain Validator.
    Menetapkan peran kepada agen berdasarkan kemampuan dan konteks misi.
    """
    
    def __init__(self):
        self.agent_capabilities = {
            'recon_specialist': ['subdomain_enum', 'port_scan', 'osint'],
            'exploit_developer': ['vuln_exploitation', 'payload_crafting', 'bypass_techniques'],
            'chain_validator': ['attack_path_validation', 'blast_radius_analysis', 'impact_assessment'],
            'report_writer': ['evidence_documentation', 'report_generation', 'communication'],
            'learning_analyst': ['feedback_processing', 'pattern_recognition', 'strategy_optimization']
        }
        
        self.mission_role_requirements = {
            'bug_bounty': {
                'recon_specialist': 1,
                'exploit_developer': 1,
                'chain_validator': 1,
                'report_writer': 1
            },
            'ctf': {
                'recon_specialist': 1,
                'exploit_developer': 2,
                'report_writer': 1
            },
            'vdp': {
                'recon_specialist': 1,
                'chain_validator': 1,
                'report_writer': 1,
                'learning_analyst': 1
            }
        }
    
    def assign_roles_to_agents(self, mission_type: str, available_agents: List[str]) -> dict:
        """
        Tetapkan peran kepada agen yang tersedia.
        """
        if mission_type not in self.mission_role_requirements:
            return {'error': f'Unsupported mission type: {mission_type}'}
        
        role_assignments = {}
        unassigned_agents = available_agents.copy()
        
        # Tetapkan peran berdasarkan kebutuhan misi
        role_requirements = self.mission_role_requirements[mission_type]
        
        for role, required_count in role_requirements.items():
            assigned_count = 0
            role_assignments[role] = []
            
            # Cari agen yang cocok untuk peran ini
            for agent in unassigned_agents[:]:  # Copy list untuk iterasi aman
                if self._is_agent_suitable_for_role(agent, role):
                    role_assignments[role].append(agent)
                    unassigned_agents.remove(agent)
                    assigned_count += 1
                    
                    if assigned_count >= required_count:
                        break
        
        # Tetapkan agen yang tersisa ke peran learning_analyst
        if unassigned_agents:
            if 'learning_analyst' not in role_assignments:
                role_assignments['learning_analyst'] = []
            role_assignments['learning_analyst'].extend(unassigned_agents)
        
        return {
            'mission_type': mission_type,
            'role_assignments': role_assignments,
            'unassigned_agents': unassigned_agents if 'learning_analyst' not in role_assignments else []
        }
    
    def _is_agent_suitable_for_role(self, agent_id: str, role: str) -> bool:
        """Periksa apakah agen cocok untuk peran tertentu."""
        # Dalam implementasi nyata, ini akan memeriksa profil kemampuan agen
        # Untuk sekarang, asumsikan semua agen serbaguna
        return True
    
    def get_role_responsibilities(self, role: str) -> List[str]:
        """Dapatkan tanggung jawab untuk peran tertentu."""
        responsibilities = {
            'recon_specialist': [
                'Perform comprehensive reconnaissance',
                'Identify attack surface',
                'Map network topology',
                'Discover hidden endpoints'
            ],
            'exploit_developer': [
                'Develop custom exploits',
                'Craft evasion payloads',
                'Test exploitation chains',
                'Validate vulnerability impact'
            ],
            'chain_validator': [
                'Verify attack path feasibility',
                'Assess blast radius',
                'Calculate business impact',
                'Ensure ethical boundaries'
            ],
            'report_writer': [
                'Document evidence professionally',
                'Write clear technical reports',
                'Communicate with stakeholders',
                'Ensure compliance requirements'
            ],
            'learning_analyst': [
                'Analyze mission feedback',
                'Update knowledge base',
                'Optimize future strategies',
                'Identify improvement areas'
            ]
        }
        return responsibilities.get(role, [])