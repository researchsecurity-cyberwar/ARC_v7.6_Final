class CryptoPatchFactory:
    """
    Smart contract & DeFi protocol fixes.
    Menghasilkan patch kode untuk kerentanan smart contract dan DeFi.
    """
    
    def __init__(self):
        self.crypto_patch_templates = {
            'reentrancy': {
                'checks_effects_interactions': '''
// Reentrancy Fix: Implement Checks-Effects-Interactions pattern
// BEFORE:
// function withdraw(uint amount) public {
//     require(balances[msg.sender] >= amount);
//     (bool success, ) = msg.sender.call{value: amount}("");
//     require(success);
//     balances[msg.sender] -= amount;
// }
// AFTER:
function withdraw(uint amount) public {
    require(balances[msg.sender] >= amount);
    balances[msg.sender] -= amount; // Effects first
    (bool success, ) = msg.sender.call{value: amount}(""); // Interactions last
    require(success);
}
''',
                'reentrancy_guard': '''
// Reentrancy Fix: Use ReentrancyGuard modifier
// BEFORE:
// function withdraw(uint amount) public {
//     // vulnerable code
// }
// AFTER:
function withdraw(uint amount) public nonReentrant {
    // protected code
}
'''
            },
            'flash_loan_attack': {
                'price_oracle_validation': '''
// Flash Loan Attack Fix: Validate price oracle updates
// BEFORE:
// uint price = oracle.getPrice(token);
// require(price > 0);
// AFTER:
uint oldPrice = oracle.getPrice(token);
uint newPrice = oracle.getUpdatedPrice(token);
require(newPrice > oldPrice * 95 / 100 && newPrice < oldPrice * 105 / 100, "Price change too large");
''',
                'circuit_breaker': '''
// Flash Loan Attack Fix: Implement circuit breaker
// BEFORE:
// executeTrade(amount);
// AFTER:
require(!emergencyMode, "Emergency mode active");
executeTrade(amount);
// Add function to activate emergency mode
function activateEmergencyMode() external onlyOwner {
    emergencyMode = true;
}
'''
            }
        }
    
    def generate_crypto_patch(self, vulnerability_type: str, language: str = 'solidity') -> str:
        """Hasilkan patch crypto untuk tipe kerentanan tertentu."""
        if vulnerability_type not in self.crypto_patch_templates:
            return f"// No patch template available for {vulnerability_type}\n// Please implement custom fix"
        
        templates = self.crypto_patch_templates[vulnerability_type]
        return next(iter(templates.values()))
    
    def generate_crypto_fix_recommendation(self, vuln_data: dict) -> dict:
        """Hasilkan rekomendasi perbaikan crypto lengkap."""
        vuln_type = vuln_data.get('type', 'unknown')
        blockchain = vuln_data.get('blockchain', 'ethereum')
        
        patch_code = self.generate_crypto_patch(vuln_type, vuln_data.get('language', 'solidity'))
        
        return {
            'vulnerability_type': vuln_type,
            'blockchain': blockchain,
            'patch_code': patch_code,
            'audit_requirements': self._get_crypto_audit_requirements(vuln_type),
            'testing_recommendations': self._get_crypto_testing_recommendations(vuln_type)
        }
    
    def _get_crypto_audit_requirements(self, vuln_type: str) -> str:
        """Dapatkan persyaratan audit crypto."""
        requirements = {
            'reentrancy': 'Requires formal verification and comprehensive reentrancy testing. All external calls should follow Checks-Effects-Interactions pattern.',
            'flash_loan_attack': 'Requires economic security analysis and price oracle validation. Implement circuit breakers for extreme market conditions.'
        }
        return requirements.get(vuln_type, 'Conduct thorough security audit before deployment.')
    
    def _get_crypto_testing_recommendations(self, vuln_type: str) -> list:
        """Dapatkan rekomendasi pengujian crypto."""
        recommendations = {
            'reentrancy': [
                'Test with reentrancy attack contracts',
                'Verify all external calls follow CEI pattern',
                'Use Slither and MythX for static analysis'
            ],
            'flash_loan_attack': [
                'Simulate flash loan attacks with Aave/Balancer',
                'Test price oracle manipulation scenarios',
                'Verify circuit breaker functionality'
            ]
        }
        return recommendations.get(vuln_type, ['Test with original exploit', 'Conduct security audit'])