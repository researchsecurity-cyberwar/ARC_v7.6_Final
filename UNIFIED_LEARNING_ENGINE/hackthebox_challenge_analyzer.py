class HackTheBoxChallengeAnalyzer:
    """
    HTB machine analysis.
    Menganalisis mesin HackTheBox untuk ekstraksi pola teknik.
    """
    
    def __init__(self):
        self.htb_categories = {
            'starting_point': ['enumeration', 'basic_exploitation'],
            'easy': ['web_exploitation', 'basic_pwn', 'simple_forensics'],
            'medium': ['advanced_web', 'windows_active_directory', 'linux_privesc'],
            'hard': ['advanced_pwn', 'kernel_exploitation', 'complex_chains']
        }
    
    def analyze_htb_machine(self, machine_data: dict):
        """
        Analisis mesin HackTheBox.
        """
        try:
            machine_name = machine_data.get('name', '')
            difficulty = machine_data.get('difficulty', 'medium').lower()
            tags = machine_data.get('tags', [])
            
            # Tentukan tipe kerentanan berdasarkan tag HTB
            vulnerability_type = self._detect_htb_vulnerability(tags)
            
            # Ekstrak pola teknik berdasarkan kesulitan
            technique_patterns = self._extract_htb_techniques(difficulty, tags)
            
            # Bangun pendekatan solusi khusus HTB
            solution_approach = self._build_htb_solution_approach(vulnerability_type, difficulty)
            
            return {
                'vulnerability_type': vulnerability_type,
                'technique_patterns': technique_patterns,
                'solution_approach': solution_approach,
                'learning_insights': {
                    'htb_specific_tips': self._get_htb_tips(difficulty, vulnerability_type),
                    'common_pitfalls': self._identify_htb_pitfalls(vulnerability_type),
                    'tool_chain': self._recommend_htb_toolchain(vulnerability_type)
                }
            }
        
        except Exception as e:
            return {
                'error': f'HTB analysis failed: {str(e)}',
                'vulnerability_type': 'unknown',
                'technique_patterns': ['generic_analysis'],
                'solution_approach': 'Follow standard CTF methodology'
            }
    
    def _detect_htb_vulnerability(self, tags: list) -> str:
        """Deteksi tipe kerentanan berdasarkan tag HTB."""
        tag_text = ' '.join(tag.lower() for tag in tags)
        
        if 'web' in tag_text:
            if 'sqli' in tag_text or 'sql' in tag_text:
                return 'sql_injection'
            elif 'xss' in tag_text:
                return 'xss'
            elif 'ssrf' in tag_text:
                return 'ssrf'
            elif 'rce' in tag_text:
                return 'rce'
            else:
                return 'web_misc'
        elif 'active directory' in tag_text:
            return 'active_directory'
        elif 'linux' in tag_text:
            return 'linux_privesc'
        elif 'windows' in tag_text:
            return 'windows_privesc'
        elif 'binary' in tag_text or 'pwn' in tag_text:
            return 'pwn'
        elif 'forensics' in tag_text:
            return 'forensics'
        else:
            return 'misc'
    
    def _extract_htb_techniques(self, difficulty: str, tags: list) -> list:
        """Ekstrak pola teknik berdasarkan kesulitan HTB."""
        base_patterns = []
        
        # Pola berdasarkan kesulitan
        if difficulty == 'starting_point':
            base_patterns.extend(['basic_enumeration', 'simple_exploitation'])
        elif difficulty == 'easy':
            base_patterns.extend(['standard_enumeration', 'common_exploits'])
        elif difficulty == 'medium':
            base_patterns.extend(['advanced_enumeration', 'chained_exploitation'])
        elif difficulty == 'hard':
            base_patterns.extend(['complex_chains', 'custom_exploitation'])
        
        # Pola berdasarkan tag
        tag_text = ' '.join(tag.lower() for tag in tags)
        if 'active directory' in tag_text:
            base_patterns.extend(['kerberoasting', 'bloodhound', 'pass_the_hash'])
        if 'linux' in tag_text:
            base_patterns.extend(['linpeas', 'sudo_misconfig', 'kernel_exploit'])
        if 'windows' in tag_text:
            base_patterns.extend(['winpeas', 'mimikatz', 'bloodhound'])
        
        return list(set(base_patterns))
    
    def _build_htb_solution_approach(self, vuln_type: str, difficulty: str) -> str:
        """Bangun pendekatan solusi khusus HTB."""
        base_approach = "1. Perform thorough enumeration\n2. Identify attack vectors\n3. Exploit vulnerabilities\n4. Escalate privileges\n5. Capture flags"
        
        if vuln_type == 'active_directory':
            return "1. Enumerate domain users and groups\n2. Perform Kerberoasting\n3. Abuse misconfigurations\n4. Move laterally\n5. Achieve domain admin"
        elif vuln_type == 'linux_privesc':
            return "1. Enumerate system information\n2. Run linpeas\n3. Identify privilege escalation vectors\n4. Exploit misconfigurations\n5. Get root shell"
        elif vuln_type == 'windows_privesc':
            return "1. Enumerate Windows system\n2. Run winpeas\n3. Check for common exploits\n4. Abuse service permissions\n5. Get SYSTEM access"
        elif difficulty == 'hard':
            return "1. Deep enumeration of all services\n2. Identify non-obvious attack vectors\n3. Chain multiple vulnerabilities\n4. Develop custom exploits\n5. Achieve complete system compromise"
        
        return base_approach
    
    def _get_htb_tips(self, difficulty: str, vuln_type: str) -> list:
        """Dapatkan tips khusus HTB."""
        tips = [
            'Always check /etc/passwd and /etc/shadow on Linux machines',
            'Use BloodHound for Active Directory machines',
            'Check for backup files and source code leaks',
            'Enumerate all ports, not just the common ones'
        ]
        
        if difficulty == 'hard':
            tips.append('Look for subtle misconfigurations and logic flaws')
        if vuln_type == 'active_directory':
            tips.append('Focus on user enumeration and group memberships')
        
        return tips[:3]
    
    def _identify_htb_pitfalls(self, vuln_type: str) -> list:
        """Identifikasi jebakan umum di HTB."""
        pitfalls = [
            'Skipping thorough enumeration',
            'Not checking for alternative attack vectors',
            'Overlooking simple solutions for complex problems'
        ]
        
        if vuln_type == 'active_directory':
            pitfalls.append('Not properly configuring BloodHound')
        if vuln_type == 'pwn':
            pitfalls.append('Not understanding binary protections properly')
        
        return pitfalls
    
    def _recommend_htb_toolchain(self, vuln_type: str) -> list:
        """Rekomendasikan rantai tool khusus HTB."""
        base_tools = ['nmap', 'gobuster', 'burpsuite', 'john']
        
        if vuln_type == 'active_directory':
            return base_tools + ['bloodhound', 'crackmapexec', 'impacket']
        elif vuln_type == 'linux_privesc':
            return base_tools + ['linpeas', 'pspy', 'gtfo_bins']
        elif vuln_type == 'windows_privesc':
            return base_tools + ['winpeas', 'mimikatz', 'sharpup']
        elif vuln_type == 'pwn':
            return base_tools + ['gdb', 'pwntools', 'ROPgadget']
        else:
            return base_tools