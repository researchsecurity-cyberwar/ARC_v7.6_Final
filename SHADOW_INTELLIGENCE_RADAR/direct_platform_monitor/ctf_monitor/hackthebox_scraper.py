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
        """Dapatkan machine aktif yang tersedia."""
        try:
            response = self.session.get(f"{self.base_url}/machines", timeout=10)
            
            if response.status_code == 200 and 'Login' not in response.text:
                soup = BeautifulSoup(response.content, 'html.parser')
                machines = []
                
                # Ekstrak machine dari halaman
                machine_names = re.findall(r'"name":"([^"]+)"', response.text)
                machine_ips = re.findall(r'"ip":"([^"]+)"', response.text)
                
                for i, name in enumerate(machine_names[:10]):
                    machines.append({
                        'name': name,
                        'ip': machine_ips[i] if i < len(machine_ips) else '',
                        'accessible': True
                    })
                
                return machines
            else:
                return []
                
        except Exception as e:
            print(f"⚠️ HTB machine scraping failed: {e}")
            return []
    
    def check_new_challenges(self):
        """Cek challenge baru yang tersedia."""
        try:
            response = self.session.get(f"{self.base_url}/challenges", timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                challenges = []
                
                # Ekstrak challenge dasar
                challenge_names = re.findall(r'"name":"([^"]+)"', response.text)
                challenge_categories = re.findall(r'"category":"([^"]+)"', response.text)
                
                for i, name in enumerate(challenge_names[:5]):
                    challenges.append({
                        'name': name,
                        'category': challenge_categories[i] if i < len(challenge_categories) else 'unknown',
                        'accessible': True
                    })
                
                return challenges
            else:
                return []
                
        except Exception as e:
            print(f"⚠️ HTB challenge scraping failed: {e}")
            return []
    
    def validate_session(self):
        """Validasi session cookie."""
        try:
            response = self.session.get(f"{self.base_url}/machines", timeout=10)
            return response.status_code == 200 and 'Login' not in response.text
        except:
            return False