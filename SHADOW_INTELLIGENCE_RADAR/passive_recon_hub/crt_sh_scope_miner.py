import requests
import json

class CRTSHScopeMiner:
    """
    Certificate Transparency → subdomain → scope inference.
    Menambang subdomain dari Certificate Transparency logs.
    """
    
    def __init__(self):
        self.crtsh_url = "https://crt.sh/"
    
    def get_subdomains_from_cert_transparency(self, domain):
        """Dapatkan subdomain dari Certificate Transparency."""
        subdomains = set()
        
        try:
            # Query crt.sh dengan format JSON
            params = {
                'q': f'%.{domain}',
                'output': 'json'
            }
            response = requests.get(self.crtsh_url, params=params, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    for entry in data:
                        name_value = entry.get('name_value', '')
                        if name_value:
                            # Handle multiple names separated by newlines
                            names = name_value.split('\n')
                            for name in names:
                                name = name.strip().lower()
                                if name.endswith(f'.{domain}') and '*' not in name:
                                    subdomains.add(name)
                except json.JSONDecodeError:
                    # Fallback ke parsing HTML jika JSON gagal
                    subdomains.update(self._parse_html_response(response.text, domain))
        except Exception as e:
            print(f"⚠️ Failed to query crt.sh: {e}")
        
        return list(subdomains)
    
    def _parse_html_response(self, html_content, domain):
        """Parse respons HTML dari crt.sh."""
        subdomains = set()
        # Cari pola subdomain dalam HTML
        import re
        pattern = rf'[a-zA-Z0-9.-]*\.{re.escape(domain)}'
        matches = re.findall(pattern, html_content)
        for match in matches:
            if '*' not in match:
                subdomains.add(match.lower())
        
        return list(subdomains)