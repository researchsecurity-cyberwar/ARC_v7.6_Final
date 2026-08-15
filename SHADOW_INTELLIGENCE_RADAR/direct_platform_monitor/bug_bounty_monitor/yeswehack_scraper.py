import requests
from bs4 import BeautifulSoup
import re
import time
from SOVEREIGN_SESSION_MANAGER.cookie_utils import set_cookie_string, set_xsrf_token

class YesWeHackScraper:
    """
    Scrap YWH dengan session cookie manual.
    Hanya bisa mengakses program yang tersedia di dashboard.
    
    REALITAS TEKNIS:
    - YesWeHack tidak memiliki API publik
    - Session cookie manual diperlukan untuk akses program
    - Semua data scope dan peraturan diambil dari halaman HTML
    """
    
    def __init__(self, session_cookie, xsrf_token=None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; ARC-Scanner/1.0)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })
        set_cookie_string(self.session, session_cookie, default='session')
        set_xsrf_token(self.session, xsrf_token, platform='yeswehack')
        self.base_url = "https://yeswehack.com"
    
    def get_all_programs(self):
        """Dapatkan program yang tersedia di dashboard."""
        try:
            response = self.session.get(f"{self.base_url}/dashboard", timeout=10)
            
            if response.status_code == 200 and 'Login' not in response.text:
                soup = BeautifulSoup(response.content, 'html.parser')
                programs = []
                
                program_links = soup.find_all('a', href=re.compile(r'^/programs/'))
                
                for link in program_links[:15]:
                    program_id = link['href'].split('/')[-1]
                    program_name = link.get_text(strip=True) or program_id
                    
                    programs.append({
                        'id': program_id,
                        'name': program_name,
                        'url': f"{self.base_url}{link['href']}",
                        'status': 'accessible'
                    })
                
                return programs
            else:
                return []
                
        except Exception as e:
            print(f"⚠️ YesWeHack dashboard access failed: {e}")
            return []
    
    def get_program_details(self, program_id):
        """Dapatkan detail program lengkap termasuk scope dan peraturan."""
        try:
            url = f"{self.base_url}/programs/{program_id}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                scopes = []
                out_of_scope = []
                rules = {}
                
                # Ekstrak scope dari konten
                content_text = soup.get_text()
                scopes = self._parse_scope_from_text(content_text, eligible=True)
                out_of_scope = self._parse_scope_from_text(content_text, eligible=False)
                
                # Ekstrak peraturan
                rules = self._extract_yeswehack_rules(soup, content_text)
                
                return {
                    'id': program_id,
                    'scope': scopes,
                    'out_of_scope': out_of_scope,
                    'rules': rules,
                    'status': 'accessible'
                }
        except Exception as e:
            print(f"⚠️ Program details fetch failed: {e}")
        
        return {'id': program_id, 'scope': [], 'out_of_scope': [], 'rules': {}, 'status': 'error'}
    
    def _parse_scope_from_text(self, text, eligible=True):
        """Parse scope dari teks."""
        scopes = []
        urls = re.findall(r'https?://[^\s<>"\']+', text)
        domains = re.findall(r'[a-zA-Z0-9.-]+\.(com|net|org|io|fr)', text)
        
        for url in urls[:10]:
            scopes.append({
                'asset_identifier': url,
                'asset_type': 'url',
                'instruction': f"Test {url}",
                'eligible_for_bounty': eligible,
                'max_severity': 'critical'
            })
        
        for domain in domains[:10]:
            scopes.append({
                'asset_identifier': f"*.{domain}",
                'asset_type': 'wildcard',
                'instruction': f"Test all subdomains of {domain}",
                'eligible_for_bounty': eligible,
                'max_severity': 'critical'
            })
        
        return scopes
    
    def _extract_yeswehack_rules(self, soup, content_text):
        """Ekstrak peraturan dari halaman YesWeHack."""
        rules = {}
        
        # Vulnerability types yang diterima
        vuln_types = re.findall(r'(xss|sqli|ssrf|rce|idor|csrf|lfi|rfi)', content_text, re.IGNORECASE)
        rules['accepted_vulnerability_types'] = list(set(v.lower() for v in vuln_types))
        
        # Bounty structure
        bounty_matches = re.findall(r'\$(\d+(?:,\d+)*)', content_text)
        if bounty_matches:
            rules['bounty_structure'] = {
                'max_bounty': max(int(b.replace(',', '')) for b in bounty_matches)
            }
        
        # Severity guidelines
        if 'critical' in content_text.lower():
            rules['severity_guidelines'] = {'critical': 'Critical vulnerabilities with significant impact'}
        elif 'high' in content_text.lower():
            rules['severity_guidelines'] = {'high': 'High impact vulnerabilities'}
        
        return rules
    
    def validate_session(self):
        """Validasi session cookie."""
        try:
            response = self.session.get(f"{self.base_url}/dashboard", timeout=10)
            return response.status_code == 200 and 'Login' not in response.text
        except:
            return False