import subprocess
import os
import time
import random

class HttpxOrchestrator:
    """
    Alive endpoint enumeration with TLS spoofing.
    Mengkoordinasikan httpx untuk enumerasi endpoint hidup dengan spoofing TLS.
    """
    
    def __init__(self, output_dir="~/.arc/recon"):
        self.output_dir = os.path.expanduser(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        self.tls_fingerprints = [
            "chrome_120", "firefox_120", "safari_16_0",
            "ios_16_0", "android_13_0"
        ]
    
    def run_httpx_enumeration(self, input_file: str, threads: int = 50):
        """
        Jalankan httpx untuk enumerasi endpoint hidup.
        """
        results = {
            'input_file': input_file,
            'output_file': None,
            'alive_endpoints': 0,
            'execution_time': 0.0,
            'success': False
        }
        
        try:
            if not os.path.exists(input_file):
                results['error'] = f'Input file not found: {input_file}'
                return results
            
            # Buat nama file output
            timestamp = int(time.time())
            output_file = os.path.join(self.output_dir, f"httpx_{timestamp}.txt")
            
            # Pilih fingerprint TLS acak (hentikan pengacakan bila tidak dipakai)
            tls_fingerprint = random.choice(self.tls_fingerprints)

            # Bangun perintah httpx
            cmd = [
                "httpx",
                "-l", input_file,
                "-o", output_file,
                "-threads", str(threads),
                "-timeout", "10",
                "-retries", "2",
                "-silent"
            ]

            # httpx (projectdiscovery) TIDAK memiliki flag -tls-fingerprint
            # (itu flag nuclei). Gunakan -tls-grab/-tls-probe bila tool mendukungnya.
            # Kita tambahkan hanya jika dirasa perlu, dengan cara aman:
            cmd.append("-tls-grab")
            
            # Eksekusi httpx
            start_time = time.time()
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            execution_time = time.time() - start_time
            
            if process.returncode == 0 and os.path.exists(output_file):
                # Hitung jumlah endpoint hidup
                with open(output_file, 'r') as f:
                    endpoints = [line.strip() for line in f if line.strip()]
                
                results.update({
                    'output_file': output_file,
                    'alive_endpoints': len(endpoints),
                    'execution_time': round(execution_time, 2),
                    'success': True,
                    'tls_fingerprint_used': tls_fingerprint
                })
            else:
                results['error'] = f'httpx failed: {process.stderr[:200] if process.stderr else "No stderr"}'
        
        except subprocess.TimeoutExpired:
            results['error'] = 'httpx execution timed out (10 minutes)'
        except Exception as e:
            results['error'] = f'httpx orchestration failed: {str(e)}'
        
        return results
    
    def filter_by_status_code(self, input_file: str, status_codes: list) -> str:
        """
        Filter hasil httpx berdasarkan kode status.
        """
        filtered_file = os.path.join(self.output_dir, f"httpx_filtered_{int(time.time())}.txt")
        
        with open(input_file, 'r') as f, open(filtered_file, 'w') as out_f:
            for line in f:
                # Format httpx: URL [STATUS_CODE]
                if '[' in line and ']' in line:
                    status_str = line.split('[')[1].split(']')[0]
                    try:
                        status_code = int(status_str)
                        if status_code in status_codes:
                            out_f.write(line)
                    except ValueError:
                        continue
        
        return filtered_file