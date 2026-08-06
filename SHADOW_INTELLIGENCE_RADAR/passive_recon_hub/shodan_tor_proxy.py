import requests

class ShodanTorProxy:
    """
    Shodan via Tor (no account, country-filtered).
    Mengakses Shodan melalui Tor tanpa memerlukan akun.
    """
    
    def __init__(self):
        self.shodan_search_url = "https://www.shodan.io/search"
        self.tor_proxies = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }
    
    def search_shodan_via_tor(self, query, country_code=None):
        """
        Cari di Shodan melalui Tor (tanpa API key).
        """
        if country_code:
            query += f" country:{country_code}"
        
        try:
            # Gunakan Tor untuk anonimitas
            response = requests.get(
                self.shodan_search_url,
                params={'q': query},
                proxies=self.tor_proxies,
                timeout=15
            )
            
            if response.status_code == 200:
                return self._parse_shodan_results(response.text)
            else:
                print(f"⚠️ Shodan search returned status {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Shodan Tor search failed: {e}")
        
        return []
    
    def _parse_shodan_results(self, html_content):
        """Parse hasil pencarian Shodan dari HTML."""
        results = []
        # Ini adalah implementasi dasar - parsing HTML Shodan bisa kompleks
        # Untuk OSINT-only, kita fokus pada ekstraksi IP dasar
        
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        ips = re.findall(ip_pattern, html_content)
        
        for ip in ips[:10]:  # Batasi untuk OSINT
            results.append({
                'ip': ip,
                'source': 'shodan_tor',
                'query_type': 'osint'
            })
        
        return results
    
    def is_tor_running(self):
        """Cek apakah Tor service sedang berjalan."""
        try:
            response = requests.get('https://check.torproject.org/api/ip', 
                                  proxies=self.tor_proxies, timeout=5)
            return response.json().get('IsTor', False)
        except:
            return False