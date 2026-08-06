import json
import os

class DynamicTemplateGenerator:
    """
    Generate template real-time dari form.
    Menghasilkan template dinamis berdasarkan struktur form yang di-scrap.
    """
    
    def __init__(self, template_dir="~/.arc/templates"):
        self.template_dir = os.path.expanduser(template_dir)
        os.makedirs(self.template_dir, exist_ok=True)
    
    def generate_dynamic_template(self, form_data: dict):
        """
        Hasilkan template dinamis dari data form.
        """
        results = {
            'form_data': form_data,
            'template_generated': False,
            'template_path': None,
            'template_content': None
        }
        
        try:
            program_name = form_data.get('program_name', 'unknown').lower().replace(' ', '_')
            timestamp = int(time.time())
            template_filename = f"immunefi_{program_name}_{timestamp}.json"
            template_path = os.path.join(self.template_dir, template_filename)
            
            # Bangun template berdasarkan field form
            template = {
                'program_name': form_data.get('program_name'),
                'program_url': form_data.get('program_url'),
                'bounty_amount': form_data.get('bounty_amount'),
                'vulnerability_types': form_data.get('vulnerability_types', []),
                'required_fields': {},
                'optional_fields': {},
                'submission_endpoint': form_data.get('submission_endpoint'),
                'template_version': '1.0'
            }
            
            # Pisahkan field wajib dan opsional
            for field in form_data.get('form_fields', []):
                field_info = {
                    'type': field.get('type', 'text'),
                    'label': field.get('label', field.get('name')),
                    'validation_rules': self._get_validation_rules(field)
                }
                
                if field.get('required', False):
                    template['required_fields'][field['name']] = field_info
                else:
                    template['optional_fields'][field['name']] = field_info
            
            # Simpan template
            with open(template_path, 'w') as f:
                json.dump(template, f, indent=2)
            
            results.update({
                'template_generated': True,
                'template_path': template_path,
                'template_content': template
            })
        
        except Exception as e:
            results['error'] = f'Template generation failed: {str(e)}'
        
        return results
    
    def _get_validation_rules(self, field: dict) -> dict:
        """Dapatkan aturan validasi berdasarkan tipe field."""
        field_type = field.get('type', 'text').lower()
        field_name = field.get('name', '').lower()
        
        rules = {'required': field.get('required', False)}
        
        if 'email' in field_name:
            rules['pattern'] = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        elif 'url' in field_name or field_type == 'url':
            rules['pattern'] = r'^https?://.*'
        elif 'amount' in field_name or 'bounty' in field_name:
            rules['min_value'] = 0
            rules['type'] = 'number'
        elif 'description' in field_name or 'detail' in field_name:
            rules['min_length'] = 50
            rules['max_length'] = 10000
        
        return rules