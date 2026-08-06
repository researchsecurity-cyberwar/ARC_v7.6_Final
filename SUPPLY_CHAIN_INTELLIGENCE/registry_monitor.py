import requests
import json
from datetime import datetime, timedelta

class RegistryMonitor:
    """
    Track new packages in public registries (npm, PyPI).
    Memantau paket baru di registry publik.
    """
    
    def __init__(self):
        self.registry_apis = {
            'npm': {
                'search_url': 'https://api.npms.io/v2/search',
                'package_url': 'https://registry.npmjs.org/'
            },
            'pypi': {
                'search_url': 'https://pypi.org/rss/updates.xml',
                'package_url': 'https://pypi.org/pypi/'
            }
        }
        
        self.suspicious_indicators = {
            'npm': ['downloads < 10', 'published < 7 days', 'no description', 'no readme'],
            'pypi': ['downloads < 100', 'uploaded < 7 days', 'no description', 'no homepage']
        }
    
    def monitor_new_packages(self, registry_type: str = 'npm', days_back: int = 7):
        """
        Pantau paket baru dalam registry.
        """
        results = {
            'registry_type': registry_type,
            'days_monitored': days_back,
            'new_packages': [],
            'suspicious_packages': [],
            'risk_assessment': {}
        }
        
        try:
            if registry_type == 'npm':
                packages = self._fetch_npm_new_packages(days_back)
            elif registry_type == 'pypi':
                packages = self._fetch_pypi_new_packages(days_back)
            else:
                results['error'] = f'Unsupported registry type: {registry_type}'
                return results
            
            results['new_packages'] = packages
            
            # Analisis paket mencurigakan
            suspicious_packages = []
            for package in packages:
                if self._is_suspicious_package(package, registry_type):
                    suspicious_packages.append(package)
            
            results['suspicious_packages'] = suspicious_packages
            results['risk_assessment'] = self._assess_registry_risk(suspicious_packages, len(packages))
        
        except Exception as e:
            results['error'] = f'Registry monitoring failed: {str(e)}'
        
        return results
    
    def _fetch_npm_new_packages(self, days_back: int) -> List[Dict]:
        """Ambil paket npm baru."""
        # Query npm registry untuk paket baru
        query = {
            'q': f'created:>={(datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")}',
            'size': 100
        }
        
        try:
            response = requests.get(self.registry_apis['npm']['search_url'], params=query, timeout=10)
            if response.status_code == 200:
                data = response.json()
                packages = []
                for pkg in data.get('results', [])[:50]:  # Batasi 50 paket
                    packages.append({
                        'name': pkg['package']['name'],
                        'version': pkg['package']['version'],
                        'description': pkg['package'].get('description', ''),
                        'author': pkg['package'].get('author', {}).get('name', 'unknown'),
                        'published_at': pkg['package'].get('date', ''),
                        'downloads': pkg.get('score', {}).get('detail', {}).get('popularity', 0) * 1000000
                    })
                return packages
        except Exception:
            pass
        
        return []
    
    def _fetch_pypi_new_packages(self, days_back: int) -> List[Dict]:
        """Ambil paket PyPI baru."""
        # Ini akan mengurai RSS feed PyPI (placeholder)
        # Implementasi penuh memerlukan parsing XML RSS
        return []
    
    def _is_suspicious_package(self, package: Dict, registry_type: str) -> bool:
        """Tentukan apakah paket mencurigakan."""
        # Cek indikator mencurigakan
        published_date = package.get('published_at', '')
        downloads = package.get('downloads', 0)
        description = package.get('description', '')
        
        try:
            # Parse tanggal publikasi
            if published_date:
                pub_date = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                days_since_pub = (datetime.now() - pub_date).days
                
                if days_since_pub <= 7 and downloads < 10:
                    return True
            
            # Cek deskripsi kosong
            if not description.strip():
                return True
            
            # Cek nama typosquatting
            typosquatting_detector = TyposquattingDetector()
            typosquatting_result = typosquatting_detector.detect_typosquatting(
                package['name'], registry_type
            )
            if typosquatting_result.get('typosquatting_detected', False):
                return True
        
        except Exception:
            pass
        
        return False
    
    def _assess_registry_risk(self, suspicious_packages: List, total_packages: int) -> Dict:
        """Nilai risiko registry."""
        risk_level = 'LOW'
        if len(suspicious_packages) > 10:
            risk_level = 'HIGH'
        elif len(suspicious_packages) > 0:
            risk_level = 'MEDIUM'
        
        return {
            'risk_level': risk_level,
            'suspicious_ratio': len(suspicious_packages) / total_packages if total_packages > 0 else 0,
            'monitoring_recommendation': 'Increase monitoring frequency' if risk_level == 'HIGH' else 'Continue standard monitoring'
        }