import requests
from urllib.parse import quote

class GitHubSecretHunter:
    """
    'filetype:env site:*.go.id' + hardcoded keys.
    Mencari secrets dan hardcoded keys di GitHub menggunakan dorks.
    """
    
    def __init__(self):
        self.github_search_url = "https://api.github.com/search/code"
        # Note: Untuk OSINT-only, kita gunakan pencarian publik tanpa API key
        # Ini akan lebih lambat tapi tidak memerlukan autentikasi
    
    def search_github_dorks(self, dork_query, max_results=10):
        """
        Cari menggunakan GitHub dorks (tanpa API key - rate limited).
        """
        results = []
        
        # Encode query untuk URL
        encoded_query = quote(dork_query)
        search_url = f"https://github.com/search?q={encoded_query}&type=code"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; ARC-Scanner/1.0)'
            }
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Parse hasil dari HTML (karena API tanpa key sangat terbatas)
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                results.extend(self._extract_code_results(soup))
        except Exception as e:
            print(f"⚠️ GitHub search failed: {e}")
        
        return results[:max_results]
    
    def _extract_code_results(self, soup):
        """Ekstrak hasil pencarian kode dari HTML GitHub."""
        results = []
        code_links = soup.find_all('a', href=re.compile(r'/.*blob/.*'))
        
        for link in code_links[:10]:  # Batasi untuk OSINT
            repo_name = link.get_text(strip=True)
            file_url = f"https://github.com{link.get('href')}"
            
            results.append({
                'repository': repo_name,
                'file_url': file_url,
                'search_type': 'github_dork'
            })
        
        return results
    
    def generate_targeted_dorks(self, target_domain):
        """Generate dorks spesifik untuk target domain."""
        dorks = [
            f'filename:.env "{target_domain}"',
            f'extension:yaml "{target_domain}" password',
            f'extension:json "{target_domain}" api_key',
            f'filename:config "{target_domain}" secret',
            f'"{target_domain}" password site:github.com'
        ]
        return dorks