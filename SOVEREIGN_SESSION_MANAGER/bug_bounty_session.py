import requests
from typing import Dict, Any
import re
import os
from SOVEREIGN_SESSION_MANAGER.session_factory import SessionFactory

class BugBountySession:
    """
    Sesi HackerOne, Bugcrowd, Intigriti, YesWeHack, Immunefi.
    Mengelola sesi untuk platform bug bounty utama dengan strategi optimal per platform.
    """
    
    def __init__(self, credential_vault):
        self.credential_vault = credential_vault
        self.session_factory = SessionFactory()
        self.platforms = ['hackerone', 'bugcrowd', 'intigriti', 'yeswehack', 'immunefi']
        self.telegram_notifier = self._initialize_telegram_notifier()
        if self.telegram_notifier:
            self.telegram_notifier.set_session_manager(self)
    
    def _initialize_telegram_notifier(self):
        """Inisialisasi Telegram notifier jika tersedia."""
        try:
            from DIALOGIC_COPILLOT.PLATFORM_COMMUNICATOR.telegram_notifier import TelegramNotifier
            return TelegramNotifier()
        except ImportError:
            return None
    
    def get_platform_session(self, platform: str):
        """
        Dapatkan sesi aktif untuk platform bug bounty dengan strategi optimal.
        """
        if platform not in self.platforms:
            return {'success': False, 'error': f'Unsupported platform: {platform}'}
        
        try:
            # Muat kredensial dari vault
            credentials = self.credential_vault.load_credentials(platform)
            
            if not credentials:
                return {'success': False, 'error': f'No credentials found for {platform}. Please configure ~/.arc/config.yaml'}
            
            # Strategi berdasarkan jenis autentikasi yang tersedia
            if self._uses_api_token(platform):
                # Platform dengan API token permanen
                return self._handle_api_token_session(platform, credentials)
            
            elif self._supports_auto_login(platform):
                # Platform dengan auto-login via form
                return self._handle_auto_login_session(platform, credentials)
            
            else:
                # Platform dengan session cookie manual
                return self._handle_manual_session(platform, credentials)
        
        except Exception as e:
            return {'success': False, 'error': f'Session management failed: {str(e)}'}
    
    def _uses_api_token(self, platform: str) -> bool:
        """Platform yang mendukung API token permanen"""
        return platform in ['hackerone', 'intigriti']
    
    def _supports_auto_login(self, platform: str) -> bool:
        """Platform yang mendukung auto-login via form"""
        return platform in ['bugcrowd']
    
    def _handle_api_token_session(self, platform: str, credentials: dict):
        """Tangani sesi untuk platform dengan API token"""
        if platform == 'hackerone':
            if 'api_token' not in credentials:
                return {'success': False, 'error': 'HackerOne requires api_token in config.yaml'}
            
            # Buat sesi dengan API token
            session = self.session_factory.create_session(platform, {'api_token': credentials['api_token']})
            session.headers['Authorization'] = f'Bearer {credentials["api_token"]}'
            
            if self._verify_session_validity(session, platform):
                return {'success': True, 'session': session, 'platform': platform}
            else:
                return {'success': False, 'error': 'Invalid HackerOne API token'}
        
        elif platform == 'intigriti':
            if 'personal_access_token' not in credentials:
                return {'success': False, 'error': 'Intigriti requires personal_access_token in config.yaml'}
            
            # Buat sesi dengan Personal Access Token
            session = self.session_factory.create_session(platform, {'personal_access_token': credentials['personal_access_token']})
            session.headers['X-API-KEY'] = credentials['personal_access_token']
            
            if self._verify_session_validity(session, platform):
                return {'success': True, 'session': session, 'platform': platform}
            else:
                return {'success': False, 'error': 'Invalid Intigriti Personal Access Token'}
    
    def _handle_auto_login_session(self, platform: str, credentials: dict):
        """Tangani sesi untuk platform dengan auto-login"""
        # Coba gunakan session cookie yang ada
        if 'session_cookie' in credentials:
            session = self.session_factory.create_session(platform, credentials)
            if self._verify_session_validity(session, platform):
                return {'success': True, 'session': session, 'platform': platform}
        
        # Jika tidak ada atau kadaluarsa, lakukan auto-login
        if 'email' not in credentials or 'password' not in credentials:
            return {'success': False, 'error': f'{platform} requires email and password in config.yaml for auto-login'}
        
        new_session = self._auto_login(platform, credentials)
        if new_session:
            # Simpan session baru ke vault
            credentials['session_cookie'] = self._extract_session_cookie(new_session)
            self.credential_vault.store_credentials(credentials, platform)
            return {'success': True, 'session': new_session, 'platform': platform}
        else:
            return {'success': False, 'error': f'Auto-login failed for {platform}'}
    
    def _handle_manual_session(self, platform: str, credentials: dict):
        """Tangani sesi untuk platform yang memerlukan session cookie manual"""
        if 'session_cookie' not in credentials:
            instruction = ""
            if platform == 'yeswehack':
                instruction = "Get session cookie from DevTools → Application → Cookies → yeswehack.com"
            elif platform == 'immunefi':
                instruction = "Get sessionid and csrftoken from DevTools → Application → Cookies → immunefi.com"
            
            return {
                'success': False, 
                'error': f'{platform} requires manual session_cookie configuration',
                'instruction': instruction
            }
        
        session = self.session_factory.create_session(platform, credentials)
        if self._verify_session_validity(session, platform):
            return {'success': True, 'session': session, 'platform': platform}
        else:
            # Session kadaluarsa - kirim notifikasi Telegram jika tersedia
            error_msg = f'Session expired for {platform}. Please update session_cookie in config.yaml'
            
            if self.telegram_notifier:
                self.telegram_notifier.send_notification(
                    f"<b>SESSION EXPIRED</b>\n"
                    f"Platform: {platform}\n"
                    f"Action: Update session cookie\n"
                    f"Command: /update_session {platform} your_new_cookie_here"
                )
            
            return {'success': False, 'error': error_msg}
    
    # ... (metode lainnya tetap sama: _auto_login, _get_csrf_token, _extract_session_cookie, _verify_session_validity, store_platform_credentials)
    
    def _auto_login(self, platform: str, credentials: dict):
        """Auto-login ke platform menggunakan email dan password."""
        try:
            session = self.session_factory.create_session(platform, credentials)
            login_url = self._get_login_url(platform)
            
            # Dapatkan CSRF token jika diperlukan
            csrf_token = self._get_csrf_token(platform, login_url)
            if csrf_token:
                credentials['csrf_token'] = csrf_token
            
            # Lakukan login
            login_data = {
                'email': credentials.get('email'),
                'password': credentials.get('password'),
                'csrf_token': csrf_token
            }
            
            response = session.post(login_url, data=login_data, timeout=30)
            
            if response.status_code == 200 and self._verify_session_validity(session, platform):
                return session
            else:
                return None
        except Exception as e:
            print(f"Auto-login failed for {platform}: {e}")
            return None
    
    def _get_login_url(self, platform: str) -> str:
        """Dapatkan URL login untuk platform."""
        login_urls = {
            'bugcrowd': 'https://bugcrowd.com/login',
            'hackerone': 'https://hackerone.com/login',
            'intigriti': 'https://www.intigriti.com/login',
            'yeswehack': 'https://yeswehack.com/login',
            'immunefi': 'https://immunefi.com/login'
        }
        return login_urls.get(platform, f'https://{platform}.com/login')
    
    def _get_csrf_token(self, platform: str, url: str) -> str:
        """Dapatkan CSRF token dari halaman login."""
        try:
            session = self.session_factory.create_session(platform)
            response = session.get(url, timeout=15)
            
            # Cari CSRF token di HTML
            import re
            patterns = [
                r'name="csrf_token"\s+value="([^"]+)"',
                r'name="csrfmiddlewaretoken"\s+value="([^"]+)"',
                r'"csrf_token":"([^"]+)"'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, response.text)
                if match:
                    return match.group(1)
            
            return None
        except Exception as e:
            print(f"Failed to get CSRF token for {platform}: {e}")
            return None
    
    def _extract_session_cookie(self, session) -> str:
        """Ekstrak session cookie dari sesi yang ter-autentikasi."""
        cookies = session.cookies.get_dict()
        
        # Platform-specific cookie names
        cookie_names = {
            'bugcrowd': '_bugcrowd_session',
            'intigriti': 'SESSION',
            'yeswehack': 'yeswehack_session',
            'immunefi': 'sessionid',
            'hackerone': 'hackerone_session'
        }
        
        for platform, cookie_name in cookie_names.items():
            if cookie_name in cookies:
                return cookies[cookie_name]
        
        # Return first cookie if specific not found
        if cookies:
            return list(cookies.values())[0]
        
        return None
    
    def store_platform_credentials(self, platform: str, credentials: dict):
        """Simpan kredensial platform ke vault."""
        try:
            self.credential_vault.store_credentials(credentials, platform)
            return {'success': True, 'message': f'Credentials stored for {platform}'}
        except Exception as e:
            return {'success': False, 'error': f'Failed to store credentials: {str(e)}'}
    
    def _verify_session_validity(self, session, platform: str) -> bool:
        """Verifikasi apakah sesi masih valid."""
        try:
            # Timeout lebih panjang untuk menghindari false negative
            timeout = 15
            
            if platform == 'hackerone':
                # Prioritaskan verifikasi API token
                if 'Authorization' in session.headers:
                    response = session.get('https://hackerone.com/api/v1/me', timeout=timeout)
                    return response.status_code == 200
                
                # Fallback ke verifikasi session cookie
                response = session.get('https://hackerone.com/hacktivity', timeout=timeout)
                return 'Sign in' not in response.text and response.status_code == 200
            
            elif platform == 'bugcrowd':
                response = session.get('https://bugcrowd.com/user.json', timeout=timeout)
                return response.status_code == 200
            
            elif platform == 'intigriti':
                response = session.get('https://api.intigriti.com/account/profile', timeout=timeout)
                return response.status_code == 200
            
            elif platform == 'yeswehack':
                response = session.get('https://yeswehack.com/api/v1/me', timeout=timeout)
                return response.status_code == 200
            
            elif platform == 'immunefi':
                response = session.get('https://immunefi.com/api/v1/user/me', timeout=timeout)
                return response.status_code == 200
            
            return False
        
        except requests.exceptions.Timeout:
            # Timeout dianggap sebagai sesi valid (network issue, bukan auth issue)
            return True
        except:
            return False