import subprocess
import os

class RegressionTester:
    """
    Verify fixes and detect regressions.
    Memverifikasi perbaikan dan mendeteksi regresi.
    """
    
    def __init__(self, test_dir="~/.arc/regression_tests"):
        self.test_dir = os.path.expanduser(test_dir)
        os.makedirs(self.test_dir, exist_ok=True)
    
    def verify_fix_and_detect_regressions(self, poc_file: str, old_binary: str, new_binary: str):
        """
        Verifikasi perbaikan dan deteksi regresi.
        """
        results = {
            'poc_file': poc_file,
            'old_binary': old_binary,
            'new_binary': new_binary,
            'fix_verified': False,
            'regressions_detected': [],
            'testing_successful': False
        }
        
        try:
            if not os.path.exists(poc_file):
                results['error'] = 'PoC file not found'
                return results
            
            # Uji binary lama (harus crash)
            old_result = self._test_binary_with_poc(old_binary, poc_file)
            
            # Uji binary baru (tidak boleh crash)
            new_result = self._test_binary_with_poc(new_binary, poc_file)
            
            # Verifikasi perbaikan
            fix_verified = old_result.get('crashed', False) and not new_result.get('crashed', False)
            results['fix_verified'] = fix_verified
            
            # Deteksi regresi (placeholder - dalam implementasi nyata, jalankan test suite lengkap)
            if new_result.get('unexpected_behavior', False):
                results['regressions_detected'].append('Unexpected behavior in new binary')
            
            results['testing_successful'] = True
        
        except Exception as e:
            results['error'] = f'Regression testing failed: {str(e)}'
        
        return results
    
    def _test_binary_with_poc(self, binary_path: str, poc_file: str) -> dict:
        """Uji binary dengan PoC."""
        try:
            if not os.path.exists(binary_path):
                return {'error': 'Binary not found'}
            
            # Untuk browser, jalankan dengan flag headless
            if 'chrome' in binary_path or 'chromium' in binary_path:
                cmd = [binary_path, '--headless', '--disable-gpu', '--no-sandbox', poc_file]
            else:
                # Untuk binary lain, jalankan langsung
                cmd = [binary_path, poc_file]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            crashed = result.returncode != 0 or 'crash' in result.stderr.lower()
            
            return {
                'crashed': crashed,
                'return_code': result.returncode,
                'stdout': result.stdout[:500],  # Batasi output
                'stderr': result.stderr[:500]
            }
        
        except subprocess.TimeoutExpired:
            return {'crashed': True, 'timeout': True}
        except Exception as e:
            return {'error': str(e)}