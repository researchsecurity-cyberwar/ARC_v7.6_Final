import requests
import json
import os
import time

class GitHubSecurityWatcher:
    """
    Detect new security tools & CVE PoCs in GitHub repos.
    Menggunakan query valid dengan parameter q yang benar.
    """
    
    def __init__(self, data_dir="~/.arc/intel", tor_proxies=None):
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        self.tor_proxies = tor_proxies or {'http': 'socks5h://127.0.0.1:9050',
                                          'https': 'socks5h://127.0.0.1:9050'}
        self.github_api_url = "https://api.github.com/search/repositories"
    
    def monitor_github_security(self):
        """Pantau GitHub untuk repositori keamanan baru."""
        results = {
            'new_security_tools': 0,
            'new_cve_pocs': 0,
            'total_new_repos': 0,
            'monitoring_successful': False
        }
        
        try:
            tools_count = self._search_security_tools()
            results['new_security_tools'] = tools_count
            
            pocs_count = self._search_cve_pocs()
            results['new_cve_pocs'] = pocs_count
            
            results['total_new_repos'] = tools_count + pocs_count
            results['monitoring_successful'] = True
        
        except Exception as e:
            results['error'] = f'GitHub security monitoring failed: {str(e)}'
        
        return results
    
    def _search_security_tools(self):
        """Cari repositori alat keamanan dengan query valid."""
        try:
            # Gunakan tanggal spesifik untuk menghindari error
            queries = [
                'security scanner language:python pushed:>2026-07-15',
                'vulnerability scanner language:go pushed:>2026-07-15'
            ]
            
            all_repos = []
            for query in queries:
                if not query.strip():
                    continue
                
                params = {
                    'q': query,  # Parameter q wajib dan tidak boleh kosong
                    'sort': 'updated',
                    'order': 'desc',
                    'per_page': 10
                }
                
                response = requests.get(
                    self.github_api_url,
                    params=params,
                    proxies=self.tor_proxies,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    all_repos.extend(data.get('items', []))
            
            if all_repos:
                timestamp = int(time.time())
                tools_file = os.path.join(self.data_dir, f"github_tools_{timestamp}.json")
                with open(tools_file, 'w') as f:
                    json.dump({'repositories': all_repos}, f, indent=2)
            
            return len(all_repos)
        
        except Exception:
            return 0
    
    def _search_cve_pocs(self):
        """Cari repositori PoC CVE dengan query valid."""
        try:
            queries = [
                'CVE exploit language:python pushed:>2026-07-15',
                'proof of concept vulnerability language:go pushed:>2026-07-15'
            ]
            
            all_repos = []
            for query in queries:
                if not query.strip():
                    continue
                
                params = {
                    'q': query,
                    'sort': 'updated',
                    'order': 'desc',
                    'per_page': 10
                }
                
                response = requests.get(
                    self.github_api_url,
                    params=params,
                    proxies=self.tor_proxies,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    all_repos.extend(data.get('items', []))
            
            if all_repos:
                timestamp = int(time.time())
                pocs_file = os.path.join(self.data_dir, f"github_pocs_{timestamp}.json")
                with open(pocs_file, 'w') as f:
                    json.dump({'repositories': all_repos}, f, indent=2)
            
            return len(all_repos)
        
        except Exception:
            return 0