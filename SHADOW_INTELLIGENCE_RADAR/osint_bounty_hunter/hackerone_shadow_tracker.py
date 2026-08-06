import requests
from bs4 import BeautifulSoup
import re

class HackerOneShadowTracker:
    """
    Archive.today + Wayback Machine scraping for new programs.
    Mendeteksi program bug bounty baru di HackerOne tanpa login.
    """
    
    def __init__(self):
        self.archive_urls = [
            "https://archive.ph",
            "https://web.archive.org"
        ]
        self.h1_programs_url = "https://hackerone.com/directory/programs"
    
    def get_archived_programs(self):
        """Dapatkan daftar program dari arsip publik."""
        programs = []
        
        for archive_base in self.archive_urls:
            try:
                archive_url = f"{archive_base}/{self.h1_programs_url}"
                response = requests.get(archive_url, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    programs.extend(self._extract_programs_from_html(soup))
                    
            except Exception as e:
                print(f"⚠️ Failed to fetch from {archive_base}: {e}")
                continue
        
        return programs
    
    def _extract_programs_from_html(self, soup):
        """Ekstrak informasi program dari HTML."""
        programs = []
        
        # Cari elemen yang mengandung informasi program
        program_elements = soup.find_all(['div', 'a'], 
            class_=re.compile(r'(program|directory).*', re.IGNORECASE))
        
        for elem in program_elements:
            program_name = elem.get_text(strip=True)
            program_url = elem.get('href', '')
            
            if program_name and 'hackerone.com' in program_url:
                programs.append({
                    'name': program_name,
                    'url': program_url,
                    'platform': 'hackerone',
                    'discovery_method': 'archive_scraping'
                })
        
        return programs
    
    def detect_new_programs(self, existing_programs):
        """Deteksi program baru dibandingkan dengan daftar existing."""
        current_programs = self.get_archived_programs()
        new_programs = []
        
        existing_urls = {prog['url'] for prog in existing_programs}
        
        for program in current_programs:
            if program['url'] not in existing_urls:
                new_programs.append(program)
        
        return new_programs