import re

class EthicsValidator:
    """
    Ensure responses comply with ethics.
    Memastikan respons mematuhi prinsip etika dan pedoman industri.
    """
    
    def __init__(self):
        self.ethical_guidelines = {
            'prohibited_content': [
                r'(?:threaten|extort|blackmail|demand payment|legal action)',
                r'(?:personal attack|insult|offensive language)',
                r'(?:disclose without permission|leak|share publicly)',
                r'(?:bypass authorization|unauthorized access|illegal)'
            ],
            'required_elements': [
                r'(?:thank|appreciate|grateful)',
                r'(?:professional|respectful|courteous)',
                r'(?:scope|program policy|guidelines)',
                r'(?:responsible disclosure|ethical|compliance)'
            ],
            'tone_guidelines': {
                'avoid_aggressive': ['you must', 'you should', 'obviously', 'clearly'],
                'prefer_collaborative': ['we could', 'perhaps', 'consider', 'suggest']
            }
        }
    
    def validate_response_ethics(self, response_text: str, platform: str = None) -> dict:
        """
        Validasi etika respons yang dihasilkan.
        """
        validation_result = {
            'response_text': response_text[:200] + '...' if len(response_text) > 200 else response_text,
            'platform': platform,
            'ethical_compliance': True,
            'violations': [],
            'recommendations': [],
            'confidence_score': 1.0
        }
        
        try:
            # Cek konten terlarang
            prohibited_violations = self._check_prohibited_content(response_text)
            if prohibited_violations:
                validation_result['ethical_compliance'] = False
                validation_result['violations'].extend(prohibited_violations)
                validation_result['confidence_score'] -= len(prohibited_violations) * 0.3
            
            # Cek elemen yang diperlukan
            missing_elements = self._check_required_elements(response_text)
            if missing_elements:
                validation_result['violations'].extend(missing_elements)
                validation_result['recommendations'].append('Include required professional elements')
                validation_result['confidence_score'] -= len(missing_elements) * 0.2
            
            # Cek nada/tone
            tone_issues = self._check_tone_guidelines(response_text)
            if tone_issues:
                validation_result['violations'].extend(tone_issues)
                validation_result['recommendations'].append('Use more collaborative language')
                validation_result['confidence_score'] -= len(tone_issues) * 0.1
            
            # Pastikan skor tidak negatif
            validation_result['confidence_score'] = max(0.0, validation_result['confidence_score'])
        
        except Exception as e:
            validation_result['error'] = f'Ethics validation failed: {str(e)}'
            validation_result['ethical_compliance'] = False
        
        return validation_result
    
    def _check_prohibited_content(self, text: str) -> list:
        """Cek konten terlarang dalam respons."""
        violations = []
        text_lower = text.lower()
        
        for pattern in self.ethical_guidelines['prohibited_content']:
            if re.search(pattern, text_lower):
                violations.append(f'Prohibited content detected: {pattern}')
        
        return violations
    
    def _check_required_elements(self, text: str) -> list:
        """Cek elemen yang diperlukan dalam respons."""
        missing = []
        text_lower = text.lower()
        
        for element in self.ethical_guidelines['required_elements']:
            if not re.search(element, text_lower):
                missing.append(f'Missing required element: {element}')
        
        return missing
    
    def _check_tone_guidelines(self, text: str) -> list:
        """Cek panduan nada/tone."""
        issues = []
        text_lower = text.lower()
        
        # Cek bahasa agresif yang harus dihindari
        for aggressive_phrase in self.ethical_guidelines['tone_guidelines']['avoid_aggressive']:
            if aggressive_phrase in text_lower:
                issues.append(f'Aggressive tone detected: "{aggressive_phrase}"')
        
        # Periksa apakah menggunakan bahasa kolaboratif
        collaborative_found = any(
            phrase in text_lower 
            for phrase in self.ethical_guidelines['tone_guidelines']['prefer_collaborative']
        )
        if not collaborative_found:
            issues.append('Missing collaborative language')
        
        return issues
    
    def suggest_ethical_improvements(self, response_text: str) -> str:
        """
        Sarankan perbaikan etis untuk respons.
        """
        validation = self.validate_response_ethics(response_text)
        
        if validation['ethical_compliance']:
            return response_text
        
        improved_response = response_text
        
        # Hapus konten terlarang (placeholder - implementasi penuh perlu NLP)
        for violation in validation['violations']:
            if 'Prohibited content' in violation:
                # Ganti dengan bahasa profesional
                improved_response = re.sub(
                    r'(you must|obviously|clearly)', 
                    'Consider', 
                    improved_response, 
                    flags=re.IGNORECASE
                )
        
        # Tambahkan elemen yang diperlukan jika belum ada
        if 'thank' not in improved_response.lower():
            improved_response = "Thank you for your feedback. " + improved_response
        
        if 'professional' not in improved_response.lower():
            improved_response += "\n\nI hope this response meets professional standards and program guidelines."
        
        return improved_response