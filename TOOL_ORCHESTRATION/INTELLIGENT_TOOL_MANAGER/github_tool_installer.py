import subprocess
import os
import requests
import tempfile
import shutil

class GitHubToolInstaller:
    """
    Install tools from GitHub repositories.
    Menginstal alat dari repositori GitHub secara otomatis.
    """
    
    def __init__(self, tools_dir="~/.arc/tools"):
        self.tools_dir = os.path.expanduser(tools_dir)
        os.makedirs(self.tools_dir, exist_ok=True)
    
    def install_from_github(self, repo_url: str, branch: str = "main"):
        """
        Instal alat dari repositori GitHub.
        """
        results = {
            'repo_url': repo_url,
            'branch': branch,
            'installation_path': None,
            'build_successful': False,
            'success': False
        }
        
        try:
            # Validasi URL GitHub
            if not self._is_github_repo(repo_url):
                results['error'] = 'Invalid GitHub repository URL'
                return results
            
            # Clone repositori
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            install_path = os.path.join(self.tools_dir, repo_name)
            
            clone_result = self._clone_repository(repo_url, install_path, branch)
            if not clone_result['success']:
                results['error'] = f'Cloning failed: {clone_result.get("error", "Unknown error")}'
                return results
            
            # Bangun alat
            build_result = self._build_tool(install_path)
            results.update({
                'installation_path': install_path,
                'build_successful': build_result['success'],
                'success': True
            })
            
            if not build_result['success']:
                results['build_error'] = build_result.get('error', 'Build failed')
        
        except Exception as e:
            results['error'] = f'GitHub installation failed: {str(e)}'
        
        return results
    
    def _is_github_repo(self, url: str) -> bool:
        """Validasi apakah URL adalah repositori GitHub."""
        return url.startswith(('https://github.com/', 'git@github.com:'))
    
    def _clone_repository(self, repo_url: str, install_path: str, branch: str) -> dict:
        """Clone repositori GitHub."""
        try:
            if os.path.exists(install_path):
                shutil.rmtree(install_path)
            
            cmd = ["git", "clone", "--branch", branch, "--depth", "1", repo_url, install_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            return {
                'success': result.returncode == 0,
                'error': result.stderr[:200] if result.stderr else None
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _build_tool(self, install_path: str) -> dict:
        """Bangun alat dari sumber kode."""
        try:
            # Cek file build yang umum
            build_files = {
                'go.mod': ['go', 'build', '-o', 'tool'],
                'Cargo.toml': ['cargo', 'build', '--release'],
                'package.json': ['npm', 'install', '&&', 'npm', 'run', 'build'],
                'setup.py': ['python3', 'setup.py', 'install', '--user']
            }
            
            for marker_file, build_cmd in build_files.items():
                if os.path.exists(os.path.join(install_path, marker_file)):
                    # Jalankan perintah build
                    result = subprocess.run(
                        build_cmd,
                        cwd=install_path,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    return {
                        'success': result.returncode == 0,
                        'error': result.stderr[:200] if result.stderr else None
                    }
            
            # Jika tidak ada file build yang dikenali, anggap sudah executable
            return {'success': True}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}