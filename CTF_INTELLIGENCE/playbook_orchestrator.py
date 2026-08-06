import os
import json

class PlaybookOrchestrator:
    """
    Execute appropriate playbook based on challenge.
    Menjalankan playbook yang sesuai berdasarkan klasifikasi challenge.
    """
    
    def __init__(self, playbook_dir="~/.arc/playbooks"):
        self.playbook_dir = os.path.expanduser(playbook_dir)
        os.makedirs(self.playbook_dir, exist_ok=True)
        self.playbooks = self._load_playbooks()
    
    def execute_playbook(self, challenge_category: str, challenge_data: dict):
        """
        Jalankan playbook berdasarkan kategori challenge.
        """
        results = {
            'challenge_category': challenge_category,
            'challenge_data': challenge_data,
            'playbook_executed': None,
            'execution_steps': [],
            'success_probability': 0.0,
            'recommended_tools': []
        }
        
        try:
            # Pilih playbook berdasarkan kategori
            playbook = self._select_playbook(challenge_category)
            if not playbook:
                # Gunakan playbook default jika tidak ada
                playbook = self._create_default_playbook(challenge_category)
            
            results['playbook_executed'] = playbook['name']
            results['execution_steps'] = playbook['steps']
            results['recommended_tools'] = playbook['tools']
            
            # Hitung probabilitas keberhasilan berdasarkan kompleksitas
            complexity = len(playbook['steps'])
            if complexity <= 3:
                success_prob = 0.8
            elif complexity <= 6:
                success_prob = 0.6
            else:
                success_prob = 0.4
            
            results['success_probability'] = success_prob
        
        except Exception as e:
            results['error'] = f'Playbook execution failed: {str(e)}'
        
        return results
    
    def _load_playbooks(self):
        """Muat playbook dari direktori."""
        playbooks = {}
        
        # Playbook dasar untuk setiap kategori
        basic_playbooks = {
            'web': {
                'name': 'Web Challenge Playbook',
                'category': 'web',
                'steps': [
                    'Reconnaissance: Identify technologies used',
                    'Enumeration: Find hidden endpoints and parameters',
                    'Vulnerability Scanning: Check for common web vulnerabilities',
                    'Exploitation: Exploit identified vulnerabilities',
                    'Post-exploitation: Extract flags and evidence'
                ],
                'tools': ['nuclei', 'dalfox', 'ffuf', 'burpsuite', 'sqlmap']
            },
            'reversing': {
                'name': 'Reversing Challenge Playbook',
                'category': 'reversing',
                'steps': [
                    'File Analysis: Determine file type and architecture',
                    'Static Analysis: Disassemble binary without execution',
                    'Dynamic Analysis: Execute binary in controlled environment',
                    'Debugging: Step through code to understand logic',
                    'Flag Extraction: Locate and extract the flag'
                ],
                'tools': ['ghidra', 'ida', 'radare2', 'gdb', 'strings']
            },
            'crypto': {
                'name': 'Crypto Challenge Playbook',
                'category': 'crypto',
                'steps': [
                    'Cipher Identification: Determine encryption algorithm',
                    'Pattern Analysis: Look for known patterns or weaknesses',
                    'Tool Selection: Choose appropriate decryption tools',
                    'Brute Force/Analysis: Apply cryptanalysis techniques',
                    'Flag Verification: Verify decrypted output contains flag'
                ],
                'tools': ['cyberchef', 'john', 'hashcat', 'openssl', 'custom scripts']
            },
            'pwn': {
                'name': 'Pwn Challenge Playbook',
                'category': 'pwn',
                'steps': [
                    'Binary Analysis: Understand program structure and protections',
                    'Vulnerability Identification: Find exploitable conditions',
                    'Exploit Development: Create payload to gain execution',
                    'Payload Delivery: Send exploit to target service',
                    'Flag Retrieval: Read flag from compromised process'
                ],
                'tools': ['pwntools', 'gdb', 'ROPgadget', 'one_gadget', 'socat']
            },
            'forensics': {
                'name': 'Forensics Challenge Playbook',
                'category': 'forensics',
                'steps': [
                    'File Analysis: Determine file type and structure',
                    'Data Carving: Extract hidden or deleted data',
                    'Memory Analysis: Analyze memory dumps for secrets',
                    'Network Analysis: Examine PCAP files for clues',
                    'Flag Reconstruction: Reconstruct flag from extracted data'
                ],
                'tools': ['binwalk', 'foremost', 'volatility', 'wireshark', 'exiftool']
            },
            'osint': {
                'name': 'OSINT Challenge Playbook',
                'category': 'osint',
                'steps': [
                    'Target Identification: Gather initial information about target',
                    'Social Media Search: Search for target across platforms',
                    'Domain Research: Investigate domain registration and DNS records',
                    'Image Analysis: Reverse search images and analyze metadata',
                    'Information Correlation: Connect disparate pieces of information'
                ],
                'tools': ['google dorks', 'shodan', 'whois', 'exiftool', 'maltego']
            }
        }
        
        return basic_playbooks
    
    def _select_playbook(self, category: str):
        """Pilih playbook berdasarkan kategori."""
        return self.playbooks.get(category, None)
    
    def _create_default_playbook(self, category: str):
        """Buat playbook default untuk kategori yang tidak dikenal."""
        return {
            'name': f'Default {category.title()} Playbook',
            'category': category,
            'steps': [
                'Initial reconnaissance and information gathering',
                'Systematic enumeration of attack surface',
                'Application of relevant exploitation techniques',
                'Verification of successful exploitation',
                'Flag extraction and documentation'
            ],
            'tools': ['general purpose tools']
        }