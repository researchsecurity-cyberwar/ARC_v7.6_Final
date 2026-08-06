import subprocess
import os
import time

class FfufOrchestrator:
    """
    Intelligent directory/parameter brute-force.
    Mengkoordinasikan ffuf untuk brute-force direktori/parameter cerdas.
    """
    
    def __init__(self, output_dir="~/.arc/scan"):
        self.output_dir = os.path.expanduser(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        self.wordlists = {
            'directories': '/usr/share/wordlists/dirb/common.txt',
            'parameters': '/usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt',
            'files': '/usr/share/seclists/Discovery/Web-Content/raft-small-files.txt'
        }
    
    def run_ffuf_scan(self, target_url: str, scan_type: str = 'directories', wordlist: str = None):
        """
        Jalankan pemindaian ffuf untuk brute-force.
        """
        results = {
            'target_url': target_url,
            'scan_type': scan_type,
            'output_file': None,
            'found_items': 0,
            'execution_time': 0.0,
            'success': False
        }
        
        try:
            # Tentukan wordlist
            if wordlist and os.path.exists(wordlist):
                use_wordlist = wordlist
            else:
                use_wordlist = self.wordlists.get(scan_type, self.wordlists['directories'])
            
            if not os.path.exists(use_wordlist):
                results['error'] = f'Wordlist not found: {use_wordlist}'
                return results
            
            timestamp = int(time.time())
            output_file = os.path.join(self.output_dir, f"ffuf_{scan_type}_{timestamp}.json")
            
            # Bangun URL target berdasarkan tipe scan
            if scan_type == 'directories':
                fuzz_url = f"{target_url.rstrip('/')}/FUZZ"
            elif scan_type == 'parameters':
                fuzz_url = f"{target_url}?FUZZ=test"
            else:
                fuzz_url = f"{target_url.rstrip('/')}/FUZZ"
            
            # Bangun perintah ffuf
            cmd = [
                "ffuf",
                "-u", fuzz_url,
                "-w", use_wordlist,
                "-o", output_file,
                "-of", "json",
                "-t", "40",
                "-p", "0.1",
                "-fc", "404",
                "-ac"
            ]
            
            # Eksekusi ffuf
            start_time = time.time()
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
            execution_time = time.time() - start_time
            
            if process.returncode == 0 and os.path.exists(output_file):
                # Hitung jumlah item yang ditemukan
                found_items = self._count_ffuf_results(output_file)
                
                results.update({
                    'output_file': output_file,
                    'found_items': found_items,
                    'execution_time': round(execution_time, 2),
                    'success': True
                })
            else:
                results['error'] = f'ffuf failed: {process.stderr[:200] if process.stderr else "No stderr"}'
        
        except subprocess.TimeoutExpired:
            results['error'] = 'ffuf execution timed out (30 minutes)'
        except Exception as e:
            results['error'] = f'ffuf orchestration failed: {str(e)}'
        
        return results
    
    def _count_ffuf_results(self, json_file: str) -> int:
        """Hitung jumlah hasil dalam file JSON ffuf."""
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                return len(data.get('results', []))
        except:
            return 0