import subprocess
import os

class DomatoIntegrator:
    """
    Google's Domato for DOM/V8 fuzzing.
    Mengintegrasikan Domato untuk fuzzing DOM/V8.
    """
    
    def __init__(self, domato_dir="~/.arc/fuzzing/domato"):
        self.domato_dir = os.path.expanduser(domato_dir)
        os.makedirs(self.domato_dir, exist_ok=True)
        self._ensure_domato_installed()
    
    def _ensure_domato_installed(self):
        """Pastikan Domato terinstal."""
        if not os.path.exists(os.path.join(self.domato_dir, 'generator.py')):
            subprocess.run([
                'git', 'clone', 'https://github.com/google/domato.git', self.domato_dir
            ], check=True)
    
    def fuzz_dom_component(self, output_dir: str, num_files: int = 100):
        """Fuzz komponen DOM."""
        cmd = [
            'python3', os.path.join(self.domato_dir, 'generator.py'),
            '--output_dir', output_dir,
            '--no_of_files', str(num_files),
            'dom/dom_template.html'
        ]
        subprocess.run(cmd, check=True)
    
    def fuzz_v8_component(self, output_dir: str, num_files: int = 100):
        """Fuzz komponen V8."""
        cmd = [
            'python3', os.path.join(self.domato_dir, 'generator.py'),
            '--output_dir', output_dir,
            '--no_of_files', str(num_files),
            'v8/v8_template.html'
        ]
        subprocess.run(cmd, check=True)