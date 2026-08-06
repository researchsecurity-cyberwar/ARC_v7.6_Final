import requests
from bs4 import BeautifulSoup
import json
import os
import time

class ImmunefiWriteupScraper:
    """
    Immunefi write-ups.
    Mengambil write-up dari blog Immunefi.
    """
    
    def __init__(self):
        self.immunefi_blog_url = "https://immunefi.com/blog/"
    
    def scrape_blog_writeups(self):
        """
        Scrap write-up dari blog Immunefi.
        """
        try:
            response = requests.get(self.immunefi_blog_url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                reports = []
                
                # Cari posting blog tentang insiden keamanan
                post_items = soup.select('article.post') or soup.select('.blog-post')
                
                for item in post_items[:10]:
                    title_elem = item.select_one('h2, h3, .post-title')
                    if title_elem and any(keyword in title_elem.text.lower() 
                                        for keyword in ['exploit', 'vulnerability', 'security', 'incident']):
                        date_elem = item.select_one('time, .post-date')
                        content_elem = item.select_one('.post-content, .entry-content')
                        
                        reports.append({
                            'title': title_elem.text.strip(),
                            'date': date_elem.text.strip() if date_elem else '',
                            'content_preview': content_elem.text[:500] if content_elem else '',
                            'url': self.immunefi_blog_url,
                            'platform': 'immunefi',
                            'source': 'direct_scraping'
                        })
                
                if reports:
                    timestamp = int(time.time())
                    writeup_file = os.path.join("~/.arc/writeups", f"immunefi_writeups_{timestamp}.json")
                    writeup_file = os.path.expanduser(writeup_file)
                    os.makedirs(os.path.dirname(writeup_file), exist_ok=True)
                    
                    with open(writeup_file, 'w') as f:
                        json.dump({'reports': reports}, f, indent=2)
                    return reports
            
            return []
        except Exception:
            return []