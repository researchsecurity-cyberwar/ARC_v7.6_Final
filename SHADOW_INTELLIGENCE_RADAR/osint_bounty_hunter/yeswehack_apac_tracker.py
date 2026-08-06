import requests
from bs4 import BeautifulSoup

class YesWeHackAPACTracker:
    """
    LATAM/APAC via public endpoints.
    Memantau program YesWeHack untuk wilayah APAC/LATAM.
    """
    
    def __init__(self):
        self.ywh_programs_url = "https://yeswehack.com/programs"
    
    def get_apac_programs(self):
        """Dapatkan program yang relevan untuk APAC/LATAM."""
        try:
            response = requests.get(self.ywh_programs_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                all_programs = self._extract_all_programs(soup)
                return self._filter_apac_latam_programs(all_programs)
        except Exception as e:
            print(f"⚠️ Failed to fetch YesWeHack programs: {e}")
        
        return []
    
    def _extract_all_programs(self, soup):
        """Ekstrak semua program dari halaman."""
        programs = []
        program_items = soup.find_all('div', class_=re.compile(r'.*program.*|.*item.*'))
        
        for item in program_items:
            name_elem = item.find(['h2', 'h3', 'span'])
            if name_elem:
                program_name = name_elem.get_text(strip=True)
                link_elem = item.find('a', href=True)
                if link_elem:
                    program_url = f"https://yeswehack.com{link_elem['href']}"
                    programs.append({
                        'name': program_name,
                        'url': program_url,
                        'platform': 'yeswehack'
                    })
        
        return programs
    
    def _filter_apac_latam_programs(self, programs):
        """Filter program berdasarkan wilayah APAC/LATAM."""
        apac_countries = ['indonesia', 'singapore', 'malaysia', 'thailand', 'vietnam', 'philippines']
        latam_countries = ['brazil', 'mexico', 'argentina', 'chile', 'colombia']
        
        filtered_programs = []
        for program in programs:
            program_lower = program['name'].lower()
            if any(country in program_lower for country in apac_countries + latam_countries):
                filtered_programs.append(program)
        
        return filtered_programs