class RiskAssessor:
    """
    Assess operational risks.
    Menilai risiko operasional dalam aktivitas red teaming.
    """
    
    def __init__(self):
        self.risk_categories = {
            'legal': {
                'factors': ['scope_violation', 'unauthorized_access', 'data_exfiltration'],
                'weight': 0.4
            },
            'technical': {
                'factors': ['detection', 'false_positive', 'system_disruption'],
                'weight': 0.3
            },
            'reputational': {
                'factors': ['public_disclosure', 'vendor_relationship', 'community_standing'],
                'weight': 0.2
            },
            'operational': {
                'factors': ['time_investment', 'resource_consumption', 'success_probability'],
                'weight': 0.1
            }
        }
    
    def assess_operational_risk(self, operation_plan: dict) -> dict:
        """
        Nilai risiko operasional dari rencana operasi.
        """
        risk_scores = {}
        total_weighted_risk = 0.0
        
        for category, config in self.risk_categories.items():
            category_score = self._calculate_category_risk(category, operation_plan)
            weighted_score = category_score * config['weight']
            risk_scores[category] = {
                'raw_score': category_score,
                'weighted_score': weighted_score,
                'factors_analyzed': config['factors']
            }
            total_weighted_risk += weighted_score
        
        overall_risk_level = self._determine_overall_risk_level(total_weighted_risk)
        
        return {
            'operation_plan': operation_plan,
            'risk_scores': risk_scores,
            'total_risk_score': min(total_weighted_risk, 1.0),
            'overall_risk_level': overall_risk_level,
            'mitigation_recommendations': self._generate_mitigation_recommendations(risk_scores)
        }
    
    def _calculate_category_risk(self, category: str, plan: dict) -> float:
        """Hitung skor risiko untuk kategori tertentu."""
        plan_text = str(plan).lower()
        factors = self.risk_categories[category]['factors']
        
        risk_indicators = sum(1 for factor in factors if factor.replace('_', '') in plan_text)
        return min(risk_indicators / len(factors), 1.0) if factors else 0.0
    
    def _determine_overall_risk_level(self, total_score: float) -> str:
        """Tentukan tingkat risiko keseluruhan."""
        if total_score >= 0.7:
            return 'CRITICAL'
        elif total_score >= 0.4:
            return 'HIGH'
        elif total_score >= 0.2:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_mitigation_recommendations(self, risk_scores: dict) -> list:
        """Hasilkan rekomendasi mitigasi."""
        recommendations = []
        
        if risk_scores.get('legal', {}).get('weighted_score', 0) > 0.3:
            recommendations.append('Ensure explicit written authorization for all activities')
        
        if risk_scores.get('technical', {}).get('weighted_score', 0) > 0.2:
            recommendations.append('Implement stealth execution with Tor and rate limiting')
        
        if risk_scores.get('reputational', {}).get('weighted_score', 0) > 0.1:
            recommendations.append('Follow responsible disclosure guidelines strictly')
        
        if risk_scores.get('operational', {}).get('weighted_score', 0) > 0.05:
            recommendations.append('Optimize resource allocation and time management')
        
        if not recommendations:
            recommendations.append('Current operation plan appears to have acceptable risk levels')
        
        return recommendations