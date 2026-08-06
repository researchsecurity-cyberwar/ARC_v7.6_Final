from SOVEREIGN_SESSION_MANAGER.bug_bounty_session import BugBountySession
from SOVEREIGN_SESSION_MANAGER.ctf_session import CTFSession
from SOVEREIGN_SESSION_MANAGER.vdp_session import VDPSession

class PlatformSessionManager:
    """
    Manajemen sesi per platform.
    Mengkoordinasikan semua jenis sesi platform.
    """
    
    def __init__(self, credential_vault):
        self.credential_vault = credential_vault
        self.platforms = ['hackerone', 'bugcrowd', 'intigriti', 'yeswehack', 'immunefi']
        self.bug_bounty_session = BugBountySession(credential_vault)
        self.ctf_session = CTFSession(credential_vault)
        self.vdp_session = VDPSession(credential_vault)
    
    def get_platform_session(self, platform: str):
        """Dapatkan sesi untuk platform bug bounty tertentu."""
        return self.bug_bounty_session.get_platform_session(platform)
    
    def get_session(self, platform_type: str, **kwargs):
        """
        Dapatkan sesi untuk tipe platform tertentu.
        
        Args:
            platform_type: 'bug_bounty', 'ctf', atau 'vdp'
            **kwargs: Parameter spesifik platform
            
        Returns:
            dict: Hasil sesi dengan status dan objek sesi
        """
        if platform_type == 'bug_bounty':
            platform = kwargs.get('platform')
            return self.bug_bounty_session.get_platform_session(platform)
        
        elif platform_type == 'ctf':
            platform = kwargs.get('platform')
            return self.ctf_session.get_platform_session(platform)
        
        elif platform_type == 'vdp':
            country = kwargs.get('country', 'indonesia')
            program = kwargs.get('program', 'kominfo')
            return self.vdp_session.get_vdp_session(country, program)
        
        else:
            return {'success': False, 'error': f'Unsupported platform type: {platform_type}'}
    
    def store_credentials(self, platform_type: str, **kwargs):
        """
        Simpan kredensial untuk tipe platform tertentu.
        """
        if platform_type == 'bug_bounty':
            platform = kwargs.get('platform')
            credentials = kwargs.get('credentials', {})
            return self.bug_bounty_session.store_platform_credentials(platform, credentials)
        
        elif platform_type == 'ctf':
            platform = kwargs.get('platform')
            credentials = kwargs.get('credentials', {})
            return self.ctf_session.store_platform_credentials(platform, credentials)
        
        elif platform_type == 'vdp':
            country = kwargs.get('country', 'indonesia')
            program = kwargs.get('program', 'kominfo')
            credentials = kwargs.get('credentials', {})
            return self.vdp_session.store_vdp_credentials(country, program, credentials)
        
        else:
            return {'success': False, 'error': f'Unsupported platform type: {platform_type}'}
    
    def list_available_sessions(self):
        """
        Daftar semua sesi yang tersedia.
        """
        available_sessions = {
            'bug_bounty': ['hackerone', 'bugcrowd', 'intigriti', 'yeswehack', 'immunefi'],
            'ctf': ['hackthebox', 'tryhackme', 'ctftime'],
            'vdp': {
                'indonesia': ['kominfo', 'ojk', 'bi', 'bssn', 'kemenkominfo'],
                'global': ['us_cisa', 'eu_enisa', 'uk_ncsc', 'au_acsc', 'sg_csa']
            }
        }
        return available_sessions