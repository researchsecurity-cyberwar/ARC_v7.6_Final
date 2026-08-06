class OpportunityDetector:
    """
    Detect high-value opportunities.
    Mendeteksi peluang bernilai tinggi dalam target.
    """
    
    def __init__(self):
        self.opportunity_indicators = {
            'high_bounty': {
                'signals': ['private_program', 'high_severity_rewards', 'critical_payout'],
                'value_score': 0.9
            },
            'low_competition': {
                'signals': ['new_program', 'few_researchers', 'undiscovered_scope'],
                'value_score': 0.8
            },
            'critical_infrastructure': {
                'signals': ['banking', 'healthcare', 'government', 'energy'],
                'value_score': 0.95
            },
            'emerging_technology': {
                'signals': ['web3', 'defi', 'ai_services', 'blockchain'],
                'value_score': 0.85
            }
        }
    
    def detect_opportunities(self, target_context: dict) -> list:
        """
        Deteksi peluang dalam konteks target.
        """
        opportunities = []
        target_description = str(target_context).lower()
        
        for opportunity_type, config in self.opportunity_indicators.items():
            signals_found = []
            for signal in config['signals']:
                if signal.lower() in target_description:
                    signals_found.append(signal)
            
            if signals_found:
                opportunities.append({
                    'type': opportunity_type,
                    'signals_detected': signals_found,
                    'value_score': config['value_score'],
                    'estimated_bounty_range': self._estimate_bounty_range(opportunity_type, target_context),
                    'recommended_focus': self._get_recommended_focus(opportunity_type)
                })
        
        # Urutkan berdasarkan nilai
        opportunities.sort(key=lambda x: x['value_score'], reverse=True)
        return opportunities[:5]  # Maksimal 5 peluang teratas
    
    def _estimate_bounty_range(self, opportunity_type: str, context: dict) -> str:
        """Estimasi rentang bounty."""
        base_ranges = {
            'high_bounty': '$5,000 - $50,000',
            'low_competition': '$1,000 - $10,000',
            'critical_infrastructure': '$10,000 - $100,000+',
            'emerging_technology': '$2,000 - $25,000'
        }
        return base_ranges.get(opportunity_type, '$500 - $5,000')
    
    def _get_recommended_focus(self, opportunity_type: str) -> str:
        """Dapatkan fokus yang direkomendasikan."""
        focus_areas = {
            'high_bounty': 'Focus on critical and high-severity vulnerabilities',
            'low_competition': 'Prioritize thorough reconnaissance and scope analysis',
            'critical_infrastructure': 'Emphasize business logic flaws and chain reactions',
            'emerging_technology': 'Specialize in protocol-specific vulnerabilities'
        }
        return focus_areas.get(opportunity_type, 'Apply comprehensive testing methodology')