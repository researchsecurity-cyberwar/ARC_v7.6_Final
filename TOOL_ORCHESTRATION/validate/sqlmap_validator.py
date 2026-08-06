import subprocess
import os
import time

class SqlmapValidator:
    """
    SQLi confirmation (batch mode only).
    Mengkonfirmasi SQLi dengan sqlmap dalam mode batch.
    """
    
    def __init__(self, output_dir="~/.arc/validate"):
        self.output_dir = os.path.expanduser(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def confirm_sqli(self, target_url: str, parameter: str = None):
        """
        Konfirmasi kerentanan SQLi dengan sqlmap.
        """
        results = {
            'target_url': target_url,
            'parameter': parameter,
            'output_dir': None,
            'sqli_confirmed': False,
            'execution_time': 0.0,
            'success': False
        }
        
        try:
            timestamp = int(time.time())
            output_dir = os.path.join(self.output_dir, f"sqlmap_{timestamp}")
            os.makedirs(output_dir, exist_ok=True)
            
            # Bangun perintah sqlmap
            cmd = [
                "sqlmap",
                "-u", target_url,
                "--batch",
                "--risk=2",
                "--level=3",
                "--timeout=10",
                "--retries=2",
                "--output-dir", output_dir,
                "--purge-output"
            ]
            
            # Tambahkan parameter spesifik jika disediakan
            if parameter:
                cmd.extend(["-p", parameter])
            
            # Eksekusi sqlmap
            start_time = time.time()
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            execution_time = time.time() - start_time
            
            # Periksa apakah SQLi dikonfirmasi
            sqli_confirmed = "is vulnerable" in process.stdout.lower() or "sql injection detected" in process.stdout.lower()
            
            results.update({
                'output_dir': output_dir,
                'sqli_confirmed': sqli_confirmed,
                'execution_time': round(execution_time, 2),
                'success': True
            })
        
        except subprocess.TimeoutExpired:
            results['error'] = 'sqlmap execution timed out (10 minutes)'
        except Exception as e:
            results['error'] = f'sqlmap validation failed: {str(e)}'
        
        return results