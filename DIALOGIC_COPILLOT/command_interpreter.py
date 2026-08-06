import re

class CommandInterpreter:
    """
    Natural language → operational intent (“Scan Bank XYZ”).
    Menginterpretasikan perintah bahasa alami menjadi maksud operasional.
    """
    
    def __init__(self):
        self.command_patterns = {
            r'(?:scan|check|test)\s+(?:for\s+)?(?:vulnerabilities|bugs|security)\s+(?:on\s+|in\s+)?([a-zA-Z0-9.-]+)': {
                'action': 'vulnerability_scan',
                'parameters': ['target']
            },
            r'(?:scan|enumerate|discover)\s+subdomains?\s+(?:of\s+|for\s+)?([a-zA-Z0-9.-]+)': {
                'action': 'subdomain_enumeration',
                'parameters': ['target']
            },
            r'(?:exploit|attack|compromise)\s+([a-zA-Z0-9.-]+)\s+(?:with\s+)?([a-zA-Z0-9_-]+)': {
                'action': 'exploitation',
                'parameters': ['target', 'vulnerability_type']
            },
            r'(?:report|document|write)\s+(?:bug|vulnerability|finding)\s+(?:for\s+)?([a-zA-Z0-9.-]+)': {
                'action': 'report_generation',
                'parameters': ['target']
            },
            r'(?:monitor|watch|track)\s+([a-zA-Z0-9.-]+)\s+(?:for\s+)?(?:changes|updates|new\s+programs)': {
                'action': 'continuous_monitoring',
                'parameters': ['target']
            }
        }
    
    def interpret_command(self, natural_language: str) -> dict:
        """
        Interpretasikan perintah bahasa alami.
        """
        natural_language = natural_language.strip().lower()
        
        for pattern, template in self.command_patterns.items():
            match = re.search(pattern, natural_language, re.IGNORECASE)
            if match:
                # Ekstrak parameter
                parameters = {}
                for i, param_name in enumerate(template['parameters']):
                    if i < len(match.groups()):
                        parameters[param_name] = match.group(i + 1)
                
                return {
                    'original_command': natural_language,
                    'interpreted_action': template['action'],
                    'parameters': parameters,
                    'confidence': 0.9 if match else 0.5
                }
        
        # Jika tidak ada pola yang cocok, coba analisis dasar
        return self._fallback_interpretation(natural_language)
    
    def _fallback_interpretation(self, command: str) -> dict:
        """Interpretasi fallback untuk perintah yang tidak dikenali."""
        # Cari kata kunci umum
        keywords = {
            'scan': 'vulnerability_scan',
            'exploit': 'exploitation',
            'report': 'report_generation',
            'monitor': 'continuous_monitoring',
            'find': 'vulnerability_scan'
        }
        
        for keyword, action in keywords.items():
            if keyword in command:
                # Coba ekstrak target dari akhir perintah
                target_match = re.search(r'([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', command)
                target = target_match.group(1) if target_match else 'unknown_target'
                
                return {
                    'original_command': command,
                    'interpreted_action': action,
                    'parameters': {'target': target},
                    'confidence': 0.6
                }
        
        return {
            'original_command': command,
            'interpreted_action': 'unknown',
            'parameters': {},
            'confidence': 0.1,
            'error': 'Could not interpret command'
        }