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
        # Sumber CWE: pakai "latest" dinamis dulu, fallback ke versi hardcoded yang sudah terbukti ada
        self.cwe_xml_url = "https://cwe.mitre.org/data/xml/cwec_latest.xml.zip"
        self.cwe_xml_url_fallback = "https://cwe.mitre.org/data/xml/cwec_v4.12.xml.zip"
        # CWE feed dirilis bulanan -> cache JSON dipakai ulang selama masih dalam masa TTL
        self.cwe_cache_ttl_days = 30
    
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
        
        # NVD dan CWE ditangani INDEPENDEN supaya satu gagal
        # (mis. rate-limit NVD tanpa API key) tidak menggagalkan yang lain.
        nvd_file = None
        nvd_success, cwe_success = False, False
        
        # 1. NVD (sumber utama)
        try:
            nvd_file = self.update_nvd_data(days_back)
            results['nvd_data'] = nvd_file
            nvd_success = True
        except Exception as e:
            results['nvd_error'] = str(e)
            print(f"⚠️ NVD update failed (tetap lanjut ke CWE): {e}")
        
        # 2. MITRE CWE (referensi bulanan) - auto-download zip bila belum ada
        try:
            cwe_file = self.update_cwe_feed()
            results['cwe_data'] = cwe_file
            cwe_success = True
        except Exception as e:
            results['cwe_error'] = str(e)
            print(f"⚠️ CWE update failed: {e}")
        
        results['success'] = nvd_success or cwe_success
        results['total_threats'] = self._count_total_threats([nvd_file] if nvd_file else [])
        
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
    
    def update_cwe_feed(self, force: bool = False) -> str:
        """
        Update feed CWE dari MITRE.
        - Auto-download ZIP -> extract XML -> konversi ke JSON.
        - Jika ada cache JSON yang masih segar (< cwe_cache_ttl_days) dipakai ulang
          (CWE feed dirilis bulanan, hindari download ulang ~30MB tiap run).
        - force=True memaksa download ulang.
        Mengembalikan path file JSON, atau raise bila semua sumber gagal & tak ada cache.
        """
        # 1) Pakai cache segar bila ada
        cached = self._get_fresh_cwe_cache()
        if cached and not force:
            print(f"♻️ CWE feed memakai cache segar: {cached}")
            return cached

        # 2) Coba unduh dari daftar URL (utama 'latest' + fallback versi terverifikasi)
        urls = [self.cwe_xml_url, self.cwe_xml_url_fallback]
        last_error = None
        for url in urls:
            try:
                return self._download_cwe_from(url)
            except Exception as e:
                last_error = e
                print(f"⚠️ CWE download gagal dari {url}: {e}")

        # 3) Semua sumber gagal -> pakai cache stale terakhir jika masih ada
        stale = self._get_latest_cwe_json_path()
        if stale:
            print(f"⚠️ Semua sumber CWE gagal, memakai data cache lama: {stale}")
            return stale

        raise Exception(f"CWE feed update failed - semua sumber gagal: {last_error}")

    def _download_cwe_from(self, url: str) -> str:
        """Unduh ZIP CWE dari satu URL, extract XML secara aman, konversi ke JSON."""
        print(f"⬇️ Downloading CWE feed: {url}")
        response = requests.get(
            url,
            proxies=self._get_proxies(),
            headers=self._get_headers(),
            timeout=120
        )
        if response.status_code != 200:
            raise Exception(f'CWE download failed: {response.status_code}')

        # Validasi magic bytes ZIP ("PK") agar file rusak/halaman HTML ikut diekstrak
        if response.content[:2] != b'PK':
            raise Exception('Respon bukan file ZIP (magic bytes tidak valid)')

        timestamp = int(time.time())
        zip_path = os.path.join(self.data_dir, f"cwec_{timestamp}.zip")
        with open(zip_path, 'wb') as f:
            f.write(response.content)

        # Extract file XML secara aman (cegah Zip Slip / path traversal)
        xml_file = None
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                if (member.lower().endswith('.xml') and not member.startswith('/')
                        and '..' not in member):
                    safe_name = os.path.basename(member)
                    if not safe_name:
                        continue
                    xml_file = os.path.join(self.data_dir, safe_name)
                    with zip_ref.open(member) as src, open(xml_file, 'wb') as dst:
                        dst.write(src.read())
                    break

        os.remove(zip_path)  # bersihkan zip setelah dipakai

        if not xml_file or not os.path.exists(xml_file):
            raise Exception('File XML tidak ditemukan di dalam ZIP CWE')

        json_file = os.path.join(self.data_dir, f"cwe_{timestamp}.json")
        self._convert_cwe_xml_to_json(xml_file, json_file)
        return json_file

    def _get_fresh_cwe_cache(self) -> Optional[str]:
        """Path JSON CWE terbaru jika usianya masih dalam masa TTL, else None."""
        path = self._get_latest_cwe_json_path()
        if not path:
            return None
        age_days = (time.time() - os.path.getmtime(path)) / 86400.0
        if age_days <= self.cwe_cache_ttl_days:
            return path
        return None

    def _get_latest_cwe_json_path(self) -> Optional[str]:
        """Path file JSON CWE paling baru (tanpa memandang umur), else None."""
        try:
            cwe_files = [f for f in os.listdir(self.data_dir)
                         if f.startswith('cwe_') and f.endswith('.json')]
        except OSError:
            return None
        if not cwe_files:
            return None
        latest_file = max(
            cwe_files,
            key=lambda f: os.path.getmtime(os.path.join(self.data_dir, f))
        )
        return os.path.join(self.data_dir, latest_file)
    
    def _convert_cwe_xml_to_json(self, xml_file: str, json_file: str):
        """Konversi file XML CWE ke format JSON (namespace-agnostic)."""
        cwe_list = []
        error_msg = None
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            # Wildcard '{*}Weakness' bekerja untuk semua versi XML CWE
            # ({http://cwe.mitre.org/cwe-6} ataupun namespace https sekalipun)
            for weakness in root.findall('.//{*}Weakness'):
                cwe_id = weakness.get('ID')
                name = weakness.get('Name')
                description = ""
                desc_elem = weakness.find('{*}Description')
                if desc_elem is not None and desc_elem.text:
                    description = desc_elem.text.strip()
                cwe_list.append({
                    'id': f"CWE-{cwe_id}",
                    'name': name,
                    'description': description[:1000]
                })
            if not cwe_list:
                error_msg = 'Tidak ada entri Weakness ditemukan (format XML berubah?)'
        except Exception as e:
            error_msg = str(e)

        data = {'weaknesses': cwe_list}
        if error_msg:
            data['error'] = error_msg
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
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
        """
        Ambil data CWE terbaru yang tersedia.
        LAZY AUTO-DOWNLOAD: jika belum ada data JSON, otomatis download CWE.
        Jika offline/gagal total, fallback ke XML lama yang tersisa di data_dir.
        Jika cache JSON rusak / kosong (0 weaknesses), force re-download.
        """
        # 1) Coba file JSON yang sudah ada
        path = self._get_latest_cwe_json_path()
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Jika cache valid (ada weaknesses dan tidak kosong), pakai
                if data.get('weaknesses') and len(data['weaknesses']) > 0:
                    return data
                # Cache rusak/kosong -> lanjut ke re-download di bawah
            except Exception:
                pass

        # 2) Cache kosong/rusak -> auto-download sendiri (force=True)
        try:
            path = self.update_cwe_feed(force=True)
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data.get('weaknesses'):
                return data
        except Exception as e:
            print(f"⚠️ CWE auto-download gagal: {e}")

        # 3) Fallback terakhir: konversi XML lama yang mungkin masih ada di data_dir
        try:
            for xf in sorted(os.listdir(self.data_dir), reverse=True):
                if xf.lower().endswith('.xml'):
                    xml_file = os.path.join(self.data_dir, xf)
                    json_file = os.path.join(self.data_dir, f"cwe_{int(time.time())}.json")
                    self._convert_cwe_xml_to_json(xml_file, json_file)
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    if data.get('weaknesses'):
                        return data
        except Exception:
            pass

        return None