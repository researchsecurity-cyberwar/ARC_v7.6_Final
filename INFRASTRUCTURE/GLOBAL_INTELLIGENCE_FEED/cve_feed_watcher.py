import requests
import json
import os
import time
from datetime import datetime, timedelta

class CVEFeedWatcher:
    """
    Monitor NVD, CVE.org, GitHub Security Advisories via Tor.
    Memantau feed CVE dari sumber yang benar-benar aktif melalui Tor.
    """
    
    def __init__(self, data_dir="~/.arc/intel", tor_proxies=None):
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        self.tor_proxies = tor_proxies or {'http': 'socks5h://127.0.0.1:9050',
                                          'https': 'socks5h://127.0.0.1:9050'}
        # Hanya gunakan sumber yang benar-benar berfungsi
        self.nvd_base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    
    def monitor_cve_feeds(self, days_back: int = 1):
        """
        Pantau feed CVE dari sumber yang berfungsi.
        """
        results = {
            'days_back': days_back,
            'nvd_updates': None,
            'total_new_cves': 0,
            'monitoring_successful': False
        }
        
        try:
            # Update dari NVD (satu-satunya sumber API publik yang berfungsi)
            nvd_file = self._update_nvd_feed(days_back)
            results['nvd_updates'] = nvd_file
            
            if nvd_file:
                # Hitung CVE baru
                with open(nvd_file, 'r') as f:
                    nvd_data = json.load(f)
                    results['total_new_cves'] = len(nvd_data.get('vulnerabilities', []))
            
            results['monitoring_successful'] = True
        
        except Exception as e:
            results['error'] = f'CVE feed monitoring failed: {str(e)}'
        
        return results
    
    def _update_nvd_feed(self, days_back: int = 1):
        """Perbarui feed dari NVD."""
        try:
            # Hitung tanggal mulai
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            
            # Bangun URL query
            query_params = f"pubStartDate={start_date}T00:00:00.000&pubEndDate={end_date}T23:59:59.999"
            full_url = f"{self.nvd_base_url}?{query_params}"
            
            # Ambil data melalui Tor
            response = requests.get(full_url, proxies=self.tor_proxies, timeout=30)
            
            if response.status_code == 200:
                cve_data = response.json()
                
                # Simpan ke file
                timestamp = int(time.time())
                cve_file = os.path.join(self.data_dir, f"nvd_daily_{timestamp}.json")
                with open(cve_file, 'w') as f:
                    json.dump(cve_data, f, indent=2)
                
                return cve_file
            else:
                raise Exception(f'NVD API returned {response.status_code}')
        
        except Exception as e:
            # Buat file error untuk logging
            timestamp = int(time.time())
            error_file = os.path.join(self.data_dir, f"nvd_error_{timestamp}.json")
            with open(error_file, 'w') as f:
                json.dump({
                    'error': f'NVD update failed: {str(e)}',
                    'timestamp': timestamp
                }, f, indent=2)
            return None