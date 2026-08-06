class EconomicSimulator:
    """
    Generate economic impact proofs.
    Menghasilkan bukti dampak ekonomi sesuai permintaan.
    """
    
    def __init__(self):
        self.financial_models = {
            'bug_bounty': {
                'base_multiplier': 1000,
                'critical_factor': 50,
                'high_factor': 20,
                'medium_factor': 5
            },
            'data_breach': {
                'per_record_cost': 150,
                'regulatory_multiplier': 2.0,
                'reputation_multiplier': 1.5
            },
            'business_disruption': {
                'hourly_cost': 10000,
                'sla_penalty': 50000
            }
        }
    
    def simulate_economic_impact(self, impact_config: dict):
        """
        Simulasikan dampak ekonomi berdasarkan konfigurasi.
        """
        impact_type = impact_config.get('impact_type', 'bug_bounty')
        model = self.financial_models.get(impact_type, self.financial_models['bug_bounty'])
        
        if impact_type == 'bug_bounty':
            severity = impact_config.get('severity', 'medium')
            base_amount = model['base_multiplier']
            if severity == 'critical':
                amount = base_amount * model['critical_factor']
            elif severity == 'high':
                amount = base_amount * model['high_factor']
            else:
                amount = base_amount * model['medium_factor']
            
            return {
                'impact_type': impact_type,
                'estimated_bounty_usd': amount,
                'confidence_interval': [amount * 0.7, amount * 1.3],
                'factors_considered': ['severity', 'target_type', 'program_tier']
            }
        
        elif impact_type == 'data_breach':
            records_affected = impact_config.get('records_affected', 1000)
            base_cost = records_affected * model['per_record_cost']
            total_cost = base_cost * model['regulatory_multiplier'] * model['reputation_multiplier']
            
            return {
                'impact_type': impact_type,
                'records_affected': records_affected,
                'estimated_cost_usd': total_cost,
                'cost_breakdown': {
                    'direct_costs': base_cost,
                    'regulatory_fines': base_cost * (model['regulatory_multiplier'] - 1),
                    'reputation_damage': base_cost * (model['reputation_multiplier'] - 1)
                }
            }
        
        elif impact_type == 'business_disruption':
            downtime_hours = impact_config.get('downtime_hours', 1)
            base_cost = downtime_hours * model['hourly_cost']
            total_cost = base_cost + model['sla_penalty']
            
            return {
                'impact_type': impact_type,
                'downtime_hours': downtime_hours,
                'estimated_cost_usd': total_cost,
                'penalty_included': True
            }
        
        return {'error': 'Unsupported impact type'}