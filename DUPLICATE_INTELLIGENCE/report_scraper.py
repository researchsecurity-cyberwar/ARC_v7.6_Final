import requests
from bs4 import BeautifulSoup
import json
import os
import time

class ReportScraper:
    """
    Scrap laporan publik dari semua platform.
    Mengumpulkan laporan publik dari platform bug bounty dan blog keamanan.
    """
    
    def __init__(self, reports_dir="~/.arc/reports"):
        self.reports_dir = os.path.expanduser(reports_dir)
        os.makedirs(self.reports_dir, exist_ok=True)
        # Platform yang benar-benar menyediakan laporan publik
        self.public_sources = {
            'immunefi_blog': 'https://immunefi.com/blog/',
            'hackerone_hacktivity': 'https://hackerone.com/hacktivity',
            'bugcrowd_disclosures': 'https://bugcrowd.com/disclosures',
            'intigriti_reports': 'https://www.intigriti.com/researcher/reports',
            'github_security': 'https://api.github.com/search/repositories'
        }
    
    def scrape_public_reports(self):
        """
        Scrap laporan publik dari semua sumber yang tersedia.
        """
        results = {
            'immunefi_reports': None,
            'hackerone_reports': None,
            'bugcrowd_reports': None,
            'intigriti_reports': None,
            'github_reports': None,
            'total_reports': 0,
            'scraping_successful': False
        }
        
        try:
            # Scrap Immunefi Blog (satu-satunya sumber yang pasti berfungsi)
            immunefi_reports = self._scrape_immunefi_blog()
            results['immunefi_reports'] = immunefi_reports
            
            # Scrap GitHub Security Repositories
            github_reports = self._scrape_github_security()
            results['github_reports'] = github_reports
            
            # Coba sumber lain jika memungkinkan
            hackerone_reports = self._scrape_hackerone_hacktivity()
            results['hackerone_reports'] = hackerone_reports
            
            bugcrowd_reports = self._scrape_bugcrowd_disclosures()
            results['bugcrowd_reports'] = bugcrowd_reports
            
            intigriti_reports = self._scrape_intigriti_reports()
            results['intigriti_reports'] = intigriti_reports
            
            total = len(immunefi_reports or []) + len(github_reports or []) + \
                   len(hackerone_reports or []) + len(bugcrowd_reports or []) + \
                   len(intigriti_reports or [])
            results['total_reports'] = total
            results['scraping_successful'] = True
        
        except Exception as e:
            results['error'] = f'Report scraping failed: {str(e)}'
        
        return results
    
    def _scrape_immunefi_blog(self):
        """Scrap laporan dari blog Immunefi."""
        try:
            response = requests.get(self.public_sources['immunefi_blog'], timeout=30)
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
                        reports.append({
                            'title': title_elem.text.strip(),
                            'date': date_elem.text.strip() if date_elem else '',
                            'source': 'immunefi_blog',
                            'url': self.public_sources['immunefi_blog']
                        })
                
                if reports:
                    timestamp = int(time.time())
                    report_file = os.path.join(self.reports_dir, f"immunefi_blog_{timestamp}.json")
                    with open(report_file, 'w') as f:
                        json.dump({'reports': reports}, f, indent=2)
                    return reports
            
            return []
        except:
            return []
    
    def _scrape_github_security(self):
        """Scrap repositori keamanan dari GitHub."""
        try:
            query = "CTF writeup language:markdown pushed:>2026-07-01"
            params = {'q': query, 'sort': 'updated', 'order': 'desc', 'per_page': 10}
            
            response = requests.get(
                self.public_sources['github_security'],
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                repos = []
                
                for item in data.get('items', [])[:10]:
                    repos.append({
                        'title': item.get('name', ''),
                        'description': item.get('description', ''),
                        'url': item.get('html_url', ''),
                        'source': 'github_security'
                    })
                
                if repos:
                    timestamp = int(time.time())
                    github_file = os.path.join(self.reports_dir, f"github_security_{timestamp}.json")
                    with open(github_file, 'w') as f:
                        json.dump({'repositories': repos}, f, indent=2)
                    return repos
            
            return []
        except:
            return []
    
    def _scrape_hackerone_hacktivity(self):
        """Scrap HackerOne Hacktivity (fallback ke pencarian)."""
        try:
            # Gunakan pencarian Google sebagai fallback
            search_url = "https://www.google.com/search?q=site:hackerone.com+hacktivity+vulnerability"
            response = requests.get(search_url, timeout=30)
            
            if response.status_code == 200:
                # Ekstrak hasil pencarian
                soup = BeautifulSoup(response.text, 'html.parser')
                results = []
                
                # Cari link ke laporan HackerOne
                links = soup.select('a[href*="hackerone.com/report"]')
                for link in links[:5]:
                    results.append({
                        'title': link.text.strip()[:100],
                        'url': link['href'],
                        'source': 'hackerone_hacktivity'
                    })
                
                return results
            return []
        except:
            return []
    
    def _scrape_bugcrowd_disclosures(self):
        """Scrap Bugcrowd Disclosures (fallback ke pencarian)."""
        try:
            search_url = "https://www.google.com/search?q=site:bugcrowd.com+disclosures+vulnerability"
            response = requests.get(search_url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                results = []
                
                links = soup.select('a[href*="bugcrowd.com/disclosures"]')
                for link in links[:5]:
                    results.append({
                        'title': link.text.strip()[:100],
                        'url': link['href'],
                        'source': 'bugcrowd_disclosures'
                    })
                
                return results
            return []
        except:
            return []
    
    def _scrape_intigriti_reports(self):
        """Scrap Intigriti Reports (fallback ke pencarian)."""
        try:
            search_url = "https://www.google.com/search?q=site:intigriti.com+reports+vulnerability"
            response = requests.get(search_url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                results = []
                
                links = soup.select('a[href*="intigriti.com/researcher/reports"]')
                for link in links[:5]:
                    results.append({
                        'title': link.text.strip()[:100],
                        'url': link['href'],
                        'source': 'intigriti_reports'
                    })
                
                return results
            return []
        except:
            return []