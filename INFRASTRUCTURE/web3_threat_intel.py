import requests
import json
import os
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

class Web3ThreatIntel:
    """
    Real-time Web3 threat intelligence from actually available public sources.
    Mengumpulkan intelijen ancaman Web3 hanya dari sumber yang benar-benar tersedia dan berguna.
    """
    
    def __init__(self, data_dir="~/.arc/web3_intel", tor_proxies=None):
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        self.tor_proxies = tor_proxies or {'http': 'socks5h://127.0.0.1:9050',
                                          'https': 'socks5h://127.0.0.1:9050'}
        # Hanya gunakan sumber yang benar-benar berfungsi
        self.sources = {
            'chainabuse_scam': 'https://chainabuse.com/reports',  # Satu-satunya sumber publik yang aktif
            'rekt_news': 'https://rekt.news/leaderboard/',        # Jika masih aktif (sering down)
            'immunefi_blog': 'https://immunefi.com/blog/'         # Ringkasan insiden resmi
        }
    
    def update_web3_threats(self, days_back: int = 7):
        """
        Perbarui intelijen ancaman Web3 dari sumber yang benar-benar tersedia.
        Fokus pada deteksi scam/pishing karena tidak ada sumber eksploitasi teknis publik.
        """
        results = {
            'chainabuse_scam_reports': None,
            'rekt_incidents': None,
            'immunefi_incident_summaries': None,
            'total_threats': 0,
            'success': False
        }
        
        try:
            # 1. Chainabuse (satu-satunya sumber publik yang konsisten)
            scam_file = self._scrape_chainabuse_scam(days_back)
            results['chainabuse_scam_reports'] = scam_file
            
            # 2. Rekt.news (jika tersedia - sering down atau lambat)
            rekt_file = self._scrape_rekt_news(days_back)
            results['rekt_incidents'] = rekt_file
            
            # 3. Immunefi Blog (ringkasan insiden resmi setelah bounty selesai)
            blog_file = self._scrape_immunefi_blog(days_back)
            results['immunefi_incident_summaries'] = blog_file
            
            results['success'] = True
            results['total_threats'] = self._count_web3_threats([
                scam_file, rekt_file, blog_file
            ])
        
        except Exception as e:
            results['error'] = f'Web3 threat update failed: {str(e)}'
        
        return results
    
    def _scrape_chainabuse_scam(self, days_back: int = 7):
        """Scrape laporan scam/pishing dari Chainabuse.com."""
        try:
            response = requests.get(
                self.sources['chainabuse_scam'],
                proxies=self.tor_proxies,
                timeout=30
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                reports = []
                
                # Ekstrak laporan scam (ini satu-satunya data yang tersedia)
                report_items = soup.select('div.report-item') or soup.select('article') or soup.select('tr')
                
                for item in report_items[:20]:
                    try:
                        title_elem = item.select_one('h3, h2, .title, a[href*="/report/"]')
                        title = title_elem.get_text().strip() if title_elem else "Unknown scam"
                        
                        blockchain_elem = item.select_one('.blockchain, .network, [data-network]')
                        blockchain = blockchain_elem.get_text().strip() if blockchain_elem else "Unknown"
                        
                        date_elem = item.select_one('.date, time, .created-at')
                        date_str = date_elem.get_text().strip() if date_elem else ""
                        
                        # Catatan penting: Ini HANYA laporan scam/pishing, BUKAN eksploitasi teknis
                        reports.append({
                            'title': title,
                            'blockchain': blockchain,
                            'date': date_str,
                            'type': 'scam_phishing',  # Bukan kerentanan teknis
                            'source': 'chainabuse',
                            'url': self.sources['chainabuse_scam']
                        })
                    except:
                        continue
                
                timestamp = int(time.time())
                report_file = os.path.join(self.data_dir, f"chainabuse_scam_{timestamp}.json")
                with open(report_file, 'w') as f:
                    json.dump({'reports': reports}, f, indent=2)
                
                return report_file
            else:
                raise Exception(f'Chainabuse returned {response.status_code}')
        
        except Exception as e:
            timestamp = int(time.time())
            error_file = os.path.join(self.data_dir, f"chainabuse_scam_{timestamp}.json")
            with open(error_file, 'w') as f:
                json.dump({
                    'error': f'Chainabuse scraping failed: {str(e)}',
                    'reports': [],
                    'note': 'Chainabuse only provides scam/phishing reports, not technical exploit details'
                }, f, indent=2)
            return error_file
    
    def _scrape_rekt_news(self, days_back: int = 7):
        """Scrape insiden DeFi dari Rekt.news (jika tersedia)."""
        try:
            response = requests.get(
                self.sources['rekt_news'],
                proxies=self.tor_proxies,
                timeout=30
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                incidents = []
                
                # Rekt.news sering down atau lambat, jadi handle dengan hati-hati
                incident_items = soup.select('div.incident') or soup.select('.project-card') or soup.select('tr')
                
                for item in incident_items[:10]:
                    try:
                        name_elem = item.select_one('.project-name, h3, h2')
                        project_name = name_elem.get_text().strip() if name_elem else "Unknown project"
                        
                        loss_elem = item.select_one('.loss, .amount')
                        loss_amount = loss_elem.get_text().strip() if loss_elem else "Unknown loss"
                        
                        incidents.append({
                            'project': project_name,
                            'loss_amount': loss_amount,
                            'type': 'defi_incident',
                            'source': 'rekt_news',
                            'url': self.sources['rekt_news']
                        })
                    except:
                        continue
                
                timestamp = int(time.time())
                incident_file = os.path.join(self.data_dir, f"rekt_incidents_{timestamp}.json")
                with open(incident_file, 'w') as f:
                    json.dump({'incidents': incidents}, f, indent=2)
                
                return incident_file
            else:
                # Rekt.news sering mengembalikan error, jadi ini normal
                timestamp = int(time.time())
                empty_file = os.path.join(self.data_dir, f"rekt_incidents_{timestamp}.json")
                with open(empty_file, 'w') as f:
                    json.dump({
                        'incidents': [],
                        'note': 'Rekt.news is often unavailable or slow to respond'
                    }, f, indent=2)
                return empty_file
        
        except Exception as e:
            timestamp = int(time.time())
            error_file = os.path.join(self.data_dir, f"rekt_incidents_{timestamp}.json")
            with open(error_file, 'w') as f:
                json.dump({
                    'error': f'Rekt.news scraping failed: {str(e)}',
                    'incidents': [],
                    'note': 'Rekt.news availability is unreliable'
                }, f, indent=2)
            return error_file
    
    def _scrape_immunefi_blog(self, days_back: int = 7):
        """Scrape ringkasan insiden dari blog Immunefi."""
        try:
            response = requests.get(
                self.sources['immunefi_blog'],
                proxies=self.tor_proxies,
                timeout=30
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                summaries = []
                
                # Cari posting blog tentang insiden keamanan
                post_items = soup.select('article.post') or soup.select('.blog-post') or soup.select('div.post')
                
                for item in post_items[:5]:  # Blog biasanya update jarang
                    try:
                        title_elem = item.select_one('h2, h3, .post-title')
                        title = title_elem.get_text().strip() if title_elem else "Security incident"
                        
                        # Hanya ambil posting yang relevan dengan keamanan
                        if any(keyword in title.lower() for keyword in ['exploit', 'vulnerability', 'security', 'incident']):
                            date_elem = item.select_one('time, .post-date')
                            date_str = date_elem.get_text().strip() if date_elem else ""
                            
                            summaries.append({
                                'title': title,
                                'date': date_str,
                                'type': 'incident_summary',
                                'source': 'immunefi_blog',
                                'url': self.sources['immunefi_blog']
                            })
                    except:
                        continue
                
                timestamp = int(time.time())
                blog_file = os.path.join(self.data_dir, f"immunefi_blog_{timestamp}.json")
                with open(blog_file, 'w') as f:
                    json.dump({'summaries': summaries}, f, indent=2)
                
                return blog_file
            else:
                # Blog Immunefi mungkin tidak selalu memiliki konten baru
                timestamp = int(time.time())
                empty_file = os.path.join(self.data_dir, f"immunefi_blog_{timestamp}.json")
                with open(empty_file, 'w') as f:
                    json.dump({
                        'summaries': [],
                        'note': 'Immunefi blog may not have recent security incident summaries'
                    }, f, indent=2)
                return empty_file
        
        except Exception as e:
            timestamp = int(time.time())
            error_file = os.path.join(self.data_dir, f"immunefi_blog_{timestamp}.json")
            with open(error_file, 'w') as f:
                json.dump({
                    'error': f'Immunefi blog scraping failed: {str(e)}',
                    'summaries': [],
                    'note': 'Immunefi blog provides official incident summaries after bounty completion'
                }, f, indent=2)
            return error_file
    
    def _count_web3_threats(self, file_paths: list) -> int:
        """Hitung total ancaman Web3 dari file-file yang diberikan."""
        total = 0
        for file_path in file_paths:
            if file_path and os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        if 'reports' in data:
                            total += len(data['reports'])
                        elif 'incidents' in data:
                            total += len(data['incidents'])
                        elif 'summaries' in data:
                            total += len(data['summaries'])
                except:
                    continue
        return total
    
    def get_latest_web3_threats(self):
        """
        Dapatkan data ancaman Web3 terbaru yang tersedia.
        """
        # Chainabuse adalah satu-satunya sumber yang konsisten
        chainabuse_files = [f for f in os.listdir(self.data_dir) if f.startswith('chainabuse_scam_')]
        if chainabuse_files:
            latest_file = max(chainabuse_files, key=lambda x: int(x.split('_')[-1].replace('.json', '')))
            with open(os.path.join(self.data_dir, latest_file), 'r') as f:
                return json.load(f)
        
        # Fallback ke sumber lain jika Chainabuse gagal
        rekt_files = [f for f in os.listdir(self.data_dir) if f.startswith('rekt_incidents_')]
        if rekt_files:
            latest_file = max(rekt_files, key=lambda x: int(x.split('_')[-1].replace('.json', '')))
            with open(os.path.join(self.data_dir, latest_file), 'r') as f:
                return json.load(f)
        
        return {'reports': [], 'incidents': [], 'summaries': []}