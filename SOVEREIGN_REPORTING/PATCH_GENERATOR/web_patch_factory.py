class WebPatchFactory:
    """
    XSS, SQLi, SSRF fixes.
    Menghasilkan patch kode spesifik untuk kerentanan web.
    """
    
    def __init__(self):
        self.patch_templates = {
            'xss': {
                'html_context': '''
// XSS Fix: Use textContent instead of innerHTML
// BEFORE:
// element.innerHTML = userInput;
// AFTER:
element.textContent = userInput;
''',
                'attribute_context': '''
// XSS Fix: Proper attribute value encoding
// BEFORE:
// element.setAttribute('href', userInput);
// AFTER:
const safeUrl = encodeURI(userInput);
element.setAttribute('href', safeUrl);
''',
                'javascript_context': '''
// XSS Fix: Avoid eval() and dynamic code execution
// BEFORE:
// eval('var x = ' + userInput);
// AFTER:
// Use JSON.parse() for data or template literals for strings
const data = JSON.parse(safeData);
'''
            },
            'sqli': {
                'parameterized_queries': '''
// SQLi Fix: Use parameterized queries
// BEFORE:
// const query = `SELECT * FROM users WHERE id = ${userId}`;
// AFTER:
const query = 'SELECT * FROM users WHERE id = ?';
db.query(query, [userId], callback);
''',
                'input_validation': '''
// SQLi Fix: Validate and sanitize input
// BEFORE:
// const username = req.body.username;
// AFTER:
const username = req.body.username;
if (!/^[a-zA-Z0-9_]+$/.test(username)) {
    throw new Error('Invalid username format');
}
'''
            },
            'ssrf': {
                'allowlist_validation': '''
// SSRF Fix: Implement URL allowlist
// BEFORE:
// const url = req.query.url;
// fetch(url);
// AFTER:
const allowedDomains = ['api.trusted.com', 'cdn.company.com'];
const url = new URL(req.query.url);
if (!allowedDomains.includes(url.hostname)) {
    throw new Error('URL not allowed');
}
fetch(url.toString());
''',
                'protocol_restriction': '''
// SSRF Fix: Restrict URL protocols
// BEFORE:
// fetch(userProvidedUrl);
// AFTER:
const url = new URL(userProvidedUrl);
if (url.protocol !== 'https:') {
    throw new Error('Only HTTPS allowed');
}
fetch(url.toString());
'''
            }
        }
    
    def generate_web_patch(self, vulnerability_type: str, context: str = 'html_context') -> str:
        """
        Hasilkan patch web untuk tipe kerentanan tertentu.
        """
        if vulnerability_type not in self.patch_templates:
            return f"// No patch template available for {vulnerability_type}\n// Please implement custom fix"
        
        templates = self.patch_templates[vulnerability_type]
        if context in templates:
            return templates[context]
        else:
            # Return first available template
            return next(iter(templates.values()))
    
    def generate_complete_fix_recommendation(self, vuln_data: dict) -> dict:
        """
        Hasilkan rekomendasi perbaikan lengkap.
        """
        vuln_type = vuln_data.get('type', 'unknown')
        language = vuln_data.get('language', 'javascript')
        framework = vuln_data.get('framework', 'generic')
        
        patch_code = self.generate_web_patch(vuln_type, vuln_data.get('context', 'html_context'))
        
        return {
            'vulnerability_type': vuln_type,
            'language': language,
            'framework': framework,
            'patch_code': patch_code,
            'implementation_notes': self._get_implementation_notes(vuln_type, language, framework),
            'testing_recommendations': self._get_testing_recommendations(vuln_type)
        }
    
    def _get_implementation_notes(self, vuln_type: str, language: str, framework: str) -> str:
        """Dapatkan catatan implementasi."""
        notes = {
            'xss': f'Ensure all user input is properly encoded based on context (HTML, JavaScript, URL, CSS). Consider implementing Content Security Policy (CSP) as defense in depth.',
            'sqli': f'Use parameterized queries or prepared statements in {language}. Never concatenate user input directly into SQL queries. Validate input format before processing.',
            'ssrf': f'Implement strict allowlist for URLs and domains. Disable unnecessary URL protocols (file://, gopher://, dict://). Use network-level restrictions where possible.'
        }
        return notes.get(vuln_type, 'Implement the provided patch and test thoroughly in staging environment.')
    
    def _get_testing_recommendations(self, vuln_type: str) -> list:
        """Dapatkan rekomendasi pengujian."""
        tests = {
            'xss': [
                'Test with <script>alert(1)</script>',
                'Test with javascript:alert(1)',
                'Test with SVG onload vectors',
                'Verify CSP headers are properly configured'
            ],
            'sqli': [
                'Test with \' OR \'1\'=\'1',
                'Test with UNION SELECT attacks',
                'Test with time-based blind injection',
                'Verify error messages don\'t leak database structure'
            ],
            'ssrf': [
                'Test with http://127.0.0.1:80',
                'Test with http://localhost:80',
                'Test with file:///etc/passwd',
                'Verify internal network addresses are blocked'
            ]
        }
        return tests.get(vuln_type, ['Test with original payload', 'Verify fix prevents exploitation'])