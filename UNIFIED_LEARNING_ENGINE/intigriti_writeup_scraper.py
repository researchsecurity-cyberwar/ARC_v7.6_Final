import requests
from bs4 import BeautifulSoup
import json
import os
import time

class IntigritiWriteupScraper:
    """
    Intigriti public write-ups.
    Mengambil write-up publik dari Intigriti.
    """
    
    def __init__(self):
        self.intigriti_base_url = "https://www.intigriti.com"
        self.reports_url = "https://www.intigriti.com/researcher/reports"
    
    def scrape_public_writeups(self):
        """
        Scrap write-up publik dari Intigriti.
        """
        try:
            # Gunakan pencarian Google sebagai fallback yang realistis
            search_url = "https://www.google.com/search?q=site:intigriti.com+reports+vulnerability+writeup"
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; ARC-AI-Agent/1.0)'
            }
            
            response = requests.get(search_url, headers=headers, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                reports = []
                
                # Cari link ke laporan Intigriti
                links = soup.select('a[href*="intigriti.com/researcher/reports"]')
                for link in links[:10]:
                    title_elem = link.find('h3')
                    title = title_elem.text.strip() if title_elem else link.text.strip()[:80]
                    
                    if any(keyword in title.lower() for keyword in 
                          ['vulnerability', 'security', 'bug', 'exploit', 'xss', 'sqli', 'csrf']):
                        reports.append({
                            'title': title,
                            'url': link['href'],
                            'platform': 'intigriti',
                            'source': 'google_search_fallback'
                        })
                
                if reports:
                    timestamp = int(time.time())
                    writeup_file = os.path.join("~/.arc/writeups", f"intigriti_writeups_{timestamp}.json")
                    writeup_file = os.path.expanduser(writeup_file)
                    os.makedirs(os.path.dirname(writeup_file), exist_ok=True)
                    
                    with open(writeup_file, 'w') as f:
                        json.dump({'reports': reports}, f, indent=2)
                    return reports
            
            return []
        except Exception:
            return []