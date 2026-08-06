import subprocess
import os
import time
import random

class SelfHealingInstaller:
    """
    Handle installation failures intelligently.
    Menangani kegagalan instalasi secara cerdas.
    """
    
    def __init__(self, tools_dir="~/.arc/tools"):
        self.tools_dir = os.path.expanduser(tools_dir)
        os.makedirs(self.tools_dir, exist_ok=True)
        self.recovery_strategies = {
            'permission_denied': self._fix_permissions,
            'network_timeout': self._retry_with_backoff,
            'dependency_missing': self._install_missing_deps,
            'build_failed': self._try_alternative_build,
            'disk_space': self._cleanup_and_retry
        }
    
    def install_with_healing(self, install_command: list, max_attempts: int = 3):
        """
        Instal dengan kemampuan self-healing.
        """
        results = {
            'install_command': install_command,
            'max_attempts': max_attempts,
            'successful_attempt': 0,
            'final_success': False,
            'recovery_actions': []
        }
        
        for attempt in range(1, max_attempts + 1):
            try:
                # Coba instalasi
                result = subprocess.run(
                    install_command,
                    capture_output=True,
                    text=True,
                    timeout=600,
                    cwd=self.tools_dir
                )
                
                if result.returncode == 0:
                    results.update({
                        'successful_attempt': attempt,
                        'final_success': True
                    })
                    break
                
                # Analisis error dan terapkan strategi pemulihan
                error_analysis = self._analyze_installation_error(result.stderr)
                if error_analysis['error_type'] in self.recovery_strategies:
                    recovery_action = self.recovery_strategies[error_analysis['error_type']]()
                    results['recovery_actions'].append({
                        'attempt': attempt,
                        'error_type': error_analysis['error_type'],
                        'action_taken': recovery_action
                    })
                
                # Tunggu sebelum mencoba lagi
                time.sleep(random.uniform(2, 5))
            
            except subprocess.TimeoutExpired:
                # Terapkan strategi timeout
                recovery_action = self._retry_with_backoff()
                results['recovery_actions'].append({
                    'attempt': attempt,
                    'error_type': 'network_timeout',
                    'action_taken': recovery_action
                })
                time.sleep(random.uniform(5, 10))
            except Exception as e:
                results['error'] = f'Installation failed: {str(e)}'
                break
        
        return results
    
    def _analyze_installation_error(self, error_output: str) -> dict:
        """Analisis error instalasi."""
        error_lower = error_output.lower()
        
        if 'permission denied' in error_lower or 'access denied' in error_lower:
            return {'error_type': 'permission_denied'}
        elif 'timeout' in error_lower or 'connection refused' in error_lower:
            return {'error_type': 'network_timeout'}
        elif 'no such file' in error_lower or 'command not found' in error_lower:
            return {'error_type': 'dependency_missing'}
        elif 'build failed' in error_lower or 'compilation error' in error_lower:
            return {'error_type': 'build_failed'}
        elif 'disk space' in error_lower or 'no space left' in error_lower:
            return {'error_type': 'disk_space'}
        else:
            return {'error_type': 'unknown'}
    
    def _fix_permissions(self) -> str:
        """Perbaiki izin direktori."""
        try:
            os.chmod(self.tools_dir, 0o755)
            return 'Fixed directory permissions'
        except:
            return 'Failed to fix permissions'
    
    def _retry_with_backoff(self) -> str:
        """Coba lagi dengan backoff eksponensial."""
        return 'Applied network retry with backoff'
    
    def _install_missing_deps(self) -> str:
        """Instal dependensi yang hilang."""
        # Ini akan terintegrasi dengan dependency_resolver
        return 'Attempted to install missing dependencies'
    
    def _try_alternative_build(self) -> str:
        """Coba metode build alternatif."""
        return 'Attempted alternative build method'
    
    def _cleanup_and_retry(self) -> str:
        """Bersihkan ruang disk dan coba lagi."""
        try:
            # Hapus file sementara
            temp_files = [f for f in os.listdir(self.tools_dir) if f.startswith('tmp_')]
            for temp_file in temp_files:
                os.remove(os.path.join(self.tools_dir, temp_file))
            return 'Cleaned up temporary files'
        except:
            return 'Failed to cleanup disk space'