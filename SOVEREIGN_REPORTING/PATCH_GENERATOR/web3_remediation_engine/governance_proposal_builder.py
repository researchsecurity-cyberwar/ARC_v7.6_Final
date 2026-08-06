class GovernanceProposalBuilder:
    """
    DAO proposal templates.
    Membangun template proposal tata kelola DAO untuk perbaikan kerentanan.
    """
    
    def __init__(self):
        self.proposal_templates = {
            'emergency_upgrade': {
                'title': 'Emergency Security Upgrade - {contract_name}',
                'description': '''
## Emergency Security Proposal

This proposal addresses a critical security vulnerability discovered in the {contract_name} contract.

### Vulnerability Details
- **Type**: {vulnerability_type}
- **Impact**: {impact_level}
- **Discovery Date**: {discovery_date}

### Proposed Solution
Deploy the patched implementation contract at address: `{new_implementation}`

### Security Review
- [x] Code audit completed by {auditor}
- [x] Formal verification passed
- [x] Testnet deployment verified

### Execution Plan
1. Execute proposal after {timelock_hours} hour timelock
2. Monitor contract behavior post-upgrade
3. Report back to governance within 24 hours

### Risk Assessment
Low risk - patch addresses critical vulnerability with minimal code changes.
''',
                'execution_payload': '''
// Upgrade proposal payload
[
    {{
        "target": "{proxy_admin_address}",
        "function": "upgrade(address,address)",
        "args": ["{proxy_address}", "{new_implementation}"]
    }}
]
'''
            },
            'parameter_update': {
                'title': 'Security Parameter Update - {parameter_name}',
                'description': '''
## Security Parameter Update

This proposal updates security-critical parameters to mitigate potential risks.

### Current Issue
The current {parameter_name} value of {current_value} may allow {attack_vector}.

### Proposed Change
Update {parameter_name} from {current_value} to {new_value}.

### Justification
- Reduces attack surface by {risk_reduction_percentage}%
- Aligns with industry best practices
- Minimal impact on normal operations

### Testing
- [x] Parameter change tested on testnet
- [x] No adverse effects observed
- [x] Emergency rollback plan prepared

### Execution
Execute immediately after proposal approval.
''',
                'execution_payload': '''
// Parameter update payload
[
    {{
        "target": "{governor_address}",
        "function": "set{ParameterName}(uint256)",
        "args": ["{new_value}"]
    }}
]
'''
            }
        }
    
    def build_governance_proposal(self, proposal_type: str, proposal_data: dict) -> dict:
        """Bangun proposal tata kelola DAO."""
        if proposal_type not in self.proposal_templates:
            return {'error': f'Unknown proposal type: {proposal_type}'}
        
        template = self.proposal_templates[proposal_type]
        
        # Replace placeholders
        title = template['title'].format(**proposal_data)
        description = template['description'].format(**proposal_data)
        execution_payload = template['execution_payload'].format(**proposal_data)
        
        return {
            'proposal_type': proposal_type,
            'title': title,
            'description': description,
            'execution_payload': execution_payload,
            'required_signatures': proposal_data.get('required_signatures', 5),
            'timelock_hours': proposal_data.get('timelock_hours', 48),
            'voting_period_days': proposal_data.get('voting_period_days', 3)
        }