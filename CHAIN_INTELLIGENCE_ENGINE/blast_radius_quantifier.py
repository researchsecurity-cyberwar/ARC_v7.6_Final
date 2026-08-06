class BlastRadiusQuantifier:
    """
    Financial + reputational impact scoring.
    Mengkuantifikasi dampak finansial dan reputasi dari jalur serangan.
    """
    
    def __init__(self):
        self.impact_categories = {
            'financial': {
                'weight': 0.5,
                'factors': ['direct_loss', 'regulatory_fines', 'remediation_costs', 'business_disruption']
            },
            'reputational': {
                'weight': 0.3,
                'factors': ['public_disclosure', 'media_coverage', 'customer_trust', 'partner_confidence']
            },
            'operational': {
                'weight': 0.2,
                'factors': ['system_downtime', 'data_loss', 'recovery_time', 'resource_consumption']
            }
        }
        
        self.severity_multipliers = {
            'critical': 10.0,
            'high': 5.0,
            'medium': 2.0,
            'low': 1.0
        }
    
    def quantify_blast_radius(self, attack_path: Dict, target_context: Dict) -> Dict:
        """
        Kuantifikasi radius dampak dari jalur serangan.
        """
        results = {
            'attack_path': attack_path,
            'target_context': target_context,
            'impact_scores': {},
            'total_blast_radius_score': 0.0,
            'financial_impact_usd': 0,
            'reputational_impact_score': 0.0,
            'risk_assessment': {}
        }
        
        try:
            # Hitung skor untuk setiap kategori dampak
            impact_scores = {}
            total_weighted_score = 0.0
            
            for category, config in self.impact_categories.items():
                category_score = self._calculate_category_impact(category, attack_path, target_context)
                weighted_score = category_score * config['weight']
                impact_scores[category] = {
                    'raw_score': category_score,
                    'weighted_score': weighted_score,
                    'factors_analyzed': config['factors']
                }
                total_weighted_score += weighted_score
            
            results['impact_scores'] = impact_scores
            results['total_blast_radius_score'] = min(total_weighted_score, 10.0)
            
            # Estimasi dampak finansial
            results['financial_impact_usd'] = self._estimate_financial_impact(
                results['total_blast_radius_score'], target_context
            )
            
            # Estimasi dampak reputasi
            results['reputational_impact_score'] = impact_scores.get('reputational', {}).get('weighted_score', 0.0)
            
            # Buat penilaian risiko
            results['risk_assessment'] = self._generate_risk_assessment(results['total_blast_radius_score'])
        
        except Exception as e:
            results['error'] = f'Blast radius quantification failed: {str(e)}'
        
        return results
    
    def _calculate_category_impact(self, category: str, attack_path: Dict, target_context: Dict) -> float:
        """Hitung dampak untuk kategori tertentu."""
        path_length = attack_path.get('length', 1)
        impact_score = attack_path.get('impact_score', 0)
        target_type = target_context.get('organization_type', 'unknown')
        
        if category == 'financial':
            # Faktor organisasi
            org_multipliers = {
                'banking': 5.0,
                'healthcare': 4.0,
                'government': 6.0,
                'ecommerce': 3.0,
                'tech': 2.0
            }
            multiplier = org_multipliers.get(target_type, 1.0)
            
            base_score = path_length * impact_score * multiplier
            return min(base_score, 10.0)
        
        elif category == 'reputational':
            # Cek apakah target memiliki visibilitas publik
            public_visibility = target_context.get('public_visibility', False)
            media_presence = target_context.get('media_presence', False)
            
            base_score = impact_score
            if public_visibility:
                base_score *= 2.0
            if media_presence:
                base_score *= 1.5
            
            return min(base_score, 10.0)
        
        elif category == 'operational':
            # Estimasi downtime berdasarkan kompleksitas jalur
            complexity_score = path_length * 0.5
            return min(complexity_score, 10.0)
        
        return 0.0
    
    def _estimate_financial_impact(self, blast_score: float, target_context: Dict) -> int:
        """Estimasi dampak finansial dalam USD."""
        target_type = target_context.get('organization_type', 'unknown')
        
        # Basis estimasi per poin skor
        base_estimates = {
            'banking': 100000,
            'healthcare': 50000,
            'government': 200000,
            'ecommerce': 30000,
            'tech': 20000
        }
        
        base_amount = base_estimates.get(target_type, 10000)
        estimated_impact = int(blast_score * base_amount)
        
        return min(estimated_impact, 10000000)  # Maks $10 juta
    
    def _generate_risk_assessment(self, total_score: float) -> Dict:
        """Hasilkan penilaian risiko berdasarkan skor total."""
        if total_score >= 7.0:
            severity = 'CRITICAL'
            description = 'Catastrophic ecosystem impact - immediate executive attention required'
            response_time = 'IMMEDIATE (within 1 hour)'
        elif total_score >= 4.0:
            severity = 'HIGH'
            description = 'Significant business impact - urgent remediation needed'
            response_time = 'URGENT (within 24 hours)'
        elif total_score >= 2.0:
            severity = 'MEDIUM'
            description = 'Moderate impact - scheduled remediation recommended'
            response_time = 'STANDARD (within 7 days)'
        else:
            severity = 'LOW'
            description = 'Limited impact - monitor and document'
            response_time = 'MONITOR (monthly review)'
        
        return {
            'severity': severity,
            'description': description,
            'recommended_response_time': response_time,
            'executive_summary': f'Blast radius score: {total_score:.1f}/10.0 - {severity} risk level'
        }