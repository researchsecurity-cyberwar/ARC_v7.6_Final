"""
ARC Autonomous Session Engine v7.6 Final
==========================================
Otak otonom untuk menjalankan ARC SECARA MANDIRI di terminal (khususnya
Kali Linux / Debian-based):

  1. DETEKSI LINGKUNGAN   -> OS/distro, package manager (apt/dnf/yum/pacman),
                            shell/terminal, cwd, python env.
  2. INSTALL MANDIRI      -> pilih metode terbaik:
                              apt > pip > go install > git clone+build >
                              ekstrak binary release (tar.gz/zip dari GitHub).
  3. UPDATE DATA          -> CVE/OSINT, template nuclei/subfinder otomatis.
  4. EKSEKUSI             -> pastikan tool -> IntelligentToolCommander
                            menjalankannya -> lapor di sesi terminal.
"""

import os
import re
import sys
import time
import shutil
import platform
import subprocess
from typing import Dict, List, Optional

try:
    from .session_approval_controller import SessionApprovalController
except ImportError:
    from TOOL_ORCHESTRATION.INTELLIGENT_TOOL_MANAGER.session_approval_controller import SessionApprovalController


class AutonomousSessionEngine:
    """
    Driver otonom yang memastikan ARC dapat meng-install, memperbarui, dan
    menjalankan tool apa pun sendiri dalam sesi terminal aktif.
    """

    # Metode install utk tool umum. Kunci=tool, nilai=daftar [metode, target].
    # 'target' = package apt / module pip / repo go / repo github.
    INSTALL_ROUTES: Dict[str, List] = {
        'nmap':       [['apt', 'nmap']],
        'masscan':    [['apt', 'masscan']],
        'wireshark':  [['apt', 'wireshark']],
        'sqlmap':     [['pip', 'sqlmap'], ['apt', 'sqlmap']],
        'nikto':      [['apt', 'nikto']],
        'gobuster':   [['apt', 'gobuster'], ['go', 'gobuster']],
        'hydra':      [['apt', 'hydra']],
        'john':       [['apt', 'john']],
        'nuclei':     [['go', 'nuclei'], ['binary', 'projectdiscovery/nuclei']],
        'httpx':      [['go', 'httpx'], ['binary', 'projectdiscovery/httpx']],
        'subfinder':  [['go', 'subfinder'], ['binary', 'projectdiscovery/subfinder']],
        'naabu':      [['go', 'naabu'], ['binary', 'projectdiscovery/naabu']],
        'dalfox':     [['go', 'dalfox'], ['binary', 'hahwul/dalfox']],
        'ffuf':       [['go', 'ffuf'], ['binary', 'ffuf/ffuf']],
        'gau':        [['go', 'gau'], ['binary', 'lc/gau']],
        'amass':      [['go', 'amass'], ['binary', 'owasp-amass/amass']],
        'waybackurls':[['go', 'waybackurls']],
        'assetfinder':[['go', 'assetfinder']],
        'scapy':      [['pip', 'scapy']],
        'requests':   [['pip', 'requests']],
        'beautifulsoup4': [['pip', 'beautifulsoup4']],
        'slither':    [['pip', 'slither']],
        'selenium':   [['pip', 'selenium']],
    }

    def __init__(self, orchestrator=None, commander=None, workdir: str = None,
                 require_sudo: bool = True,
                 approval_controller: Optional['SessionApprovalController'] = None):
        self.orchestrator = orchestrator
        self.commander = commander
        self.workdir = workdir or os.getcwd()
        self.require_sudo = require_sudo
        self.installed_this_session = []
        self.updated_this_session = []
        self.log: List[str] = []
        self.env = self.detect_environment()
        self.approval_controller = approval_controller

    # ------------------------------------------------------------------
    # 1. DETEKSI LINGKUNGAN (OS/distro, package manager, terminal, cwd)
    # ------------------------------------------------------------------
    def detect_environment(self) -> Dict:
        env = {
            'platform': platform.system().lower(),
            'python': sys.executable,
            'cwd': self.workdir,
            'is_posix': os.name == 'posix',
        }
        distro = self._detect_distro()
        env['distro'] = distro
        env['is_kali'] = 'kali' in distro.lower()
        env['is_debian'] = any(d in distro.lower() for d in
                               ('debian', 'ubuntu', 'kali', 'linuxmint'))
        env['package_managers'] = self._detect_pkg_managers()
        env['has_apt'] = 'apt' in env['package_managers']
        env['sudo_available'] = bool(shutil.which('sudo'))
        env['shell'] = os.environ.get('SHELL', '')
        env['term'] = os.environ.get('TERM', '')
        env['session_type'] = os.environ.get('XDG_SESSION_TYPE', '')
        return env

    @staticmethod
    def _detect_distro() -> str:
        for path in ('/etc/os-release', '/etc/lsb-release'):
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        for line in f:
                            if line.startswith('PRETTY_NAME='):
                                return line.split('=', 1)[1].strip().strip('"')
                except Exception:
                    pass
        return platform.platform()

    @staticmethod
    def _detect_pkg_managers() -> List[str]:
        found = []
        for pm in ('apt', 'dnf', 'yum', 'pacman', 'zypper', 'brew'):
            if shutil.which(pm):
                found.append(pm)
        return found

    def log_msg(self, msg: str):
        self.log.append(msg)
        print(msg)

    @staticmethod
    def _make_install_pin(tool: str) -> str:
        import random, string
        return ''.join(random.choices(string.digits, k=6))

    # ------------------------------------------------------------------
    # util eksekusi (memakai sudo bila perlu untuk apt di sesi non-root)
    # ------------------------------------------------------------------
    def _run(self, argv: List[str], timeout: int = 900,
             cwd: Optional[str] = None, sudo: bool = False) -> Dict:
        cmd = list(argv)
        if sudo and self.env.get('has_apt') and shutil.which('sudo'):
            try:
                if os.geteuid() != 0:
                    cmd = ['sudo'] + cmd
            except Exception:
                pass
        started = time.time()
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True,
                                  timeout=timeout, cwd=cwd or self.workdir)
            return {
                'success': proc.returncode == 0,
                'returncode': proc.returncode,
                'stdout': (proc.stdout or '')[:120000],
                'stderr': (proc.stderr or '')[:30000],
                'argv': cmd,
                'execution_time': round(time.time() - started, 2),
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'timeout', 'argv': cmd,
                    'stderr': f'Timeout after {timeout}s'}
        except FileNotFoundError:
            return {'success': False, 'error': 'not_found',
                    'stderr': f'Not found: {argv[0]}', 'argv': cmd}
        except Exception as e:
            return {'success': False, 'error': str(e), 'argv': cmd}

    def require_root_privileges(self) -> bool:
        """Akses root/sudo non-interaktif tersedia (untuk apt)."""
        if not self.env.get('has_apt'):
            return False
        try:
            if os.geteuid() == 0:
                return True
        except Exception:
            pass
        if self.env.get('sudo_available'):
            probe = self._run(['sudo', '-n', 'true'], timeout=15)
            return probe.get('success', False)
        return False


    # ------------------------------------------------------------------
    # 2. INSTALL MANDIRI (apt / pip / go / git / binary release)
    # ------------------------------------------------------------------
    def _pip_cmd(self) -> str:
        if shutil.which('pip3'):
            return 'pip3'
        if shutil.which('pip'):
            return 'pip'
        return 'python3'

    def install_apt(self, pkg: str) -> Dict:
        if not self.env.get('has_apt'):
            return {'success': False, 'error': 'apt tidak tersedia di sistem ini'}
        self.log_msg(f"📦 [apt] menginstal {pkg}")
        upd = self._run(['apt-get', 'update', '-y'], timeout=1200, sudo=True)
        inst = self._run(['apt-get', 'install', '-y', pkg], timeout=1800, sudo=True)
        return {'success': inst.get('success', False), 'method': 'apt',
                'update_ok': upd.get('success', False),
                'stderr': inst.get('stderr', '')[:300]}

    def install_pip(self, module: str) -> Dict:
        self.log_msg(f"🐍 [pip] menginstal {module}")
        pip = self._pip_cmd()
        if pip == 'python3':
            cmd = ['python3', '-m', 'pip', 'install', '--user', module]
        else:
            cmd = [pip, 'install', '--user', module]
        r = self._run(cmd, timeout=1200)
        return {'success': r.get('success', False), 'method': 'pip',
                'stderr': r.get('stderr', '')[:300]}

    def install_go(self, tool: str) -> Dict:
        self.log_msg(f"🐹 [go] menginstal {tool}")
        if self.orchestrator is not None and hasattr(self.orchestrator, '_install_go_tool'):
            res = self.orchestrator._install_go_tool(tool)
            return {'success': bool(res.get('success', False)), 'method': 'go',
                    'error': res.get('error')}
        return {'success': False, 'error': 'orchestrator tidak tersedia untuk go install',
                'method': 'go'}

    def install_git(self, repo_url: str) -> Dict:
        self.log_msg(f"📥 [git] kloning {repo_url}")
        if self.orchestrator is not None and hasattr(self.orchestrator, 'github_installer'):
            res = self.orchestrator.github_installer.install_from_github(repo_url)
            return {'success': res.get('success', False), 'method': 'git',
                    'error': res.get('error')}
        name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
        dest = os.path.join(self.workdir, 'tools', name)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        r = self._run(['git', 'clone', '--depth', '1', repo_url, dest], timeout=600)
        if r.get('success'):
            return {'success': True, 'method': 'git', 'path': dest}
        return {'success': False, 'method': 'git', 'error': r.get('stderr', '')[:300]}


    def install_binary_release(self, repo: str, exec_name: str = None) -> Dict:
        """
        Download & ekstrak binary release dari GitHub (tar.gz/zip) lalu pasang
        ke /usr/local/bin — "download, ekstrak, pasang sendiri".
        """
        if not self.env.get('is_posix'):
            return {'success': False, 'error': 'binary release hanya utk POSIX',
                    'method': 'binary'}
        self.log_msg(f"⬇️  [binary] unduh release {repo}")
        try:
            import requests
            api = f"https://api.github.com/repos/{repo}/releases/latest"
            info = requests.get(api, timeout=30).json()
            assets = info.get('assets', [])
            asset = None
            for a in assets:
                n = a['name'].lower()
                if 'linux' in n and ('amd64' in n or 'x86_64' in n or '64' in n):
                    if n.endswith(('.tar.gz', '.tgz', '.zip')):
                        asset = a
                        break
            if not asset:
                return {'success': False,
                        'error': f'tidak ada asset linux utk {repo}', 'method': 'binary'}
            url = asset['browser_download_url']
            tmp = tempfile.mkdtemp(prefix='arc_bin_')
            arch = os.path.join(tmp, os.path.basename(url))
            dl = self._run(['wget', '-q', '-O', arch, url], timeout=1200)
            if not dl.get('success'):
                dl = self._run(['curl', '-sL', '-o', arch, url], timeout=1200)
            if not dl.get('success'):
                shutil.rmtree(tmp, ignore_errors=True)
                return {'success': False, 'error': 'download gagal', 'method': 'binary'}
            if arch.endswith('.zip'):
                self._run(['unzip', '-o', arch, '-d', tmp], timeout=300)
            else:
                self._run(['tar', '-xzf', arch, '-C', tmp], timeout=300)
            exe = exec_name or repo.split('/')[-1]
            found = None
            for root, _, files in os.walk(tmp):
                for f in files:
                    if f == exe or (exe in f and '.' not in f):
                        p = os.path.join(root, f)
                        found = p
                        break
                if found:
                    break
            if not found:
                found = self._find_executable(tmp)
            if not found:
                shutil.rmtree(tmp, ignore_errors=True)
                return {'success': False, 'error': 'binary tidak ditemukan di release',
                        'method': 'binary'}
            os.chmod(found, 0o755)
            target = '/usr/local/bin/' + os.path.basename(found)
            inst = self._run(['install', '-m', '0755', found, target],
                             timeout=120, sudo=True)
            shutil.rmtree(tmp, ignore_errors=True)
            return {'success': inst.get('success', False), 'method': 'binary',
                    'path': target}
        except Exception as e:
            return {'success': False, 'error': str(e)[:300], 'method': 'binary'}

    @staticmethod
    def _find_executable(root: str) -> Optional[str]:
        for dirpath, _, files in os.walk(root):
            for f in files:
                if f.endswith(('.go', '.py', '.txt', '.md', '.json')):
                    continue
                p = os.path.join(dirpath, f)
                if os.path.isfile(p) and not f.startswith('.'):
                    return p
        return None


    # ------------------------------------------------------------------
    # 3. ENSURE + UPDATE DATA (CVE, template nuclei/subfinder, dst)
    # ------------------------------------------------------------------
    def ensure_tool(self, tool: str) -> Dict:
        """Pastikan tool tersedia; bila tidak, install dengan metode terbaik."""
        if shutil.which(tool):
            return {'success': True, 'tool': tool, 'action': 'already_installed'}

        routes = self.INSTALL_ROUTES.get(tool, [])
        if not routes:
            # tool tak dikenal -> serahkan ke orkestrator/commander auto-install
            if self.orchestrator is not None and hasattr(self.orchestrator, 'ensure_tool_available'):
                res = self.orchestrator.ensure_tool_available(tool)
                return {'success': bool(res.get('success', False)), 'tool': tool,
                        'action': 'orchestrator', 'error': res.get('error')}
            return {'success': False, 'tool': tool,
                    'error': f'tidak ada rute install & orchestrator tidak tersedia'}

        # Approval gate: minta izin sebelum install (terutama apt/sudo)
        if self.approval_controller is not None:
            needs_sudo = any(m == 'apt' for m, _ in routes)
            level = 'sudo_pin' if needs_sudo else 'install'
            pin = self._make_install_pin(tool) if needs_sudo else None
            req = self.approval_controller.request(
                title=f"Install tool: {tool}",
                description=f"ARC akan menginstall {tool} via {', '.join(m for m,_ in routes)}",
                level=level,
                pin=pin,
                meta={'tool': tool, 'routes': routes, 'needs_sudo': needs_sudo},
                timeout=600,
            )
            decision = self.approval_controller.await_decision(req.id)
            if decision != 'approved':
                return {'success': False, 'tool': tool,
                        'error': f'Install {tool} ditolak/ditolak otomatis: {decision}'}

        for method, target in routes:
            try:
                if method == 'apt':
                    if not self.env.get('has_apt'):
                        continue
                    res = self.install_apt(target)
                elif method == 'pip':
                    res = self.install_pip(target)
                elif method == 'go':
                    res = self.install_go(tool)
                elif method == 'git':
                    res = self.install_git(target)
                elif method == 'binary':
                    res = self.install_binary_release(target, exec_name=tool)
                else:
                    continue
            except Exception as e:
                res = {'success': False, 'error': str(e)[:300], 'method': method}

            if res.get('success') and shutil.which(tool):
                self.installed_this_session.append(tool)
                self.log_msg(f"✅ {tool} terinstall via {res.get('method')}")
                return {'success': True, 'tool': tool, 'action': 'installed',
                        'method': res.get('method')}

        return {'success': False, 'tool': tool,
                'error': 'semua metode install gagal; cek jaringan/izin/sudo'}

    def update_tool_data(self, tool: str) -> Dict:
        """Perbarui data/severity tool yang punya mekanisme update sendiri."""
        self.log_msg(f"🔄 [update] memperbarui data {tool}")
        if tool == 'nuclei':
            r = self._run(['nuclei', '-update-templates'], timeout=1200)
        elif tool == 'subfinder':
            r = self._run(['subfinder', '-up'], timeout=600)
        elif tool == 'amass':
            r = self._run(['amass', '-update'], timeout=600)
        elif tool == 'sqlmap':
            r = self._run(['sqlmap', '--update'], timeout=900)
        else:
            return {'success': False, 'tool': tool,
                    'error': f'tidak ada mekanisme update utk {tool}'}
        if r.get('success'):
            self.updated_this_session.append(tool)
        return {'success': r.get('success', False), 'tool': tool,
                'stderr': r.get('stderr', '')[:300]}

    def update_all_data(self, tools: Optional[List[str]] = None) -> Dict:
        """Perbarui CVE/OSINT (via INFRASTRUCTURE) + data tool penting."""
        results = {'cve_osint': {}, 'tool_updates': {}}
        try:
            from INFRASTRUCTURE.cve_osint_updater import CVEOSINTUpdater
            updater = CVEOSINTUpdater()
            results['cve_osint'] = updater.update_realtime_threats(days_back=1)
        except Exception as e:
            results['cve_osint'] = {'error': str(e)[:300]}
        tools = tools or ['nuclei', 'subfinder']
        for t in tools:
            if shutil.which(t):
                results['tool_updates'][t] = self.update_tool_data(t)
        return results

    # ------------------------------------------------------------------
    # 4. EKSEKUSI OTONOM (ensure + commander.smart_execute + lapor)
    # ------------------------------------------------------------------
    def run_autonomously(self, task: Dict, timeout: int = 600) -> Dict:
        """Jalankan task otonom penuh dalam sesi terminal aktif."""
        tool = task.get('tool') or self._recommend(task.get('intent'))
        if not tool:
            return {'success': False, 'error': 'tool & intent tidak diketahui'}

        # 1) pastikan tool tersedia (install sendiri bila perlu)
        ensure = self.ensure_tool(tool)

        # 2) update data bila minta
        if task.get('update_data'):
            self.update_tool_data(tool)

        # 3) eksekusi via commander (belajar antarmuka + jalankan)
        if ensure.get('success'):
            if self.commander is not None:
                res = self.commander.smart_execute(
                    tool_name=tool,
                    intent=task.get('intent', 'generic'),
                    params=task.get('params', {}),
                    subcommand=task.get('subcommand'),
                    timeout=task.get('timeout', timeout),
                )
                return {'tool': tool, 'ensure': ensure, 'execution': res,
                        'session': self.session_report()}
            return {'tool': tool, 'success': True, 'ensure': ensure,
                    'note': 'tool siap; commander tidak tersedia utk eksekusi'}

        return {'tool': tool, 'success': False, 'ensure': ensure}

    @staticmethod
    def _recommend(intent: Optional[str]) -> Optional[str]:
        return None

    def session_report(self) -> Dict:
        return {
            'environment': self.env,
            'root_sudo': self.require_root_privileges(),
            'installed_this_session': self.installed_this_session,
            'updated_this_session': self.updated_this_session,
            'log': self.log[-50:],
        }



