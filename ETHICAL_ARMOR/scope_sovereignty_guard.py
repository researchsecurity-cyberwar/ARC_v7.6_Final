import os
import json
from urllib.parse import urlparse

class ScopeSovereigntyGuard:
    """
    Block if not in client/bounty manifest.
    Memblokir operasi jika target tidak ada dalam manifest klien/bounty.
    """
    
    def __init__(self, manifest_dir="~/.arc/manifests"):
        self.manifest_dir = os.path.expanduser(manifest_dir)
        os.makedirs(self.manifest_dir, exist_ok=True)
    
    def check_target_authorization(self, target_url: str, operation_type: str) -> dict:
        """
        Periksa apakah target diizinkan berdasarkan manifest.
        """
        results = {
            'target_url': target_url,
            'operation_type': operation_type,
            'authorized': False,
            'manifest_found': False,
            'scope_match': False,
            'blocking_reason': None
        }
        
        try:
            # Ekstrak domain dari URL target
            parsed_url = urlparse(target_url)
            target_domain = parsed_url.netloc.lower().replace('www.', '')
            
            # Cari manifest yang relevan
            manifest_file = self._find_relevant_manifest(target_domain)
            if not manifest_file:
                results['blocking_reason'] = 'No authorization manifest found for target'
                return results
            
            results['manifest_found'] = True
            
            # Muat manifest
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
            
            # Periksa otorisasi
            auth_check = self._verify_manifest_authorization(manifest, target_domain, operation_type)
            results.update(auth_check)
            
            # Jika tidak diizinkan, blokir operasi
            if not results['authorized']:
                if not results['blocking_reason']:
                    results['blocking_reason'] = 'Target not authorized in manifest'
        
        except Exception as e:
            results['blocking_reason'] = f'Authorization check failed: {str(e)}'
        
        return results
    
    def _find_relevant_manifest(self, target_domain: str) -> str:
        """Cari file manifest yang relevan untuk domain target."""
        # Cari manifest berdasarkan nama domain atau program
        manifest_files = [f for f in os.listdir(self.manifest_dir) if f.endswith('.json')]
        
        for manifest_file in manifest_files:
            manifest_path = os.path.join(self.manifest_dir, manifest_file)
            try:
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                
                # Periksa apakah domain target ada dalam scope
                scope_domains = manifest.get('scope', {}).get('domains', [])
                if any(target_domain == domain.lower().replace('www.', '') for domain in scope_domains):
                    return manifest_path
                
                # Periksa wildcard subdomain
                program_name = manifest.get('program_name', '').lower()
                if target_domain.endswith(f".{program_name}") or target_domain == program_name:
                    return manifest_path
                    
            except:
                continue
        
        return None
    
    def _verify_manifest_authorization(self, manifest: dict, target_domain: str, operation_type: str) -> dict:
        """Verifikasi otorisasi berdasarkan manifest."""
        results = {'authorized': False, 'scope_match': False, 'blocking_reason': None}
        
        # Periksa scope domains
        scope_domains = [d.lower().replace('www.', '') for d in manifest.get('scope', {}).get('domains', [])]
        if target_domain in scope_domains:
            results['scope_match'] = True
            
            # Periksa jenis operasi yang diizinkan
            allowed_operations = manifest.get('allowed_operations', ['recon', 'scan', 'exploit'])
            if operation_type in allowed_operations:
                results['authorized'] = True
            else:
                results['blocking_reason'] = f'Operation type "{operation_type}" not allowed in manifest'
        
        # Periksa status program
        program_status = manifest.get('status', 'active')
        if program_status != 'active':
            results['authorized'] = False
            results['blocking_reason'] = f'Program status is "{program_status}", not active'
        
        # Periksa tanggal kedaluwarsa
        expiry_date = manifest.get('expiry_date')
        if expiry_date:
            from datetime import datetime
            try:
                expiry_dt = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
                if datetime.now() > expiry_dt:
                    results['authorized'] = False
                    results['blocking_reason'] = 'Authorization manifest expired'
            except:
                pass
        
        return results
    
    def create_authorization_manifest(self, program_name: str, scope_domains: list, 
                                    allowed_operations: list = None, expiry_days: int = 30) -> str:
        """
        Buat manifest otorisasi baru.
        """
        from datetime import datetime, timedelta
        
        manifest = {
            'program_name': program_name,
            'created_at': datetime.now().isoformat(),
            'expiry_date': (datetime.now() + timedelta(days=expiry_days)).isoformat(),
            'status': 'active',
            'scope': {
                'domains': scope_domains,
                'ip_ranges': [],
                'technologies': []
            },
            'allowed_operations': allowed_operations or ['recon', 'scan'],
            'bounty_tier': 'standard',
            'legal_contact': 'authorized_security_researcher@example.com'
        }
        
        manifest_file = os.path.join(self.manifest_dir, f"{program_name}_manifest.json")
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return manifest_file