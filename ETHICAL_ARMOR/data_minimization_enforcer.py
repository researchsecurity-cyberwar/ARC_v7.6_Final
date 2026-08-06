import re
import json
from typing import List, Dict

class DataMinimizationEnforcer:
    """
    Exfil 1 record only for PoC (ethical constraint).
    Menerapkan pembatasan etis untuk hanya mengekstraksi 1 record untuk PoC.
    """
    
    def __init__(self):
        self.sensitive_patterns = {
            'pii': r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            'password': r'(?i)password["\']?\s*[:=]\s*["\']([^"\']{8,})',
            'api_key': r'(?i)api[_-]?key["\']?\s*[:=]\s*["\']([A-Za-z0-9_-]{32,})'
        }
    
    def enforce_data_minimization(self, data_input: str, context: dict) -> dict:
        """
        Terapkan pembatasan minimisasi data.
        """
        results = {
            'original_data_size': len(data_input),
            'minimized_data': '',
            'records_extracted': 0,
            'sensitive_data_found': [],
            'ethically_compliant': False,
            'compliance_notes': []
        }
        
        try:
            # Identifikasi jenis data
            data_type = context.get('data_type', 'unknown')
            
            if data_type == 'database_dump':
                minimized = self._minimize_database_data(data_input)
            elif data_type == 'file_system':
                minimized = self._minimize_file_system_data(data_input)
            elif data_type == 'api_response':
                minimized = self._minimize_api_response_data(data_input)
            else:
                minimized = self._minimize_generic_data(data_input)
            
            results['minimized_data'] = minimized['data']
            results['records_extracted'] = minimized['record_count']
            results['sensitive_data_found'] = minimized['sensitive_items']
            
            # Verifikasi kepatuhan etis
            ethical_check = self._verify_ethical_compliance(minimized, context)
            results['ethically_compliant'] = ethical_check['compliant']
            results['compliance_notes'] = ethical_check['notes']
        
        except Exception as e:
            results['error'] = f'Data minimization failed: {str(e)}'
        
        return results
    
    def _minimize_database_data(self, data_input: str) -> dict:
        """Minimalkan data dump database."""
        lines = data_input.split('\n')
        first_record = ""
        record_count = 0
        sensitive_items = []
        
        for line in lines:
            if line.strip() and not line.startswith('--'):
                if record_count == 0:
                    first_record = line
                    # Cari data sensitif dalam record pertama
                    sensitive_items = self._find_sensitive_data(first_record)
                record_count += 1
                if record_count >= 1:  # Hanya ambil 1 record
                    break
        
        return {
            'data': first_record,
            'record_count': 1 if first_record else 0,
            'sensitive_items': sensitive_items
        }
    
    def _minimize_file_system_data(self, data_input: str) -> dict:
        """Minimalkan data filesystem."""
        lines = data_input.split('\n')
        first_file = ""
        file_count = 0
        sensitive_items = []
        
        for line in lines:
            if line.strip() and ('/' in line or '\\' in line):
                if file_count == 0:
                    first_file = line
                    sensitive_items = self._find_sensitive_data(first_file)
                file_count += 1
                if file_count >= 1:
                    break
        
        return {
            'data': first_file,
            'record_count': 1 if first_file else 0,
            'sensitive_items': sensitive_items
        }
    
    def _minimize_api_response_data(self, data_input: str) -> dict:
        """Minimalkan data respons API."""
        try:
            # Coba parse sebagai JSON
            json_data = json.loads(data_input)
            if isinstance(json_data, list):
                first_item = json_data[0] if json_data else {}
                sensitive_items = self._find_sensitive_data_in_json(first_item)
                return {
                    'data': json.dumps(first_item),
                    'record_count': 1 if first_item else 0,
                    'sensitive_items': sensitive_items
                }
            else:
                sensitive_items = self._find_sensitive_data_in_json(json_data)
                return {
                    'data': data_input,
                    'record_count': 1,
                    'sensitive_items': sensitive_items
                }
        except:
            # Jika bukan JSON, perlakukan sebagai teks biasa
            first_line = data_input.split('\n')[0] if '\n' in data_input else data_input
            sensitive_items = self._find_sensitive_data(first_line)
            return {
                'data': first_line,
                'record_count': 1,
                'sensitive_items': sensitive_items
            }
    
    def _minimize_generic_data(self, data_input: str) -> dict:
        """Minimalkan data generik."""
        first_line = data_input.split('\n')[0] if '\n' in data_input else data_input
        sensitive_items = self._find_sensitive_data(first_line)
        return {
            'data': first_line,
            'record_count': 1,
            'sensitive_items': sensitive_items
        }
    
    def _find_sensitive_data(self, text: str) -> List[Dict]:
        """Temukan data sensitif dalam teks."""
        sensitive_items = []
        text_lower = text.lower()
        
        for data_type, pattern in self.sensitive_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                sensitive_items.append({
                    'type': data_type,
                    'value_preview': match.group()[:20] + '...',
                    'position': match.span()
                })
        
        return sensitive_items
    
    def _find_sensitive_data_in_json(self, json_obj: dict) -> List[Dict]:
        """Temukan data sensitif dalam objek JSON."""
        sensitive_items = []
        
        def scan_json(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    if isinstance(value, str):
                        for data_type, pattern in self.sensitive_patterns.items():
                            if re.search(pattern, value, re.IGNORECASE):
                                sensitive_items.append({
                                    'type': data_type,
                                    'value_preview': value[:20] + '...',
                                    'path': new_path
                                })
                    else:
                        scan_json(value, new_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    scan_json(item, f"{path}[{i}]")
        
        scan_json(json_obj)
        return sensitive_items
    
    def _verify_ethical_compliance(self, minimized_data: dict, context: dict) -> dict:
        """Verifikasi kepatuhan etis."""
        notes = []
        compliant = True
        
        # Cek jumlah record
        if minimized_data['record_count'] > 1:
            compliant = False
            notes.append('More than 1 record extracted - violates data minimization principle')
        
        # Cek data sensitif
        if minimized_data['sensitive_items']:
            notes.append(f'{len(minimized_data["sensitive_items"])} sensitive data items found - redaction recommended')
        
        # Cek konteks penggunaan
        usage_context = context.get('usage_context', 'poc')
        if usage_context != 'poc':
            compliant = False
            notes.append('Data extraction only allowed for Proof of Concept purposes')
        
        return {
            'compliant': compliant,
            'notes': notes or ['Data minimization requirements satisfied']
        }