import requests
from bs4 import BeautifulSoup
import re
import time

class TryHackMeScraper:
    """
    Scrap THM dengan session cookie manual.
    Hanya bisa mengakses room dan challenge yang tersedia.
    
    REALITAS TEKNIS:
    - THM tidak memiliki form login yang bisa diautomasi  
    - Session cookie manual diperlukan untuk akses room
    - Tidak ada API publik untuk scraping room
    """
    
    def __init__(self, session_cookie):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; ARC-Scanner/1.0)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })
        self.session.cookies.set('connect.sid', session_cookie)
        self.base_url = "https://tryhackme.com"
    
    def get_available_rooms(self):
        """Dapatkan room yang tersedia."""
        try:
            response = self.session.get(f"{self.base_url}/rooms", timeout=10)
            
            if response.status_code == 200 and 'Login' not in response.text:
                soup = BeautifulSoup(response.content, 'html.parser')
                rooms = []
                
                # Ekstrak room dari halaman
                room_codes = re.findall(r'"code":"([^"]+)"', response.text)
                room_titles = re.findall(r'"title":"([^"]+)"', response.text)
                
                for i, code in enumerate(room_codes[:10]):
                    rooms.append({
                        'code': code,
                        'title': room_titles[i] if i < len(room_titles) else code,
                        'accessible': True
                    })
                
                return rooms
            else:
                return []
                
        except Exception as e:
            print(f"⚠️ THM room scraping failed: {e}")
            return []
    
    def get_room_details(self, room_code):
        """Dapatkan detail room dasar."""
        try:
            url = f"{self.base_url}/room/{room_code}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                tasks = []
                
                # Ekstrak task dasar
                task_matches = re.findall(r'"task":(\d+)', response.text)
                for task_num in set(task_matches[:5]):
                    tasks.append({'task': int(task_num), 'accessible': True})
                
                return {'code': room_code, 'tasks': tasks, 'accessible': True}
        except Exception as e:
            print(f"⚠️ Room details fetch failed: {e}")
        
        return {'code': room_code, 'tasks': [], 'accessible': False}
    
    def validate_session(self):
        """Validasi session cookie."""
        try:
            response = self.session.get(f"{self.base_url}/rooms", timeout=10)
            return response.status_code == 200 and 'Login' not in response.text
        except:
            return False