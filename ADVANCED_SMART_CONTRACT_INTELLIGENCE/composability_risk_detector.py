import json
import re

class ComposabilityRiskDetector:
    """
    DeFi composability risk detection.
    Mendeteksi risiko komposabilitas DeFi.
    """
    
    def __init__(self):
        self.composability_patterns = {
            'flash_loan': r'flashLoan|borrow\(|lend\(',
            'yield_farming': r'farm|stake|harvest|reward',
            'liquidity_pool': r'pool|liquidity|LP',
            'oracle_dependency': r'price\(|oracle|feed',
            'governance': r'govern|proposal|vote'
        }
    
    def detect_composability_risks(self, contract_path: str, protocol_data: dict = None):
        """
        Deteksi risiko komposabilitas DeFi.
        """
        results = {
            'contract_path': contract_path,
            'protocol_data': protocol_data or {},
            'composability_patterns_found': [],
            'risk_vectors': [],
            'blast_radius': 'limited',
            'analysis_successful': False
        }
        
        try:
            with open(contract_path, 'r') as f:
                contract_code = f.read()
            
            # Deteksi pola komposabilitas
            patterns_found = self._detect_composability_patterns(contract_code)
            results['composability_patterns_found'] = patterns_found
            
            # Identifikasi vektor risiko
            risk_vectors = self._identify_risk_vectors(contract_code, patterns_found, protocol_data)
            results['risk_vectors'] = risk_vectors
            
            # Tentukan blast radius
            blast_radius = self._assess_blast_radius(patterns_found, protocol_data)
            results['blast_radius'] = blast_radius
            
            results['analysis_successful'] = True
        
        except Exception as e:
            results['error'] = f'Composability risk detection failed: {str(e)}'
        
        return results
    
    def _detect_composability_patterns(self, contract_code: str) -> list:
        """Deteksi pola komposabilitas dalam kode."""
        patterns = []
        
        for pattern_name, pattern_regex in self.composability_patterns.items():
            if re.search(pattern_regex, contract_code, re.IGNORECASE):
                patterns.append(pattern_name)
        
        return patterns
    
    def _identify_risk_vectors(self, contract_code: str, patterns_found: list, protocol_data: dict) -> list:
        """Identifikasi vektor risiko berdasarkan pola yang ditemukan."""
        risk_vectors = []
        
        # Risiko berdasarkan pola flash loan
        if 'flash_loan' in patterns_found:
            if 'require(' not in contract_code or 'reentrancy' in contract_code.lower():
                risk_vectors.append('Flash loan attack vector with reentrancy potential')
            else:
                risk_vectors.append('Flash loan integration - potential for economic attacks')
        
        # Risiko berdasarkan yield farming
        if 'yield_farming' in patterns_found:
            if 'harvest' in contract_code and 'onlyOwner' not in contract_code:
                risk_vectors.append('Yield farming harvest function lacks access control')
            risk_vectors.append('Yield farming complexity - potential for reward manipulation')
        
        # Risiko berdasarkan liquidity pool
        if 'liquidity_pool' in patterns_found:
            if 'removeLiquidity' in contract_code and 'slippage' not in contract_code.lower():
                risk_vectors.append('Liquidity removal without slippage protection')
            risk_vectors.append('Liquidity pool manipulation through price oracle attacks')
        
        # Risiko berdasarkan oracle dependency
        if 'oracle_dependency' in patterns_found:
            if 'updatePrice' in contract_code and 'onlyOracle' not in contract_code:
                risk_vectors.append('Oracle price manipulation through unauthorized updates')
            risk_vectors.append('Oracle dependency - single point of failure for price feeds')
        
        # Risiko berdasarkan governance
        if 'governance' in patterns_found:
            if 'proposalThreshold' in contract_code:
                threshold_match = re.search(r'proposalThreshold\s*=\s*(\d+)', contract_code)
                if threshold_match and int(threshold_match.group(1)) < 10000:
                    risk_vectors.append('Low governance proposal threshold - easy manipulation')
            risk_vectors.append('Governance attacks through voting mechanism exploitation')
        
        return risk_vectors
    
    def _assess_blast_radius(self, patterns_found: list, protocol_data: dict) -> str:
        """Nilai blast radius berdasarkan pola dan data protokol."""
        if not patterns_found:
            return 'limited'
        
        # Hitung skor risiko berdasarkan pola
        risk_score = len(patterns_found)
        
        # Tambahkan faktor berdasarkan data protokol
        tvl = protocol_data.get('tvl_usd', 0)
        if tvl > 100000000:  # $100M+
            risk_score += 2
        elif tvl > 10000000:  # $10M+
            risk_score += 1
        
        if risk_score >= 4:
            return 'critical'
        elif risk_score >= 2:
            return 'high'
        else:
            return 'medium'