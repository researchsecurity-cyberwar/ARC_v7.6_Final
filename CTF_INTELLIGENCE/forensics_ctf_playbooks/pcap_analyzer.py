import subprocess
import os
import re

class PCAPAnalyzer:
    """
    Network forensics solver.
    Menganalisis file PCAP untuk challenge forensik jaringan.
    """
    
    def __init__(self):
        self.tools = ['tshark', 'wireshark', 'tcpdump', 'binwalk']
    
    def analyze_pcap_file(self, pcap_path: str):
        """
        Analisis file PCAP.
        """
        results = {
            'pcap_path': pcap_path,
            'protocol_statistics': {},
            'http_requests': [],
            'dns_queries': [],
            'extracted_files': [],
            'flag_found': False,
            'analysis_complete': False
        }
        
        try:
            if not os.path.exists(pcap_path):
                results['error'] = 'PCAP file not found'
                return results
            
            # Statistik protokol
            protocol_stats = self._get_protocol_statistics(pcap_path)
            results['protocol_statistics'] = protocol_stats
            
            # Permintaan HTTP
            http_requests = self._extract_http_requests(pcap_path)
            results['http_requests'] = http_requests
            
            # Query DNS
            dns_queries = self._extract_dns_queries(pcap_path)
            results['dns_queries'] = dns_queries
            
            # Ekstrak file
            extracted_files = self._extract_files_from_pcap(pcap_path)
            results['extracted_files'] = extracted_files
            
            # Cari flag
            flag_found = self._search_pcap_for_flags(pcap_path)
            results['flag_found'] = flag_found
            
            results['analysis_complete'] = True
        
        except Exception as e:
            results['error'] = f'PCAP analysis failed: {str(e)}'
        
        return results
    
    def _get_protocol_statistics(self, pcap_path: str) -> dict:
        """Dapatkan statistik protokol."""
        try:
            result = subprocess.run(['tshark', '-r', pcap_path, '-q', '-z', 'proto,col'], capture_output=True, text=True)
            stats = {}
            for line in result.stdout.split('\n'):
                if ':' in line and 'frames' not in line.lower():
                    parts = line.split(':')
                    if len(parts) >= 2:
                        protocol = parts[0].strip()
                        count = parts[1].strip().split()[0] if parts[1].strip() else '0'
                        try:
                            stats[protocol] = int(count)
                        except:
                            stats[protocol] = 0
            return stats
        except:
            return {}
    
    def _extract_http_requests(self, pcap_path: str) -> list:
        """Ekstrak permintaan HTTP."""
        try:
            result = subprocess.run([
                'tshark', '-r', pcap_path, '-Y', 'http.request', 
                '-T', 'fields', '-e', 'http.host', '-e', 'http.request.uri'
            ], capture_output=True, text=True)
            requests = []
            for line in result.stdout.split('\n'):
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        requests.append({'host': parts[0], 'uri': parts[1]})
            return requests[:20]
        except:
            return []
    
    def _extract_dns_queries(self, pcap_path: str) -> list:
        """Ekstrak query DNS."""
        try:
            result = subprocess.run([
                'tshark', '-r', pcap_path, '-Y', 'dns.qry.name', 
                '-T', 'fields', '-e', 'dns.qry.name'
            ], capture_output=True, text=True)
            queries = []
            for line in result.stdout.split('\n'):
                if line.strip():
                    queries.append(line.strip())
            return queries[:20]
        except:
            return []
    
    def _extract_files_from_pcap(self, pcap_path: str) -> list:
        """Ekstrak file dari PCAP menggunakan binwalk."""
        try:
            # Buat direktori ekstraksi
            extract_dir = f"/tmp/pcap_extract_{os.path.basename(pcap_path)}"
            os.makedirs(extract_dir, exist_ok=True)
            
            # Gunakan binwalk untuk ekstraksi file
            subprocess.run(['binwalk', '-e', '-C', extract_dir, pcap_path], 
                          capture_output=True, timeout=60)
            
            # Daftar file yang diekstrak
            extracted_files = []
            for root, dirs, files in os.walk(extract_dir):
                for file in files[:10]:  # Batasi 10 file
                    file_path = os.path.join(root, file)
                    if os.path.getsize(file_path) > 0:
                        extracted_files.append(file_path)
            
            return extracted_files
        except:
            return []
    
    def _search_pcap_for_flags(self, pcap_path: str) -> bool:
        """Cari flag dalam file PCAP."""
        try:
            # Ekstrak semua teks dari PCAP
            result = subprocess.run(['tshark', '-r', pcap_path, '-V'], capture_output=True, text=True)
            
            # Pola flag umum CTF
            flag_patterns = [
                r'CTF\{[^}]+\}',
                r'flag\{[^}]+\}',
                r'FLAG\{[^}]+\}',
                r'picoCTF\{[^}]+\}',
                r'DESC\{[^}]+\}',
                r'HTB\{[^}]+\}',
                r'TRYHACKME\{[^}]+\}'
            ]
            
            # Cari pola flag dalam output
            for pattern in flag_patterns:
                if re.search(pattern, result.stdout, re.IGNORECASE):
                    return True
            
            return False
        except:
            return False