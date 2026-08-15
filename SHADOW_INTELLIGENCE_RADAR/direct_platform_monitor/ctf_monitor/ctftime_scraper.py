import requests
import time
from datetime import datetime, timezone

class CTFtimeScraper:
    """
    Scrap CTFtime.org langsung dengan API publik.
    TIDAK memerlukan login atau kredensial — semua data tersedia secara public
    melalui REST API yang resmi dokumentasi di https://ctftime.org/api
    
    REALITAS TEKNIS:
    - CTFtime menyediakan REST API publik tanpa autentikasi
    - Data berupa JSON: events, teams, top, results, votes
    - Rate limit ~ 5 request/menit (patokan tak resmi)
    - Scraper ini bisa berjalan 24/7 tanpa perlu update token/cookie
    - Data: CTF yang akan datang, deadline pendaftaran, prize pools, format
    
    Digunakan untuk:
    1. Intelijen: menemukan CTF baru yang akan dimainkan
    2. Knowledge: mengumpulkan problem description & writeup
    3. Timing: memantau deadline & start time
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        self.base_url = "https://ctftime.org/api/v1"
    
    def validate_session(self) -> bool:
        """Validasi koneksi ke CTFtime API (selalu True karena publik)."""
        try:
            response = self.session.get(f"{self.base_url}/events/", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def get_upcoming_events(self, limit: int = 50) -> list:
        """
        Dapatkan event CTF yang akan datang (start time >= now).
        
        Returns list of dict dengan key:
        - id, title, start, finish, duration (jam/hari), 
          format, location, onsite, participants, organizers, 
          prizes, url, ctftime_url, logo
        """
        try:
            now_ts = int(time.time())
            url = f"{self.base_url}/events/"
            params = {
                'limit': limit,
                'start': now_ts
            }
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                events = response.json()
                upcoming = []
                for ev in events:
                    start_ts = datetime.fromisoformat(ev['start']).timestamp()
                    if start_ts > now_ts:
                        upcoming.append(self._normalize_event(ev))
                return upcoming
            else:
                print(f"⚠️ CTFtime API error: {response.status_code}")
                return []
        except Exception as e:
            print(f"⚠️ CTFtime upcoming events fetch failed: {e}")
            return []
    
    def get_past_events(self, limit: int = 20, days_back: int = 30) -> list:
        """
        Dapatkan event CTF yang sudah berakhir (untuk analisis writeup).
        days_back: berapa hari ke belakang dari sekarang
        """
        try:
            now_ts = int(time.time())
            finish_ts = now_ts
            start_ts = now_ts - (days_back * 86400)
            
            url = f"{self.base_url}/events/"
            params = {
                'limit': limit,
                'start': start_ts,
                'finish': finish_ts
            }
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                events = response.json()
                past = []
                for ev in events:
                    finish_iso = ev.get('finish')
                    if finish_iso:
                        finish_dt = datetime.fromisoformat(finish_iso)
                        if finish_dt.timestamp() < now_ts:
                            ev_norm = self._normalize_event(ev)
                            ev_norm['has_writeup'] = True
                            past.append(ev_norm)
                return past
            else:
                return []
        except Exception as e:
            print(f"⚠️ CTFtime past events fetch failed: {e}")
            return []
    
    def get_top_teams(self, limit: int = 10) -> list:
        """
        Dapatkan tim teratas di CTFtime (insight: tim kuat yang harus diwaspadai).
        Returns list of dict: rank, name, score, country, organization
        """
        try:
            url = f"{self.base_url}/top/"
            params = {'limit': limit}
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                teams = []
                # CTFtime mengembalikan format {"2026": [{"team_name":..., "points":..., "team_id":...}, ...]}
                # Kunci tahun bisa berupa string tahun berjalan
                year_key = str(datetime.now(timezone.utc).year)
                team_list = data.get(year_key, data.get(list(data.keys())[0] if data else ''))
                for i, team in enumerate(team_list or [], 1):
                    teams.append({
                        'rank': i,
                        'name': team.get('team_name', team.get('name', '')),
                        'score': team.get('points', 0),
                        'country': team.get('country', ''),
                        'organization': team.get('organization', ''),
                        'team_id': team.get('team_id', 0)
                    })
                return teams
            else:
                print(f"⚠️ CTFtime API error: {response.status_code}")
                return []
        except Exception as e:
            print(f"⚠️ CTFtime top teams fetch failed: {e}")
        
        return []
    
    def get_event_by_id(self, event_id: int) -> dict:
        """Dapatkan detail satu event CTF tertentu."""
        try:
            url = f"{self.base_url}/events/{event_id}/"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return self._normalize_event(response.json())
            else:
                return {}
        except Exception as e:
            print(f"⚠️ CTFtime event fetch failed: {e}")
            return {}
    
    def get_all_programs(self) -> dict:
        """
        Kompatibilitas dengan ARC main loop.
        CTFtime adalah aggregator CTF, bukan platform bug bounty.
        Sebagai pengganti 'programs', mengembalikan event yang akan datang
        dalam format dict untuk arc_main._update_intelligence_feed().
        """
        programs = {}
        upcoming = self.get_upcoming_events(limit=50)
        for ev in upcoming:
            key = f"ctf_{ev['id']}"
            programs[key] = {
                'name': ev.get('title', ''),
                'url': ev.get('ctf_url', ''),
                'platform': 'ctftime',
                'status': 'upcoming',
                'start': ev.get('start', ''),
                'finish': ev.get('finish', ''),
                'format': ev.get('format', ''),
                'onsite': ev.get('onsite', False),
                'location': ev.get('location', ''),
                'participants': ev.get('participants', 0),
                'duration_hours': ev.get('duration_hours', 0),
                'organizers': ev.get('organizers', []),
                'prizes': ev.get('prizes', ''),
                'weight': ev.get('weight', 0)
            }
        
        return programs
    
    def _normalize_event(self, ev: dict) -> dict:
        """Normalkan struktur event agar konsisten."""
        duration = ev.get('duration', {})
        hours = duration.get('hours', 0)
        days = duration.get('days', 0)
        total_hours = days * 24 + hours
        
        return {
            'id': ev.get('id'),
            'title': ev.get('title', ''),
            'start': ev.get('start'),
            'finish': ev.get('finish'),
            'duration_hours': total_hours,
            'duration_days': days,
            'duration_hours_remainder': hours,
            'format': ev.get('format', ''),
            'format_id': ev.get('format_id', 0),
            'location': ev.get('location', ''),
            'onsite': ev.get('onsite', False),
            'restrictions': ev.get('restrictions', ''),
            'participants': ev.get('participants', 0),
            'weight': ev.get('weight', 0),
            'organizers': [o.get('name', '') for o in ev.get('organizers', [])],
            'url': ev.get('url', ''),
            'ctf_url': ev.get('ctftime_url', ''),
            'logo': ev.get('logo', ''),
            'description': ev.get('description', ''),
            'prizes': ev.get('prizes', ''),
            'is_votable_now': ev.get('is_votable_now', False)
        }
    
    def get_intelligence(self) -> dict:
        """Kumpulkan seluruh intelligence CTFtime untuk ARC."""
        return {
            'source': 'ctftime',
            'upcoming_events': self.get_upcoming_events(limit=30),
            'top_teams': self.get_top_teams(limit=10),
            'past_events': self.get_past_events(limit=15, days_back=60),
            'timestamp': time.time()
        }



