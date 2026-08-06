class APIPatchFactory:
    """
    BOLA, mass assignment fixes.
    Menghasilkan patch kode untuk kerentanan API.
    """
    
    def __init__(self):
        self.api_patch_templates = {
            'bola': {
                'authorization_check': '''
// BOLA Fix: Implement proper authorization check
// BEFORE:
// const user = await User.findById(req.params.id);
// res.json(user);
// AFTER:
const user = await User.findById(req.params.id);
if (user.ownerId !== req.user.id && !req.user.isAdmin) {
    throw new Error('Unauthorized access');
}
res.json(user);
''',
                'scope_validation': '''
// BOLA Fix: Validate resource scope
// BEFORE:
// const resource = getResource(req.params.resourceId);
// AFTER:
const resource = getResource(req.params.resourceId);
if (!userHasAccess(req.user, resource)) {
    throw new Error('Access denied');
}
'''
            },
            'mass_assignment': {
                'whitelist_approach': '''
// Mass Assignment Fix: Use whitelist approach
// BEFORE:
// const user = new User(req.body);
// AFTER:
const allowedFields = ['name', 'email', 'profile'];
const userData = {};
for (const field of allowedFields) {
    if (field in req.body) {
        userData[field] = req.body[field];
    }
}
const user = new User(userData);
''',
                'explicit_assignment': '''
// Mass Assignment Fix: Explicit field assignment
// BEFORE:
// Object.assign(user, req.body);
// AFTER:
user.name = req.body.name;
user.email = req.body.email;
// Only assign explicitly allowed fields
'''
            }
        }
    
    def generate_api_patch(self, vulnerability_type: str, context: str = 'authorization_check') -> str:
        """Hasilkan patch API untuk tipe kerentanan tertentu."""
        if vulnerability_type not in self.api_patch_templates:
            return f"// No patch template available for {vulnerability_type}\n// Please implement custom fix"
        
        templates = self.api_patch_templates[vulnerability_type]
        if context in templates:
            return templates[context]
        else:
            return next(iter(templates.values()))
    
    def generate_api_fix_recommendation(self, vuln_data: dict) -> dict:
        """Hasilkan rekomendasi perbaikan API lengkap."""
        vuln_type = vuln_data.get('type', 'unknown')
        api_framework = vuln_data.get('api_framework', 'express')
        
        patch_code = self.generate_api_patch(vuln_type, vuln_data.get('context', 'authorization_check'))
        
        return {
            'vulnerability_type': vuln_type,
            'api_framework': api_framework,
            'patch_code': patch_code,
            'security_principles': self._get_security_principles(vuln_type),
            'testing_scenarios': self._get_api_testing_scenarios(vuln_type)
        }
    
    def _get_security_principles(self, vuln_type: str) -> str:
        """Dapatkan prinsip keamanan."""
        principles = {
            'bola': 'Implement proper authorization checks for every object access. Never trust client-provided IDs without validation.',
            'mass_assignment': 'Use whitelist approach for object creation/update. Never allow direct mapping of client input to model attributes.'
        }
        return principles.get(vuln_type, 'Follow principle of least privilege and validate all input.')
    
    def _get_api_testing_scenarios(self, vuln_type: str) -> list:
        """Dapatkan skenario pengujian API."""
        scenarios = {
            'bola': [
                'Access another user\'s resource with valid session',
                'Modify resource ID in request to access admin resources',
                'Test with UUID enumeration to find accessible resources'
            ],
            'mass_assignment': [
                'Add admin=true to user creation request',
                'Include password field in profile update',
                'Add role field to registration request'
            ]
        }
        return scenarios.get(vuln_type, ['Test with original exploit payload', 'Verify unauthorized fields are rejected'])