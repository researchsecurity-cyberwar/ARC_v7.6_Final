import requests
from bs4 import BeautifulSoup
import json
import re
import time

class IntigritiScraper:
    """
    Scrap Intigriti langsung dengan Personal Access Token.
    Menggunakan API resmi Intigriti untuk mengakses program yang tersedia.
    
    REALITAS TEKNIS:
    - Intigriti API hanya mengembalikan program yang tersedia untuk peneliti
    - Semua data scope dan peraturan diambil dari API resmi
    - Format data mengikuti dokumentasi API Intigriti
    """
    
    def __init__(self, personal_access_token):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; ARC-Scanner/1.0)',
            'Accept': 'application/json',
            'X-API-KEY': personal_access_token
        })
        self.base_url = "https://api.intigriti.com/external/researcher/v1"
    
    def get_all_programs(self, include_inactive=False):
        """
        Dapatkan daftar program yang TERSEDIA untuk peneliti ini.
        """
        try:
            programs = []
            page = 0
            
            while True:
                url = f"{self.base_url}/companies"
                params = {
                    'size': 100,
                    'page': page
                }
                
                response = self.session.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    content = data.get('content', [])
                    
                    if not content:
                        break
                    
                    for company in content:
                        program_info = {
                            'handle': company.get('handle'),
                            'name': company.get('name', company.get('handle')),
                            'state': 'open' if company.get('isOpen', False) else 'closed',
                            'url': f"https://www.intigriti.com/dashboard/companies/{company.get('handle')}",
                            'offers_bounties': company.get('hasBounty', False),
                            'is_public': company.get('isPublic', False)
                        }
                        
                        if include_inactive or program_info['state'] == 'open':
                            programs.append(program_info)
                    
                    if page >= data.get('totalPages', 1) - 1:
                        break
                    page += 1
                    time.sleep(1)
                
                else:
                    break
            
            return programs
            
        except Exception as e:
            print(f"⚠️ Intigriti API fetch failed: {e}")
            return []
    
    def get_program_details(self, company_handle):
        """
        Dapatkan detail program lengkap termasuk scope, peraturan, dan persyaratan.
        """
        try:
            # Dapatkan domains dari API
            url = f"{self.base_url}/companies/{company_handle}/domains"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                scopes = []
                out_of_scope = []
                
                for domain in data.get('domains', []):
                    scope_entry = {
                        'asset_identifier': domain.get('domain', ''),
                        'asset_type': 'url',
                        'instruction': domain.get('description', f"Test {domain.get('domain', '')}"),
                        'eligible_for_bounty': domain.get('eligibleForBounty', False),
                        'max_severity': domain.get('maxSeverity', 'CRITICAL').lower(),
                        'created_at': domain.get('createdAt'),
                        'updated_at': domain.get('updatedAt')
                    }
                    
                    if domain.get('eligibleForBounty', False):
                        scopes.append(scope_entry)
                    else:
                        out_of_scope.append(scope_entry)
                
                # Dapatkan peraturan tambahan
                rules = self._get_intigriti_rules(company_handle)
                
                return {
                    'handle': company_handle,
                    'scope': scopes,
                    'out_of_scope': out_of_scope,
                    'rules': rules,
                    'status': 'accessible'
                }
        except Exception as e:
            print(f"⚠️ Intigriti program details failed: {e}")
        
        return {'handle': company_handle, 'scope': [], 'out_of_scope': [], 'rules': {}, 'status': 'error'}
    
    def _get_intigriti_rules(self, company_handle):
        """
        Dapatkan peraturan dari halaman company Intigriti.
        """
        try:
            url = f"https://www.intigriti.com/companies/{company_handle}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                content = response.text
                
                # Vulnerability types yang diterima
                vuln_types = re.findall(r'"vulnerabilityType":"([^"]+)"', content)
                
                # Bounty structure
                bounty_info = {}
                bounty_matches = re.findall(r'"bounty":(\d+\.?\d*)', content)
                if bounty_matches:
                    bounty_info['max_bounty'] = max(float(b) for b in bounty_matches)
                
                # Severity guidelines berdasarkan nilai bounty
                severity_guidelines = {}
                if bounty_info.get('max_bounty', 0) > 10000:
                    severity_guidelines['critical'] = f"Bounty up to ${bounty_info['max_bounty']:,.0f}"
                elif bounty_info.get('max_bounty', 0) > 1000:
                    severity_guidelines['high'] = f"Bounty up to ${bounty_info['max_bounty']:,.0f}"
                
                return {
                    'accepted_vulnerability_types': list(set(v.lower() for v in vuln_types)),
                    'severity_guidelines': severity_guidelines,
                    'bounty_structure': bounty_info,
                    'last_updated': time.time()
                }
        except Exception as e:
            print(f"⚠️ Intigriti rules extraction failed: {e}")
        
        return {}
    
    def get_program_scope(self, company_handle):
        """Dapatkan scope untuk program tertentu."""
        try:
            url = f"{self.base_url}/companies/{company_handle}/domains"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                scopes = []
                for domain in data.get('domains', []):
                    scopes.append({
                        'instruction': domain.get('domain', ''),
                        'asset_identifier': domain.get('domain', ''),
                        'asset_type': 'url',
                        'eligible_for_bounty': domain.get('eligibleForBounty', False),
                        'max_severity': domain.get('maxSeverity', 'CRITICAL').lower()
                    })
                return scopes
        except Exception as e:
            print(f"⚠️ Scope fetch failed for {company_handle}: {e}")
        
        return []
    
    def check_new_reports(self):
        """Cek laporan baru via API."""
        try:
            url = f"{self.base_url}/reports"
            params = {'size': 20, 'page': 0}
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                reports = []
                for report in data.get('content', []):
                    reports.append({
                        'id': report.get('id'),
                        'title': report.get('title', f"Report #{report.get('id')}"),
                        'url': f"https://www.intigriti.com/dashboard/reports/{report.get('id')}",
                        'status': report.get('status', 'NEW')
                    })
                return reports
        except Exception as e:
            print(f"⚠️ Report check failed: {e}")
        
        return []
    
    def validate_session(self):
        """Validasi Personal Access Token."""
        try:
            response = self.session.get(f"{self.base_url}/profile", timeout=10)
            return response.status_code == 200
        except:
            return False