# ----------------------------------------------------------------------
# CLI: jalankan langsung di terminal, misal:
#   python autonomous_session_engine.py status
#   python autonomous_session_engine.py ensure nmap
#   python autonomous_session_engine.py update
#   python autonomous_session_engine.py run nuclei web_scan --url https://example.com
# ----------------------------------------------------------------------
def create_autonomous_engine(orchestrator=None, commander=None,
                             approval_controller: Optional['SessionApprovalController'] = None) -> AutonomousSessionEngine:
    # Import aman: relatif bila dipakai sebagai bagian paket, absolut bila
    # modul ini dijalankan langsung dari terminal (python ...py).
    try:
        from .auto_tool_orchestrator import AutoToolOrchestrator
        from .intelligent_tool_commander import create_smart_tool_commander
    except ImportError:
        from TOOL_ORCHESTRATION.INTELLIGENT_TOOL_MANAGER.auto_tool_orchestrator import AutoToolOrchestrator
        from TOOL_ORCHESTRATION.INTELLIGENT_TOOL_MANAGER.intelligent_tool_commander import create_smart_tool_commander
    if orchestrator is None:
        try:
            orchestrator = AutoToolOrchestrator()
        except Exception:
            orchestrator = None
    if commander is None:
        commander = create_smart_tool_commander(orchestrator=orchestrator)
    if approval_controller is None:
        try:
            approval_controller = SessionApprovalController(auto_start_poller=False)
        except Exception:
            approval_controller = None
    return AutonomousSessionEngine(
        orchestrator=orchestrator,
        commander=commander,
        approval_controller=approval_controller,
    )


