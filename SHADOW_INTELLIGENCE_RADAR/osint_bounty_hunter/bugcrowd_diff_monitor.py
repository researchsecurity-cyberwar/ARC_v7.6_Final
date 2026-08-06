import requests
from bs4 import BeautifulSoup
import hashlib

class BugcrowdDiffMonitor:
    """
    Daily scope diff from public pages.
    Memantau perubahan scope program Bugcrowd dari halaman publik.
    """
    
    def __init__(self):
        self.bc_public_url = "https://bugcrowd.com/programs"
        self.cache_file = "~/.arc/cache/bugcrowd_programs_hash.txt"
    
    def get_current_programs_hash(self):
        """Dapatkan hash dari halaman program saat ini."""
        try:
            response = requests.get(self.bc_public_url, timeout=10)
            if response.status_code == 200:
                content_hash = hashlib.md5(response.content).hexdigest()
                return content_hash
        except Exception as e:
            print(f"⚠️ Failed to fetch Bugcrowd programs: {e}")
        
        return None
    
    def has_scope_changed(self):
        """Cek apakah scope program telah berubah."""
        current_hash = self.get_current_programs_hash()
        if not current_hash:
            return False
        
        # Baca hash sebelumnya
        cache_path = self.cache_file.replace("~", "")
        try:
            with open(cache_path, 'r') as f:
                previous_hash = f.read().strip()
        except FileNotFoundError:
            previous_hash = ""
        
        # Simpan hash saat ini
        with open(cache_path, 'w') as f:
            f.write(current_hash)
        
        return current_hash != previous_hash
    
    def extract_program_details(self):
        """Ekstrak detail program dari halaman publik."""
        try:
            response = requests.get(self.bc_public_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                return self._parse_program_listings(soup)
        except Exception as e:
            print(f"⚠️ Failed to parse Bugcrowd programs: {e}")
        
        return []
    
    def _parse_program_listings(self, soup):
        """Parse daftar program dari HTML."""
        programs = []
        program_links = soup.find_all('a', href=re.compile(r'/programs/.*'))
        
        for link in program_links:
            program_name = link.get_text(strip=True)
            program_url = f"https://bugcrowd.com{link.get('href', '')}"
            
            if program_name:
                programs.append({
                    'name': program_name,
                    'url': program_url,
                    'platform': 'bugcrowd',
                    'scope_type': self._detect_scope_type(link)
                })
        
        return programs
    
    def _detect_scope_type(self, element):
        """Deteksi tipe scope dari elemen HTML."""
        element_text = element.get_text().lower()
        if 'vdp' in element_text or 'vulnerability disclosure' in element_text:
            return 'vdp'
        elif 'private' in element_text:
            return 'private'
        else:
            return 'public'