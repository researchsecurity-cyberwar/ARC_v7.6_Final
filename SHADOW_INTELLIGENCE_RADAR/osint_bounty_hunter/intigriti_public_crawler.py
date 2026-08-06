import requests
from bs4 import BeautifulSoup

class IntigritiPublicCrawler:
    """
    EU program monitoring (no login required).
    Memantau program publik Intigriti tanpa memerlukan akun.
    """
    
    def __init__(self):
        self.intigriti_public_url = "https://www.intigriti.com/explore"
    
    def get_public_programs(self):
        """Dapatkan daftar program publik dari Intigriti."""
        try:
            response = requests.get(self.intigriti_public_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                return self._extract_program_info(soup)
        except Exception as e:
            print(f"⚠️ Failed to fetch Intigriti programs: {e}")
        
        return []
    
    def _extract_program_info(self, soup):
        """Ekstrak informasi program dari halaman Explore."""
        programs = []
        
        # Cari card program
        program_cards = soup.find_all('div', class_=re.compile(r'.*card.*|.*program.*', re.IGNORECASE))
        
        for card in program_cards:
            program_name_elem = card.find(['h2', 'h3', 'div'], 
                string=re.compile(r'.*', re.IGNORECASE))
            
            if program_name_elem:
                program_name = program_name_elem.get_text(strip=True)
                # Cari link program
                program_link = card.find('a', href=re.compile(r'/company/.*'))
                
                if program_link:
                    program_url = f"https://www.intigriti.com{program_link.get('href')}"
                    programs.append({
                        'name': program_name,
                        'url': program_url,
                        'platform': 'intigriti',
                        'region': 'eu'
                    })
        
        return programs