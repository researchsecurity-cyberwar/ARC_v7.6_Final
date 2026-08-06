import json
import os

from .hackthebox_challenge_analyzer import HackTheBoxChallengeAnalyzer
from .tryhackme_challenge_analyzer import TryHackMeChallengeAnalyzer

class CTFChallengeAnalyzer:
    """
    Analyze CTF challenges & solutions.
    Menganalisis tantangan dan solusi CTF untuk ekstraksi pola teknik.
    """
    
    def __init__(self, analysis_dir="~/.arc/ctf_analysis"):
        self.analysis_dir = os.path.expanduser(analysis_dir)
        os.makedirs(self.analysis_dir, exist_ok=True)
        self.htb_analyzer = HackTheBoxChallengeAnalyzer()
        self.thm_analyzer = TryHackMeChallengeAnalyzer()
    
    def analyze_ctf_challenge(self, challenge_data: dict, platform: str):
        """
        Analisis tantangan CTF berdasarkan platform.
        """
        results = {
            'challenge_data': challenge_data,
            'platform': platform,
            'analysis_successful': False,
            'technique_patterns': [],
            'vulnerability_type': None,
            'solution_approach': None,
            'learning_insights': {}
        }
        
        try:
            if platform == 'hackthebox':
                analysis = self.htb_analyzer.analyze_htb_machine(challenge_data)
            elif platform == 'tryhackme':
                analysis = self.thm_analyzer.analyze_thm_room(challenge_data)
            else:
                # Analisis generik untuk platform lain
                analysis = self._analyze_generic_challenge(challenge_data)
            
            results.update({
                'analysis_successful': True,
                'technique_patterns': analysis.get('technique_patterns', []),
                'vulnerability_type': analysis.get('vulnerability_type'),
                'solution_approach': analysis.get('solution_approach'),
                'learning_insights': analysis.get('learning_insights', {})
            })
        
        except Exception as e:
            results['error'] = f'CTF challenge analysis failed: {str(e)}'
        
        return results
    
    def _analyze_generic_challenge(self, challenge_data: dict) -> dict:
        """Analisis generik untuk tantangan CTF."""
        title = challenge_data.get('title', '').lower()
        description = challenge_data.get('description', '').lower()
        
        # Deteksi tipe kerentanan dari judul dan deskripsi
        vulnerability_type = self._detect_vulnerability_type(title + ' ' + description)
        
        # Ekstrak pola teknik
        technique_patterns = self._extract_technique_patterns(title + ' ' + description)
        
        # Bangun pendekatan solusi
        solution_approach = self._build_solution_approach(vulnerability_type, technique_patterns)
        
        return {
            'vulnerability_type': vulnerability_type,
            'technique_patterns': technique_patterns,
            'solution_approach': solution_approach,
            'learning_insights': {
                'complexity_level': self._assess_complexity(title, description),
                'prerequisite_skills': self._identify_prerequisites(vulnerability_type),
                'tool_recommendations': self._recommend_tools(vulnerability_type)
            }
        }
    
    def _detect_vulnerability_type(self, text: str) -> str:
        """Deteksi tipe kerentanan dari teks."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['web', 'http', 'website']):
            if 'sqli' in text_lower or 'sql injection' in text_lower:
                return 'sql_injection'
            elif 'xss' in text_lower:
                return 'xss'
            elif 'ssrf' in text_lower:
                return 'ssrf'
            elif 'rce' in text_lower or 'command injection' in text_lower:
                return 'rce'
            else:
                return 'web_misc'
        elif any(word in text_lower for word in ['rev', 'reverse', 'binary']):
            return 'reversing'
        elif any(word in text_lower for word in ['crypto', 'cipher']):
            return 'crypto'
        elif any(word in text_lower for word in ['pwn', 'exploit', 'buffer']):
            return 'pwn'
        elif any(word in text_lower for word in ['forensics', 'pcap', 'memory']):
            return 'forensics'
        else:
            return 'misc'
    
    def _extract_technique_patterns(self, text: str) -> list:
        """Ekstrak pola teknik dari teks."""
        patterns = []
        text_lower = text.lower()
        
        # Pola berdasarkan kata kunci
        technique_keywords = {
            'enumeration': ['enum', 'nmap', 'gobuster', 'dirb', 'ffuf'],
            'exploitation': ['exploit', 'metasploit', 'payload', 'shell'],
            'post_exploitation': ['privesc', 'linpeas', 'winpeas', 'mimikatz'],
            'web_analysis': ['burp', 'proxy', 'intercept', 'repeater'],
            'password_cracking': ['hashcat', 'john', 'rockyou', 'brute']
        }
        
        for technique, keywords in technique_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                patterns.append(technique)
        
        return patterns or ['basic_analysis']
    
    def _build_solution_approach(self, vuln_type: str, patterns: list) -> str:
        """Bangun pendekatan solusi berdasarkan tipe kerentanan."""
        approaches = {
            'sql_injection': '1. Identify injection point\n2. Test with basic payloads\n3. Extract database schema\n4. Dump sensitive data',
            'xss': '1. Identify input vectors\n2. Test with alert(1)\n3. Craft payload for session theft\n4. Verify impact',
            'ssrf': '1. Find URL parameters\n2. Test with localhost\n3. Access internal services\n4. Extract sensitive data',
            'rce': '1. Identify command injection\n2. Bypass filters\n3. Execute system commands\n4. Establish reverse shell',
            'reversing': '1. Analyze binary type\n2. Disassemble with Ghidra\n3. Identify main function\n4. Reverse engineer logic',
            'crypto': '1. Identify cipher type\n2. Analyze encryption pattern\n3. Apply cryptanalysis\n4. Decrypt flag',
            'pwn': '1. Analyze binary protections\n2. Find buffer overflow\n3. Craft ROP chain\n4. Execute shellcode',
            'forensics': '1. Analyze file type\n2. Extract hidden data\n3. Reconstruct artifacts\n4. Find flag',
            'misc': '1. Analyze challenge files\n2. Look for steganography\n3. Decode encoded data\n4. Extract flag'
        }
        
        return approaches.get(vuln_type, '1. Analyze challenge\n2. Identify attack vector\n3. Exploit vulnerability\n4. Capture flag')
    
    def _assess_complexity(self, title: str, description: str) -> str:
        """Nilai tingkat kompleksitas."""
        combined_text = (title + ' ' + description).lower()
        
        if any(word in combined_text for word in ['easy', 'beginner', 'simple']):
            return 'beginner'
        elif any(word in combined_text for word in ['medium', 'intermediate']):
            return 'intermediate'
        elif any(word in combined_text for word in ['hard', 'advanced', 'expert']):
            return 'advanced'
        else:
            return 'intermediate'
    
    def _identify_prerequisites(self, vuln_type: str) -> list:
        """Identifikasi keterampilan prasyarat."""
        prerequisites = {
            'sql_injection': ['SQL basics', 'Web application knowledge', 'Burp Suite'],
            'xss': ['JavaScript knowledge', 'DOM understanding', 'Web security'],
            'ssrf': ['Network knowledge', 'Internal service enumeration', 'Cloud security'],
            'rce': ['Command injection techniques', 'Filter bypass', 'Reverse shell'],
            'reversing': ['Assembly knowledge', 'Ghidra/IDA usage', 'Binary analysis'],
            'crypto': ['Cryptography basics', 'Cipher identification', 'Mathematical analysis'],
            'pwn': ['Buffer overflow concepts', 'ROP chain building', 'Memory layout'],
            'forensics': ['File format analysis', 'Memory forensics', 'Network analysis'],
            'misc': ['Steganography', 'Encoding/decoding', 'Pattern recognition']
        }
        
        return prerequisites.get(vuln_type, ['General CTF knowledge'])
    
    def _recommend_tools(self, vuln_type: str) -> list:
        """Rekomendasikan tools berdasarkan tipe kerentanan."""
        tools = {
            'sql_injection': ['sqlmap', 'burpsuite', 'nuclei'],
            'xss': ['dalfox', 'xsstrike', 'burpsuite'],
            'ssrf': ['interact.sh', 'burpsuite', 'nuclei'],
            'rce': ['metasploit', 'nc', 'bash'],
            'reversing': ['ghidra', 'ida', 'radare2'],
            'crypto': ['cyberchef', 'john', 'hashcat'],
            'pwn': ['pwntools', 'gdb', 'ROPgadget'],
            'forensics': ['binwalk', 'volatility', 'wireshark'],
            'misc': ['steghide', 'exiftool', 'foremost']
        }
        
        return tools.get(vuln_type, ['general purpose tools'])