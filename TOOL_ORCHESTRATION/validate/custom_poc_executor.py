import subprocess
import os
import time
import tempfile

class CustomPOCExecutor:
    """
    Execute custom exploit scripts safely.
    Menjalankan skrip eksploitasi kustom dengan aman.
    """
    
    def __init__(self, output_dir="~/.arc/validate"):
        self.output_dir = os.path.expanduser(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def execute_custom_poc(self, poc_script: str, script_args: list = None):
        """
        Jalankan skrip PoC kustom dengan aman.
        """
        results = {
            'poc_script': poc_script[:100] + '...' if len(poc_script) > 100 else poc_script,
            'script_args': script_args or [],
            'output_file': None,
            'execution_successful': False,
            'execution_time': 0.0,
            'success': False
        }
        
        try:
            # Buat file sementara untuk skrip PoC
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(poc_script)
                temp_script_path = temp_file.name
            
            os.chmod(temp_script_path, 0o755)
            
            # Bangun perintah eksekusi
            cmd = ["python3", temp_script_path]
            if script_args:
                cmd.extend(script_args)
            
            # Eksekusi skrip
            start_time = time.time()
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=self.output_dir
            )
            execution_time = time.time() - start_time
            
            # Simpan output
            timestamp = int(time.time())
            output_file = os.path.join(self.output_dir, f"poc_output_{timestamp}.txt")
            with open(output_file, 'w') as f:
                f.write(f"STDOUT:\n{process.stdout}\n\nSTDERR:\n{process.stderr}\n")
            
            # Periksa keberhasilan
            execution_successful = process.returncode == 0 and "EXPLOIT SUCCESSFUL" in process.stdout
            
            results.update({
                'output_file': output_file,
                'execution_successful': execution_successful,
                'execution_time': round(execution_time, 2),
                'success': True,
                'return_code': process.returncode
            })
        
        except subprocess.TimeoutExpired:
            results['error'] = 'Custom PoC execution timed out (5 minutes)'
        except Exception as e:
            results['error'] = f'Custom PoC execution failed: {str(e)}'
        finally:
            # Bersihkan file sementara
            try:
                os.unlink(temp_script_path)
            except:
                pass
        
        return results