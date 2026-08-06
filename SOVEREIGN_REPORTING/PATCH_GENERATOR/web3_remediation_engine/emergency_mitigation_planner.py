class EmergencyMitigationPlanner:
    """
    Emergency pause & fund recovery.
    Merencanakan mitigasi darurat untuk kerentanan kritis Web3.
    """
    
    def __init__(self):
        self.emergency_measures = {
            'protocol_pause': {
                'description': 'Emergency pause of protocol functionality',
                'implementation': '''
// Emergency pause function
function emergencyPause() external onlyEmergencyCouncil {
    paused = true;
    emit EmergencyPaused(msg.sender);
}

// Modifier to check pause state
modifier whenNotPaused() {
    require(!paused, "Protocol paused");
    _;
}
''',
                'activation_requirements': [
                    'Multi-sig emergency council approval (3/5)',
                    'Security team confirmation of active exploitation',
                    'Legal team consultation'
                ]
            },
            'fund_recovery': {
                'description': 'Emergency fund recovery mechanism',
                'implementation': '''
// Emergency fund recovery
function emergencyRecover(address token, address recipient, uint256 amount) 
    external onlyEmergencyCouncil 
{
    require(block.timestamp > recoveryDelay, "Recovery delay not met");
    IERC20(token).transfer(recipient, amount);
    emit FundsRecovered(token, recipient, amount);
}
''',
                'activation_requirements': [
                    'Proof of funds at risk',
                    'Multi-sig approval (4/5)',
                    '72-hour recovery delay',
                    'Public announcement'
                ]
            }
        }
    
    def plan_emergency_mitigation(self, vulnerability_data: dict) -> dict:
        """Rencanakan mitigasi darurat untuk kerentanan."""
        vuln_type = vulnerability_data.get('type', 'unknown')
        impact_level = vulnerability_data.get('impact_level', 'medium')
        
        # Tentukan tindakan darurat berdasarkan dampak
        if impact_level == 'critical':
            measures = ['protocol_pause', 'fund_recovery']
        elif impact_level == 'high':
            measures = ['protocol_pause']
        else:
            measures = []
        
        mitigation_plan = {
            'vulnerability_data': vulnerability_data,
            'recommended_measures': [],
            'activation_timeline': {},
            'stakeholder_notifications': []
        }
        
        for measure in measures:
            if measure in self.emergency_measures:
                measure_data = self.emergency_measures[measure]
                mitigation_plan['recommended_measures'].append({
                    'measure_type': measure,
                    'description': measure_data['description'],
                    'implementation': measure_data['implementation'],
                    'activation_requirements': measure_data['activation_requirements']
                })
                
                # Timeline aktivasi
                mitigation_plan['activation_timeline'][measure] = self._get_activation_timeline(measure)
        
        # Notifikasi stakeholder
        mitigation_plan['stakeholder_notifications'] = self._get_stakeholder_notifications(vuln_type, impact_level)
        
        return mitigation_plan
    
    def _get_activation_timeline(self, measure: str) -> dict:
        """Dapatkan timeline aktivasi untuk tindakan darurat."""
        timelines = {
            'protocol_pause': {
                'detection_to_confirmation': '1 hour',
                'confirmation_to_activation': '30 minutes',
                'total_time': '1.5 hours'
            },
            'fund_recovery': {
                'detection_to_approval': '24 hours',
                'approval_to_execution': '72 hours (delay)',
                'total_time': '96 hours'
            }
        }
        return timelines.get(measure, {'total_time': 'Immediate'})
    
    def _get_stakeholder_notifications(self, vuln_type: str, impact_level: str) -> list:
        """Dapatkan daftar notifikasi stakeholder."""
        notifications = [
            'Security team',
            'Development team',
            'Governance council',
            'Legal counsel'
        ]
        
        if impact_level == 'critical':
            notifications.extend([
                'Insurance provider',
                'Regulatory bodies',
                'Public announcement'
            ])
        
        return notifications