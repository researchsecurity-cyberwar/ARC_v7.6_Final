import subprocess
import os

class StegoSolver:
    """
    Steganography solver (image/audio).
    Menyelesaikan challenge steganografi pada gambar dan audio.
    """
    
    def __init__(self):
        self.tools = ['steghide', 'binwalk', 'foremost', 'exiftool', 'zsteg']
    
    def solve_stego_challenge(self, file_path: str):
        """
        Selesaikan challenge steganografi.
        """
        results = {
            'file_path': file_path,
            'file_type': None,
            'extracted_data': [],
            'flag_found': False,
            'solution_found': False
        }
        
        try:
            if not os.path.exists(file_path):
                results['error'] = 'File not found'
                return results
            
            # Deteksi tipe file
            file_result = subprocess.run(['file', file_path], capture_output=True, text=True)
            results['file_type'] = file_result.stdout.strip()
            
            # Ekstrak metadata EXIF
            exif_data = self._extract_exif_data(file_path)
            if exif_data:
                results['extracted_data'].append({'type': 'exif', 'data': exif_data})
            
            # Coba steghide (untuk JPEG/PNG)
            if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                steghide_data = self._try_steghide(file_path)
                if steghide_data:
                    results['extracted_data'].append({'type': 'steghide', 'data': steghide_data})
            
            # Coba binwalk untuk semua file
            binwalk_data = self._try_binwalk(file_path)
            if binwalk_data:
                results['extracted_data'].append({'type': 'binwalk', 'data': binwalk_data})
            
            # Cari flag dalam data yang diekstrak
            flag_found = self._search_for_flags(results['extracted_data'])
            results['flag_found'] = flag_found
            results['solution_found'] = flag_found
        
        except Exception as e:
            results['error'] = f'Stego solving failed: {str(e)}'
        
        return results
    
    def _extract_exif_data(self, file_path: str) -> str:
        """Ekstrak data EXIF."""
        try:
            result = subprocess.run(['exiftool', file_path], capture_output=True, text=True)
            return result.stdout
        except:
            return ""
    
    def _try_steghide(self, file_path: str) -> str:
        """Coba ekstrak dengan steghide (tanpa password)."""
        try:
            # Buat direktori sementara untuk ekstraksi
            temp_dir = f"/tmp/stego_{os.path.basename(file_path)}"
            os.makedirs(temp_dir, exist_ok=True)
            
            # Coba ekstrak tanpa password
            result = subprocess.run(
                ['steghide', 'extract', '-sf', file_path, '-xf', os.path.join(temp_dir, 'extracted.txt'), '-p', ''],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                extracted_file = os.path.join(temp_dir, 'extracted.txt')
                if os.path.exists(extracted_file):
                    with open(extracted_file, 'r') as f:
                        return f.read()
            
            return ""
        except:
            return ""
    
    def _try_binwalk(self, file_path: str) -> str:
        """Coba ekstrak dengan binwalk."""
        try:
            result = subprocess.run(['binwalk', '-e', file_path], capture_output=True, text=True, timeout=30)
            return result.stdout
        except:
            return ""
    
    def _search_for_flags(self, extracted_data: list) -> bool:
        """Cari flag dalam data yang diekstrak."""
        flag_patterns = ['CTF{', 'flag{', 'FLAG{']
        for item in extracted_data:
            data = item.get('data', '')
            if any(pattern in data for pattern in flag_patterns):
                return True
        return False