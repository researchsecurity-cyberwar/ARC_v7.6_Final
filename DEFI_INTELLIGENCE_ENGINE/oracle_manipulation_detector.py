import requests
import json
from datetime import datetime, timedelta

class OracleManipulationDetector:
    """
    Detect price oracle manipulation vectors.
    Mendeteksi vektor manipulasi oracle harga.
    """
    
    def __init__(self):
        self.oracle_types = ['chainlink', 'uniswap_twap', 'sushiswap_twap', 'custom']
        self.manipulation_patterns = {
            'flash_loan_attack': 'Large flash loan followed by oracle query',
            'sandwich_attack': 'Price manipulation before and after oracle update',
            'volume_spike': 'Abnormal trading volume affecting TWAP',
            'liquidity_removal': 'Sudden liquidity removal from pool'
        }
    
    def detect_oracle_manipulation(self, protocol_data: dict, oracle_config: dict):
        """
        Deteksi potensi manipulasi oracle harga.
        """
        results = {
            'protocol_data': protocol_data,
            'oracle_config': oracle_config,
            'manipulation_detected': False,
            'manipulation_vectors': [],
            'risk_level': 'low',
            'recommended_mitigations': [],
            'detection_complete': False
        }
        
        try:
            # Identifikasi tipe oracle
            oracle_type = oracle_config.get('type', 'unknown')
            
            # Deteksi vektor manipulasi berdasarkan tipe oracle
            manipulation_vectors = self._detect_manipulation_vectors(oracle_type, protocol_data, oracle_config)
            results['manipulation_vectors'] = manipulation_vectors
            
            # Tentukan tingkat risiko
            risk_level = self._assess_manipulation_risk(manipulation_vectors, protocol_data)
            results['risk_level'] = risk_level
            
            # Hasilkan rekomendasi mitigasi
            mitigations = self._generate_mitigation_recommendations(oracle_type, manipulation_vectors)
            results['recommended_mitigations'] = mitigations
            
            # Tentukan apakah manipulasi terdeteksi
            results['manipulation_detected'] = len(manipulation_vectors) > 0
            
            results['detection_complete'] = True
        
        except Exception as e:
            results['error'] = f'Oracle manipulation detection failed: {str(e)}'
        
        return results
    
    def _detect_manipulation_vectors(self, oracle_type: str, protocol_data: dict, oracle_config: dict) -> list:
        """Deteksi vektor manipulasi berdasarkan tipe oracle."""
        vectors = []
        
        if oracle_type == 'uniswap_twap' or oracle_type == 'sushiswap_twap':
            # TWAP rentan terhadap serangan volume
            vectors.append({
                'type': 'volume_spike',
                'description': self.manipulation_patterns['volume_spike'],
                'likelihood': 0.8,
                'impact': 'high'
            })
            
            vectors.append({
                'type': 'liquidity_removal',
                'description': self.manipulation_patterns['liquidity_removal'],
                'likelihood': 0.7,
                'impact': 'high'
            })
        
        if oracle_type == 'chainlink':
            # Chainlink lebih aman tapi masih rentan terhadap delay
            vectors.append({
                'type': 'stale_price',
                'description': 'Use of stale price data during market volatility',
                'likelihood': 0.4,
                'impact': 'medium'
            })
        
        # Semua oracle rentan terhadap flash loan
        vectors.append({
            'type': 'flash_loan_attack',
            'description': self.manipulation_patterns['flash_loan_attack'],
            'likelihood': 0.9,
            'impact': 'critical'
        })
        
        return vectors
    
    def _assess_manipulation_risk(self, manipulation_vectors: list, protocol_data: dict) -> str:
        """Nilai tingkat risiko manipulasi."""
        if not manipulation_vectors:
            return 'low'
        
        # Hitung skor risiko berdasarkan vektor yang terdeteksi
        risk_score = 0
        for vector in manipulation_vectors:
            likelihood = vector.get('likelihood', 0)
            impact = vector.get('impact', 'low')
            
            impact_score = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}.get(impact, 1)
            risk_score += likelihood * impact_score
        
        tvl = protocol_data.get('tvl_usd', 0)
        if tvl > 100000000:  # Protokol besar = risiko lebih tinggi
            risk_score *= 1.5
        
        if risk_score >= 5.0:
            return 'critical'
        elif risk_score >= 3.0:
            return 'high'
        elif risk_score >= 1.5:
            return 'medium'
        else:
            return 'low'
    
    def _generate_mitigation_recommendations(self, oracle_type: str, manipulation_vectors: list) -> list:
        """Hasilkan rekomendasi mitigasi."""
        mitigations = []
        
        if oracle_type in ['uniswap_twap', 'sushiswap_twap']:
            mitigations.extend([
                'Implement circuit breaker for abnormal price movements',
                'Use multiple oracle sources with median aggregation',
                'Add minimum time window for TWAP calculations',
                'Monitor liquidity depth and alert on sudden changes'
            ])
        
        if oracle_type == 'chainlink':
            mitigations.extend([
                'Implement heartbeat check for price updates',
                'Use deviation threshold to detect stale prices',
                'Combine with secondary oracle source for critical operations'
            ])
        
        # Mitigasi umum untuk semua oracle
        mitigations.extend([
            'Implement flash loan detection mechanism',
            'Add transaction origin validation',
            'Use commit-reveal scheme for critical price queries',
            'Monitor for sandwich attack patterns'
        ])
        
        return mitigations[:5]  # Batasi 5 rekomendasi teratas