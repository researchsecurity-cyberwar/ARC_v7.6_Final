import subprocess
import tempfile
import os
import shutil

class SandboxIntegrator:
    """
    Test new tools in isolated environment.
    Menguji alat baru dalam lingkungan terisolasi.
    """
    
    def __init__(self, sandbox_dir="~/.arc/sandbox"):
        self.sandbox_dir = os.path.expanduser(sandbox_dir)
        os.makedirs(self.sandbox_dir, exist_ok=True)
    
    def test_in_sandbox(self, tool_path: str, test_command: list, timeout: int = 60):
        """
        Uji alat dalam sandbox terisolasi.
        """
        results = {
            'tool_path': tool_path,
            'test_command': test_command,
            'sandbox_path': None,
            'execution_successful': False,
            'security_violations': [],
            'success': False
        }
        
        try:
            # Buat direktori sandbox sementara
            sandbox_path = tempfile.mkdtemp(dir=self.sandbox_dir)
            results['sandbox_path'] = sandbox_path
            
            # Salin alat ke sandbox
            if os.path.isdir(tool_path):
                shutil.copytree(tool_path, os.path.join(sandbox_path, 'tool'))
            else:
                shutil.copy2(tool_path, os.path.join(sandbox_path, 'tool'))
            
            # Jalankan pengujian dalam sandbox
            test_result = self._execute_in_sandbox(sandbox_path, test_command, timeout)
            results['execution_successful'] = test_result['success']
            
            # Periksa pelanggaran keamanan
            security_violations = self._check_security_violations(sandbox_path)
            results['security_violations'] = security_violations
            
            results['success'] = test_result['success'] and len(security_violations) == 0
        
        except Exception as e:
            results['error'] = f'Sandbox integration failed: {str(e)}'
        finally:
            # Bersihkan sandbox
            try:
                shutil.rmtree(sandbox_path)
            except:
                pass
        
        return results
    
    def _execute_in_sandbox(self, sandbox_path: str, test_command: list, timeout: int) -> dict:
        """Eksekusi dalam sandbox."""
        try:
            # Gunakan firejail untuk isolasi (jika tersedia)
            if shutil.which('firejail'):
                cmd = ['firejail', '--net=none', '--private', '--quiet'] + test_command
            else:
                cmd = test_command
            
            result = subprocess.run(
                cmd,
                cwd=sandbox_path,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _check_security_violations(self, sandbox_path: str) -> list:
        """Periksa pelanggaran keamanan dalam sandbox."""
        violations = []
        
        # Cek akses jaringan (file log firejail)
        net_log = os.path.join(sandbox_path, 'firejail.net.log')
        if os.path.exists(net_log):
            with open(net_log, 'r') as f:
                if f.read().strip():
                    violations.append('Network access detected')
        
        # Cek akses file sistem di luar sandbox
        # Ini akan diimplementasikan dengan auditd atau sistem serupa
        
        return violations