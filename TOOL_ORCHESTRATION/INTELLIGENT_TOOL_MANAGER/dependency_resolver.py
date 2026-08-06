import subprocess
import os
import sys
import tempfile

class DependencyResolver:
    """
    Resolve complex dependencies automatically.
    Menyelesaikan dependensi kompleks secara otomatis.
    """
    
    def __init__(self, env_dir="~/.arc/tool_envs"):
        self.env_dir = os.path.expanduser(env_dir)
        os.makedirs(self.env_dir, exist_ok=True)
    
    def resolve_dependencies(self, tool_path: str, language: str = None):
        """
        Selesaikan dependensi untuk alat tertentu.
        """
        results = {
            'tool_path': tool_path,
            'language': language,
            'env_path': None,
            'dependencies_resolved': False,
            'success': False
        }
        
        try:
            # Deteksi bahasa pemrograman jika tidak disediakan
            if language is None:
                language = self._detect_language(tool_path)
            
            # Buat environment terisolasi
            env_name = os.path.basename(tool_path).replace('.', '_')
            env_path = os.path.join(self.env_dir, env_name)
            
            if language == 'python':
                resolve_result = self._resolve_python_deps(tool_path, env_path)
            elif language == 'nodejs':
                resolve_result = self._resolve_nodejs_deps(tool_path, env_path)
            elif language == 'go':
                resolve_result = self._resolve_go_deps(tool_path)
            elif language == 'rust':
                resolve_result = self._resolve_rust_deps(tool_path)
            else:
                resolve_result = {'success': True, 'message': 'No dependencies to resolve'}
            
            results.update({
                'language': language,
                'env_path': env_path if language in ['python', 'nodejs'] else None,
                'dependencies_resolved': resolve_result['success'],
                'success': True
            })
            
            if not resolve_result['success']:
                results['dependency_error'] = resolve_result.get('error', 'Dependency resolution failed')
        
        except Exception as e:
            results['error'] = f'Dependency resolution failed: {str(e)}'
        
        return results
    
    def _detect_language(self, tool_path: str) -> str:
        """Deteksi bahasa pemrograman berdasarkan file dalam direktori."""
        if os.path.isdir(tool_path):
            files = os.listdir(tool_path)
        else:
            files = [os.path.basename(tool_path)]
        
        if any(f.endswith('.py') for f in files):
            return 'python'
        elif 'package.json' in files:
            return 'nodejs'
        elif 'go.mod' in files:
            return 'go'
        elif 'Cargo.toml' in files:
            return 'rust'
        else:
            return 'unknown'
    
    def _resolve_python_deps(self, tool_path: str, env_path: str) -> dict:
        """Selesaikan dependensi Python."""
        try:
            # Buat virtual environment
            subprocess.run([sys.executable, '-m', 'venv', env_path], check=True, timeout=60)
            
            # Aktifkan environment dan instal dependensi
            pip_path = os.path.join(env_path, 'bin', 'pip')
            
            # Cari requirements.txt atau setup.py
            req_files = ['requirements.txt', 'requirements-dev.txt']
            for req_file in req_files:
                req_path = os.path.join(tool_path, req_file)
                if os.path.exists(req_path):
                    subprocess.run([pip_path, 'install', '-r', req_path], check=True, timeout=300)
                    break
            
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _resolve_nodejs_deps(self, tool_path: str, env_path: str) -> dict:
        """Selesaikan dependensi Node.js."""
        try:
            # Gunakan npm install di direktori alat
            subprocess.run(['npm', 'install'], cwd=tool_path, check=True, timeout=300)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _resolve_go_deps(self, tool_path: str) -> dict:
        """Selesaikan dependensi Go."""
        try:
            # Gunakan go mod tidy
            subprocess.run(['go', 'mod', 'tidy'], cwd=tool_path, check=True, timeout=120)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _resolve_rust_deps(self, tool_path: str) -> dict:
        """Selesaikan dependensi Rust."""
        try:
            # Gunakan cargo build untuk mengunduh dependensi
            subprocess.run(['cargo', 'build', '--release'], cwd=tool_path, check=True, timeout=600)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}