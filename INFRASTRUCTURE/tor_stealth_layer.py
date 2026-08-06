import subprocess
import time
import random
from stem import Signal
from stem.control import Controller
import requests

class TorStealthLayer:
    """
    Free IP rotation + TLS impersonation for all outbound.
    Menyediakan rotasi IP gratis dan impersonasi TLS untuk semua koneksi keluar.
    """
    
    def __init__(self, tor_socks_port=9050, tor_control_port=9051):
        self.tor_socks_port = tor_socks_port
        self.tor_control_port = tor_control_port
        self.session = requests.Session()
        self.setup_complete = False
    
    def setup_tor_stealth(self):
        """
        Siapkan lapisan stealth Tor.
        """
        results = {
            'tor_socks_port': self.tor_socks_port,
            'tor_control_port': self.tor_control_port,
            'setup_successful': False,
            'errors': []
        }
        
        try:
            # Instal Tor jika belum ada
            if not shutil.which('tor'):
                subprocess.run(['sudo', 'apt', 'install', '-y', 'tor'], check=True, timeout=300)
            
            # Konfigurasi Tor dengan kontrol port
            tor_config = f'''
SocksPort {self.tor_socks_port}
ControlPort {self.tor_control_port}
CookieAuthentication 1
'''
            with open('/tmp/torrc', 'w') as f:
                f.write(tor_config)
            
            # Mulai layanan Tor
            subprocess.run(['tor', '-f', '/tmp/torrc'], 
                          stdout=subprocess.DEVNULL, 
                          stderr=subprocess.DEVNULL,
                          preexec_fn=os.setpgrp)
            
            # Tunggu Tor siap
            time.sleep(5)
            
            # Uji koneksi Tor
            test_proxies = {'http': f'socks5h://127.0.0.1:{self.tor_socks_port}',
                           'https': f'socks5h://127.0.0.1:{self.tor_socks_port}'}
            response = requests.get('https://check.torproject.org/api/ip', 
                                   proxies=test_proxies, timeout=10)
            
            if response.json().get('IsTor', False):
                self.setup_complete = True
                results['setup_successful'] = True
            else:
                results['errors'].append('Tor connection test failed')
        
        except Exception as e:
            results['errors'].append(f'Tor setup failed: {str(e)}')
        
        return results
    
    def rotate_tor_circuit(self):
        """
        Rotasi sirkuit Tor untuk mengganti IP.
        """
        if not self.setup_complete:
            return {'success': False, 'error': 'Tor not set up'}
        
        try:
            with Controller.from_port(port=self.tor_control_port) as controller:
                controller.authenticate()
                controller.signal(Signal.NEWNYM)
                time.sleep(controller.get_newnym_wait())
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_stealth_session(self, rotate_ip: bool = True):
        """
        Dapatkan sesi HTTP dengan stealth Tor.
        """
        if not self.setup_complete:
            raise RuntimeError('Tor stealth layer not set up')
        
        if rotate_ip:
            self.rotate_tor_circuit()
        
        # Konfigurasi sesi dengan proxy Tor
        self.session.proxies = {
            'http': f'socks5h://127.0.0.1:{self.tor_socks_port}',
            'https': f'socks5h://127.0.0.1:{self.tor_socks_port}'
        }
        
        # Atur header untuk impersonasi TLS
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        self.session.headers.update({
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        return self.session