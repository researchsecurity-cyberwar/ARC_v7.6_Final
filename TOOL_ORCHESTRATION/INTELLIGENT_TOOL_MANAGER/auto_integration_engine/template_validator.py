import yaml
import json
import os
from typing import Dict, List

class TemplateValidator:
    """
    Validate YAML templates syntax & safety.
    Memvalidasi sintaksis dan keamanan template YAML.
    """
    
    def __init__(self):
        self.required_fields = {
            'tool': ['name', 'description', 'command'],
            'workflow': ['name', 'steps', 'output_format']
        }
        self.dangerous_patterns = [
            r'rm\s+-rf',
            r'shred\s+',
            r'del\s+/s\s+/q',
            r'format\s+',
            r'encrypt\s+.*-password'
        ]
    
    def validate_template(self, template_path: str) -> Dict:
        """
        Validasi template YAML.
        """
        results = {
            'template_path': template_path,
            'syntax_valid': False,
            'structure_valid': False,
            'safety_valid': False,
            'errors': [],
            'success': False
        }
        
        try:
            # Validasi sintaksis YAML
            with open(template_path, 'r') as f:
                template_data = yaml.safe_load(f)
            
            results['syntax_valid'] = True
            
            # Validasi struktur
            structure_errors = self._validate_structure(template_data)
            if not structure_errors:
                results['structure_valid'] = True
            else:
                results['errors'].extend(structure_errors)
            
            # Validasi keamanan
            safety_errors = self._validate_safety(template_data)
            if not safety_errors:
                results['safety_valid'] = True
            else:
                results['errors'].extend(safety_errors)
            
            results['success'] = all([
                results['syntax_valid'],
                results['structure_valid'],
                results['safety_valid']
            ])
        
        except yaml.YAMLError as e:
            results['errors'].append(f'YAML syntax error: {str(e)}')
        except Exception as e:
            results['errors'].append(f'Template validation failed: {str(e)}')
        
        return results
    
    def _validate_structure(self, template_data: dict) -> List[str]:
        """Validasi struktur template."""
        errors = []
        
        # Cek tipe template
        template_type = template_data.get('type', 'tool')
        required = self.required_fields.get(template_type, [])
        
        for field in required:
            if field not in template_data:
                errors.append(f'Missing required field: {field}')
        
        return errors
    
    def _validate_safety(self, template_data: dict) -> List[str]:
        """Validasi keamanan template."""
        errors = []
        
        # Cek perintah berbahaya
        command = template_data.get('command', '')
        for pattern in self.dangerous_patterns:
            if pattern in command.lower():
                errors.append(f'Dangerous pattern detected: {pattern}')
        
        # Cek parameter berbahaya
        parameters = template_data.get('parameters', {})
        for param_name, param_config in parameters.items():
            if 'default' in param_config:
                default_value = str(param_config['default']).lower()
                for pattern in self.dangerous_patterns:
                    if pattern in default_value:
                        errors.append(f'Dangerous default value in parameter {param_name}: {pattern}')
        
        return errors