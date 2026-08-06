import requests
from bs4 import BeautifulSoup
import hashlib
import time

class PlatformChangeDetector:
    """
    Monitor UI changes across platforms.
    Mendeteksi perubahan antarmuka pengguna di platform bug bounty.
    """
    
    def __init__(self):
        self.platforms = {
            'hackerone': 'https://hackerone.com',
            'bugcrowd': 'https://bugcrowd.com',
            'intigriti': 'https://www.intigriti.com',
            'yeswehack': 'https://yeswehack.com'
        }
        self.cache_dir = "~/.arc/cache/platform_ui/"
    
    def detect_ui_changes(self, platform_name):
        """Deteksi perubahan UI untuk platform tertentu."""
        if platform_name not in self.platforms:
            return False
        
        url = self.platforms[platform_name]
        current_hash = self._get_page_hash(url)
        
        if not current_hash:
            return False
        
        cache_file = f"{self.cache_dir}{platform_name}_ui_hash.txt"
        cache_path = cache_file.replace("~", "")
        
        # Baca hash sebelumnya
        try:
            with open(cache_path, 'r') as f:
                previous_hash = f.read().strip()
        except FileNotFoundError:
            previous_hash = ""
        
        # Simpan hash saat ini
        with open(cache_path, 'w') as f:
            f.write(current_hash)
        
        return current_hash != previous_hash
    
    def _get_page_hash(self, url):
        """Dapatkan hash dari halaman web."""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Fokus pada bagian utama konten
                soup = BeautifulSoup(response.content, 'html.parser')
                main_content = soup.find('main') or soup.find('body')
                if main_content:
                    content_str = str(main_content)
                    return hashlib.md5(content_str.encode()).hexdigest()
        except Exception as e:
            print(f"⚠️ Failed to hash {url}: {e}")
        
        return None