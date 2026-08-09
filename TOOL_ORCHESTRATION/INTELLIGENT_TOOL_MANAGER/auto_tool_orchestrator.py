"""
ARC Auto Tool Orchestrator v7.6 Final
Sistem orkestrasi tool otomatis yang adaptif dan self-healing.

Fitur:
- Deteksi tool yang dibutuhkan berdasarkan task
- Auto-download dari GitHub jika tool belum ada
- Build dan install otomatis
- Test di sandbox sebelum integrate
- Error handling yang robust untuk Kali Linux
- Self-healing saat instalasi gagal
"""

import subprocess
import os
import sys
import json
import time
import shutil
import tempfile
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Import komponen ARC
from .github_tool_installer import GitHubToolInstaller
from .dependency_resolver import DependencyResolver
from .self_healing_installer import SelfHealingInstaller
from .cli_tool_adapter import CLIToolAdapter
from .auto_integration_engine.sandbox_integrator import SandboxIntegrator
from .auto_integration_engine.template_validator import TemplateValidator


class AutoToolOrchestrator:
    """
    Orkestrator utama untuk manajemen tool otomatis ARC.
    Menangani: discovery -> download -> build -> test -> integrate
    """
    
    def __init__(self, tools_dir: str = "~/.arc/tools", sandbox_dir: str = "~/.arc/sandbox"):
        """
        Initialize orchestrator dengan direktori tool dan sandbox.
        
        Args:
            tools_dir: Direktori tempat tool diinstall
            sandbox_dir: Direktori untuk testing tool
        """
        self.tools_dir = os.path.expanduser(tools_dir)
        self.sandbox_dir = os.path.expanduser(sandbox_dir)
        
        # Buat direktori jika belum ada
        os.makedirs(self.tools_dir, exist_ok=True)
        os.makedirs(self.sandbox_dir, exist_ok=True)
        
        # Initialize komponen
        self.github_installer = GitHubToolInstaller(tools_dir)
        self.dependency_resolver = DependencyResolver()
        self.self_healing = SelfHealingInstaller(tools_dir)
        self.cli_adapter = CLIToolAdapter(tools_dir)
        self.sandbox = SandboxIntegrator(sandbox_dir)
        self.template_validator = TemplateValidator()
        
        # Registry tool yang dikenali ARC
        self.tool_registry = self._load_tool_registry()
        
        # Cache untuk tool yang sudah diinstall
        self.installed_tools_cache = self._load_installed_cache()

    def _load_tool_registry(self) -> Dict:
        """
        Load registry tool yang dikenali ARC.
        Registry ini mendefinisikan tool apa saja yang dibutuhkan untuk setiap kategori.
        """
        return {
            # Reconnaissance tools
            'subdomain_enum': {
                'primary': ['amass', 'subfinder', 'assetfinder'],
                'github_fallback': [
                    'https://github.com/owasp-amass/amass',
                    'https://github.com/projectdiscovery/subfinder',
                    'https://github.com/tomnomnom/assetfinder'
                ],
                'install_method': 'go',
                'required': True
            },
            'port_scan': {
                'primary': ['naabu', 'masscan', 'nmap'],
                'github_fallback': [
                    'https://github.com/projectdiscovery/naabu',
                    'https://github.com/robertdavidgraham/masscan'
                ],
                'install_method': 'go',
                'required': True
            },
            'web_scan': {
                'primary': ['nuclei', 'dalfox', 'ffuf'],
                'github_fallback': [
                    'https://github.com/projectdiscovery/nuclei',
                    'https://github.com/hahwul/dalfox',
                    'https://github.com/ffuf/ffuf'
                ],
                'install_method': 'go',
                'required': True
            },
            'wayback': {
                'primary': ['gau', 'waybackurls'],
                'github_fallback': [
                    'https://github.com/lc/gau',
                    'https://github.com/tomnomnom/waybackurls'
                ],
                'install_method': 'go',
                'required': False
            },
            'http_probe': {
                'primary': ['httpx'],
                'github_fallback': [
                    'https://github.com/projectdiscovery/httpx'
                ],
                'install_method': 'go',
                'required': True
            },
            # Vulnerability scanners
            'sql_injection': {
                'primary': ['sqlmap'],
                'github_fallback': [],
                'install_method': 'pip',
                'required': False
            },
            # Smart contract analysis
            'smart_contract': {
                'primary': ['slither'],
                'github_fallback': [
                    'https://github.com/crytic/slither'
                ],
                'install_method': 'pip',
                'required': False
            },
            # Browser automation
            'browser_automation': {
                'primary': ['playwright'],
                'github_fallback': [],
                'install_method': 'pip',
                'required': False
            }
        }
    
    def _load_installed_cache(self) -> Dict:
        """
        Load cache tool yang sudah diinstall dari file.
        """
        cache_file = os.path.join(self.tools_dir, '.installed_cache.json')
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_installed_cache(self):
        """Save cache tool yang diinstall ke file."""
        cache_file = os.path.join(self.tools_dir, '.installed_cache.json')
        try:
            with open(cache_file, 'w') as f:
                json.dump(self.installed_tools_cache, f, indent=2)
        except Exception as e:
            print(f"⚠️  Failed to save installed cache: {e}")

    def check_tool_available(self, tool_name: str) -> Tuple[bool, str]:
        """
        Cek apakah tool tersedia di system.
        
        Args:
            tool_name: Nama tool yang dicek
            
        Returns:
            Tuple[bool, str]: (is_available, path_or_error)
        """
        # Cek di PATH
        path = shutil.which(tool_name)
        if path:
            return True, path
        
        # Cek di tools_dir ARC
        tool_path = os.path.join(self.tools_dir, tool_name)
        if os.path.exists(tool_path):
            if os.access(tool_path, os.X_OK):
                return True, tool_path
            else:
                # Try to make it executable
                try:
                    os.chmod(tool_path, 0o755)
                    return True, tool_path
                except:
                    return False, f"Tool exists but not executable: {tool_path}"
        
        # Cek di ~/go/bin (untuk Go tools)
        go_bin = os.path.expanduser("~/go/bin")
        go_tool_path = os.path.join(go_bin, tool_name)
        if os.path.exists(go_tool_path):
            return True, go_tool_path
        
        return False, f"Tool not found: {tool_name}"
    
    def ensure_tool_available(self, tool_name: str, category: str = None) -> Dict:
        """
        Pastikan tool tersedia, download jika perlu.
        Ini adalah method UTAMA untuk auto-integration.
        
        Args:
            tool_name: Nama tool yang dibutuhkan
            category: Kategori tool (untuk mencari alternatif)
            
        Returns:
            Dict dengan status dan path tool
        """
        results = {
            'tool_name': tool_name,
            'category': category,
            'action_taken': None,
            'tool_path': None,
            'success': False,
            'error': None
        }
        
        try:
            # 1. Cek apakah tool sudah ada
            available, path = self.check_tool_available(tool_name)
            
            if available:
                results['action_taken'] = 'already_installed'
                results['tool_path'] = path
                results['success'] = True
                print(f"✅ Tool already available: {tool_name} at {path}")
                return results
            
            # 2. Tool belum ada, coba install
            print(f"🔍 Tool not found: {tool_name}, attempting auto-install...")
            
            # Tentukan strategi instalasi
            install_strategy = self._determine_install_strategy(tool_name, category)
            
            if install_strategy['method'] == 'go':
                install_result = self._install_go_tool(tool_name)
            elif install_strategy['method'] == 'pip':
                install_result = self._install_pip_tool(tool_name)
            elif install_strategy['method'] == 'github':
                install_result = self._install_from_github(
                    install_strategy.get('repo_url'), 
                    tool_name
                )
            else:
                install_result = {
                    'success': False, 
                    'error': f"Unknown install method: {install_strategy['method']}"
                }
            
            if install_result['success']:
                # Verifikasi instalasi
                available, path = self.check_tool_available(tool_name)
                if available:
                    results['action_taken'] = 'auto_installed'
                    results['tool_path'] = path
                    results['success'] = True
                    
                    # Update cache
                    self.installed_tools_cache[tool_name] = {
                        'path': path,
                        'installed_at': int(time.time()),
                        'method': install_strategy['method']
                    }
                    self._save_installed_cache()
                    
                    print(f"✅ Successfully installed: {tool_name} at {path}")
                else:
                    results['error'] = "Installation reported success but tool not found"
            else:
                results['error'] = install_result.get('error', 'Installation failed')
                results['action_taken'] = 'install_failed'
                print(f"❌ Failed to install {tool_name}: {results['error']}")
        
        except Exception as e:
            results['error'] = f"Unexpected error: {str(e)}"
            print(f"❌ Error ensuring tool {tool_name}: {e}")
        
        return results

    def _determine_install_strategy(self, tool_name: str, category: str = None) -> Dict:
        """
        Tentukan strategi instalasi untuk tool.
        """
        # Cek di registry terlebih dahulu
        if category and category in self.tool_registry:
            cat_tools = self.tool_registry[category]
            if tool_name in cat_tools.get('primary', []):
                return {
                    'method': cat_tools['install_method'],
                    'repo_url': None
                }
        
        # Deteksi berdasarkan tool_name
        go_tools = ['amass', 'subfinder', 'assetfinder', 'naabu', 'masscan', 'nmap',
                    'nuclei', 'dalfox', 'ffuf', 'gau', 'waybackurls', 'httpx']
        
        if tool_name in go_tools:
            return {'method': 'go', 'repo_url': None}
        
        pip_tools = ['sqlmap', 'slither', 'playwright', 'requests', 'beautifulsoup4']
        
        if tool_name in pip_tools:
            return {'method': 'pip', 'repo_url': None}
        
        # Default: coba GitHub search
        return {'method': 'github', 'repo_url': None}
    
    def _install_go_tool(self, tool_name: str) -> Dict:
        """
        Install Go tool menggunakan go install.
        """
        try:
            # Pastikan Go terinstall
            if not shutil.which('go'):
                print("📦 Go not found, installing Go...")
                go_result = self._install_go()
                if not go_result['success']:
                    return go_result
            
            # Setup Go environment
            env = os.environ.copy()
            env['PATH'] = f"/usr/local/go/bin:{env['PATH']}"
            env['GOPATH'] = os.path.expanduser('~/go')
            env['GOBIN'] = os.path.expanduser('~/go/bin')
            
            # Mapping tool ke module path
            go_modules = {
                'amass': 'github.com/owasp-amass/amass/v4/...',
                'httpx': 'github.com/projectdiscovery/httpx/cmd/httpx',
                'nuclei': 'github.com/projectdiscovery/nuclei/v3/cmd/nuclei',
                'dalfox': 'github.com/hahwul/dalfox/v2',
                'ffuf': 'github.com/ffuf/ffuf',
                'gau': 'github.com/lc/gau/v2/cmd/gau',
                'waybackurls': 'github.com/tomnomnom/waybackurls',
                'subfinder': 'github.com/projectdiscovery/subfinder/v2/cmd/subfinder',
                'naabu': 'github.com/projectdiscovery/naabu/v2/cmd/naabu'
            }
            
            module_path = go_modules.get(tool_name)
            if not module_path:
                return {'success': False, 'error': f"Unknown Go tool: {tool_name}"}
            
            print(f"🔨 Installing {tool_name} via go install...")
            
            # Use self-healing installer
            result = self.self_healing.install_with_healing(
                ['go', 'install', '-v', module_path],
                max_attempts=3
            )
            
            if result['final_success']:
                return {'success': True, 'attempt': result['successful_attempt']}
            else:
                return {'success': False, 'error': 'Go install failed after retries'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _install_pip_tool(self, tool_name: str) -> Dict:
        """
        Install Python tool menggunakan pip.
        """
        try:
            print(f"🔨 Installing {tool_name} via pip...")
            
            # Gunakan pip dari venv ARC jika ada, atau pip system
            pip_cmd = self._get_pip_command()
            
            result = self.self_healing.install_with_healing(
                [pip_cmd, 'install', '--user', tool_name],
                max_attempts=3
            )
            
            if result['final_success']:
                return {'success': True, 'attempt': result['successful_attempt']}
            else:
                return {'success': False, 'error': 'Pip install failed after retries'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _install_from_github(self, repo_url: str, tool_name: str) -> Dict:
        """
        Install tool dari GitHub repository.
        """
        try:
            print(f"🔨 Installing {tool_name} from GitHub: {repo_url}")
            
            result = self.github_installer.install_from_github(repo_url)
            
            if result['success']:
                return {'success': True, 'path': result['installation_path']}
            else:
                return {'success': False, 'error': result.get('error', 'GitHub install failed')}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _install_go(self) -> Dict:
        """
        Install Go programming language.
        """
        try:
            if shutil.which('go'):
                return {'success': True, 'message': 'Go already installed'}
            
            print("📦 Installing Go 1.21.0...")
            
            # Download dan install Go
            go_url = "https://go.dev/dl/go1.21.0.linux-amd64.tar.gz"
            go_tar = "/tmp/go1.21.0.linux-amd64.tar.gz"
            
            # Download
            subprocess.run(['wget', '-q', go_url, '-O', go_tar], check=True, timeout=120)
            
            # Extract
            subprocess.run(['sudo', 'rm', '-rf', '/usr/local/go'], check=True)
            subprocess.run(['sudo', 'tar', '-C', '/usr/local', '-xzf', go_tar], check=True)
            
            # Setup PATH
            bashrc = os.path.expanduser('~/.bashrc')
            with open(bashrc, 'a') as f:
                f.write('\nexport PATH=$PATH:/usr/local/go/bin\n')
                f.write('export GOPATH=$HOME/go\n')
                f.write('export GOBIN=$HOME/go/bin\n')
            
            return {'success': True, 'message': 'Go installed successfully'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_pip_command(self) -> str:
        """
        Dapatkan command pip yang sesuai.
        Prioritas: venv ARC > pip3 > pip
        """
        # Cek venv ARC
        venv_pip = os.path.join(self.tools_dir, '..', 'arc-env', 'bin', 'pip')
        if os.path.exists(venv_pip):
            return venv_pip
        
        # Cek pip3
        if shutil.which('pip3'):
            return 'pip3'
        
        # Fallback ke pip
        return 'pip'

    def ensure_tools_for_task(self, task_type: str) -> Dict:
        """
        Pastikan semua tool yang dibutuhkan untuk suatu task tersedia.
        
        Args:
            task_type: Jenis task (subdomain_enum, port_scan, web_scan, dll)
            
        Returns:
            Dict dengan status semua tool yang dibutuhkan
        """
        results = {
            'task_type': task_type,
            'tools_checked': [],
            'tools_available': [],
            'tools_failed': [],
            'all_ready': False
        }
        
        # Ambil daftar tool yang dibutuhkan
        task_config = self.tool_registry.get(task_type)
        
        if not task_config:
            results['error'] = f"Unknown task type: {task_type}"
            return results
        
        required_tools = task_config.get('primary', [])
        
        print(f"\n🎯 Ensuring tools for task: {task_type}")
        print(f"   Required tools: {', '.join(required_tools)}")
        
        for tool in required_tools:
            tool_result = self.ensure_tool_available(tool, task_type)
            results['tools_checked'].append({
                'tool': tool,
                'result': tool_result
            })
            
            if tool_result['success']:
                results['tools_available'].append(tool)
            else:
                results['tools_failed'].append({
                    'tool': tool,
                    'error': tool_result.get('error')
                })
        
        # Cek apakah semua tool tersedia
        results['all_ready'] = len(results['tools_failed']) == 0
        
        if results['all_ready']:
            print(f"✅ All tools ready for {task_type}: {len(results['tools_available'])}/{len(required_tools)}")
        else:
            print(f"⚠️  Some tools missing for {task_type}: {len(results['tools_available'])}/{len(required_tools)}")
            for failed in results['tools_failed']:
                print(f"   ❌ {failed['tool']}: {failed['error']}")
        
        return results
    
    def get_tool_executor(self, tool_name: str) -> Optional[Dict]:
        """
        Dapatkan executor config untuk tool.
        
        Args:
            tool_name: Nama tool
            
        Returns:
            Dict dengan config executor atau None
        """
        available, path = self.check_tool_available(tool_name)
        
        if not available:
            return None
        
        # Adapt tool menggunakan CLIToolAdapter
        adapter_result = self.cli_adapter.adapt_cli_tool(tool_name)
        
        if adapter_result['success']:
            return {
                'tool_name': tool_name,
                'path': path,
                'execution_method': adapter_result['execution_method'],
                'capabilities': adapter_result['detected_capabilities']
            }
        
        return None
    
    def test_tool_in_sandbox(self, tool_name: str, test_command: List[str] = None) -> Dict:
        """
        Test tool di sandbox sebelum digunakan.
        
        Args:
            tool_name: Nama tool yang ditest
            test_command: Command untuk test (default: --help)
            
        Returns:
            Dict dengan hasil testing
        """
        if test_command is None:
            test_command = ['--help']
        
        # Dapatkan path tool
        available, path = self.check_tool_available(tool_name)
        
        if not available:
            return {
                'success': False,
                'error': f"Tool not available: {tool_name}"
            }
        
        # Test di sandbox
        return self.sandbox.test_in_sandbox(path, test_command)

    def get_status_report(self) -> Dict:
        """
        Dapatkan laporan status semua tool.
        
        Returns:
            Dict dengan status tool management
        """
        report = {
            'orchestrator_version': '7.6.0',
            'tools_dir': self.tools_dir,
            'sandbox_dir': self.sandbox_dir,
            'installed_tools': len(self.installed_tools_cache),
            'tool_registry_categories': len(self.tool_registry),
            'tools': {}
        }
        
        # Cek setiap tool di registry
        for category, config in self.tool_registry.items():
            primary_tools = config.get('primary', [])
            for tool in primary_tools:
                available, path = self.check_tool_available(tool)
                report['tools'][tool] = {
                    'available': available,
                    'path': path if available else None,
                    'category': category,
                    'required': config.get('required', False)
                }
        
        return report
    
    def integrate_with_arc_main(self, arc_main_instance):
        """
        Integrasi dengan arc_main.py untuk auto-tool management.
        
        Args:
            arc_main_instance: Instance dari ARCOrchestrator di arc_main.py
        """
        try:
            # Tambahkan method ke arc_main instance
            arc_main_instance.ensure_tool_available = self.ensure_tool_available
            arc_main_instance.ensure_tools_for_task = self.ensure_tools_for_task
            arc_main_instance.get_tool_executor = self.get_tool_executor
            arc_main_instance.test_tool_in_sandbox = self.test_tool_in_sandbox
            arc_main_instance.tool_orchestrator = self
            
            print("✅ AutoToolOrchestrator integrated with ARC Main")
            return True
        except Exception as e:
            print(f"❌ Failed to integrate with ARC Main: {e}")
            return False



    def search_and_install_tool_from_github(self, tool_name, category=None):
        """
        Cari tool di GitHub secara dinamis jika tidak ada di registry.
        """
        results = {
            'tool_name': tool_name,
            'category': category,
            'search_performed': False,
            'github_candidates': [],
            'success': False
        }
        
        try:
            if category and category in self.tool_registry:
                cat_tools = self.tool_registry[category]
                if tool_name in cat_tools.get('primary', []):
                    return self.ensure_tool_available(tool_name, category)
            
            print(f"Searching GitHub for: {tool_name}")
            results['search_performed'] = True
            
            github_candidates = self._search_github_for_tool(tool_name, category)
            results['github_candidates'] = github_candidates
            
            if not github_candidates:
                results['error'] = f"No GitHub repos found for: {tool_name}"
                return results
            
            best_candidate = self._select_best_tool_candidate(github_candidates)
            
            if not best_candidate:
                results['error'] = "No suitable candidate found"
                return results
            
            print(f"Best candidate: {best_candidate['name']} ({best_candidate.get('stars', 0)} stars)")
            
            install_result = self._install_from_github(best_candidate['url'], tool_name)
            results['installation_result'] = install_result
            results['success'] = install_result['success']
            
            if install_result['success']:
                available, path = self.check_tool_available(tool_name)
                if available:
                    results['tool_path'] = path
                    results['action_taken'] = 'github_search_and_install'
                    
                    self.installed_tools_cache[tool_name] = {
                        'path': path,
                        'installed_at': int(time.time()),
                        'method': 'github_dynamic',
                        'source_url': best_candidate['url']
                    }
                    self._save_installed_cache()
                    print(f"Successfully installed: {tool_name}")
        
        except Exception as e:
            results['error'] = f"Search and install failed: {str(e)}"
        
        return results

    def _search_github_for_tool(self, tool_name, category=None):
        """Cari tool di GitHub menggunakan API."""
        candidates = []
        
        try:
            query = f"{tool_name} security tool"
            if category:
                query += f" {category}"
            
            params = {
                'q': query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': 10
            }
            
            print(f"   GitHub query: {query}")
            
            response = requests.get(
                "https://api.github.com/search/repositories",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                repos = data.get('items', [])
                
                for repo in repos:
                    candidate = {
                        'name': repo.get('name'),
                        'url': repo.get('html_url'),
                        'stars': repo.get('stargazers_count', 0),
                        'language': repo.get('language'),
                        'description': repo.get('description', '')
                    }
                    candidates.append(candidate)
                
                print(f"   Found {len(candidates)} candidates")
        
        except Exception as e:
            print(f"   GitHub search failed: {e}")
        
        return candidates
    
    def _select_best_tool_candidate(self, candidates):
        """Pilih kandidat terbaik berdasarkan stars dan relevance."""
        if not candidates:
            return None
        
        candidates.sort(key=lambda x: x.get('stars', 0), reverse=True)
        
        best = candidates[0]
        if best.get('stars', 0) >= 10:
            return best
        
        return None
    
    def discover_and_install_tools(self, task_type):
        """
        Discover tools baru di GitHub untuk task tertentu.
        """
        results = {
            'task_type': task_type,
            'tools_installed': [],
            'tools_failed': []
        }
        
        try:
            task_config = self.tool_registry.get(task_type, {})
            required_tools = task_config.get('primary', [])
            
            print(f"\nDiscovering tools for: {task_type}")
            
            for tool in required_tools:
                available, _ = self.check_tool_available(tool)
                
                if not available:
                    print(f"  Discovering: {tool}")
                    result = self.search_and_install_tool_from_github(tool, task_type)
                    
                    if result['success']:
                        results['tools_installed'].append(tool)
                    else:
                        results['tools_failed'].append({
                            'tool': tool,
                            'error': result.get('error')
                        })
        
        except Exception as e:
            results['error'] = str(e)
        
        return results

# Utility function untuk quick usage
def ensure_security_tools() -> Dict:
    """
    Quick function untuk memastikan semua security tools utama tersedia.
    """
    orchestrator = AutoToolOrchestrator()
    
    results = {
        'subdomain_enum': orchestrator.ensure_tools_for_task('subdomain_enum'),
        'port_scan': orchestrator.ensure_tools_for_task('port_scan'),
        'web_scan': orchestrator.ensure_tools_for_task('web_scan'),
        'wayback': orchestrator.ensure_tools_for_task('wayback'),
        'http_probe': orchestrator.ensure_tools_for_task('http_probe')
    }
    
    return results


if __name__ == "__main__":
    # Test orchestrator
    print("=== ARC Auto Tool Orchestrator Test ===\n")
    
    orchestrator = AutoToolOrchestrator()
    
    # Test 1: Check status
    print("📊 Checking tool status...")
    status = orchestrator.get_status_report()
    print(f"   Installed tools cache: {status['installed_tools']}")
    print(f"   Registry categories: {status['tool_registry_categories']}")
    
    # Test 2: Ensure tools for subdomain enumeration
    print("\n🎯 Testing auto-install for subdomain_enum...")
    result = orchestrator.ensure_tools_for_task('subdomain_enum')
    print(f"   All ready: {result['all_ready']}")
    print(f"   Available: {result['tools_available']}")
    print(f"   Failed: {[f['tool'] for f in result['tools_failed']]}")
    
    # Test 3: Check specific tool
    print("\n🔍 Testing specific tool check (nuclei)...")
    nuclei_result = orchestrator.ensure_tool_available('nuclei', 'web_scan')
    print(f"   Success: {nuclei_result['success']}")
    print(f"   Action: {nuclei_result['action_taken']}")
    print(f"   Path: {nuclei_result.get('tool_path')}")
    
    print("\n✅ Orchestrator test complete")

