class ProxyUpgradeAdvisor:
    """
    Upgradeable contract patterns.
    Memberikan saran untuk pola kontrak upgradeable yang aman.
    """
    
    def __init__(self):
        self.upgradeable_patterns = {
            'transparent_proxy': {
                'description': 'Transparent Proxy pattern with admin separation',
                'security_considerations': [
                    'Admin must be separate from implementation',
                    'Implementation must be immutable after deployment',
                    'Proxy storage layout must be compatible with implementation'
                ],
                'code_example': '''
// Transparent Proxy Admin
contract ProxyAdmin is Ownable {
    function upgrade(TransparentUpgradeableProxy proxy, address newImplementation) external onlyOwner {
        proxy.upgradeTo(newImplementation);
    }
}

// Implementation contract (must be immutable)
contract MyContractV1 {
    // Implementation logic
}
'''
            },
            'uups_proxy': {
                'description': 'UUPS (Universal Upgradeable Proxy Standard) pattern',
                'security_considerations': [
                    'Upgrade function must have proper access control',
                    'Implementation must include upgrade authorization logic',
                    'Avoid storage layout collisions during upgrades'
                ],
                'code_example': '''
// UUPS Implementation
contract MyContractV2 is UUPSUpgradeable {
    function _authorizeUpgrade(address newImplementation) internal override onlyOwner {
        // Authorization logic
    }
}
'''
            }
        }
    
    def advise_proxy_upgrade(self, current_pattern: str, upgrade_requirements: dict) -> dict:
        """Berikan saran untuk upgrade kontrak proxy."""
        if current_pattern not in self.upgradeable_patterns:
            return {'error': f'Unknown proxy pattern: {current_pattern}'}
        
        current_info = self.upgradeable_patterns[current_pattern]
        
        return {
            'current_pattern': current_pattern,
            'pattern_description': current_info['description'],
            'security_considerations': current_info['security_considerations'],
            'recommended_implementation': current_info['code_example'],
            'upgrade_risks': self._assess_upgrade_risks(current_pattern, upgrade_requirements),
            'mitigation_strategies': self._get_mitigation_strategies(current_pattern)
        }
    
    def _assess_upgrade_risks(self, pattern: str, requirements: dict) -> list:
        """Nilai risiko upgrade."""
        risks = []
        
        if requirements.get('storage_layout_change', False):
            risks.append('Storage layout collision possible during upgrade')
        
        if requirements.get('access_control_change', False):
            risks.append('Access control modification may introduce vulnerabilities')
        
        if pattern == 'transparent_proxy' and requirements.get('admin_compromise_risk', False):
            risks.append('Proxy admin key compromise would allow malicious upgrades')
        
        return risks or ['No significant upgrade risks identified']
    
    def _get_mitigation_strategies(self, pattern: str) -> list:
        """Dapatkan strategi mitigasi."""
        strategies = {
            'transparent_proxy': [
                'Use multi-sig wallet for proxy admin',
                'Implement time-locked upgrades',
                'Conduct thorough storage layout compatibility testing'
            ],
            'uups_proxy': [
                'Implement robust access control in _authorizeUpgrade',
                'Use OpenZeppelin upgrade plugins for safe deployments',
                'Test upgrade process in staging environment'
            ]
        }
        return strategies.get(pattern, ['Follow upgrade best practices', 'Conduct security audit'])