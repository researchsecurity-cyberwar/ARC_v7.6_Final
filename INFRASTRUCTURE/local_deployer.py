import subprocess
import os
import sys
import time

class LocalDeployer:
    """
    Ubuntu setup + llama.cpp + tools automation.
    Menyiapkan infrastruktur lokal di Ubuntu secara otomatis.
    """
    
    def __init__(self, arc_dir="~/arc-project"):
        self.arc_dir = os.path.expanduser(arc_dir)
        self.tools = [
            'amass', 'httpx', 'nuclei', 'dalfox', 'ffuf',
            'gau', 'waybackurls', 'sqlmap', 'playwright'
        ]
    
    def deploy_local_infrastructure(self, components: list = None):
        """
        Deploy infrastruktur lokal lengkap.
        """
        results = {
            'arc_directory': self.arc_dir,
            'components_deployed': [],
            'errors': [],
            'success': False
        }
        
        try:
            # Buat direktori ARC
            os.makedirs(self.arc_dir, exist_ok=True)
            
            # Deploy komponen yang diminta
            if components is None:
                components = ['system', 'ai_model', 'tools', 'environment']
            
            for component in components:
                if component == 'system':
                    sys_result = self._setup_system_dependencies()
                    if not sys_result['success']:
                        results['errors'].append(f'System setup failed: {sys_result.get("error", "Unknown")}')
                    else:
                        results['components_deployed'].append('system')
                
                elif component == 'ai_model':
                    model_result = self._setup_ai_model()
                    if not model_result['success']:
                        results['errors'].append(f'AI model setup failed: {model_result.get("error", "Unknown")}')
                    else:
                        results['components_deployed'].append('ai_model')
                
                elif component == 'tools':
                    tools_result = self._install_security_tools()
                    if not tools_result['success']:
                        results['errors'].append(f'Tools installation failed: {tools_result.get("error", "Unknown")}')
                    else:
                        results['components_deployed'].append('tools')
                
                elif component == 'environment':
                    env_result = self._setup_python_environment()
                    if not env_result['success']:
                        results['errors'].append(f'Environment setup failed: {env_result.get("error", "Unknown")}')
                    else:
                        results['components_deployed'].append('environment')
            
            results['success'] = len(results['errors']) == 0
        
        except Exception as e:
            results['error'] = f'Local deployment failed: {str(e)}'
        
        return results
    
    def _setup_system_dependencies(self):
        """Siapkan dependensi sistem."""
        try:
            # Update package list
            subprocess.run(['sudo', 'apt', 'update'], check=True, timeout=300)
            
            # Install dependensi dasar
            base_packages = [
                'git', 'curl', 'wget', 'build-essential',
                'python3', 'python3-pip', 'python3-venv',
                'unzip', 'tar', 'jq', 'tmux', 'htop'
            ]
            subprocess.run(['sudo', 'apt', 'install', '-y'] + base_packages, check=True, timeout=600)
            
            # Install dependensi untuk browser automation
            browser_deps = ['libnss3', 'libatk1.0-0', 'libatk-bridge2.0-0']
            subprocess.run(['sudo', 'apt', 'install', '-y'] + browser_deps, check=True, timeout=300)
            
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _setup_ai_model(self):
        """Siapkan model AI Mistral-7B."""
        try:
            models_dir = os.path.expanduser('~/.arc/models')
            os.makedirs(models_dir, exist_ok=True)
            
            model_path = os.path.join(models_dir, 'mistral-7b-instruct-v0.2.Q4_K_M.gguf')
            
            # Cek apakah model sudah ada
            if os.path.exists(model_path):
                return {'success': True, 'message': 'Model already exists'}
            
            # Download model dari HuggingFace
            download_url = 'https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf'
            subprocess.run([
                'wget', '-O', model_path, download_url
            ], check=True, timeout=3600)  # 1 jam timeout
            
            # Verifikasi ukuran file (harus ~4.1GB)
            if os.path.getsize(model_path) < 4000000000:  # 4GB
                os.remove(model_path)
                return {'success': False, 'error': 'Model download incomplete'}
            
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _install_security_tools(self):
        """Instal alat keamanan."""
        try:
            # Install Go jika belum ada
            if not shutil.which('go'):
                go_install_cmd = '''
                wget https://go.dev/dl/go1.21.0.linux-amd64.tar.gz &&
                sudo rm -rf /usr/local/go &&
                sudo tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz &&
                echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
                '''
                subprocess.run(['bash', '-c', go_install_cmd], check=True, timeout=600)
            
            # Setup Go environment
            env = os.environ.copy()
            env['PATH'] = f"/usr/local/go/bin:{env['PATH']}"
            env['GOPATH'] = os.path.expanduser('~/go')
            env['GOBIN'] = os.path.expanduser('~/go/bin')
            
            # Install alat Go
            go_tools = {
                'amass': 'github.com/owasp-amass/amass/v4/...',
                'httpx': 'github.com/projectdiscovery/httpx/cmd/httpx',
                'nuclei': 'github.com/projectdiscovery/nuclei/v3/cmd/nuclei',
                'dalfox': 'github.com/hahwul/dalfox/v2',
                'ffuf': 'github.com/ffuf/ffuf',
                'gau': 'github.com/lc/gau/v2/cmd/gau',
                'waybackurls': 'github.com/tomnomnom/waybackurls'
            }
            
            for tool_name, tool_path in go_tools.items():
                subprocess.run([
                    'go', 'install', '-v', tool_path
                ], env=env, check=True, timeout=300)
            
            # Install sqlmap (Python)
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'sqlmap'], check=True, timeout=300)
            
            # Install Playwright
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'playwright'], check=True, timeout=300)
            subprocess.run(['playwright', 'install', 'chromium'], check=True, timeout=300)
            
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _setup_python_environment(self):
        """Siapkan environment Python virtual."""
        try:
            venv_path = os.path.join(self.arc_dir, 'arc-env')
            
            # Buat virtual environment
            subprocess.run([sys.executable, '-m', 'venv', venv_path], check=True, timeout=60)
            
            # Install dependensi ARC
            pip_path = os.path.join(venv_path, 'bin', 'pip')
            requirements = [
                'requests', 'beautifulsoup4', 'lxml', 'playwright',
                'llama-cpp-python', 'PyYAML', 'watchdog', 'stem',
                'networkx', 'cryptography', 'PyPDF2', 'pdfplumber',
                'python-docx', 'openpyxl', 'web3', 'slither-analyzer'
            ]
            subprocess.run([pip_path, 'install'] + requirements, check=True, timeout=600)
            
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}