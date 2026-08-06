class TryHackMeChallengeAnalyzer:
    """
    THM room analysis.
    Menganalisis room TryHackMe untuk ekstraksi pola teknik.
    """
    
    def __init__(self):
        self.thm_paths = {
            'presecurity': ['basic_concepts', 'fundamentals'],
            'jrpenetrationtester': ['web_app_testing', 'network_scanning', 'vulnerability_assessment'],
            'adventofcyber': ['web_exploitation', 'forensics', 'malware_analysis']
        }
    
    def analyze_thm_room(self, room_data: dict):
        """
        Analisis room TryHackMe.
        """
        try:
            room_name = room_data.get('name', '')
            path = room_data.get('path', 'general')
            tasks = room_data.get('tasks', [])
            
            # Tentukan tipe kerentanan berdasarkan path dan nama
            vulnerability_type = self._detect_thm_vulnerability(path, room_name)
            
            # Ekstrak pola teknik berdasarkan path
            technique_patterns = self._extract_thm_techniques(path, tasks)
            
            # Bangun pendekatan solusi khusus THM
            solution_approach = self._build_thm_solution_approach(vulnerability_type, path)
            
            return {
                'vulnerability_type': vulnerability_type,
                'technique_patterns': technique_patterns,
                'solution_approach': solution_approach,
                'learning_insights': {
                    'thm_learning_objectives': self._get_thm_objectives(path, vulnerability_type),
                    'step_by_step_guidance': self._provide_thm_guidance(vulnerability_type),
                    'recommended_modules': self._recommend_thm_modules(path)
                }
            }
        
        except Exception as e:
            return {
                'error': f'THM analysis failed: {str(e)}',
                'vulnerability_type': 'unknown',
                'technique_patterns': ['guided_learning'],
                'solution_approach': 'Follow THM room instructions step by step'
            }
    
    def _detect_thm_vulnerability(self, path: str, room_name: str) -> str:
        """Deteksi tipe kerentanan berdasarkan path THM."""
        combined_text = f"{path} {room_name}".lower()
        
        if 'web' in combined_text or 'owasp' in combined_text:
            if 'sqli' in combined_text:
                return 'sql_injection'
            elif 'xss' in combined_text:
                return 'xss'
            elif 'ssrf' in combined_text:
                return 'ssrf'
            else:
                return 'web_misc'
        elif 'network' in combined_text or 'nmap' in combined_text:
            return 'network_scanning'
        elif 'forensics' in combined_text:
            return 'forensics'
        elif 'malware' in combined_text:
            return 'malware_analysis'
        elif 'cryptography' in combined_text:
            return 'crypto'
        elif 'reversing' in combined_text:
            return 'reversing'
        else:
            return 'misc'
    
    def _extract_thm_techniques(self, path: str, tasks: list) -> list:
        """Ekstrak pola teknik berdasarkan path THM."""
        base_patterns = []
        
        # Pola berdasarkan path
        if path == 'presecurity':
            base_patterns.extend(['basic_concepts', 'fundamental_tools'])
        elif path == 'jrpenetrationtester':
            base_patterns.extend(['methodical_testing', 'standard_methodology'])
        elif path == 'adventofcyber':
            base_patterns.extend(['holiday_themed_challenges', 'varied_techniques'])
        
        # Pola berdasarkan jumlah task
        if len(tasks) > 10:
            base_patterns.append('comprehensive_analysis')
        elif len(tasks) > 5:
            base_patterns.append('structured_approach')
        else:
            base_patterns.append('focused_analysis')
        
        return list(set(base_patterns))
    
    def _build_thm_solution_approach(self, vuln_type: str, path: str) -> str:
        """Bangun pendekatan solusi khusus THM."""
        if path == 'presecurity':
            return "1. Read the theory carefully\n2. Follow the guided steps\n3. Understand the concepts\n4. Complete the questions"
        elif path == 'jrpenetrationtester':
            return "1. Set up your environment\n2. Follow the methodology\n3. Use the recommended tools\n4. Document your findings\n5. Answer all questions"
        else:
            return "1. Understand the scenario\n2. Apply relevant techniques\n3. Use provided hints\n4. Complete all tasks\n5. Reflect on learning"
    
    def _get_thm_objectives(self, path: str, vuln_type: str) -> list:
        """Dapatkan tujuan pembelajaran THM."""
        objectives = [
            'Understand fundamental security concepts',
            'Learn to use security tools effectively',
            'Develop methodical testing approach'
        ]
        
        if path == 'jrpenetrationtester':
            objectives.append('Master penetration testing methodology')
        if vuln_type != 'misc':
            objectives.append(f'Gain hands-on experience with {vuln_type.replace("_", " ")}')
        
        return objectives
    
    def _provide_thm_guidance(self, vuln_type: str) -> list:
        """Berikan panduan langkah demi langkah THM."""
        guidance = [
            'Read all instructions carefully before starting',
            'Use the hints provided in each task',
            'Take notes of commands and findings',
            'Don\'t skip the theory sections'
        ]
        
        if vuln_type == 'sql_injection':
            guidance.append('Start with basic UNION-based injections')
        elif vuln_type == 'xss':
            guidance.append('Test with simple <script>alert(1)</script> first')
        
        return guidance
    
    def _recommend_thm_modules(self, path: str) -> list:
        """Rekomendasikan modul THM terkait."""
        if path == 'presecurity':
            return ['Introduction to Cyber Security', 'Intro to Web Apps', 'Linux Fundamentals']
        elif path == 'jrpenetrationtester':
            return ['Nmap', 'Metasploit', 'OWASP Top 10', 'Vulnerability Capstone']
        else:
            return ['Complete beginner paths first', 'Practice with easy rooms', 'Join THM Discord for help']