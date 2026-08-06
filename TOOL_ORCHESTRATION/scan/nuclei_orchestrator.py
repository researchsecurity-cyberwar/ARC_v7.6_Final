import subprocess
import os
import time
import json

class NucleiOrchestrator:
    """
    CVE/pattern scanning with template selection.
    Mengkoordinasikan nuclei untuk pemindaian CVE/pola dengan seleksi template.
    """
    
    def __init__(self, output_dir="~/.arc/scan"):
        self.output_dir = os.path.expanduser(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        self.template_categories = {
            'critical': ['cves/', 'misconfiguration/', 'exposure/'],
            'high': ['technologies/', 'vulnerabilities/'],
            'medium': ['workflows/', 'dns/'],
            'low': ['fuzzing/', 'helpers/']
        }
    
    def run_nuclei_scan(self, input_file: str, severity: str = 'high', custom_templates: list = None):
        """
        Jalankan pemindaian nuclei dengan seleksi template.
        """
        results = {
            'input_file': input_file,
            'output_file': None,
            'findings_count': 0,
            'execution_time': 0.0,
            'success': False
        }
        
        try:
            if not os.path.exists(input_file):
                results['error'] = f'Input file not found: {input_file}'
                return results
            
            timestamp = int(time.time())
            output_file = os.path.join(self.output_dir, f"nuclei_{severity}_{timestamp}.json")
            
            # Bangun perintah nuclei
            cmd = [
                "nuclei",
                "-l", input_file,
                "-json-export", output_file,
                "-severity", severity,
                "-rate-limit", "150",
                "-timeout", "10",
                "-retries", "2",
                "-silent"
            ]
            
            # Tambahkan template kustom jika tersedia
            if custom_templates:
                for template in custom_templates:
                    cmd.extend(["-t", template])
            
            # Eksekusi nuclei
            start_time = time.time()
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
            execution_time = time.time() - start_time
            
            if process.returncode == 0 and os.path.exists(output_file):
                # Hitung jumlah temuan
                findings_count = self._count_nuclei_findings(output_file)
                
                results.update({
                    'output_file': output_file,
                    'findings_count': findings_count,
                    'execution_time': round(execution_time, 2),
                    'success': True
                })
            else:
                results['error'] = f'nuclei failed: {process.stderr[:200] if process.stderr else "No stderr"}'
        
        except subprocess.TimeoutExpired:
            results['error'] = 'nuclei execution timed out (30 minutes)'
        except Exception as e:
            results['error'] = f'nuclei orchestration failed: {str(e)}'
        
        return results
    
    def _count_nuclei_findings(self, json_file: str) -> int:
        """Hitung jumlah temuan dalam file JSON nuclei."""
        try:
            with open(json_file, 'r') as f:
                count = 0
                for line in f:
                    if line.strip():
                        count += 1
                return count
        except:
            return 0
    
    def filter_nuclei_results(self, input_file: str, vulnerability_types: list) -> str:
        """
        Filter hasil nuclei berdasarkan tipe kerentanan.
        """
        filtered_file = os.path.join(self.output_dir, f"nuclei_filtered_{int(time.time())}.json")
        
        with open(input_file, 'r') as f, open(filtered_file, 'w') as out_f:
            for line in f:
                if line.strip():
                    try:
                        finding = json.loads(line)
                        if any(vuln_type.lower() in finding.get('info', {}).get('name', '').lower() 
                               for vuln_type in vulnerability_types):
                            out_f.write(line)
                    except:
                        continue
        
        return filtered_file