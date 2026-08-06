import requests
from bs4 import BeautifulSoup
import re

class ArchitectureFingerprinter:
    """
    Detect cloud (AWS/GCP), frameworks, auth flows.
    Mengidentifikasi arsitektur teknologi target enterprise.
    """
    
    def __init__(self):
        self.cloud_indicators = {
            'aws': ['amazonaws.com', 's3.amazonaws.com', 'cloudfront.net'],
            'gcp': ['googleapis.com', 'storage.googleapis.com', 'appspot.com'],
            'azure': ['azurewebsites.net', 'blob.core.windows.net', 'cloudapp.azure.com']
        }
        
        self.framework_indicators = {
            'react': ['_react_', 'react-dom', 'create-react-app'],
            'angular': ['ng-version', 'angular.js', '@angular/core'],
            'vue': ['__VUE__', 'vue.runtime.esm.js'],
            'nextjs': ['_next/', 'next/static'],
            'nuxt': ['_nuxt/', '__NUXT__']
        }
        
        self.auth_indicators = {
            'oauth': ['oauth', 'openid', 'authorize', 'token'],
            'saml': ['saml', 'sso', 'assertion'],
            'jwt': ['jwt', 'bearer', 'authorization: bearer'],
            'session': ['sessionid', 'phpsessid', 'jsessionid']
        }
    
    def fingerprint_target(self, target_url):
        """Lakukan fingerprinting lengkap terhadap target."""
        try:
            response = requests.get(target_url, timeout=10)
            headers = response.headers
            content = response.text
            
            return {
                'cloud_providers': self._detect_cloud_providers(headers, content),
                'frameworks': self._detect_frameworks(content),
                'auth_flows': self._detect_auth_flows(headers, content),
                'tech_stack': self._extract_tech_stack(headers, content)
            }
        except Exception as e:
            print(f"⚠️ Fingerprinting failed for {target_url}: {e}")
            return {}
    
    def _detect_cloud_providers(self, headers, content):
        """Deteksi penyedia cloud dari header dan konten."""
        detected = []
        combined_text = str(headers) + content.lower()
        
        for provider, indicators in self.cloud_indicators.items():
            if any(indicator in combined_text for indicator in indicators):
                detected.append(provider)
        
        return detected
    
    def _detect_frameworks(self, content):
        """Deteksi framework frontend/backend."""
        detected = []
        content_lower = content.lower()
        
        for framework, indicators in self.framework_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                detected.append(framework)
        
        return detected
    
    def _detect_auth_flows(self, headers, content):
        """Deteksi alur autentikasi."""
        detected = []
        combined_text = (str(headers) + content).lower()
        
        for auth_type, indicators in self.auth_indicators.items():
            if any(indicator in combined_text for indicator in indicators):
                detected.append(auth_type)
        
        return detected
    
    def _extract_tech_stack(self, headers, content):
        """Ekstrak informasi tech stack dari header server."""
        tech_stack = []
        
        # Cek header Server
        server_header = headers.get('Server', '').lower()
        if 'apache' in server_header:
            tech_stack.append('Apache')
        if 'nginx' in server_header:
            tech_stack.append('Nginx')
        if 'iis' in server_header:
            tech_stack.append('IIS')
        
        # Cek header X-Powered-By
        powered_by = headers.get('X-Powered-By', '').lower()
        if 'php' in powered_by:
            tech_stack.append('PHP')
        if 'asp.net' in powered_by:
            tech_stack.append('ASP.NET')
        
        return tech_stack