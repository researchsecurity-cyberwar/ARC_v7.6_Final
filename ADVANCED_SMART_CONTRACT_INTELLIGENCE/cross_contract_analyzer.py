import json
import re

class CrossContractAnalyzer:
    """
    Inter-contract interaction analysis.
    Menganalisis interaksi antar-kontrak.
    """
    
    def __init__(self):
        self.interaction_patterns = {
            'external_call': r'\.call\(|\.delegatecall\(|\.staticcall\(',
            'contract_reference': r'contract\s+\w+\s*:\s*\w+',
            'interface_usage': r'interface\s+\w+'
        }
    
    def analyze_cross_contract_interactions(self, contract_path: str, related_contracts: list = None):
        """
        Analisis interaksi antar-kontrak.
        """
        results = {
            'contract_path': contract_path,
            'related_contracts': related_contracts or [],
            'interactions_found': [],
            'security_risks': [],
            'analysis_successful': False
        }
        
        try:
            with open(contract_path, 'r') as f:
                contract_code = f.read()
            
            # Temukan interaksi antar-kontrak
            interactions = self._find_contract_interactions(contract_code)
            results['interactions_found'] = interactions
            
            # Identifikasi risiko keamanan
            security_risks = self._identify_interaction_security_risks(contract_code, interactions)
            results['security_risks'] = security_risks
            
            results['analysis_successful'] = True
        
        except Exception as e:
            results['error'] = f'Cross-contract analysis failed: {str(e)}'
        
        return results
    
    def _find_contract_interactions(self, contract_code: str) -> list:
        """Temukan interaksi antar-kontrak dalam kode."""
        interactions = []
        
        # Cari panggilan eksternal
        external_calls = re.findall(r'(\w+)\.call\(', contract_code)
        for call in external_calls:
            interactions.append({
                'type': 'external_call',
                'target': call,
                'risk_level': 'high'
            })
        
        # Cari delegatecall
        delegate_calls = re.findall(r'(\w+)\.delegatecall\(', contract_code)
        for call in delegate_calls:
            interactions.append({
                'type': 'delegatecall',
                'target': call,
                'risk_level': 'critical'
            })
        
        # Cari referensi kontrak
        contract_refs = re.findall(r'contract\s+(\w+)\s*:\s*(\w+)', contract_code)
        for ref_name, ref_base in contract_refs:
            interactions.append({
                'type': 'contract_inheritance',
                'target': ref_base,
                'risk_level': 'low'
            })
        
        return interactions
    
    def _identify_interaction_security_risks(self, contract_code: str, interactions: list) -> list:
        """Identifikasi risiko keamanan dari interaksi antar-kontrak."""
        risks = []
        
        # Risiko umum dari panggilan eksternal
        if '.call(' in contract_code and 'require(' not in contract_code:
            risks.append('External calls without return value checking')
        
        if '.delegatecall(' in contract_code:
            risks.append('Delegatecall usage - potential for storage manipulation')
        
        # Periksa pola berbahaya
        if 'address(' in contract_code and ').call(' in contract_code:
            risks.append('Arbitrary address calls - potential for malicious contract interaction')
        
        # Periksa kurangnya validasi
        if any(interaction['type'] == 'external_call' for interaction in interactions):
            if 'require(' not in contract_code and 'if (' not in contract_code:
                risks.append('Missing validation on external contract interactions')
        
        return risks