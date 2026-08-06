import requests
from typing import Dict, Any

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
        """Atur cookies sesi berdasarkan kredensial."""
        if platform == 'hackerone':
            if 'session_token' in credentials:
                session.headers['Authorization'] = f'Bearer {credentials["session_token"]}'
        
        elif platform == 'bugcrowd':
            if 'session_cookie' in credentials:
                session.cookies.set('_bugcrowd_session', credentials['session_cookie'])
        
        elif platform == 'intigriti':
            if 'session_cookie' in credentials:
                session.cookies.set('SESSION', credentials['session_cookie'])
        
        elif platform == 'immunefi':
            if 'session_cookie' in credentials:
                session.cookies.set('sessionid', credentials['session_cookie'])
        
        elif platform == 'hackthebox':
            if 'session_cookie' in credentials:
                session.cookies.set('htb_session', credentials['session_cookie'])
        
        elif platform == 'tryhackme':
            if 'session_cookie' in credentials:
                session.cookies.set('connect.sid', credentials['session_cookie'])