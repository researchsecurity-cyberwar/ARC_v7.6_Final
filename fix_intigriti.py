import re

filepath = r'c:\Projects\ARC_v7.6_Final\SHADOW_INTELLIGENCE_RADAR\direct_platform_monitor\bug_bounty_monitor\intigriti_scraper.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the get_all_programs method using regex
pattern = r'(    def get_all_programs\(self, include_inactive=False\):.*?)(?=    def )'
match = re.search(pattern, content, re.DOTALL)
if match:
    new_method = '''    def get_all_programs(self, include_inactive=False):
        """Dapatkan daftar program yang TERSEDIA untuk peneliti ini."""
        try:
            programs = []
            page = 0
            
            while True:
                # Intigriti API: /companies returns programs for the researcher
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
                        # Check if researcher has access to this program
                        if not company.get('isOpen', False) and not include_inactive:
                            continue
                            
                        program_info = {
                            'handle': company.get('handle'),
                            'name': company.get('name', company.get('handle')),
                            'state': 'open' if company.get('isOpen', False) else 'closed',
                            'url': f"https://www.intigriti.com/dashboard/companies/{company.get('handle')}",
                            'offers_bounties': company.get('hasBounty', False),
                            'is_public': company.get('isPublic', False)
                        }
                        
                        programs.append(program_info)
                    
                    if page >= data.get('totalPages', 1) - 1:
                        break
                    page += 1
                    time.sleep(1)
                
                elif response.status_code == 401:
                    print(f"⚠️ Intigriti API: Unauthorized (401) - Check Personal Access Token")
                    break
                elif response.status_code == 403:
                    print(f"⚠️ Intigriti API: Forbidden (403) - Token may lack permissions")
                    break
                else:
                    print(f"⚠️ Intigriti API: HTTP {response.status_code} - {response.text[:200]}")
                    break
            
            print(f"✅ Intigriti: Found {len(programs)} programs")
            return programs
            
        except Exception as e:
            print(f"⚠️ Intigriti API fetch failed: {e}")
            import traceback
            traceback.print_exc()
            return []'''
    
    content = content[:match.start()] + new_method + content[match.end():]
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Intigriti scraper updated successfully via regex")
else:
    print("❌ Regex also failed")