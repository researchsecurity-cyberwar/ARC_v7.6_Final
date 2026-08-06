import subprocess
import os

class IOSRevSolver:
    """
    iOS IPA reverse engineering solver.
    Menyelesaikan challenge reverse engineering IPA iOS.
    """
    
    def __init__(self):
        self.tools = ['unzip', 'strings', 'class-dump', 'otool']
    
    def solve_ios_challenge(self, ipa_path: str):
        """
        Selesaikan challenge iOS.
        """
        results = {
            'ipa_path': ipa_path,
            'bundle_id': None,
            'executable_name': None,
            'sensitive_strings': [],
            'flag_patterns': [],
            'solution_found': False
        }
        
        try:
            if not os.path.exists(ipa_path):
                results['error'] = 'IPA file not found'
                return results
            
            # Ekstrak IPA
            extract_dir = f"{ipa_path}_extracted"
            os.makedirs(extract_dir, exist_ok=True)
            subprocess.run(['unzip', '-q', ipa_path, '-d', extract_dir], check=True)
            
            # Cari executable
            app_dirs = [d for d in os.listdir(os.path.join(extract_dir, 'Payload')) if d.endswith('.app')]
            if app_dirs:
                app_dir = os.path.join(extract_dir, 'Payload', app_dirs[0])
                executables = [f for f in os.listdir(app_dir) if not f.endswith(('.plist', '.png', '.storyboardc'))]
                if executables:
                    executable_path = os.path.join(app_dir, executables[0])
                    results['executable_name'] = executables[0]
                    
                    # Cari string sensitif
                    sensitive_strings = self._find_sensitive_strings(executable_path)
                    results['sensitive_strings'] = sensitive_strings
                    
                    # Cari pola flag
                    flag_patterns = self._find_flag_patterns(executable_path)
                    results['flag_patterns'] = flag_patterns
            
            results['solution_found'] = len(results['flag_patterns']) > 0
        
        except Exception as e:
            results['error'] = f'iOS solving failed: {str(e)}'
        
        return results
    
    def _find_sensitive_strings(self, executable_path: str) -> list:
        """Cari string sensitif dalam executable iOS."""
        try:
            strings_result = subprocess.run(['strings', executable_path], capture_output=True, text=True)
            sensitive_keywords = ['flag', 'secret', 'password', 'key', 'token']
            sensitive_strings = []
            for line in strings_result.stdout.split('\n'):
                if any(keyword in line.lower() for keyword in sensitive_keywords):
                    sensitive_strings.append(line)
            return sensitive_strings[:20]
        except:
            return []
    
    def _find_flag_patterns(self, executable_path: str) -> list:
        """Cari pola flag dalam executable iOS."""
        try:
            strings_result = subprocess.run(['strings', executable_path], capture_output=True, text=True)
            flag_patterns = []
            for line in strings_result.stdout.split('\n'):
                if 'CTF{' in line or 'flag{' in line or 'FLAG{' in line:
                    flag_patterns.append(line)
            return flag_patterns
        except:
            return []