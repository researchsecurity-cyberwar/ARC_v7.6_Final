import requests
from bs4 import BeautifulSoup
import re
import time

class HackTheBoxScraper:
    """
    Scrap HTB dengan session cookie manual.
    Hanya bisa mengakses machine dan challenge yang tersedia.
    
    REALITAS TEKNIS:
    - HTB tidak memiliki form login yang bisa diautomasi
    - Session cookie manual diperlukan untuk akses premium
    - Tidak ada API publik untuk scraping machine
    """
    
    def __init__(self, session_cookie):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; ARC-Scanner/1.0)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })
        self.session.cookies.set('PHPSESSID', session_cookie)
        self.base_url = "https://www.hackthebox.com"
    
    def get_active_machines(self):
        """Dapatkan machine aktif yang tersedia (parse link HTML server-rendered)."""
        try:
            response = self.session.get(f"{self.base_url}/machines", timeout=10)
            
            if response.status_code == 200 and 'Login' not in response.text:
                machines = []
                # Halaman HTB server-rendered berisi link /machines/<slug>
                machine_links = re.findall(r'href="[^"]*?/machines/([a-zA-Z0-9-]+)"', response.text)
                seen = set()
                for slug in machine_links:
                    if slug in seen or len(slug) < 2:
                        continue
                    seen.add(slug)
                    name = slug.replace('-', ' ').title()
                    machines.append({
                        'name': name,
                        'slug': slug,
                        'ip': '',
                        'accessible': True
                    })
                    if len(machines) >= 10:
                        break
                
                return machines
            else:
                return []
                
        except Exception as e:
            print(f"⚠️ HTB machine scraping failed: {e}")
            return []
    
    def check_new_challenges(self):
        """Cek challenge baru yang tersedia (parse link HTML server-rendered)."""
        try:
            response = self.session.get(f"{self.base_url}/challenges", timeout=10)
            
            if response.status_code == 200:
                challenges = []
                # Halaman HTB server-rendered berisi link /challenges/<slug>
                challenge_links = re.findall(r'href="[^"]*?/challenges/([a-zA-Z0-9-]+)"', response.text)
                seen = set()
                for slug in challenge_links:
                    if slug in seen or len(slug) < 2:
                        continue
                    seen.add(slug)
                    name = slug.replace('-', ' ').title()
                    challenges.append({
                        'name': name,
                        'slug': slug,
                        'category': 'unknown',
                        'accessible': True
                    })
                    if len(challenges) >= 5:
                        break
                
                return challenges
            else:
                return []
                
        except Exception as e:
            print(f"⚠️ HTB challenge scraping failed: {e}")
            return []
    
    def get_all_programs(self) -> dict:
        """Kompatibilitas dengan ARC main loop.
        
        HTB adalah platform CTF, bukan bug bounty, jadi tidak ada 'program'
        seperti di HackerOne/BugCrowd. Sebagai pengganti, kami menggabungkan
        active machines dan challenges yang tersedia sebagai 'programs' dalam
        format dict agar kompatibel dengan arc_main._update_intelligence_feed().
        """
        programs = {}
        # Masukkan machine aktif
        for machine in self.get_active_machines():
            key = machine.get('name', f'machine_{len(programs)}')
            programs[key] = {
                'name': machine.get('name', ''),
                'type': 'machine',
                'ip': machine.get('ip', ''),
                'accessible': machine.get('accessible', False),
                'platform': 'hackthebox',
                'status': 'active'
            }
        # Masukkan challenges
        for challenge in self.check_new_challenges():
            key = f"challenge_{challenge.get('name', len(programs))}"
            programs[key] = {
                'name': challenge.get('name', ''),
                'type': 'challenge',
                'category': challenge.get('category', 'unknown'),
                'accessible': challenge.get('accessible', False),
                'platform': 'hackthebox',
                'status': 'active'
            }
        return programs

    def validate_session(self):
        """Validasi session cookie."""
        try:
            response = self.session.get(f"{self.base_url}/machines", timeout=10)
            return response.status_code == 200 and 'Login' not in response.text
        except:
            return False