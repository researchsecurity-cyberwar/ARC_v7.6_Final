import requests
from bs4 import BeautifulSoup
import re
import time
from SOVEREIGN_SESSION_MANAGER.cookie_utils import set_cookie_string, set_xsrf_token

class ImmunefiScraper:
    """
    Scrap Immunefi dengan session cookie manual.
    Hanya bisa mengakses informasi dasar dari halaman bounty.
    
    REALITAS TEKNIS:
    - Immunefi tidak memiliki API publik
    - Session cookie manual diperlukan untuk akses form
    - Fokus pada ekstraksi scope DeFi dan persyaratan ekonomi
    """
    
    def __init__(self, session_cookie, xsrf_token=None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; ARC-Scanner/1.0)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })
        # Set cookies: raw cookie-string 'name=value; name2=value2' (session+xsrf),
        # atau nilai tunggal -> dipasang sebagai cookie 'sessionid' (Firebase).
        set_cookie_string(self.session, session_cookie, default='sessionid')
        set_xsrf_token(self.session, xsrf_token, platform='immunefi')
        self.base_url = "https://immunefi.com"
    
    def get_all_programs(self):
        """Dapatkan daftar form bounty yang tersedia."""
        try:
            response = self.session.get(f"{self.base_url}/bounties", timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                programs = []
                
                bounty_links = soup.find_all('a', href=re.compile(r'/bounty/'))
                
                for link in bounty_links[:10]:
                    program_name = link['href'].split('/')[-1]
                    programs.append({
                        'name': program_name,
                        'url': f"{self.base_url}{link['href']}",
                        'form_available': True
                    })
                
                return programs
            else:
                return []
                
        except Exception as e:
            print(f"⚠️ Immunefi bounty page access failed: {e}")
            return []
    
    def get_program_details(self, program_name):
        """Dapatkan detail program lengkap termasuk scope DeFi dan persyaratan ekonomi."""
        try:
            url = f"{self.base_url}/bounty/{program_name}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                scopes = []
                out_of_scope = []
                rules = {}
                
                # Ekstrak scope DeFi spesifik
                scopes = self._parse_immunefi_scope_from_text(content, eligible=True)
                out_of_scope = self._parse_immunefi_scope_from_text(content, eligible=False)
                
                # Ekstrak peraturan khusus Immunefi
                rules = self._extract_immunefi_rules(content)
                
                return {
                    'name': program_name,
                    'scope': scopes,
                    'out_of_scope': out_of_scope,
                    'rules': rules,
                    'status': 'accessible'
                }
        except Exception as e:
            print(f"⚠️ Program details fetch failed: {e}")
        
        return {'name': program_name, 'scope': [], 'out_of_scope': [], 'rules': {}, 'status': 'error'}
    
    def _parse_immunefi_scope_from_text(self, content, eligible=True):
        """Parse scope Immunefi dari teks."""
        scopes = []
        
        # Contract addresses
        contracts = re.findall(r'0x[a-fA-F0-9]{40}', content)
        for contract in contracts[:5]:
            scopes.append({
                'asset_identifier': contract,
                'asset_type': 'contract',
                'instruction': f"Test smart contract {contract}",
                'eligible_for_bounty': eligible,
                'max_severity': 'critical'
            })
        
        # URLs/domains
        urls = re.findall(r'https?://[^\s<>"\']+\.com|[^\s<>"\']+\.finance', content)
        for url in urls[:5]:
            scopes.append({
                'asset_identifier': url,
                'asset_type': 'url',
                'instruction': f"Test frontend {url}",
                'eligible_for_bounty': eligible,
                'max_severity': 'high'
            })
        
        return scopes
    
    def _extract_immunefi_rules(self, content):
        """Ekstrak peraturan khusus Immunefi."""
        rules = {}
        
        # Vulnerability types DeFi spesifik
        vuln_types = []
        if 'reentrancy' in content.lower():
            vuln_types.append('reentrancy')
        if 'flash loan' in content.lower():
            vuln_types.append('flash_loan')
        if 'oracle' in content.lower():
            vuln_types.append('oracle_manipulation')
        if 'governance' in content.lower():
            vuln_types.append('governance_attack')
        if 'economic' in content.lower():
            vuln_types.append('economic_exploit')
        
        rules['accepted_vulnerability_types'] = vuln_types
        
        # Economic requirements
        economic_rules = {}
        profit_matches = re.findall(r'minimum profit.*?\$(\d+(?:,\d+)*)', content, re.IGNORECASE)
        if profit_matches:
            economic_rules['minimum_profit'] = int(profit_matches[0].replace(',', ''))
        
        rules['economic_requirements'] = economic_rules
        
        # Severity guidelines berdasarkan dampak ekonomi
        severity_guidelines = {}
        if economic_rules.get('minimum_profit', 0) > 100000:
            severity_guidelines['critical'] = f"Economic exploit with profit > ${economic_rules['minimum_profit']:,.0f}"
        elif economic_rules.get('minimum_profit', 0) > 10000:
            severity_guidelines['high'] = f"Economic exploit with profit > ${economic_rules['minimum_profit']:,.0f}"
        
        rules['severity_guidelines'] = severity_guidelines
        
        return rules
    
    def validate_session(self):
        """Validasi session cookie."""
        try:
            response = self.session.get(f"{self.base_url}/bounties", timeout=10)
            return response.status_code == 200
        except:
            return False