class BlastRadiusForecaster:
    """
    Predict ecosystem impact before exploitation (financial + reputational).
    Memprediksi dampak ledakan dari eksploitasi yang direncanakan.
    """
    
    IMPACT_WEIGHTS = {
        'user_data_exposure': 0.3,
        'financial_loss': 0.25,
        'service_disruption': 0.2,
        'reputational_damage': 0.15,
        'regulatory_penalties': 0.1
    }
    
    SEVERITY_MAP = {
        'low': 0.1,
        'medium': 0.3,
        'high': 0.6,
        'critical': 0.9
    }
    
    def __init__(self):
        pass
    
    def forecast_blast_radius(self, vulnerability_data):
        """
        Prediksi dampak ledakan berdasarkan data kerentanan.
        """
        impact_scores = {}
        
        # Hitung skor untuk setiap kategori dampak
        for impact_type, weight in self.IMPACT_WEIGHTS.items():
            severity = vulnerability_data.get(f'{impact_type}_severity', 'low')
            severity_score = self.SEVERITY_MAP.get(severity, 0.1)
            impact_scores[impact_type] = weight * severity_score
        
        # Hitung total blast radius score (0.0 - 1.0)
        total_score = sum(impact_scores.values())
        
        # Klasifikasi dampak
        if total_score >= 0.7:
            impact_level = "CRITICAL"
        elif total_score >= 0.4:
            impact_level = "HIGH"
        elif total_score >= 0.2:
            impact_level = "MEDIUM"
        else:
            impact_level = "LOW"
        
        return {
            'total_score': total_score,
            'impact_level': impact_level,
            'detailed_scores': impact_scores,
            'estimated_financial_impact': self._estimate_financial_impact(vulnerability_data, total_score),
            'estimated_reputational_impact': self._estimate_reputational_impact(vulnerability_data, total_score)
        }
    
    def _estimate_financial_impact(self, vuln_data, score):
        """Estimasi dampak finansial dalam USD."""
        # Estimasi kasar berdasarkan skor dan tipe organisasi
        org_type = vuln_data.get('organization_type', 'unknown')
        base_estimates = {
            'banking': 500000,
            'healthcare': 300000,
            'ecommerce': 200000,
            'government': 1000000,
            'tech': 150000,
            'unknown': 100000
        }
        
        base_amount = base_estimates.get(org_type, 100000)
        estimated_impact = base_amount * score
        
        return round(estimated_impact, 2)
    
    def _estimate_reputational_impact(self, vuln_data, score):
        """Estimasi dampak reputasi (skala 1-10)."""
        # Skala 1-10, di mana 10 adalah kerusakan reputasi maksimal
        return min(10, round(score * 10, 1))