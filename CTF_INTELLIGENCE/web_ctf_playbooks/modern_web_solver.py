import requests
import json

class ModernWebSolver:
    """
    Next.js/Nuxt/SvelteKit CTF solver.
    Menyelesaikan challenge CTF framework web modern.
    """
    
    def __init__(self):
        self.modern_endpoints = [
            '/_next/static/chunks/',
            '/_nuxt/',
            '/__sapper__/',
            '/api/',
            '/.git/'
        ]
    
    def solve_modern_web_challenge(self, target_url: str):
        """
        Selesaikan challenge web modern.
        """
        results = {
            'target_url': target_url,
            'framework_detected': None,
            'sensitive_paths': [],
            'vulnerabilities_found': [],
            'solution_found': False
        }
        
        try:
            # Deteksi framework
            framework = self._detect_framework(target_url)
            results['framework_detected'] = framework
            
            # Cari path sensitif
            sensitive_paths = self._find_sensitive_paths(target_url)
            results['sensitive_paths'] = sensitive_paths
            
            # Cari kerentanan
            vulnerabilities = self._find_vulnerabilities(target_url, framework)
            results['vulnerabilities_found'] = vulnerabilities
            
            results['solution_found'] = len(vulnerabilities) > 0
        
        except Exception as e:
            results['error'] = f'Modern web solving failed: {str(e)}'
        
        return results
    
    def _detect_framework(self, url: str) -> str:
        """Deteksi framework web modern."""
        try:
            response = requests.get(url, timeout=10)
            content = response.text
            
            if '/_next/' in content:
                return 'nextjs'
            elif '/_nuxt/' in content:
                return 'nuxt'
            elif '/__sapper__/' in content:
                return 'sveltekit'
            else:
                return 'unknown'
        except:
            return 'unknown'
    
    def _find_sensitive_paths(self, url: str) -> list:
        """Cari path sensitif."""
        sensitive_paths = []
        
        for endpoint in self.modern_endpoints:
            test_url = f"{url.rstrip('/')}{endpoint}"
            try:
                response = requests.get(test_url, timeout=5)
                if response.status_code == 200:
                    sensitive_paths.append(test_url)
            except:
                continue
        
        return sensitive_paths
    
    def _find_vulnerabilities(self, url: str, framework: str) -> list:
        """Cari kerentanan framework."""
        vulnerabilities = []
        
        if framework == 'nextjs':
            # Cari API routes yang terbuka
            api_routes = ['/api/debug', '/api/config', '/api/secrets']
            for route in api_routes:
                test_url = f"{url.rstrip('/')}{route}"
                try:
                    response = requests.get(test_url, timeout=5)
                    if response.status_code == 200 and 'secret' in response.text.lower():
                        vulnerabilities.append(f'Exposed API route: {route}')
                except:
                    continue
        
        return vulnerabilities