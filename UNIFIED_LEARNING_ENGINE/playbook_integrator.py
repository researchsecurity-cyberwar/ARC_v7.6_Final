import json
import os

class PlaybookIntegrator:
    """
    Integrate learning into all playbooks.
    Mengintegrasikan pembelajaran ke dalam semua playbook.
    """
    
    def __init__(self, playbook_dir="~/.arc/playbooks"):
        self.playbook_dir = os.path.expanduser(playbook_dir)
        os.makedirs(self.playbook_dir, exist_ok=True)
        self.knowledge_graph = TechniqueKnowledgeGraph()
    
    def integrate_learning_into_playbooks(self, learning_data: dict):
        """
        Integrasikan data pembelajaran ke dalam playbook yang relevan.
        """
        results = {
            'learning_data': learning_data,
            'playbooks_updated': [],
            'integration_successful': False,
            'new_playbook_created': False
        }
        
        try:
            # Dapatkan kategori target dari data pembelajaran
            target_category = learning_data.get('target_category')
            if not target_category:
                results['error'] = 'No target category specified in learning data'
                return results
            
            # Temukan jalur teknik optimal
            optimal_path = self.knowledge_graph.find_optimal_technique_path(
                target_category,
                learning_data.get('constraints', {})
            )
            
            if not optimal_path.get('path_found', False):
                results['warning'] = 'No optimal path found, creating basic playbook'
                playbook_content = self._create_basic_playbook(target_category, learning_data)
            else:
                playbook_content = self._create_advanced_playbook(optimal_path, learning_data)
            
            # Simpan playbook
            playbook_filename = f"playbook_{target_category}_{int(time.time())}.json"
            playbook_path = os.path.join(self.playbook_dir, playbook_filename)
            
            with open(playbook_path, 'w') as f:
                json.dump(playbook_content, f, indent=2)
            
            results.update({
                'playbooks_updated': [playbook_path],
                'integration_successful': True,
                'new_playbook_created': True
            })
        
        except Exception as e:
            results['error'] = f'Playbook integration failed: {str(e)}'
        
        return results
    
    def _create_basic_playbook(self, category: str, learning_data: dict) -> dict:
        """Buat playbook dasar untuk kategori target."""
        return {
            'name': f'Basic {category.title()} Playbook',
            'category': category,
            'version': '1.0',
            'created_from': 'unified_learning_engine',
            'steps': [
                {
                    'step_number': 1,
                    'name': 'Initial Reconnaissance',
                    'description': 'Gather basic information about the target',
                    'tools': ['nmap', 'gobuster', 'whatweb'],
                    'commands': []
                },
                {
                    'step_number': 2,
                    'name': 'Vulnerability Identification',
                    'description': 'Identify potential vulnerabilities in the target',
                    'tools': ['nuclei', 'dalfox', 'ffuf'],
                    'commands': []
                },
                {
                    'step_number': 3,
                    'name': 'Exploitation',
                    'description': 'Exploit identified vulnerabilities',
                    'tools': ['manual exploitation', 'custom scripts'],
                    'commands': []
                },
                {
                    'step_number': 4,
                    'name': 'Post-Exploitation',
                    'description': 'Extract evidence and escalate privileges if possible',
                    'tools': ['manual analysis'],
                    'commands': []
                }
            ],
            'metadata': {
                'confidence_score': 0.5,
                'success_probability': learning_data.get('success_rate', 0.5),
                'recommended_for': 'beginners',
                'last_updated': time.time()
            }
        }
    
    def _create_advanced_playbook(self, optimal_path: dict, learning_data: dict) -> dict:
        """Buat playbook lanjutan berdasarkan jalur optimal."""
        path = optimal_path['optimal_path']
        confidence = optimal_path['confidence_score']
        
        steps = []
        for i, technique in enumerate(path):
            step = {
                'step_number': i + 1,
                'name': f'{technique.title()} Analysis',
                'description': f'Apply {technique} techniques based on knowledge graph',
                'tools': self._get_recommended_tools(technique),
                'commands': self._get_recommended_commands(technique),
                'success_indicators': self._get_success_indicators(technique)
            }
            steps.append(step)
        
        return {
            'name': f'Advanced {path[-1].title()} Playbook',
            'category': path[-1],
            'version': '1.0',
            'created_from': 'unified_learning_engine',
            'steps': steps,
            'metadata': {
                'confidence_score': confidence,
                'success_probability': learning_data.get('success_rate', confidence),
                'recommended_for': 'advanced users' if confidence > 0.7 else 'intermediate users',
                'knowledge_graph_path': path,
                'last_updated': time.time()
            }
        }
    
    def _get_recommended_tools(self, technique: str) -> list:
        """Dapatkan tools yang direkomendasikan untuk teknik tertentu."""
        tool_mapping = {
            'xss': ['dalfox', 'xsstrike', 'burpsuite'],
            'sqli': ['sqlmap', 'burpsuite', 'nuclei'],
            'ssrf': ['interact.sh', 'burpsuite', 'nuclei'],
            'rce': ['metasploit', 'nc', 'custom scripts'],
            'reversing': ['ghidra', 'ida', 'radare2'],
            'crypto': ['cyberchef', 'john', 'hashcat'],
            'pwn': ['pwntools', 'gdb', 'ROPgadget'],
            'forensics': ['binwalk', 'volatility', 'wireshark'],
            'web_misc': ['burpsuite', 'nuclei', 'ffuf'],
            'binary_analysis': ['ghidra', 'ida', 'strings'],
            'cryptography': ['cyberchef', 'openssl', 'custom scripts'],
            'memory_corruption': ['pwntools', 'gdb', 'checksec'],
            'digital_forensics': ['binwalk', 'foremost', 'exiftool']
        }
        return tool_mapping.get(technique, ['general purpose tools'])
    
    def _get_recommended_commands(self, technique: str) -> list:
        """Dapatkan perintah yang direkomendasikan untuk teknik tertentu."""
        # Ini akan diisi dengan perintah spesifik berdasarkan teknik
        return [f"# Commands for {technique} will be generated dynamically"]
    
    def _get_success_indicators(self, technique: str) -> list:
        """Dapatkan indikator keberhasilan untuk teknik tertentu."""
        indicators = {
            'xss': ['alert popup appears', 'cookie exfiltrated', 'session hijacked'],
            'sqli': ['database error messages', 'data extraction successful', 'authentication bypassed'],
            'ssrf': ['internal service responses', 'cloud metadata accessed', 'file inclusion successful'],
            'rce': ['command output received', 'reverse shell established', 'file created'],
            'reversing': ['main function identified', 'flag logic reversed', 'input validation understood'],
            'crypto': ['cipher identified', 'key recovered', 'plaintext decrypted'],
            'pwn': ['segmentation fault controlled', 'arbitrary write achieved', 'shellcode executed'],
            'forensics': ['hidden files extracted', 'memory dumps analyzed', 'network traffic reconstructed']
        }
        return indicators.get(technique, ['vulnerability successfully exploited'])