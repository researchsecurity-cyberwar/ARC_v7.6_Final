import subprocess
import os
import time

class DalfoxOrchestrator:
    """
    DOM-aware XSS scanning.
    Mengkoordinasikan dalfox untuk pemindaian XSS yang sadar DOM.
    """
    
    def __init__(self, output_dir="~/.arc/scan"):
        self.output_dir = os.path.expanduser(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def run_dalfox_scan(self, input_file: str, parameter: str = None):
        """
        Jalankan pemindaian dalfox untuk XSS.
        """
        results = {
            'input_file': input_file,
            'output_file': None,
            'xss_findings': 0,
            'execution_time': 0.0,
            'success': False
        }
        
        try:
            if not os.path.exists(input_file):
                results['error'] = f'Input file not found: {input_file}'
                return results
            
            timestamp = int(time.time())
            output_file = os.path.join(self.output_dir, f"dalfox_{timestamp}.txt")
            
            # Bangun perintah dalfox
            cmd = [
                "dalfox",
                "file", input_file,
                "--output", output_file,
                "--silence",
                "--timeout", "10",
                "--delay", "1"
            ]
            
            # Tambahkan parameter spesifik jika disediakan
            if parameter:
                cmd.extend(["--param", parameter])
            
            # Eksekusi dalfox
            start_time = time.time()
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            execution_time = time.time() - start_time
            
            if process.returncode == 0 and os.path.exists(output_file):
                # Hitung jumlah temuan XSS
                with open(output_file, 'r') as f:
                    xss_findings = len([line for line in f if '[VULN]' in line])
                
                results.update({
                    'output_file': output_file,
                    'xss_findings': xss_findings,
                    'execution_time': round(execution_time, 2),
                    'success': True
                })
            else:
                results['error'] = f'dalfox failed: {process.stderr[:200] if process.stderr else "No stderr"}'
        
        except subprocess.TimeoutExpired:
            results['error'] = 'dalfox execution timed out (10 minutes)'
        except Exception as e:
            results['error'] = f'dalfox orchestration failed: {str(e)}'
        
        return results