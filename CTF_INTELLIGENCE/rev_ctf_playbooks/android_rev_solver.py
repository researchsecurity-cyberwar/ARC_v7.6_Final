import subprocess
import os
import zipfile

class AndroidRevSolver:
    """
    Android APK reverse engineering solver.
    Menyelesaikan challenge reverse engineering APK Android.
    """
    
    def __init__(self):
        self.tools = ['apktool', 'jadx', 'adb', 'strings']
    
    def solve_android_challenge(self, apk_path: str):
        """
        Selesaikan challenge Android.
        """
        results = {
            'apk_path': apk_path,
            'package_name': None,
            'main_activity': None,
            'sensitive_strings': [],
            'flag_patterns': [],
            'solution_found': False
        }
        
        try:
            if not os.path.exists(apk_path):
                results['error'] = 'APK file not found'
                return results
            
            # Ekstrak informasi dasar APK
            apk_info = self._get_apk_info(apk_path)
            results.update(apk_info)
            
            # Cari string sensitif
            sensitive_strings = self._find_sensitive_strings(apk_path)
            results['sensitive_strings'] = sensitive_strings
            
            # Cari pola flag
            flag_patterns = self._find_flag_patterns(apk_path)
            results['flag_patterns'] = flag_patterns
            
            results['solution_found'] = len(flag_patterns) > 0
        
        except Exception as e:
            results['error'] = f'Android solving failed: {str(e)}'
        
        return results
    
    def _get_apk_info(self, apk_path: str) -> dict:
        """Dapatkan informasi dasar APK."""
        info = {}
        try:
            # Gunakan aapt atau unzip untuk mendapatkan AndroidManifest.xml
            with zipfile.ZipFile(apk_path, 'r') as apk_zip:
                manifest_content = apk_zip.read('AndroidManifest.xml')
                # Parsing sederhana untuk package name
                if b'package="' in manifest_content:
                    start = manifest_content.find(b'package="') + 9
                    end = manifest_content.find(b'"', start)
                    info['package_name'] = manifest_content[start:end].decode()
        except:
            info['package_name'] = 'unknown'
        
        return info
    
    def _find_sensitive_strings(self, apk_path: str) -> list:
        """Cari string sensitif dalam APK."""
        try:
            strings_result = subprocess.run(['strings', apk_path], capture_output=True, text=True)
            sensitive_keywords = ['flag', 'secret', 'password', 'key', 'token']
            sensitive_strings = []
            for line in strings_result.stdout.split('\n'):
                if any(keyword in line.lower() for keyword in sensitive_keywords):
                    sensitive_strings.append(line)
            return sensitive_strings[:20]
        except:
            return []
    
    def _find_flag_patterns(self, apk_path: str) -> list:
        """Cari pola flag dalam APK."""
        try:
            strings_result = subprocess.run(['strings', apk_path], capture_output=True, text=True)
            flag_patterns = []
            for line in strings_result.stdout.split('\n'):
                if 'CTF{' in line or 'flag{' in line or 'FLAG{' in line:
                    flag_patterns.append(line)
            return flag_patterns
        except:
            return []