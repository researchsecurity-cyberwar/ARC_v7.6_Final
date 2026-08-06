import json
import re

class UpgradeabilityAnalyzer:
    """
    Proxy pattern & storage layout analysis.
    Menganalisis pola proxy dan tata letak penyimpanan untuk upgradeability.
    """
    
    def __init__(self):
        self.proxy_patterns = {
            'transparent_proxy': r'function implementation\(\)',
            'uups_proxy': r'function _authorizeUpgrade\(',
            'beacon_proxy': r'function beacon\(\)',
            'diamond_proxy': r'function diamondCut\('
        }
    
    def analyze_upgradeability(self, contract_path: str, implementation_address: str = None):
        """
        Analisis kemampuan upgrade kontrak.
        """
        results = {
            'contract_path': contract_path,
            'implementation_address': implementation_address,
            'proxy_pattern_detected': None,
            'storage_layout_safe': True,
            'upgrade_security_issues': [],
            'analysis_successful': False
        }
        
        try:
            with open(contract_path, 'r') as f:
                contract_code = f.read()
            
            # Deteksi pola proxy
            proxy_pattern = self._detect_proxy_pattern(contract_code)
            results['proxy_pattern_detected'] = proxy_pattern
            
            # Analisis tata letak penyimpanan
            storage_safe = self._analyze_storage_layout(contract_code)
            results['storage_layout_safe'] = storage_safe
            
            # Identifikasi isu keamanan upgrade
            security_issues = self._identify_upgrade_security_issues(contract_code, proxy_pattern)
            results['upgrade_security_issues'] = security_issues
            
            results['analysis_successful'] = True
        
        except Exception as e:
            results['error'] = f'Upgradeability analysis failed: {str(e)}'
        
        return results
    
    def _detect_proxy_pattern(self, contract_code: str) -> str:
        """Deteksi pola proxy dalam kode kontrak."""
        for pattern_name, pattern_regex in self.proxy_patterns.items():
            if re.search(pattern_regex, contract_code):
                return pattern_name
        return 'none'
    
    def _analyze_storage_layout(self, contract_code: str) -> bool:
        """Analisis keamanan tata letak penyimpanan."""
        # Periksa apakah kontrak mengikuti pola penyimpanan aman
        if 'contract Storage' in contract_code or 'struct Storage' in contract_code:
            return True
        
        # Periksa apakah ada variabel penyimpanan yang tumpang tindih
        storage_vars = re.findall(r'(uint|int|address|bool|string|bytes)\s+(\w+)', contract_code)
        if len(storage_vars) > 10:  # Terlalu banyak variabel penyimpanan
            return False
        
        return True
    
    def _identify_upgrade_security_issues(self, contract_code: str, proxy_pattern: str) -> list:
        """Identifikasi isu keamanan terkait upgrade."""
        issues = []
        
        # Isu umum untuk semua pola proxy
        if 'onlyOwner' not in contract_code and 'initializer' in contract_code:
            issues.append('Missing access control on initializer function')
        
        if proxy_pattern == 'transparent_proxy':
            if 'admin' not in contract_code:
                issues.append('Transparent proxy missing admin functionality')
        
        elif proxy_pattern == 'uups_proxy':
            if '_authorizeUpgrade' not in contract_code:
                issues.append('UUPS proxy missing _authorizeUpgrade function')
            elif 'onlyOwner' not in contract_code and '_authorizeUpgrade' in contract_code:
                issues.append('UUPS proxy upgrade function lacks access control')
        
        elif proxy_pattern == 'beacon_proxy':
            if 'beacon' not in contract_code:
                issues.append('Beacon proxy missing beacon reference')
        
        elif proxy_pattern == 'diamond_proxy':
            if 'diamondCut' not in contract_code:
                issues.append('Diamond proxy missing diamondCut function')
        
        # Periksa potensi storage collision
        if 'immutable' in contract_code and proxy_pattern != 'none':
            issues.append('Immutable variables in proxy contracts can cause storage collisions')
        
        return issues