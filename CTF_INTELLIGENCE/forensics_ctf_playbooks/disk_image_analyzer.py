import subprocess
import os

class DiskImageAnalyzer:
    """
    Disk image forensics solver.
    Menganalisis image disk untuk challenge forensik.
    """
    
    def __init__(self):
        self.tools = ['binwalk', 'foremost', 'sleuthkit', 'mmls', 'fls', 'icat']
    
    def analyze_disk_image(self, image_path: str):
        """
        Analisis image disk.
        """
        results = {
            'image_path': image_path,
            'file_system_detected': None,
            'partition_info': [],
            'extracted_files': [],
            'flag_found': False,
            'analysis_complete': False
        }
        
        try:
            if not os.path.exists(image_path):
                results['error'] = 'Disk image not found'
                return results
            
            # Deteksi sistem file
            fs_type = self._detect_filesystem(image_path)
            results['file_system_detected'] = fs_type
            
            # Analisis partisi
            partition_info = self._analyze_partitions(image_path)
            results['partition_info'] = partition_info
            
            # Ekstrak file
            extracted_files = self._extract_files_from_image(image_path)
            results['extracted_files'] = extracted_files
            
            # Cari flag
            flag_found = self._search_disk_for_flags(image_path)
            results['flag_found'] = flag_found
            
            results['analysis_complete'] = True
        
        except Exception as e:
            results['error'] = f'Disk image analysis failed: {str(e)}'
        
        return results
    
    def _detect_filesystem(self, image_path: str) -> str:
        """Deteksi tipe sistem file."""
        try:
            result = subprocess.run(['file', '-b', image_path], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return 'unknown'
    
    def _analyze_partitions(self, image_path: str) -> list:
        """Analisis partisi dalam image disk."""
        try:
            result = subprocess.run(['mmls', image_path], capture_output=True, text=True)
            partitions = []
            for line in result.stdout.split('\n')[3:]:
                if line.strip() and line[0].isdigit():
                    partitions.append(line.strip())
            return partitions[:10]
        except:
            return []
    
    def _extract_files_from_image(self, image_path: str) -> list:
        """Ekstrak file dari image disk."""
        try:
            # Buat direktori ekstraksi
            extract_dir = f"/tmp/disk_extract_{os.path.basename(image_path)}"
            os.makedirs(extract_dir, exist_ok=True)
            
            # Gunakan foremost untuk ekstraksi file
            subprocess.run(['foremost', '-i', image_path, '-o', extract_dir], 
                          capture_output=True, timeout=60)
            
            # Daftar file yang diekstrak
            extracted_files = []
            for root, dirs, files in os.walk(extract_dir):
                for file in files[:20]:  # Batasi 20 file
                    extracted_files.append(os.path.join(root, file))
            
            return extracted_files
        except:
            return []
    
    def _search_disk_for_flags(self, image_path: str) -> bool:
        """Cari flag dalam image disk."""
        try:
            # Gunakan strings pada image disk
            result = subprocess.run(['strings', image_path], capture_output=True, text=True)
            flag_patterns = ['CTF{', 'flag{', 'FLAG{']
            return any(pattern in result.stdout for pattern in flag_patterns)
        except:
            return False