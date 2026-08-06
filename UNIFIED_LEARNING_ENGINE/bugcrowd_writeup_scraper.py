import requests
from bs4 import BeautifulSoup
import json
import os
import time

class BugCrowdWriteupScraper:
    """
    BC disclosure reports.
    Mengambil laporan pengungkapan dari BugCrowd.
    """
    
    def __init__(self):
        self.bc_base_url = "https://bugcrowd.com"
        self.disclosures_url = "https://bugcrowd.com/disclosures"
    
    def scrape_disclosure_reports(self):
        """
        Scrap laporan pengungkapan dari BugCrowd.
        """
        try:
            # Gunakan pencarian Google sebagai fallback yang realistis
            search_url = "https://www.google.com/search?q=site:bugcrowd.com+disclosures+vulnerability+report"
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; ARC-AI-Agent/1.0)'
            }
            
            response = requests.get(search_url, headers=headers, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                reports = []
                
                # Cari link ke laporan BugCrowd
                links = soup.select('a[href*="bugcrowd.com/disclosures"]')
                for link in links[:10]:
                    title_elem = link.find('h3')
                    title = title_elem.text.strip() if title_elem else link.text.strip()[:80]
                    
                    if any(keyword in title.lower() for keyword in 
                          ['vulnerability', 'security', 'bug', 'exploit', 'xss', 'sqli', 'csrf']):
                        reports.append({
                            'title': title,
                            'url': link['href'],
                            'platform': 'bugcrowd',
                            'source': 'google_search_fallback'
                        })
                
                if reports:
                    timestamp = int(time.time())
                    writeup_file = os.path.join("~/.arc/writeups", f"bc_writeups_{timestamp}.json")
                    writeup_file = os.path.expanduser(writeup_file)
                    os.makedirs(os.path.dirname(writeup_file), exist_ok=True)
                    
                    with open(writeup_file, 'w') as f:
                        json.dump({'reports': reports}, f, indent=2)
                    return reports
            
            return []
        except Exception:
            return []