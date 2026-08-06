import requests
from bs4 import BeautifulSoup
import re

class PostMortemAnalyzer:
    """
    Analyze official write-ups when failed.
    Menganalisis write-up resmi ketika ARC gagal menyelesaikan challenge.
    """
    
    def __init__(self, analysis_dir="~/.arc/ctf_analysis"):
        self.analysis_dir = os.path.expanduser(analysis_dir)
        os.makedirs(self.analysis_dir, exist_ok=True)
    
    def analyze_failure_and_find_writeup(self, challenge_data: dict):
        """
        Analisis kegagalan dan cari write-up terkait.
        """
        results = {
            'challenge_data': challenge_data,
            'failure_root_cause': None,
            'found_writeups': [],
            'learning_opportunities': [],
            'playbook_update_needed': False
        }
        
        try:
            # Identifikasi penyebab kegagalan
            root_cause = self._identify_failure_root_cause(challenge_data)
            results['failure_root_cause'] = root_cause
            
            # Cari write-up terkait
            writeups = self._search_relevant_writeups(challenge_data, root_cause)
            results['found_writeups'] = writeups
            
            # Identifikasi peluang belajar
            learning_ops = self._extract_learning_opportunities(writeups, root_cause)
            results['learning_opportunities'] = learning_ops
            
            # Tentukan apakah perlu update playbook
            results['playbook_update_needed'] = len(learning_ops) > 0
        
        except Exception as e:
            results['error'] = f'Post-mortem analysis failed: {str(e)}'
        
        return results
    
    def _identify_failure_root_cause(self, challenge_data: dict) -> str:
        """Identifikasi akar penyebab kegagalan."""
        # Ini akan diimplementasi berdasarkan log eksekusi
        category = challenge_data.get('category', 'unknown')
        
        if category == 'web':
            return 'insufficient_web_enumeration'
        elif category == 'crypto':
            return 'unknown_cipher_algorithm'
        elif category == 'reversing':
            return 'anti_debugging_techniques'
        elif category == 'pwn':
            return 'inadequate_exploit_development'
        else:
            return 'general_insufficient_knowledge'
    
    def _search_relevant_writeups(self, challenge_data: dict, root_cause: str) -> list:
        """Cari write-up yang relevan."""
        writeups = []
        category = challenge_data.get('category', 'misc')
        platform = challenge_data.get('platform', 'unknown')
        
        # Cari di GitHub
        github_writeups = self._search_github_for_writeups(category, root_cause)
        writeups.extend(github_writeups)
        
        # Cari di CTFtime
        ctftime_writeups = self._search_ctftime_for_writeups(category, platform)
        writeups.extend(ctftime_writeups)
        
        return writeups[:5]  # Batasi 5 write-up
    
    def _search_github_for_writeups(self, category: str, root_cause: str) -> list:
        """Cari write-up di GitHub."""
        try:
            query = f"{category} CTF writeup {root_cause.replace('_', ' ')} language:markdown"
            params = {'q': query, 'sort': 'updated', 'order': 'desc', 'per_page': 5}
            
            response = requests.get(
                'https://api.github.com/search/repositories',
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                writeups = []
                for item in data.get('items', []):
                    writeups.append({
                        'title': item.get('name', ''),
                        'url': item.get('html_url', ''),
                        'source': 'github',
                        'relevance_score': 0.8
                    })
                return writeups
        except:
            pass
        return []
    
    def _search_ctftime_for_writeups(self, category: str, platform: str) -> list:
        """Cari write-up di CTFtime."""
        try:
            response = requests.get('https://ctftime.org/writeups', timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                writeups = []
                
                items = soup.select('.writeup-list-item')[:5]
                for item in items:
                    title_elem = item.select_one('a')
                    if title_elem and category in title_elem.text.lower():
                        writeups.append({
                            'title': title_elem.text.strip(),
                            'url': f"https://ctftime.org{title_elem['href']}",
                            'source': 'ctftime',
                            'relevance_score': 0.7
                        })
                return writeups
        except:
            pass
        return []
    
    def _extract_learning_opportunities(self, writeups: list, root_cause: str) -> list:
        """Ekstrak peluang belajar dari write-up."""
        opportunities = []
        
        for writeup in writeups:
            opportunities.append({
                'writeup_title': writeup['title'],
                'writeup_url': writeup['url'],
                'root_cause_addressed': root_cause,
                'technique_learned': f"Technique from {writeup['source']} writeup",
                'confidence_improvement': 0.2
            })
        
        return opportunities