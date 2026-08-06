import subprocess
import os

class MemoryAnalyzer:
    """
    Memory dump analysis.
    Menganalisis dump memori untuk challenge forensik.
    """
    
    def __init__(self):
        self.tools = ['volatility', 'rekall', 'strings']
    
    def analyze_memory_dump(self, dump_path: str, profile: str = None):
        """
        Analisis dump memori.
        """
        results = {
            'dump_path': dump_path,
            'profile': profile,
            'processes_found': [],
            'network_connections': [],
            'files_extracted': [],
            'flag_found': False,
            'analysis_complete': False
        }
        
        try:
            if not os.path.exists(dump_path):
                results['error'] = 'Memory dump not found'
                return results
            
            # Deteksi profil jika tidak disediakan
            if not profile:
                profile = self._detect_memory_profile(dump_path)
                results['profile'] = profile
            
            # Analisis proses
            processes = self._analyze_processes(dump_path, profile)
            results['processes_found'] = processes
            
            # Analisis koneksi jaringan
            connections = self._analyze_network(dump_path, profile)
            results['network_connections'] = connections
            
            # Ekstrak file
            files = self._extract_files(dump_path, profile)
            results['files_extracted'] = files
            
            # Cari flag
            flag_found = self._search_memory_for_flags(dump_path)
            results['flag_found'] = flag_found
            
            results['analysis_complete'] = True
        
        except Exception as e:
            results['error'] = f'Memory analysis failed: {str(e)}'
        
        return results
    
    def _detect_memory_profile(self, dump_path: str) -> str:
        """Deteksi profil memori."""
        try:
            result = subprocess.run(['volatility', '-f', dump_path, 'imageinfo'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'Suggested Profile(s)' in line:
                    profiles = line.split(':')[1].strip().split(',')[0]
                    return profiles
            return 'WinXPSP2x86'
        except:
            return 'WinXPSP2x86'
    
    def _analyze_processes(self, dump_path: str, profile: str) -> list:
        """Analisis proses dalam memori."""
        try:
            result = subprocess.run(['volatility', '-f', dump_path, '--profile', profile, 'pslist'], capture_output=True, text=True)
            processes = []
            for line in result.stdout.split('\n')[3:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 3:
                        processes.append({'pid': parts[2], 'name': parts[1]})
            return processes[:20]
        except:
            return []
    
    def _analyze_network(self, dump_path: str, profile: str) -> list:
        """Analisis koneksi jaringan."""
        try:
            result = subprocess.run(['volatility', '-f', dump_path, '--profile', profile, 'netscan'], capture_output=True, text=True)
            connections = []
            for line in result.stdout.split('\n')[2:]:
                if line.strip() and 'TCP' in line:
                    connections.append(line.strip())
            return connections[:10]
        except:
            return []
    
    def _extract_files(self, dump_path: str, profile: str) -> list:
        """Ekstrak file dari memori."""
        try:
            # Buat direktori ekstraksi
            extract_dir = f"/tmp/mem_extract_{os.path.basename(dump_path)}"
            os.makedirs(extract_dir, exist_ok=True)
            
            result = subprocess.run(['volatility', '-f', dump_path, '--profile', profile, 'filescan'], capture_output=True, text=True)
            files = []
            for line in result.stdout.split('\n')[:10]:
                if '.txt' in line or '.log' in line:
                    files.append(line.strip())
            return files
        except:
            return []
    
    def _search_memory_for_flags(self, dump_path: str) -> bool:
        """Cari flag dalam dump memori."""
        try:
            result = subprocess.run(['strings', dump_path], capture_output=True, text=True)
            flag_patterns = ['CTF{', 'flag{', 'FLAG{']
            return any(pattern in result.stdout for pattern in flag_patterns)
        except:
            return False