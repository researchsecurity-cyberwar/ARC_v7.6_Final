class SystemicRiskAssessor:
    """
    Assess cross-protocol contagion risk.
    Menilai risiko penularan lintas protokol.
    """
    
    def __init__(self):
        self.protocol_dependencies = {}
        self.contagion_patterns = {
            'direct_exposure': 'Direct lending/borrowing relationships',
            'shared_liquidity': 'Shared liquidity pools or AMMs',
            'common_oracles': 'Shared price oracle sources',
            'composability_risk': 'Complex composability creating attack surfaces'
        }
    
    def assess_systemic_risk(self, target_protocol: dict, ecosystem_data: dict):
        """
        Nilai risiko sistemik protokol target dalam ekosistem yang lebih luas.
        """
        results = {
            'target_protocol': target_protocol,
            'ecosystem_data': ecosystem_data,
            'contagion_risk_level': 'low',
            'dependent_protocols': [],
            'exposure_pathways': [],
            'risk_amplification_factors': [],
            'mitigation_recommendations': [],
            'assessment_complete': False
        }
        
        try:
            # Identifikasi protokol yang bergantung pada target
            dependent_protocols = self._find_dependent_protocols(target_protocol, ecosystem_data)
            results['dependent_protocols'] = dependent_protocols
            
            # Identifikasi jalur eksposur
            exposure_pathways = self._identify_exposure_pathways(target_protocol, ecosystem_data)
            results['exposure_pathways'] = exposure_pathways
            
            # Nilai tingkat risiko penularan
            contagion_risk = self._assess_contagion_risk_level(dependent_protocols, exposure_pathways, target_protocol)
            results['contagion_risk_level'] = contagion_risk
            
            # Identifikasi faktor amplifikasi risiko
            amplification_factors = self._identify_risk_amplification_factors(target_protocol, ecosystem_data)
            results['risk_amplification_factors'] = amplification_factors
            
            # Hasilkan rekomendasi mitigasi
            mitigations = self._generate_systemic_mitigations(contagion_risk, exposure_pathways)
            results['mitigation_recommendations'] = mitigations
            
            results['assessment_complete'] = True
        
        except Exception as e:
            results['error'] = f'Systemic risk assessment failed: {str(e)}'
        
        return results
    
    def _find_dependent_protocols(self, target_protocol: dict, ecosystem_data: dict) -> list:
        """Temukan protokol yang bergantung pada protokol target."""
        dependencies = []
        target_name = target_protocol.get('name', '').lower()
        
        for protocol in ecosystem_data.get('protocols', []):
            # Periksa ketergantungan langsung
            if target_name in str(protocol.get('dependencies', [])).lower():
                dependencies.append({
                    'protocol': protocol.get('name', 'Unknown'),
                    'dependency_type': 'direct_integration',
                    'exposure_level': 'high'
                })
            
            # Periksa ketergantungan melalui likuiditas bersama
            target_tokens = set(target_protocol.get('tokens', []))
            protocol_tokens = set(protocol.get('tokens', []))
            if target_tokens.intersection(protocol_tokens):
                dependencies.append({
                    'protocol': protocol.get('name', 'Unknown'),
                    'dependency_type': 'shared_liquidity',
                    'exposure_level': 'medium'
                })
        
        return dependencies[:10]  # Batasi 10 protokol dependen
    
    def _identify_exposure_pathways(self, target_protocol: dict, ecosystem_data: dict) -> list:
        """Identifikasi jalur eksposur penularan."""
        pathways = []
        
        # Jalur eksposur langsung
        pathways.append({
            'type': 'direct_exposure',
            'description': self.contagion_patterns['direct_exposure'],
            'severity': 'high',
            'protocols_affected': len([p for p in self._find_dependent_protocols(target_protocol, ecosystem_data) 
                                     if p['dependency_type'] == 'direct_integration'])
        })
        
        # Jalur eksposur likuiditas bersama
        pathways.append({
            'type': 'shared_liquidity',
            'description': self.contagion_patterns['shared_liquidity'],
            'severity': 'medium',
            'protocols_affected': len([p for p in self._find_dependent_protocols(target_protocol, ecosystem_data) 
                                     if p['dependency_type'] == 'shared_liquidity'])
        })
        
        # Jalur eksposur oracle bersama
        if target_protocol.get('oracle_type'):
            pathways.append({
                'type': 'common_oracles',
                'description': self.contagion_patterns['common_oracles'],
                'severity': 'high',
                'protocols_affected': self._count_shared_oracle_protocols(target_protocol, ecosystem_data)
            })
        
        # Jalur eksposur komposabilitas
        if target_protocol.get('composable', False):
            pathways.append({
                'type': 'composability_risk',
                'description': self.contagion_patterns['composability_risk'],
                'severity': 'critical',
                'protocols_affected': len(ecosystem_data.get('protocols', [])) // 10  # Estimasi kasar
            })
        
        return pathways
    
    def _count_shared_oracle_protocols(self, target_protocol: dict, ecosystem_data: dict) -> int:
        """Hitung jumlah protokol yang menggunakan oracle yang sama."""
        target_oracle = target_protocol.get('oracle_type', '')
        if not target_oracle:
            return 0
        
        count = 0
        for protocol in ecosystem_data.get('protocols', []):
            if protocol.get('oracle_type') == target_oracle:
                count += 1
        
        return count
    
    def _assess_contagion_risk_level(self, dependent_protocols: list, exposure_pathways: list, target_protocol: dict) -> str:
        """Nilai tingkat risiko penularan."""
        risk_score = 0
        
        # Faktor jumlah protokol dependen
        dependent_count = len(dependent_protocols)
        if dependent_count >= 10:
            risk_score += 4
        elif dependent_count >= 5:
            risk_score += 3
        elif dependent_count >= 2:
            risk_score += 2
        else:
            risk_score += 1
        
        # Faktor jalur eksposur kritis
        for pathway in exposure_pathways:
            if pathway['severity'] == 'critical':
                risk_score += 3
            elif pathway['severity'] == 'high':
                risk_score += 2
            elif pathway['severity'] == 'medium':
                risk_score += 1
        
        # Faktor ukuran protokol target
        tvl = target_protocol.get('tvl_usd', 0)
        if tvl > 1000000000:  # $1B+
            risk_score += 3
        elif tvl > 100000000:  # $100M+
            risk_score += 2
        elif tvl > 10000000:   # $10M+
            risk_score += 1
        
        if risk_score >= 8:
            return 'critical'
        elif risk_score >= 5:
            return 'high'
        elif risk_score >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _identify_risk_amplification_factors(self, target_protocol: dict, ecosystem_data: dict) -> list:
        """Identifikasi faktor yang memperkuat risiko sistemik."""
        factors = []
        
        # Leverage tinggi
        if target_protocol.get('leverage_enabled', False):
            factors.append('High leverage amplifies loss propagation')
        
        # Likuiditas terkonsentrasi
        top_pools = target_protocol.get('top_pools', [])
        if top_pools and len(top_pools) <= 3:
            factors.append('Concentrated liquidity increases systemic vulnerability')
        
        # Oracle tunggal
        if target_protocol.get('oracle_type') and not target_protocol.get('oracle_redundancy', False):
            factors.append('Single oracle dependency creates single point of failure')
        
        # Integrasi kompleks
        if target_protocol.get('integration_complexity', 'low') == 'high':
            factors.append('Complex integrations create unforeseen attack vectors')
        
        return factors
    
    def _generate_systemic_mitigations(self, risk_level: str, exposure_pathways: list) -> list:
        """Hasilkan rekomendasi mitigasi risiko sistemik."""
        mitigations = []
        
        if risk_level in ['critical', 'high']:
            mitigations.extend([
                'Implement circuit breakers for cross-protocol interactions',
                'Diversify oracle sources with median aggregation',
                'Limit maximum exposure to any single protocol',
                'Conduct regular stress testing of ecosystem dependencies',
                'Establish emergency shutdown procedures for systemic events'
            ])
        elif risk_level == 'medium':
            mitigations.extend([
                'Monitor dependent protocol health metrics',
                'Implement gradual exposure limits',
                'Add redundancy to critical oracle feeds',
                'Conduct quarterly dependency audits'
            ])
        else:
            mitigations.extend([
                'Maintain awareness of ecosystem dependencies',
                'Implement basic monitoring for protocol health',
                'Review integration security regularly'
            ])
        
        # Mitigasi spesifik berdasarkan jalur eksposur
        for pathway in exposure_pathways:
            if pathway['type'] == 'composability_risk':
                mitigations.append('Implement strict composability boundaries')
            elif pathway['type'] == 'common_oracles':
                mitigations.append('Add oracle deviation thresholds')
        
        return mitigations[:5]  # Batasi 5 rekomendasi