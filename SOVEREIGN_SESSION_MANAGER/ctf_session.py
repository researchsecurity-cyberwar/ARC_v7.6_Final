import requests
from typing import Dict, Any
from SOVEREIGN_SESSION_MANAGER.session_factory import SessionFactory

class CTFSession:
    """
    Sesi HTB, TryHackMe, CTFtime.
    Mengelola sesi untuk platform CTF utama dengan strategi optimal per platform.
    """
    
    def __init__(self, credential_vault):
        self.credential_vault = credential_vault
        self.session_factory = SessionFactory()
        self.platforms = ['hackthebox', 'tryhackme', 'ctftime']
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
        Dapatkan sesi aktif untuk platform CTF dengan strategi realistis.
        """
        if platform not in self.platforms:
            return {'success': False, 'error': f'Unsupported platform: {platform}'}
        
        try:
            # Muat kredensial dari vault
            credentials = self.credential_vault.load_credentials(platform)
            
            if not credentials:
                return {'success': False, 'error': f'No credentials found for {platform}. Please configure ~/.arc/config.yaml'}
            
            # Strategi berdasarkan platform
            if platform == 'ctftime':
                # CTFtime tidak memerlukan login - selalu valid
                return {'success': True, 'session': None, 'platform': platform}
            else:
                # HTB dan TryHackMe - gunakan session cookie manual
                return self._handle_manual_session(platform, credentials)
        
        except Exception as e:
            return {'success': False, 'error': f'Session management failed: {str(e)}'}
    
    def _handle_manual_session(self, platform: str, credentials: dict):
        """Tangani sesi untuk platform CTF yang memerlukan session cookie manual."""
        if 'session_cookie' not in credentials:
            instruction = ""
            if platform == 'hackthebox':
                instruction = "Get session cookie from DevTools → Application → Cookies → hackthebox.com"
            elif platform == 'tryhackme':
                instruction = "Get session cookie from DevTools → Application → Cookies → tryhackme.com"
            
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
    
    def _verify_session_validity(self, session, platform: str) -> bool:
        """Verifikasi apakah sesi masih valid."""
        try:
            # Timeout lebih panjang untuk menghindari false negative
            timeout = 15
            
            if platform == 'hackthebox':
                # Verifikasi akses premium HTB
                response = session.get('https://www.hackthebox.com/api/v4/user/info', timeout=timeout)
                return response.status_code == 200
            
            elif platform == 'tryhackme':
                # Verifikasi sesi TryHackMe
                response = session.get('https://tryhackme.com/api/user', timeout=timeout)
                return response.status_code == 200
            
            elif platform == 'ctftime':
                # CTFtime selalu valid (tidak perlu login)
                return True
            
            return False
        
        except requests.exceptions.Timeout:
            # Timeout dianggap sebagai sesi valid (network issue, bukan auth issue)
            return True
        except:
            return False
    
    def store_platform_credentials(self, platform: str, credentials: Dict[str, Any]):
        """
        Simpan kredensial untuk platform CTF.
        """
        if platform not in self.platforms:
            return {'success': False, 'error': f'Unsupported platform: {platform}'}
        
        return self.credential_vault.store_credentials(credentials, platform)