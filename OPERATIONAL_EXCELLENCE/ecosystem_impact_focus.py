class EcosystemImpactFocus:
    """
    Prioritize blast radius over isolated bugs.
    Memprioritaskan dampak ekosistem daripada bug terisolasi.
    """
    
    def __init__(self):
        self.impact_categories = {
            'critical': {
                'blast_radius': 'full_ecosystem_compromise',
                'affected_systems': ['identity', 'data', 'infrastructure', 'financial'],
                'business_impact': 'catastrophic',
                'priority_score': 10.0
            },
            'high': {
                'blast_radius': 'multi_system_compromise',
                'affected_systems': ['identity', 'data', 'infrastructure'],
                'business_impact': 'severe',
                'priority_score': 7.0
            },
            'medium': {
                'blast_radius': 'single_system_compromise',
                'affected_systems': ['data', 'infrastructure'],
                'business_impact': 'moderate',
                'priority_score': 4.0
            },
            'low': {
                'blast_radius': 'isolated_component',
                'affected_systems': ['single_component'],
                'business_impact': 'minimal',
                'priority_score': 1.0
            }
        }
    
    def assess_ecosystem_impact(self, vulnerability_data: dict):
        """
        Nilai dampak ekosistem dari kerentanan.
        """
        results = {
            'vulnerability_data': vulnerability_data,
            'blast_radius': None,
            'affected_systems': [],
            'business_impact_level': None,
            'priority_score': 0.0,
            'ecosystem_impact_score': 0.0,
            'recommendation': None
        }
        
        try:
            # Tentukan kategori dampak
            impact_category = self._determine_impact_category(vulnerability_data)
            
            # Ekstrak informasi dampak
            blast_radius = self.impact_categories[impact_category]['blast_radius']
            affected_systems = self.impact_categories[impact_category]['affected_systems']
            business_impact = self.impact_categories[impact_category]['business_impact']
            priority_score = self.impact_categories[impact_category]['priority_score']
            
            results.update({
                'blast_radius': blast_radius,
                'affected_systems': affected_systems,
                'business_impact_level': business_impact,
                'priority_score': priority_score
            })
            
            # Hitung skor dampak ekosistem
            ecosystem_score = self._calculate_ecosystem_impact_score(vulnerability_data, impact_category)
            results['ecosystem_impact_score'] = ecosystem_score
            
            # Hasilkan rekomendasi
            recommendation = self._generate_impact_recommendation(impact_category, ecosystem_score, vulnerability_data)
            results['recommendation'] = recommendation
        
        except Exception as e:
            results['error'] = f'Ecosystem impact assessment failed: {str(e)}'
        
        return results
    
    def _determine_impact_category(self, vuln_data: dict) -> str:
        """Tentukan kategori dampak berdasarkan data kerentanan."""
        # Analisis berdasarkan tipe kerentanan dan konteks
        vuln_type = vuln_data.get('type', '').lower()
        severity = vuln_data.get('severity', 'medium').lower()
        chain_potential = vuln_data.get('chain_potential', False)
        affected_users = vuln_data.get('affected_users', 0)
        
        # Kriteria Critical
        critical_indicators = [
            'chain_potential' in vuln_data and vuln_data['chain_potential'],
            'identity' in vuln_type or 'auth' in vuln_type,
            'cloud' in vuln_type or 'iam' in vuln_type,
            affected_users > 10000
        ]
        
        if severity == 'critical' or sum(critical_indicators) >= 2:
            return 'critical'
        
        # Kriteria High
        high_indicators = [
            severity == 'high',
            'data' in vuln_type or 'sqli' in vuln_type,
            affected_users > 1000,
            'financial' in str(vuln_data.get('business_impact', ''))
        ]
        
        if sum(high_indicators) >= 2:
            return 'high'
        
        # Kriteria Medium
        medium_indicators = [
            severity == 'medium',
            'xss' in vuln_type or 'csrf' in vuln_type,
            affected_users > 100
        ]
        
        if sum(medium_indicators) >= 1:
            return 'medium'
        
        return 'low'
    
    def _calculate_ecosystem_impact_score(self, vuln_data: dict, category: str) -> float:
        """Hitung skor dampak ekosistem."""
        base_score = self.impact_categories[category]['priority_score']
        
        # Penyesuaian berdasarkan konteks tambahan
        chain_multiplier = 1.5 if vuln_data.get('chain_potential', False) else 1.0
        user_multiplier = min(2.0, 1.0 + (vuln_data.get('affected_users', 0) / 10000))
        financial_multiplier = 1.3 if 'financial' in str(vuln_data.get('business_impact', '')).lower() else 1.0
        
        ecosystem_score = base_score * chain_multiplier * user_multiplier * financial_multiplier
        return min(10.0, ecosystem_score)
    
    def _generate_impact_recommendation(self, category: str, ecosystem_score: float, vuln_data: dict) -> str:
        """Hasilkan rekomendasi berdasarkan dampak ekosistem."""
        if category == 'critical':
            return f"IMMEDIATE ACTION REQUIRED: Ecosystem impact score {ecosystem_score:.1f}/10.0 - Full compromise potential."
        elif category == 'high':
            return f"HIGH PRIORITY: Ecosystem impact score {ecosystem_score:.1f}/10.0 - Multi-system compromise likely."
        elif category == 'medium':
            return f"MEDIUM PRIORITY: Ecosystem impact score {ecosystem_score:.1f}/10.0 - Single system impact confirmed."
        else:
            return f"LOW PRIORITY: Ecosystem impact score {ecosystem_score:.1f}/10.0 - Isolated component affected."
    
    def prioritize_vulnerabilities(self, vulnerabilities: list) -> list:
        """
        Prioritaskan daftar kerentanan berdasarkan dampak ekosistem.
        """
        prioritized = []
        
        for vuln in vulnerabilities:
            impact_assessment = self.assess_ecosystem_impact(vuln)
            prioritized.append({
                'vulnerability': vuln,
                'impact_assessment': impact_assessment,
                'priority_score': impact_assessment['ecosystem_impact_score']
            })
        
        # Urutkan berdasarkan skor prioritas (tertinggi dulu)
        prioritized.sort(key=lambda x: x['priority_score'], reverse=True)
        return prioritized