import requests
from bs4 import BeautifulSoup
import json
import re
import time

class HackerOneScraper:
    """
    Scrap H1 langsung dengan API token.
    Menggunakan Personal Access Token untuk mengakses program public.
    TIDAK BISA mengakses program private tanpa invite eksplisit.
    
    REALITAS TEKNIS:
    - HackerOne API hanya mengembalikan program yang tersedia untuk peneliti
    - Program private hanya terlihat jika sudah di-invite
    - Semua data scope dan peraturan diambil dari API resmi
    """
    
    def __init__(self, api_token, api_token_id=None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; ARC-Scanner/1.0)',
            'Accept': 'application/json',
        })
        # HackerOne memakai HTTP Basic Auth: identifier=username, value=password.
        # API token H1 terdiri dari 2 bagian: identifier (username) + value (secret).
        if api_token_id:
            self.session.auth = (api_token_id, api_token)
        elif ':' in api_token:
            # Backward-compat: bila token digabung "identifier:secret" dalam satu string
            self.session.auth = (api_token.split(':', 1)[0], api_token.split(':', 1)[1])
        else:
            # Backward-compat: nilai tunggal dipakai untuk username & password
            self.session.auth = (api_token, api_token)
        self.base_url = "https://api.hackerone.com/v1"
    
    def get_all_programs(self, include_inactive=False):
        """
        Dapatkan daftar program yang TERSEDIA untuk peneliti ini.
        Hanya mengembalikan program yang benar-benar bisa diakses.
        """
        try:
            programs = []
            page = 1
            
            while True:
                url = f"{self.base_url}/hackers/programs"
                params = {
                    'page[size]': 100,
                    'page[number]': page
                }
                
                response = self.session.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    program_list = data.get('data', [])
                    
                    if not program_list:
                        break
                    
                    for program in program_list:
                        attrs = program.get('attributes', {})
                        program_info = {
                            'handle': program.get('id'),
                            'name': attrs.get('name', program.get('id')),
                            'state': attrs.get('state', 'open'),
                            'url': f"https://hackerone.com/{program.get('id')}",
                            'offers_bounties': attrs.get('offers_bounties', False),
                            'is_public': attrs.get('submission_state') == 'open'
                        }
                        
                        if include_inactive or program_info['state'] == 'open':
                            programs.append(program_info)
                    
                    links = data.get('links', {})
                    if 'next' not in links:
                        break
                    page += 1
                    time.sleep(1)
                
                else:
                    print(f"⚠️ HackerOne API: HTTP {response.status_code} - {response.text[:200]}")
                    return self._get_public_programs_only()
            
            print(f"✅ HackerOne: Found {len(programs)} programs")
            return programs
            
        except Exception as e:
            print(f"⚠️ HackerOne API fetch failed: {e}")
            return self._get_public_programs_only()

    def _get_public_programs_only(self):
        """
        Fallback: dapatkan program publik dari HackerOne public hacktivity API.
        Endpoint ini tidak memerlukan authentication token -- data hacktivity
        tersedia secara public melalui https://api.hackerone.com/v1/hackers/hacktivity
        """
        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (compatible; ARC-Scanner/1.0)',
                'Accept': 'application/json'
            })

            programs = []
            seen_handles = set()
            page = 1

            while True:
                url = "https://api.hackerone.com/v1/hackers/hacktivity"
                params = {
                    'page[number]': page,
                    'page[size]': 50
                }
                response = session.get(url, params=params, timeout=15)

                if response.status_code == 200:
                    data = response.json()
                    items = data.get('data', [])

                    if not items:
                        break

                    for item in items:
                        rels = item.get('relationships', {})
                        program_rel = rels.get('program', {}).get('data', {})
                        if isinstance(program_rel, dict):
                            attrs = program_rel.get('attributes', {})
                            handle = attrs.get('handle')
                            if handle and handle not in seen_handles:
                                seen_handles.add(handle)
                                program_info = {
                                    'handle': handle,
                                    'name': attrs.get('name', handle),
                                    'state': 'open',
                                    'url': f"https://hackerone.com/{handle}",
                                    'offers_bounties': True,
                                    'is_public': True
                                }
                                programs.append(program_info)

                    # Check pagination
                    links = data.get('links', {})
                    if 'next' not in links:
                        break
                    page += 1
                    time.sleep(1)
                else:
                    break

            if programs:
                print(f"✅ HackerOne (public hacktivity): Found {len(programs)} programs")

            return programs
        except Exception as e:
            print(f"⚠️ Public program scraping failed: {e}")

        return []

    def get_program_details(self, program_handle):
        """
        Dapatkan detail program lengkap termasuk scope, peraturan, dan persyaratan.
        """
        try:
            # Dapatkan structured scopes dari API
            url = f"{self.base_url}/hackers/programs/{program_handle}/structured_scopes"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                scopes = []
                out_of_scope = []
                
                for scope_item in data.get('data', []):
                    attrs = scope_item.get('attributes', {})
                    scope_entry = {
                        'asset_identifier': attrs.get('asset_identifier', ''),
                        'asset_type': attrs.get('asset_type', ''),
                        'instruction': attrs.get('instruction', ''),
                        'eligible_for_bounty': attrs.get('eligible_for_bounty', False),
                        'max_severity': attrs.get('max_severity', 'critical'),
                        'created_at': attrs.get('created_at'),
                        'updated_at': attrs.get('updated_at')
                    }
                    
                    if attrs.get('eligible_for_bounty', False):
                        scopes.append(scope_entry)
                    else:
                        out_of_scope.append(scope_entry)
                
                # Dapatkan peraturan tambahan dari halaman program
                rules = self._get_program_rules(program_handle)
                
                return {
                    'handle': program_handle,
                    'scope': scopes,
                    'out_of_scope': out_of_scope,
                    'rules': rules,
                    'status': 'accessible'
                }
        except Exception as e:
            print(f"⚠️ Program details fetch failed: {e}")
        
        return {'handle': program_handle, 'scope': [], 'out_of_scope': [], 'rules': {}, 'status': 'error'}
    
    def _get_program_rules(self, program_handle):
        """
        Dapatkan peraturan program dari halaman HTML.
        """
        try:
            url = f"https://hackerone.com/{program_handle}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Ekstrak vulnerability types yang diterima
                vuln_types = []
                content_text = soup.get_text()
                vuln_matches = re.findall(r'(xss|sqli|ssrf|rce|idor|csrf|lfi|rfi|auth.*bypass)', content_text, re.IGNORECASE)
                vuln_types.extend([v.lower() for v in vuln_matches])
                
                # Ekstrak severity guidelines
                severity_guidelines = {}
                if 'critical' in content_text.lower():
                    severity_guidelines['critical'] = 'Critical vulnerabilities that can lead to complete system compromise'
                if 'high' in content_text.lower():
                    severity_guidelines['high'] = 'High impact vulnerabilities with significant business impact'
                
                # Ekstrak bounty structure jika tersedia
                bounty_structure = {}
                bounty_matches = re.findall(r'\$(\d+(?:,\d+)*)', content_text)
                if bounty_matches:
                    bounty_structure['max_bounty'] = max(int(b.replace(',', '')) for b in bounty_matches)
                
                return {
                    'accepted_vulnerability_types': list(set(vuln_types)),
                    'severity_guidelines': severity_guidelines,
                    'bounty_structure': bounty_structure,
                    'last_updated': time.time()
                }
        except Exception as e:
            print(f"⚠️ Rules extraction failed: {e}")
        
        return {}
    
    def get_program_scope(self, program_handle):
        """Dapatkan scope untuk program tertentu via API."""
        try:
            url = f"{self.base_url}/hackers/programs/{program_handle}/structured_scopes"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                scopes = []
                for scope_item in data.get('data', []):
                    attrs = scope_item.get('attributes', {})
                    scopes.append({
                        'instruction': attrs.get('instruction', ''),
                        'asset_identifier': attrs.get('asset_identifier', ''),
                        'asset_type': attrs.get('asset_type', ''),
                        'eligible_for_bounty': attrs.get('eligible_for_bounty', False),
                        'max_severity': attrs.get('max_severity', 'critical')
                    })
                return scopes
        except Exception as e:
            print(f"⚠️ Scope fetch failed for {program_handle}: {e}")
        
        return []
    
    def check_new_reports(self):
        """Cek laporan baru via API."""
        try:
            url = f"{self.base_url}/hackers/reports"
            params = {'page[size]': 20}
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                reports = []
                for report in data.get('data', []):
                    attrs = report.get('attributes', {})
                    reports.append({
                        'id': report.get('id'),
                        'title': attrs.get('title', f"Report #{report.get('id')}"),
                        'url': f"https://hackerone.com/reports/{report.get('id')}",
                        'status': attrs.get('state', 'new')
                    })
                return reports
        except Exception as e:
            print(f"⚠️ Report check failed: {e}")
        
        return []
    
    def validate_session(self):
        """Validasi API token."""
        try:
            response = self.session.get(f"{self.base_url}/me", timeout=10)
            return response.status_code == 200
        except:
            return False