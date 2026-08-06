class EconomicImpactReasoner:
    """
    Analyze economic impact of proposed fixes and vulnerabilities.
    Menganalisis dampak ekonomi dari perbaikan yang diusulkan.
    """
    
    def __init__(self):
        pass
    
    def calculate_bounty_value(self, vulnerability_data):
        """Hitung estimasi nilai bounty berdasarkan faktor ekonomi."""
        base_factors = {
            'severity': vulnerability_data.get('severity_score', 0.5),
            'exploitability': vulnerability_data.get('exploitability_score', 0.5),
            'impact_scope': vulnerability_data.get('affected_users', 1000) / 1000000,  # Normalized
            'business_criticality': vulnerability_data.get('business_criticality', 0.5)
        }
        
        # Formula estimasi bounty (disesuaikan dengan pasar bug bounty)
        severity_weight = 0.4
        exploitability_weight = 0.25
        scope_weight = 0.2
        criticality_weight = 0.15
        
        bounty_score = (
            base_factors['severity'] * severity_weight +
            base_factors['exploitability'] * exploitability_weight +
            min(base_factors['impact_scope'], 1.0) * scope_weight +
            base_factors['business_criticality'] * criticality_weight
        )
        
        # Konversi skor ke estimasi USD
        platform_multipliers = {
            'immunefi': 100000,  # DeFi bounty sangat tinggi
            'hackerone_enterprise': 25000,
            'bugcrowd_premium': 15000,
            'intigriti': 8000,
            'standard': 2000
        }
        
        platform = vulnerability_data.get('platform', 'standard')
        multiplier = platform_multipliers.get(platform, 2000)
        
        estimated_bounty = bounty_score * multiplier
        
        return {
            'estimated_bounty_usd': round(estimated_bounty, 2),
            'bounty_score': round(bounty_score, 3),
            'confidence_interval': [estimated_bounty * 0.7, estimated_bounty * 1.3],
            'market_factors': self._analyze_market_factors(vulnerability_data)
        }
    
    def _analyze_market_factors(self, vuln_data):
        """Analisis faktor pasar yang mempengaruhi nilai bounty."""
        factors = []
        
        # Faktor waktu
        if vuln_data.get('novelty', False):
            factors.append('Novel vulnerability - higher value')
        
        if vuln_data.get('competition_level', 'low') == 'high':
            factors.append('High competition - lower value')
        
        # Faktor program
        program_status = vuln_data.get('program_status', 'active')
        if program_status == 'private':
            factors.append('Private program - potentially higher value')
        elif program_status == 'public':
            factors.append('Public program - standard value')
        
        return factors
    
    def calculate_remediation_cost(self, vulnerability_data):
        """Hitung estimasi biaya perbaikan untuk organisasi target."""
        complexity_levels = {
            'low': {'hours': 2, 'cost_per_hour': 100},
            'medium': {'hours': 8, 'cost_per_hour': 150},
            'high': {'hours': 40, 'cost_per_hour': 200},
            'critical': {'hours': 160, 'cost_per_hour': 250}
        }
        
        complexity = vulnerability_data.get('remediation_complexity', 'medium')
        if complexity in complexity_levels:
            level_data = complexity_levels[complexity]
            total_cost = level_data['hours'] * level_data['cost_per_hour']
            return {
                'estimated_hours': level_data['hours'],
                'hourly_rate_usd': level_data['cost_per_hour'],
                'total_cost_usd': total_cost,
                'complexity_level': complexity
            }
        
        return {'estimated_hours': 0, 'hourly_rate_usd': 0, 'total_cost_usd': 0, 'complexity_level': 'unknown'}