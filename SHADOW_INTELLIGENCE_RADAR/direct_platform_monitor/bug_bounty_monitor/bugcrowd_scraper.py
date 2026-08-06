import requests
from bs4 import BeautifulSoup
import re
import json
import time

class BugCrowdScraper:
    """
    Scrap BC dengan session cookie manual.
    Hanya bisa mengakses program yang tersedia di dashboard.
    TIDAK BISA mengakses semua program secara otomatis.
    
    REALITAS TEKNIS:
    - BugCrowd menggunakan OAuth 2.0 + Okta yang tidak bisa diautomasi
    - Session cookie manual hanya berlaku untuk program yang sudah diakses
    - Semua data scope dan peraturan diambil dari halaman HTML
    """
    
    def __init__(self, session_cookie):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; ARC-Scanner/1.0)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })
        # Set session cookie manual
        self.session.cookies.set('_bugcrowd_session', session_cookie)
        self.base_url = "https://bugcrowd.com"
    
    def get_all_programs(self):
        """
        Dapatkan program yang TERSEDIA di dashboard.
        Hanya mengembalikan program yang benar-benar bisa diakses.
        """
        try:
            response = self.session.get(f"{self.base_url}/dashboard", timeout=10)
            
            if response.status_code == 200 and 'Sign in' not in response.text:
                soup = BeautifulSoup(response.content, 'html.parser')
                programs = []
                
                program_links = soup.find_all('a', href=re.compile(r'^/programs/[^/]+$'))
                
                for link in program_links[:20]:
                    program_slug = link['href'].replace('/programs/', '')
                    program_name = link.get_text(strip=True) or program_slug
                    
                    programs.append({
                        'slug': program_slug,
                        'name': program_name,
                        'url': f"{self.base_url}/programs/{program_slug}",
                        'status': 'accessible'
                    })
                
                return programs
            else:
                return self._get_public_programs_only()
                
        except Exception as e:
            print(f"⚠️ BugCrowd dashboard access failed: {e}")
            return self._get_public_programs_only()
    
    def _get_public_programs_only(self):
        """Fallback: hanya dapatkan informasi publik dasar."""
        try:
            response = self.session.get(f"{self.base_url}/programs", timeout=10)
            if response.status_code == 200:
                programs = []
                program_slugs = re.findall(r'/programs/([a-zA-Z0-9-]+)', response.text)
                
                for slug in set(program_slugs[:10]):
                    programs.append({
                        'slug': slug,
                        'name': slug,
                        'url': f"{self.base_url}/programs/{slug}",
                        'status': 'public'
                    })
                
                return programs
        except Exception as e:
            print(f"⚠️ Public program scraping failed: {e}")
        
        return []
    
    def get_program_details(self, program_slug):
        """
        Dapatkan detail program lengkap termasuk scope, peraturan, dan persyaratan.
        """
        try:
            url = f"{self.base_url}/programs/{program_slug}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                scopes = []
                out_of_scope = []
                rules = {}
                
                # Ekstrak scope dari target list
                scope_sections = soup.find_all(attrs={'data-test-id': 'target-list'})
                for section in scope_sections:
                    targets = section.find_all(attrs={'data-test-id': 'target-row'})
                    for target in targets:
                        url_elem = target.find(attrs={'data-test-id': 'target-url'})
                        type_elem = target.find(attrs={'data-test-id': 'target-type'})
                        bounty_elem = target.find(attrs={'data-test-id': 'target-bounty'})
                        
                        if url_elem:
                            scope_entry = {
                                'asset_identifier': url_elem.get_text(strip=True),
                                'asset_type': type_elem.get_text(strip=True) if type_elem else 'unknown',
                                'instruction': f"Test {url_elem.get_text(strip=True)}",
                                'eligible_for_bounty': bool(bounty_elem),
                                'max_severity': 'critical'
                            }
                            
                            if bounty_elem:
                                scopes.append(scope_entry)
                            else:
                                out_of_scope.append(scope_entry)
                
                # Ekstrak peraturan dari halaman
                rules = self._extract_bugcrowd_rules(soup)
                
                return {
                    'slug': program_slug,
                    'scope': scopes,
                    'out_of_scope': out_of_scope,
                    'rules': rules,
                    'status': 'accessible' if 'Sign in' not in response.text else 'public_only'
                }
        except Exception as e:
            print(f"⚠️ Program details fetch failed: {e}")
        
        return {'slug': program_slug, 'scope': [], 'out_of_scope': [], 'rules': {}, 'status': 'error'}
    
    def _extract_bugcrowd_rules(self, soup):
        """Ekstrak peraturan dari halaman BugCrowd."""
        rules = {}
        
        # Vulnerability types yang diterima
        vuln_classes = soup.find_all(attrs={'data-test-id': 'vulnerability-class'})
        rules['accepted_vulnerability_types'] = [vc.get_text(strip=True).lower() for vc in vuln_classes]
        
        # Severity guidelines dari bounty table
        bounty_table = soup.find(attrs={'data-test-id': 'bounty-table'})
        if bounty_table:
            severity_guidelines = {}
            rows = bounty_table.find_all('tr')[1:]
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    severity = cells[0].get_text(strip=True).lower()
                    reward = cells[1].get_text(strip=True)
                    severity_guidelines[severity] = reward
            rules['severity_guidelines'] = severity_guidelines
        
        # Out-of-scope dari bagian khusus
        oos_section = soup.find(attrs={'data-test-id': 'out-of-scope'})
        if oos_section:
            oos_items = oos_section.find_all('li')
            rules['out_of_scope_guidelines'] = [item.get_text(strip=True) for item in oos_items]
        
        return rules
    
    def validate_session(self):
        """Validasi session cookie."""
        try:
            response = self.session.get(f"{self.base_url}/dashboard", timeout=10)
            return response.status_code == 200 and 'Sign in' not in response.text
        except:
            return False