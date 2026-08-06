import subprocess
import os
import time
import requests

class WaybackOrchestrator:
    """
    Historical URL discovery from archives.
    Mengkoordinasikan gau dan waybackurls untuk penemuan URL historis.
    """
    
    def __init__(self, output_dir="~/.arc/recon"):
        self.output_dir = os.path.expanduser(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def run_wayback_discovery(self, target_domain: str):
        """
        Jalankan penemuan URL historis menggunakan gau dan waybackurls.
        """
        results = {
            'target_domain': target_domain,
            'gau_output': None,
            'wayback_output': None,
            'total_urls': 0,
            'execution_time': 0.0,
            'success': False
        }
        
        try:
            timestamp = int(time.time())
            
            # Jalankan gau
            gau_file = os.path.join(self.output_dir, f"gau_{target_domain}_{timestamp}.txt")
            gau_success = self._run_gau(target_domain, gau_file)
            
            # Jalankan waybackurls
            wayback_file = os.path.join(self.output_dir, f"wayback_{target_domain}_{timestamp}.txt")
            wayback_success = self._run_waybackurls(target_domain, wayback_file)
            
            # Gabungkan hasil
            if gau_success or wayback_success:
                merged_file = self._merge_wayback_results([gau_file, wayback_file], target_domain, timestamp)
                results.update({
                    'gau_output': gau_file if gau_success else None,
                    'wayback_output': wayback_file if wayback_success else None,
                    'merged_output': merged_file,
                    'total_urls': self._count_urls(merged_file),
                    'execution_time': time.time() - timestamp,
                    'success': True
                })
            else:
                results['error'] = 'Both gau and waybackurls failed'
        
        except Exception as e:
            results['error'] = f'Wayback orchestration failed: {str(e)}'
        
        return results
    
    def _run_gau(self, domain: str, output_file: str) -> bool:
        """Jalankan gau."""
        try:
            cmd = ["gau", "--subs", domain]
            with open(output_file, 'w') as f:
                process = subprocess.run(cmd, stdout=f, stderr=subprocess.DEVNULL, timeout=120)
            return process.returncode == 0 and os.path.getsize(output_file) > 0
        except:
            return False
    
    def _run_waybackurls(self, domain: str, output_file: str) -> bool:
        """Jalankan waybackurls."""
        try:
            cmd = ["waybackurls", domain]
            with open(output_file, 'w') as f:
                process = subprocess.run(cmd, stdout=f, stderr=subprocess.DEVNULL, timeout=120)
            return process.returncode == 0 and os.path.getsize(output_file) > 0
        except:
            return False
    
    def _merge_wayback_results(self, files: list, domain: str, timestamp: int) -> str:
        """Gabungkan hasil gau dan waybackurls."""
        merged_file = os.path.join(self.output_dir, f"wayback_merged_{domain}_{timestamp}.txt")
        urls_set = set()
        
        for file_path in files:
            if file_path and os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    for line in f:
                        url = line.strip()
                        if url and domain in url:
                            urls_set.add(url)
        
        with open(merged_file, 'w') as f:
            for url in sorted(urls_set):
                f.write(f"{url}\n")
        
        return merged_file
    
    def _count_urls(self, file_path: str) -> int:
        """Hitung jumlah URL dalam file."""
        if not os.path.exists(file_path):
            return 0
        with open(file_path, 'r') as f:
            return len([line for line in f if line.strip()])