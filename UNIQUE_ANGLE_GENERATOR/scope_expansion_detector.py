import subprocess
import requests
from urllib.parse import urlparse

class ScopeExpansionDetector:
    """
    Find affected subdomains/services.
    Menemukan subdomain dan layanan tambahan yang terdampak.
    """
    
    def __init__(self, recon_dir="~/.arc/recon"):
        self.recon_dir = os.path.expanduser(recon_dir)
        os.makedirs(self.recon_dir, exist_ok=True)
    
    def detect_expanded_scope(self, initial_target: str):
        """
        Deteksi cakupan yang diperluas dari target awal.
        """
        results = {
            'initial_target': initial_target,
            'expanded_subdomains': [],
            'related_services': [],
            'cloud_assets': [],
            'mobile_endpoints': [],
            'detection_successful': False
        }
        
        try:
            # Ekstrak domain dasar
            parsed_url = urlparse(initial_target)
            base_domain = parsed_url.netloc.lower().replace('www.', '')
            
            # Temukan subdomain tambahan
            subdomains = self._discover_subdomains(base_domain)
            results['expanded_subdomains'] = subdomains
            
            # Identifikasi layanan terkait
            related_services = self._identify_related_services(base_domain, subdomains)
            results['related_services'] = related_services
            
            # Deteksi aset cloud
            cloud_assets = self._detect_cloud_assets(base_domain)
            results['cloud_assets'] = cloud_assets
            
            # Cari endpoint mobile
            mobile_endpoints = self._find_mobile_endpoints(base_domain)
            results['mobile_endpoints'] = mobile_endpoints
            
            results['detection_successful'] = True
        
        except Exception as e:
            results['error'] = f'Scope expansion detection failed: {str(e)}'
        
        return results
    
    def _discover_subdomains(self, base_domain: str) -> list:
        """Temukan subdomain menggunakan amass dan crt.sh."""
        subdomains = set()
        
        # Gunakan crt.sh untuk sertifikat publik
        try:
            crt_url = f"https://crt.sh/?q=%.{base_domain}&output=json"
            response = requests.get(crt_url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                for entry in data:
                    name_value = entry.get('name_value', '')
                    if name_value and base_domain in name_value:
                        subdomains.add(name_value.strip().lower())
        except:
            pass
        
        # Gunakan amass jika tersedia
        try:
            amass_result = subprocess.run([
                'amass', 'enum', '-d', base_domain, '-passive'
            ], capture_output=True, text=True, timeout=120)
            
            if amass_result.returncode == 0:
                for line in amass_result.stdout.split('\n'):
                    if line.strip() and base_domain in line:
                        subdomains.add(line.strip().lower())
        except:
            pass
        
        return sorted(list(subdomains))[:50]  # Batasi 50 subdomain
    
    def _identify_related_services(self, base_domain: str, subdomains: list) -> list:
        """Identifikasi layanan terkait berdasarkan pola penamaan."""
        service_patterns = {
            'api': ['api', 'rest', 'graphql'],
            'admin': ['admin', 'cms', 'dashboard'],
            'staging': ['staging', 'dev', 'test'],
            'mobile': ['mobile', 'app', 'm.'],
            'cdn': ['cdn', 'static', 'assets']
        }
        
        related_services = []
        all_targets = [base_domain] + subdomains
        
        for target in all_targets:
            for service_type, patterns in service_patterns.items():
                if any(pattern in target for pattern in patterns):
                    related_services.append({
                        'service_type': service_type,
                        'endpoint': f"https://{target}",
                        'potential_impact': self._assess_service_impact(service_type)
                    })
        
        return related_services[:20]  # Batasi 20 layanan
    
    def _assess_service_impact(self, service_type: str) -> str:
        """Nilai dampak potensial berdasarkan jenis layanan."""
        impact_levels = {
            'admin': 'critical',
            'api': 'high',
            'mobile': 'high',
            'staging': 'medium',
            'cdn': 'low'
        }
        return impact_levels.get(service_type, 'medium')
    
    def _detect_cloud_assets(self, base_domain: str) -> list:
        """Deteksi aset cloud berdasarkan pola nama domain."""
        cloud_providers = {
            'aws': ['.execute-api.', '.s3.', '.cloudfront.'],
            'gcp': ['.appspot.', '.googleapis.'],
            'azure': ['.azurewebsites.', '.blob.core.windows.']
        }
        
        cloud_assets = []
        # Untuk implementasi nyata, ini akan memeriksa DNS records
        # Untuk sekarang, kembalikan placeholder berdasarkan pola
        return cloud_assets
    
    def _find_mobile_endpoints(self, base_domain: str) -> list:
        """Cari endpoint mobile berdasarkan pola umum."""
        mobile_patterns = ['mobile', 'api-mobile', 'app', 'm.']
        mobile_endpoints = []
        
        # Periksa subdomain untuk pola mobile
        try:
            # Ini akan diimplementasikan dengan pemindaian HTTP sebenarnya
            return mobile_endpoints
        except:
            return []