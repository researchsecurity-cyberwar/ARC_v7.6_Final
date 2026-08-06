class AIPatchFactory:
    """
    LLM prompt sanitization, AI pipeline fixes.
    Menghasilkan patch untuk kerentanan sistem AI/LLM.
    """
    
    def __init__(self):
        self.ai_patch_templates = {
            'prompt_injection': {
                'input_sanitization': '''
// Prompt Injection Fix: Sanitize user input
// BEFORE:
// const prompt = `Answer this question: ${userInput}`;
// const response = await llm.generate(prompt);
// AFTER:
const sanitizedInput = sanitizeUserInput(userInput);
const prompt = `Answer this question: ${sanitizedInput}`;
const response = await llm.generate(prompt);

function sanitizeUserInput(input) {
    // Remove dangerous characters and patterns
    return input
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/system:/gi, '[REDACTED]')
        .replace(/user:/gi, '[REDACTED]')
        .replace(/assistant:/gi, '[REDACTED]');
}
''',
                'output_filtering': '''
// Prompt Injection Fix: Filter LLM output
// BEFORE:
// res.json({ response: llmResponse });
// AFTER:
const filteredResponse = filterLLMOutput(llmResponse);
res.json({ response: filteredResponse });

function filterLLMOutput(output) {
    // Remove system prompts and internal instructions
    return output
        .replace(/system:/gi, '')
        .replace(/user:/gi, '')
        .replace(/assistant:/gi, '')
        .trim();
}
'''
            },
            'training_data_leak': {
                'output_monitoring': '''
// Training Data Leak Fix: Monitor LLM output for sensitive data
// BEFORE:
// return llm.generate(prompt);
// AFTER:
const response = llm.generate(prompt);
if (containsSensitiveData(response)) {
    console.warn('Potential training data leak detected');
    return 'I cannot provide that information.';
}
return response;

function containsSensitiveData(text) {
    const sensitivePatterns = [
        /\\b\\d{3}-\\d{2}-\\d{4}\\b/, // SSN
        /\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b/, // Email
        /(?:password|secret|api_key)["']?\\s*[:=]\\s*["'][^"']+/ // Credentials
    ];
    return sensitivePatterns.some(pattern => pattern.test(text));
}
''',
                'prompt_template_isolation': '''
// Training Data Leak Fix: Isolate prompt templates
// BEFORE:
// const prompt = `You are a helpful assistant. ${userContext} ${userQuery}`;
// AFTER:
const systemPrompt = 'You are a helpful assistant.';
const userPrompt = `${sanitizeContext(userContext)} ${sanitizeQuery(userQuery)}`;
const prompt = `${systemPrompt}\\n\\n${userPrompt}`;
'''
            }
        }
    
    def generate_ai_patch(self, vulnerability_type: str, framework: str = 'generic') -> str:
        """Hasilkan patch AI untuk tipe kerentanan tertentu."""
        if vulnerability_type not in self.ai_patch_templates:
            return f"// No patch template available for {vulnerability_type}\n// Please implement custom fix"
        
        templates = self.ai_patch_templates[vulnerability_type]
        return next(iter(templates.values()))
    
    def generate_ai_fix_recommendation(self, vuln_data: dict) -> dict:
        """Hasilkan rekomendasi perbaikan AI lengkap."""
        vuln_type = vuln_data.get('type', 'unknown')
        ai_framework = vuln_data.get('ai_framework', 'generic')
        
        patch_code = self.generate_ai_patch(vuln_type, ai_framework)
        
        return {
            'vulnerability_type': vuln_type,
            'ai_framework': ai_framework,
            'patch_code': patch_code,
            'security_principles': self._get_ai_security_principles(vuln_type),
            'monitoring_requirements': self._get_ai_monitoring_requirements(vuln_type)
        }
    
    def _get_ai_security_principles(self, vuln_type: str) -> str:
        """Dapatkan prinsip keamanan AI."""
        principles = {
            'prompt_injection': 'Never trust user input in LLM prompts. Always sanitize and validate input before concatenation. Implement output filtering to prevent leakage of system instructions.',
            'training_data_leak': 'Monitor LLM output for sensitive data patterns. Implement redaction mechanisms for PII and credentials. Use separate prompt templates for system and user contexts.'
        }
        return principles.get(vuln_type, 'Implement defense in depth for AI systems.')
    
    def _get_ai_monitoring_requirements(self, vuln_type: str) -> list:
        """Dapatkan persyaratan pemantauan AI."""
        requirements = {
            'prompt_injection': [
                'Log all user inputs for security analysis',
                'Monitor for prompt injection patterns in real-time',
                'Implement rate limiting for suspicious inputs'
            ],
            'training_data_leak': [
                'Scan LLM output for PII and sensitive data',
                'Implement automatic redaction of detected sensitive data',
                'Audit training data for sensitive information'
            ]
        }
        return requirements.get(vuln_type, ['Monitor LLM inputs and outputs', 'Implement security logging'])