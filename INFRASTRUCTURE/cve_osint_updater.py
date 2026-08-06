import requests
import json
import os
import time
import zipfile
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional

# Tambahkan import ConfigLoader untuk dukungan config.yaml
try:
    from SOVEREIGN_SESSION_MANAGER.config_loader import get_config_loader
except ImportError:
    def get_config_loader():
        return None


class CVEOSINTUpdater:
    """
    Real-time threat intelligence from NVD + MITRE CWE.
    Mendukung NVD API key untuk rate limit lebih tinggi dan fallback tanpa Tor.
    """
    
    def __init__(self, data_dir="~/.arc/osint", tor_proxies=None, nvd_api_key=None):
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        self.tor_proxies = tor_proxies
        
        # NVD API key dari: parameter > env var > config.yaml
        config_loader = get_config_loader()
        config_nvd_key = None
        if config_loader:
            config_nvd_key = config_loader.get_api_key('nvd')
        
        self.nvd_api_key = nvd_api_key or os.environ.get('NVD_API_KEY') or config_nvd_key
        self.nvd_base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        self.cwe_xml_url = "https://cwe.mitre.org/data/xml/cwec_v4.12.xml.zip"
    
    def _get_proxies(self) -> Optional[Dict[str, str]]:
        """Gunakan Tor proxy hanya jika tersedia, fallback ke direct connection."""
        if self.tor_proxies:
            return self.tor_proxies
        return None
    
    def _get_headers(self) -> Dict[str, str]:
        """Headers dengan NVD API key jika tersedia."""
        headers = {'User-Agent': 'ARC-Security-Agent/7.6'}
        if self.nvd_api_key:
            headers['apiKey'] = self.nvd_api_key
        return headers
    
    def update_realtime_threats(self, days_back: int = 7) -> Dict[str, Any]:
        """
        Perbarui intelijen ancaman dari sumber yang berfungsi.
        """
        results = {
            'nvd_data': None,
            'cwe_data': None,
            'total_threats': 0,
            'success': False
        }
        
        try:
            # 1. NVD (sumber utama)
            nvd_file = self.update_nvd_data(days_back)
            results['nvd_data'] = nvd_file
            
            # 2. MITRE CWE (referensi bulanan)
            cwe_file = self.update_cwe_feed()
            results['cwe_data'] = cwe_file
            
            results['success'] = True
            results['total_threats'] = self._count_total_threats([nvd_file])
        
        except Exception as e:
            results['error'] = f'Threat update failed: {str(e)}'
        
        return results
    
    def update_nvd_data(self, days_back: int = 7) -> str:
        """
        Perbarui data CVE dari NVD API.
        """
        try:
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            
            query_params = f"pubStartDate={start_date}T00:00:00.000&pubEndDate={end_date}T23:59:59.999"
            full_url = f"{self.nvd_base_url}?{query_params}"
            
            response = requests.get(
                full_url,
                proxies=self._get_proxies(),
                headers=self._get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                cve_data = response.json()
                
                timestamp = int(time.time())
                cve_file = os.path.join(self.data_dir, f"nvd_cves_{timestamp}.json")
                with open(cve_file, 'w') as f:
                    json.dump(cve_data, f, indent=2)
                
                return cve_file
            else:
                raise Exception(f'NVD API returned {response.status_code}')
        
        except Exception as e:
            raise Exception(f'NVD data update failed: {str(e)}')
    
    def update_cwe_feed(self) -> str:
        """
        Perbarui feed CWE dari MITRE.
        """
        try:
            response = requests.get(
                self.cwe_xml_url,
                proxies=self._get_proxies(),
                headers=self._get_headers(),
                timeout=60
            )
            
            if response.status_code == 200:
                zip_path = os.path.join(self.data_dir, "cwec_v4.12.xml.zip")
                with open(zip_path, 'wb') as f:
                    f.write(response.content)
                
                xml_file = os.path.join(self.data_dir, "cwec_v4.12.xml")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.data_dir)
                
                json_file = os.path.join(self.data_dir, f"cwe_{int(time.time())}.json")
                self._convert_cwe_xml_to_json(xml_file, json_file)
                
                return json_file
            else:
                raise Exception(f'CWE download failed: {response.status_code}')
        
        except Exception as e:
            raise Exception(f'CWE feed update failed: {str(e)}')
    
    def _convert_cwe_xml_to_json(self, xml_file: str, json_file: str):
        """Konversi file XML CWE ke format JSON."""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            namespace = {'cwe': 'http://cwe.mitre.org/cwe-6'}
            
            cwe_list = []
            for weakness in root.findall('.//cwe:Weakness', namespace):
                cwe_id = weakness.get('ID')
                name = weakness.get('Name')
                description_elem = weakness.find('.//cwe:Description', namespace)
                description = description_elem.text if description_elem is not None else ""
                
                cwe_list.append({
                    'id': f"CWE-{cwe_id}",
                    'name': name,
                    'description': description
                })
            
            with open(json_file, 'w') as f:
                json.dump({'weaknesses': cwe_list}, f, indent=2)
                
        except Exception as e:
            with open(json_file, 'w') as f:
                json.dump({
                    'error': f'CWE XML to JSON conversion failed: {str(e)}',
                    'weaknesses': []
                }, f, indent=2)
    
    def _count_total_threats(self, file_paths: list) -> int:
        """Hitung total ancaman dari file-file yang diberikan."""
        total = 0
        for file_path in file_paths:
            if file_path and os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        if 'vulnerabilities' in data:
                            total += len(data['vulnerabilities'])
                except:
                    continue
        return total
    
    def get_latest_threat_data(self) -> Optional[Dict[str, Any]]:
        """Dapatkan data ancaman terbaru yang tersedia."""
        nvd_files = [f for f in os.listdir(self.data_dir) if f.startswith('nvd_cves_')]
        if nvd_files:
            latest_file = max(nvd_files, key=lambda x: int(x.split('_')[-1].replace('.json', '')))
            with open(os.path.join(self.data_dir, latest_file), 'r') as f:
                return json.load(f)
        return None
    
    def get_latest_cwe_data(self) -> Optional[Dict[str, Any]]:
        """Dapatkan data CWE terbaru yang tersedia."""
        cwe_files = [f for f in os.listdir(self.data_dir) if f.startswith('cwe_')]
        if cwe_files:
            latest_file = max(cwe_files, key=lambda x: int(x.split('_')[-1].replace('.json', '')))
            with open(os.path.join(self.data_dir, latest_file), 'r') as f:
                return json.load(f)
        return None