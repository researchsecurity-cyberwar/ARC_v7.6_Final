import re

filepath = r'c:\Projects\ARC_v7.6_Final\SHADOW_INTELLIGENCE_RADAR\direct_platform_monitor\bug_bounty_monitor\bugcrowd_scraper.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix BugCrowd get_all_programs with better error handling
old_pattern = r'(    def get_all_programs\(self\):.*?)(?=    def )'
match = re.search(old_pattern, content, re.DOTALL)
if match:
    new_method = '''    def get_all_programs(self):
        """Dapatkan program yang TERSEDIA di dashboard."""
        try:
            # BugCrowd uses _bugcrowd_session cookie
            response = self.session.get(f"{self.base_url}/dashboard", timeout=15)
            
            if response.status_code == 200 and 'Sign in' not in response.text:
                soup = BeautifulSoup(response.content, 'html.parser')
                programs = []
                
                # Try multiple selectors for program links
                program_links = soup.find_all('a', href=re.compile(r'^/programs/[^/]+/?$'))
                
                for link in program_links[:20]:
                    href = link.get('href', '')
                    program_slug = href.strip('/').replace('programs/', '')
                    program_name = link.get_text(strip=True) or program_slug
                    
                    programs.append({
                        'slug': program_slug,
                        'name': program_name,
                        'url': f"{self.base_url}/programs/{program_slug}",
                        'status': 'accessible'
                    })
                
                print(f"✅ BugCrowd: Found {len(programs)} programs")
                return programs
            elif response.status_code == 401 or 'Sign in' in response.text:
                print(f"⚠️ BugCrowd: Session expired or invalid - please update session_cookie")
                return []
            else:
                print(f"⚠️ BugCrowd: HTTP {response.status_code} - {response.text[:200]}")
                return []
                
        except Exception as e:
            print(f"⚠️ BugCrowd dashboard access failed: {e}")
            import traceback
            traceback.print_exc()
            return []'''
    
    content = content[:match.start()] + new_method + content[match.end():]
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ BugCrowd scraper updated")
else:
    print("❌ BugCrowd regex failed")