if __name__ == "__main__":
    import argparse
    # Pastikan root proyek ada di sys.path agar import absolut berhasil
    _root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if _root not in sys.path:
        sys.path.insert(0, _root)

    p = argparse.ArgumentParser(prog="arc-session",
                                description="ARC Autonomous Session Engine (Kali terminal)")
    sub = p.add_subparsers(dest="cmd")

    sp = sub.add_parser("status", help="tampilkan info lingkungan & sesi")
    se = sub.add_parser("ensure", help="pastikan tool tersedia (install sendiri)")
    se.add_argument("tool")
    su = sub.add_parser("update", help="perbarui data tool penting")
    sr = sub.add_parser("run", help="jalankan task otonom")
    sr.add_argument("tool")
    sr.add_argument("--intent", default="generic")
    sr.add_argument("--url", default=None)
    sr.add_argument("--subcommand", default=None)

    args = p.parse_args()
    engine = create_autonomous_engine()

    if args.cmd == "status":
        print("=== ARC Autonomous Session — status ===")
        for k, v in engine.env.items():
            print(f"  {k}: {v}")
        print("  root/sudo:", engine.require_root_privileges())
    elif args.cmd == "ensure":
        r = engine.ensure_tool(args.tool)
        print(r)
    elif args.cmd == "update":
        r = engine.update_all_data()
        print(r)
    elif args.cmd == "run":
        params = {}
        if args.url:
            params['target'] = args.url
        r = engine.run_autonomously({
            'tool': args.tool, 'intent': args.intent,
            'params': params, 'subcommand': args.subcommand,
        })
        print(r)
    else:
        p.print_help()

