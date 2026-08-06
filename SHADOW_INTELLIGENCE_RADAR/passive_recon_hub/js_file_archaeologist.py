import requests
from bs4 import BeautifulSoup
import re

class JSFileArchaeologist:
    """
    Wayback JS → API endpoints, logic flows.
    Menganalisis file JavaScript dari arsip Wayback Machine.
    """
    
    def __init__(self):
        self.wayback_url = "https://web.archive.org/web/"
    
    def get_wayback_js_files(self, target_url):
        """Dapatkan file JS dari arsip Wayback untuk target."""
        js_files = []
        
        try:
            # Dapatkan snapshot terbaru dari target
            snapshot_url = f"{self.wayback_url}*/{target_url}"
            response = requests.get(snapshot_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Temukan timestamp snapshot terbaru
                latest_snapshot = self._get_latest_snapshot(soup)
                
                if latest_snapshot:
                    # Dapatkan halaman lengkap dari snapshot tersebut
                    full_snapshot_url = f"{self.wayback_url}{latest_snapshot}/{target_url}"
                    full_response = requests.get(full_snapshot_url, timeout=10)
                    
                    if full_response.status_code == 200:
                        js_files.extend(self._extract_js_files(full_response.text, target_url))
        except Exception as e:
            print(f"⚠️ Wayback JS analysis failed: {e}")
        
        return js_files
    
    def _get_latest_snapshot(self, soup):
        """Dapatkan timestamp snapshot terbaru dari hasil Wayback."""
        # Cari link snapshot dengan timestamp
        snapshot_links = soup.find_all('a', href=re.compile(r'/web/\d+/.+'))
        if snapshot_links:
            # Ambil yang pertama (biasanya terbaru)
            href = snapshot_links[0].get('href')
            # Ekstrak timestamp (contoh: /web/20231201120000/...)
            match = re.search(r'/web/(\d+)/', href)
            if match:
                return match.group(1)
        return None
    
    def _extract_js_files(self, html_content, base_url):
        """Ekstrak file JS dari konten HTML."""
        js_files = []
        soup = BeautifulSoup(html_content, 'html.parser')
        script_tags = soup.find_all('script', src=True)
        
        for script in script_tags:
            src = script['src']
            if src.endswith('.js'):
                # Handle relative URLs
                if src.startswith('//'):
                    js_url = f"https:{src}"
                elif src.startswith('/'):
                    from urllib.parse import urljoin
                    js_url = urljoin(base_url, src)
                elif src.startswith('http'):
                    js_url = src
                else:
                    from urllib.parse import urljoin
                    js_url = urljoin(base_url, src)
                
                js_files.append(js_url)
        
        return js_files
    
    def analyze_js_for_endpoints(self, js_url):
        """Analisis file JS untuk mencari API endpoints."""
        endpoints = []
        
        try:
            response = requests.get(js_url, timeout=10)
            if response.status_code == 200:
                # Cari pola endpoint API dalam file JS
                content = response.text
                
                # Pola umum untuk endpoint API
                api_patterns = [
                    r'https?://[a-zA-Z0-9.-]*/api/[a-zA-Z0-9/_-]*',
                    r'/api/[a-zA-Z0-9/_-]*',
                    r'fetch\([\'"`](.*?)[\'"`]\)',
                    r'axios\.(get|post|put|delete)\([\'"`](.*?)[\'"`]\)'
                ]
                
                for pattern in api_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        if isinstance(match, tuple):
                            endpoint = match[-1]  # Ambil grup terakhir
                        else:
                            endpoint = match
                        
                        if endpoint and not endpoint.startswith(('http', 'https')):
                            # Endpoint relatif
                            endpoints.append(endpoint)
                        elif endpoint.startswith(('http', 'https')):
                            # Endpoint absolut
                            endpoints.append(endpoint)
        
        except Exception as e:
            print(f"⚠️ JS endpoint analysis failed for {js_url}: {e}")
        
        return list(set(endpoints))  # Remove duplicates