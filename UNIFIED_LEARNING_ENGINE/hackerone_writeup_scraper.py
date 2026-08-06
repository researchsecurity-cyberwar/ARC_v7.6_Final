import requests
from bs4 import BeautifulSoup
import json
import os
import time

class HackerOneWriteupScraper:
    """
    H1 public reports.
    Mengambil laporan publik dari HackerOne Hacktivity.
    """
    
    def __init__(self):
        self.h1_base_url = "https://hackerone.com"
        self.hacktivity_url = "https://hackerone.com/hacktivity"
    
    def scrape_public_reports(self):
        """
        Scrap laporan publik dari HackerOne Hacktivity.
        """
        try:
            # Gunakan pencarian Google sebagai fallback yang realistis
            search_url = "https://www.google.com/search?q=site:hackerone.com+hacktivity+vulnerability+report"
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; ARC-AI-Agent/1.0)'
            }
            
            response = requests.get(search_url, headers=headers, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                reports = []
                
                # Cari link ke laporan HackerOne
                links = soup.select('a[href*="hackerone.com/report"]')
                for link in links[:10]:  # Batasi 10 laporan
                    title_elem = link.find('h3')
                    title = title_elem.text.strip() if title_elem else link.text.strip()[:80]
                    
                    if any(keyword in title.lower() for keyword in 
                          ['vulnerability', 'security', 'bug', 'exploit', 'xss', 'sqli', 'csrf']):
                        reports.append({
                            'title': title,
                            'url': link['href'],
                            'platform': 'hackerone',
                            'source': 'google_search_fallback'
                        })
                
                if reports:
                    timestamp = int(time.time())
                    writeup_file = os.path.join("~/.arc/writeups", f"h1_writeups_{timestamp}.json")
                    writeup_file = os.path.expanduser(writeup_file)
                    os.makedirs(os.path.dirname(writeup_file), exist_ok=True)
                    
                    with open(writeup_file, 'w') as f:
                        json.dump({'reports': reports}, f, indent=2)
                    return reports
            
            return []
        except Exception:
            return []