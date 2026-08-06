class MobilePatchFactory:
    """
    Deep link validation, OAuth token protection.
    Menghasilkan patch kode untuk kerentanan mobile.
    """
    
    def __init__(self):
        self.mobile_patch_templates = {
            'deep_link_validation': {
                'scheme_verification': '''
// Deep Link Validation Fix: Verify URL scheme and host
// BEFORE:
// Intent intent = getIntent();
// String data = intent.getDataString();
// handleDeepLink(data);
// AFTER:
Intent intent = getIntent();
Uri data = intent.getData();
if (data != null) {
    // Verify scheme and host
    if ("myapp".equals(data.getScheme()) && 
        "secure.myapp.com".equals(data.getHost())) {
        handleDeepLink(data);
    } else {
        Log.w("DeepLink", "Invalid deep link: " + data);
    }
}
''',
                'parameter_sanitization': '''
// Deep Link Validation Fix: Sanitize deep link parameters
// BEFORE:
// String userId = data.getQueryParameter("user_id");
// loadUserProfile(userId);
// AFTER:
String userIdParam = data.getQueryParameter("user_id");
if (userIdParam != null && userIdParam.matches("\\d+")) {
    long userId = Long.parseLong(userIdParam);
    loadUserProfile(userId);
} else {
    Log.w("DeepLink", "Invalid user_id parameter");
}
'''
            },
            'oauth_token_protection': {
                'secure_storage': '''
// OAuth Token Protection Fix: Use secure storage
// BEFORE:
// SharedPreferences prefs = getSharedPreferences("auth", MODE_PRIVATE);
// String token = prefs.getString("token", "");
// AFTER:
EncryptedSharedPreferences prefs = EncryptedSharedPreferences.create(
    "auth_secure",
    MasterKeys.getOrCreate(MasterKeys.AES256_GCM_SPEC),
    context,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
);
String token = prefs.getString("token", "");
''',
                'token_validation': '''
// OAuth Token Protection Fix: Validate token before use
// BEFORE:
// makeApiCall(token);
// AFTER:
if (isValidToken(token) && !isTokenExpired(token)) {
    makeApiCall(token);
} else {
    refreshTokenAndRetry();
}
'''
            }
        }
    
    def generate_mobile_patch(self, vulnerability_type: str, platform: str = 'android') -> str:
        """Hasilkan patch mobile untuk tipe kerentanan tertentu."""
        if vulnerability_type not in self.mobile_patch_templates:
            return f"// No patch template available for {vulnerability_type}\n// Please implement custom fix"
        
        templates = self.mobile_patch_templates[vulnerability_type]
        return next(iter(templates.values()))
    
    def generate_mobile_fix_recommendation(self, vuln_data: dict) -> dict:
        """Hasilkan rekomendasi perbaikan mobile lengkap."""
        vuln_type = vuln_data.get('type', 'unknown')
        platform = vuln_data.get('platform', 'android')
        
        patch_code = self.generate_mobile_patch(vuln_type, platform)
        
        return {
            'vulnerability_type': vuln_type,
            'platform': platform,
            'patch_code': patch_code,
            'security_best_practices': self._get_mobile_security_practices(vuln_type, platform),
            'testing_guidelines': self._get_mobile_testing_guidelines(vuln_type, platform)
        }
    
    def _get_mobile_security_practices(self, vuln_type: str, platform: str) -> str:
        """Dapatkan praktik keamanan mobile."""
        practices = {
            'deep_link_validation': f'Always validate deep link schemes, hosts, and parameters. Implement allowlist for trusted domains. Never trust user input from deep links without sanitization.',
            'oauth_token_protection': f'Use platform-specific secure storage (EncryptedSharedPreferences for Android, Keychain for iOS). Implement proper token validation and refresh mechanisms. Never store tokens in plain text.'
        }
        return practices.get(vuln_type, 'Follow platform security best practices and validate all input.')
    
    def _get_mobile_testing_guidelines(self, vuln_type: str, platform: str) -> list:
        """Dapatkan panduan pengujian mobile."""
        guidelines = {
            'deep_link_validation': [
                'Test deep links with malicious schemes (javascript:, data:)',
                'Test parameter injection in deep link parameters',
                'Test host spoofing attacks'
            ],
            'oauth_token_protection': [
                'Verify tokens are stored in secure storage',
                'Test token leakage in logs and memory dumps',
                'Verify token validation prevents replay attacks'
            ]
        }
        return guidelines.get(vuln_type, ['Test with original exploit', 'Verify secure storage implementation'])