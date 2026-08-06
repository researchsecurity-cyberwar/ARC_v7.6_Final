import subprocess
import os
import time
import random

class AmassOrchestrator:
    """
    Subdomain discovery with rate limiting.
    Mengkoordinasikan amass untuk penemuan subdomain dengan rate limiting.
    """
    
    def __init__(self, output_dir="~/.arc/recon"):
        self.output_dir = os.path.expanduser(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        self.rate_limit_delay = (1, 3)  # Delay acak antara 1-3 detik
    
    def run_amass_discovery(self, target_domain: str, config_file: str = None):
        """
        Jalankan amass untuk penemuan subdomain.
        """
        results = {
            'target_domain': target_domain,
            'output_file': None,
            'subdomains_found': 0,
            'execution_time': 0.0,
            'success': False
        }
        
        try:
            # Buat nama file output
            timestamp = int(time.time())
            output_file = os.path.join(self.output_dir, f"amass_{target_domain}_{timestamp}.txt")
            
            # Bangun perintah amass
            cmd = ["amass", "enum", "-d", target_domain, "-o", output_file]
            
            # Tambahkan file konfigurasi jika tersedia
            if config_file and os.path.exists(config_file):
                cmd.extend(["-config", config_file])
            
            # Tambahkan rate limiting
            cmd.extend(["-delay", str(random.randint(100, 300))])  # 100-300ms delay
            
            # Eksekusi amass
            start_time = time.time()
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            execution_time = time.time() - start_time
            
            if process.returncode == 0 and os.path.exists(output_file):
                # Hitung jumlah subdomain
                with open(output_file, 'r') as f:
                    subdomains = [line.strip() for line in f if line.strip()]
                
                results.update({
                    'output_file': output_file,
                    'subdomains_found': len(subdomains),
                    'execution_time': round(execution_time, 2),
                    'success': True
                })
            else:
                results['error'] = f'amass failed: {process.stderr[:200]}'
        
        except subprocess.TimeoutExpired:
            results['error'] = 'amass execution timed out (5 minutes)'
        except Exception as e:
            results['error'] = f'amass orchestration failed: {str(e)}'
        
        return results
    
    def merge_amass_results(self, result_files: list) -> str:
        """
        Gabungkan hasil amass dari beberapa file.
        """
        merged_file = os.path.join(self.output_dir, f"amass_merged_{int(time.time())}.txt")
        subdomains_set = set()
        
        for file_path in result_files:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    for line in f:
                        subdomain = line.strip().lower()
                        if subdomain:
                            subdomains_set.add(subdomain)
        
        # Tulis hasil gabungan
        with open(merged_file, 'w') as f:
            for subdomain in sorted(subdomains_set):
                f.write(f"{subdomain}\n")
        
        return merged_file