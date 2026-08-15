import requests
from typing import Dict, Any
from SOVEREIGN_SESSION_MANAGER.cookie_utils import set_cookie_string, set_xsrf_token

class SessionFactory:
    """
    Factory sesi universal.
    Membuat sesi HTTP universal untuk berbagai platform.
    """
    
    def __init__(self):
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; ARC-AI-Agent/1.0)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def create_session(self, platform: str, credentials: Dict[str, Any] = None):
        """
        Buat sesi untuk platform tertentu.
        """
        session = requests.Session()
        session.headers.update(self.default_headers)
        
        # Tambahkan header khusus platform
        platform_headers = self._get_platform_headers(platform)
        session.headers.update(platform_headers)
        
        # Atur cookies jika kredensial disediakan
        if credentials:
            self._setup_session_cookies(session, platform, credentials)
        
        return session
    
    def _get_platform_headers(self, platform: str) -> Dict[str, str]:
        """Dapatkan header khusus platform."""
        headers = {}
        
        if platform == 'hackerone':
            headers.update({
                'X-Csrf-Token': 'auto-detect',
                'Referer': 'https://hackerone.com/'
            })
        elif platform == 'bugcrowd':
            headers.update({
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'https://bugcrowd.com/'
            })
        elif platform == 'intigriti':
            headers.update({
                'X-XSRF-TOKEN': 'auto-detect',
                'Referer': 'https://www.intigriti.com/'
            })
        elif platform == 'immunefi':
            headers.update({
                'Referer': 'https://immunefi.com/'
            })
        elif platform == 'hackthebox':
            headers.update({
                'Referer': 'https://www.hackthebox.com/'
            })
        elif platform == 'tryhackme':
            headers.update({
                'Referer': 'https://tryhackme.com/'
            })
        
        return headers
    
    def _setup_session_cookies(self, session, platform: str, credentials: Dict[str, Any]):
        """Atur cookies sesi berdasarkan kredensial.

        Semua platform memakai jalur seragam lewat ``set_cookie_string``:
        dukung raw cookie-string 'nama=value; nama2=value2' (session+xsrf sekaligus)
        ATAU nilai tunggal -> dipasang dengan nama cookie default platform.
        """
        session_cookie = credentials.get('session_cookie')

        if platform == 'hackerone':
            # H1 API token = Identifier (username) + Value (password) via HTTP Basic
            # atau gunakan session cookie + xsrf token untuk hybrid mode
            if 'api_token_id' in credentials and 'api_token' in credentials:
                # Mode API token: gunakan HTTP Basic Auth
                session.auth = (credentials['api_token_id'], credentials['api_token'])
            elif 'session_cookie' in credentials:
                # Mode session cookie: set cookie dan xsrf token
                set_cookie_string(session, credentials['session_cookie'], default='hackerone_session')
                set_xsrf_token(session, credentials.get('xsrf_token'), platform='hackerone')
            elif 'session_token' in credentials:
                # Mode Bearer token
                session.headers['Authorization'] = f'Bearer {credentials["session_token"]}'

        elif platform == 'bugcrowd':
            set_cookie_string(session, session_cookie, default='_bugcrowd_session')

        elif platform == 'intigriti':
            # Intigriti: dukungan dual untuk Personal Access Token dan session cookie
            if 'personal_access_token' in credentials:
                # Mode Personal Access Token: set X-API-KEY header
                session.headers['X-API-KEY'] = credentials['personal_access_token']
                # juga set session cookie jika ada (hybrid mode)
                if 'session_cookie' in credentials:
                    set_cookie_string(session, credentials['session_cookie'], default='SESSION')
            elif 'session_cookie' in credentials:
                # Mode session cookie saja
                set_cookie_string(session, credentials['session_cookie'], default='SESSION')
            # set xsrf token untuk intigriti (X-XSRF-TOKEN header)
            set_xsrf_token(session, credentials.get('xsrf_token'), platform='intigriti')

        elif platform == 'yeswehack':
            set_cookie_string(session, session_cookie, default='session')

        elif platform == 'immunefi':
            set_cookie_string(session, session_cookie, default='sessionid')

        elif platform == 'hackthebox':
            set_cookie_string(session, session_cookie, default='htb_session')

        elif platform == 'tryhackme':
            set_cookie_string(session, session_cookie, default='connect.sid')

        # XSRF/CSRF token opsional (untuk aksi POST/submit report)
        set_xsrf_token(session, credentials.get('xsrf_token'), platform=platform)