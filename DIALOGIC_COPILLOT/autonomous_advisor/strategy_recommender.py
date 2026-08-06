class StrategyRecommender:
    """
    Recommend optimal strategies.
    Merekomendasikan strategi optimal berdasarkan konteks dan risiko.
    """
    
    def __init__(self):
        self.strategy_templates = {
            'high_value_low_risk': {
                'approach': 'stealth_recon_first',
                'tools': ['httpx', 'gau', 'nuclei_light'],
                'timing': 'off_peak_hours',
                'focus': 'business_logic_flaws'
            },
            'high_value_high_risk': {
                'approach': 'phased_escalation',
                'tools': ['manual_testing', 'custom_exploits', 'chain_exploiter'],
                'timing': 'controlled_windows',
                'focus': 'critical_chain_reactions'
            },
            'low_value_low_risk': {
                'approach': 'automated_scanning',
                'tools': ['nuclei', 'dalfox', 'sqlmap'],
                'timing': 'background_processing',
                'focus': 'common_vulnerabilities'
            },
            'emerging_technology': {
                'approach': 'specialized_research',
                'tools': ['slither', 'web3_scanner', 'protocol_analyzer'],
                'timing': 'continuous_monitoring',
                'focus': 'protocol_specific_flaws'
            }
        }
    
    def recommend_optimal_strategy(self, opportunity_assessment: dict, risk_assessment: dict) -> dict:
        """
        Rekomendasikan strategi optimal berdasarkan penilaian peluang dan risiko.
        """
        opportunity_score = max(
            opp.get('value_score', 0) 
            for opp in opportunity_assessment.get('opportunities', [])
        ) if opportunity_assessment.get('opportunities') else 0
        
        risk_score = risk_assessment.get('total_risk_score', 0)
        
        # Tentukan strategi berdasarkan matriks peluang-risiko
        if opportunity_score >= 0.8 and risk_score <= 0.3:
            strategy_key = 'high_value_low_risk'
        elif opportunity_score >= 0.8 and risk_score > 0.3:
            strategy_key = 'high_value_high_risk'
        elif opportunity_score < 0.8 and risk_score <= 0.3:
            strategy_key = 'low_value_low_risk'
        else:
            strategy_key = 'emerging_technology'
        
        base_strategy = self.strategy_templates[strategy_key].copy()
        
        return {
            'strategy_type': strategy_key,
            'recommended_approach': base_strategy['approach'],
            'suggested_tools': base_strategy['tools'],
            'optimal_timing': base_strategy['timing'],
            'primary_focus': base_strategy['focus'],
            'confidence_score': 0.85,
            'adaptation_notes': self._generate_adaptation_notes(strategy_key, opportunity_assessment, risk_assessment)
        }
    
    def _generate_adaptation_notes(self, strategy_key: str, opportunity: dict, risk: dict) -> str:
        """Hasilkan catatan adaptasi untuk strategi."""
        notes = {
            'high_value_low_risk': 'Leverage low competition and high bounty potential with minimal risk exposure',
            'high_value_high_risk': 'Proceed with extreme caution; ensure all legal boundaries are respected',
            'low_value_low_risk': 'Efficient use of automated tools for maximum coverage with minimal investment',
            'emerging_technology': 'Stay ahead of the curve with specialized knowledge in cutting-edge technologies'
        }
        return notes.get(strategy_key, 'Standard operational approach recommended')