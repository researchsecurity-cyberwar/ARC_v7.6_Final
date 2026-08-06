import re
import json

class RedactionEngine:
    """
    Auto-redact sensitive data (emails, tokens, IPs).
    Meng-redaksi otomatis data sensitif dalam artefak bukti.
    """
    
    def __init__(self):
        self.redaction_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'ip_address': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'api_key': r'(?:api[_-]?key|token)["\']?\s*[:=]\s*["\']([A-Za-z0-9_-]{32,})',
            'password': r'(?:password|passwd)["\']?\s*[:=]\s*["\']([^"\']{8,})',
            'aws_access_key': r'(?:AKIA|ABIA|ACCA|ASIA)[A-Z0-9]{16}',
            'private_key': r'-----BEGIN (?:RSA|DSA|EC|OPENSSH) PRIVATE KEY-----'
        }
        
        self.redaction_replacements = {
            'email': '[REDACTED_EMAIL]',
            'ip_address': '[REDACTED_IP]',
            'credit_card': '[REDACTED_CC]',
            'ssn': '[REDACTED_SSN]',
            'api_key': '[REDACTED_API_KEY]',
            'password': '[REDACTED_PASSWORD]',
            'aws_access_key': '[REDACTED_AWS_KEY]',
            'private_key': '[REDACTED_PRIVATE_KEY]'
        }
    
    def redact_sensitive_data(self, content: str, content_type: str = 'text') -> dict:
        """
        Redaksi data sensitif dari konten.
        """
        redacted_content = content
        redacted_items = []
        
        try:
            for data_type, pattern in self.redaction_patterns.items():
                matches = re.finditer(pattern, redacted_content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    original_value = match.group()
                    replacement = self.redaction_replacements[data_type]
                    
                    # For API keys and passwords, only redact the value part
                    if data_type in ['api_key', 'password']:
                        if match.groups():
                            # Replace only the captured group (the actual key/value)
                            redacted_content = redacted_content.replace(match.group(1), replacement)
                            redacted_items.append({
                                'type': data_type,
                                'original': match.group(1)[:20] + '...',
                                'replacement': replacement
                            })
                        else:
                            # Replace the entire match
                            redacted_content = redacted_content.replace(original_value, replacement)
                            redacted_items.append({
                                'type': data_type,
                                'original': original_value[:20] + '...',
                                'replacement': replacement
                            })
                    else:
                        # Replace the entire match for other types
                        redacted_content = redacted_content.replace(original_value, replacement)
                        redacted_items.append({
                            'type': data_type,
                            'original': original_value[:20] + '...',
                            'replacement': replacement
                        })
            
            return {
                'original_size': len(content),
                'redacted_size': len(redacted_content),
                'redacted_items': redacted_items,
                'redacted_content': redacted_content,
                'success': True
            }
        
        except Exception as e:
            return {
                'error': f'Redaction failed: {str(e)}',
                'success': False,
                'redacted_content': content
            }
    
    def redact_har_file(self, har_path: str) -> dict:
        """Redaksi file HAR."""
        try:
            with open(har_path, 'r') as f:
                har_data = json.load(f)
            
            # Redact sensitive data in HAR entries
            for entry in har_data.get('log', {}).get('entries', []):
                # Redact request headers
                if 'request' in entry:
                    headers = entry['request'].get('headers', [])
                    for header in headers:
                        if 'value' in header:
                            result = self.redact_sensitive_data(header['value'])
                            if result['success']:
                                header['value'] = result['redacted_content']
                
                # Redact response content
                if 'response' in entry and 'content' in entry['response']:
                    content_text = entry['response']['content'].get('text', '')
                    if content_text:
                        result = self.redact_sensitive_data(content_text)
                        if result['success']:
                            entry['response']['content']['text'] = result['redacted_content']
            
            # Save redacted HAR
            redacted_path = har_path.replace('.har', '_redacted.har')
            with open(redacted_path, 'w') as f:
                json.dump(har_data, f, indent=2)
            
            return {
                'original_har': har_path,
                'redacted_har': redacted_path,
                'success': True
            }
        
        except Exception as e:
            return {
                'error': f'HAR redaction failed: {str(e)}',
                'success': False
            }