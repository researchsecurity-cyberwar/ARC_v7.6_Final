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
        """Dapatkan room yang tersedia (parse link HTML server-rendered)."""
        try:
            response = self.session.get(f"{self.base_url}/rooms", timeout=10)
            
            if response.status_code == 200 and 'Login' not in response.text:
                rooms = []
                # Halaman THM server-rendered berisi link /room/<code>
                room_links = re.findall(r'href="[^"]*?/room/([a-zA-Z0-9-]+)"', response.text)
                seen = set()
                for code in room_links:
                    if code in seen or len(code) < 2:
                        continue
                    seen.add(code)
                    title = code.replace('-', ' ').title()
                    rooms.append({
                        'code': code,
                        'title': title,
                        'accessible': True
                    })
                    if len(rooms) >= 10:
                        break
                
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
    
    def get_all_programs(self) -> dict:
        """Kompatibilitas dengan ARC main loop.
        
        THM adalah platform CTF, bukan bug bounty, jadi tidak ada 'program'
        seperti di HackerOne/BugCrowd. Sebagai pengganti, kami mengekspor room
        yang tersedia sebagai 'programs' dalam format dict agar kompatibel
        dengan arc_main._update_intelligence_feed().
        """
        programs = {}
        for room in self.get_available_rooms():
            key = room.get('code', f'room_{len(programs)}')
            programs[key] = {
                'code': room.get('code', ''),
                'title': room.get('title', room.get('code', '')),
                'accessible': room.get('accessible', False),
                'platform': 'tryhackme',
                'status': 'active'
            }
        return programs

    def validate_session(self):
        """Validasi session cookie."""
        try:
            response = self.session.get(f"{self.base_url}/rooms", timeout=10)
            return response.status_code == 200 and 'Login' not in response.text
        except:
            return False