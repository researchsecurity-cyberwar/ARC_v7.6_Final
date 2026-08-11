"""
ARC Intelligent Tool Commander v7.6 Final
===========================================
Mesin "pintar" untuk MEMAKAI tool CLI apa pun secara MANDIRI.

Masalah yang dipecahkan:
  Setiap tool punya sintaks perintah yang berbeda-beda (amass, nuclei, ffuf,
  httpx, sqlmap, tool Kali Linux, tool Python/Go/Node/Rust yang baru di-download
  nanti). ARC TIDAK boleh bergantung pada hardcode perintah per-tool.

Solusi (self-learning tool executor):
  1. DISCOVER  -> jalankan `--help`/`-h`/`--version`/`help` untuk menggali
                  antarmuka CLI tool (opsi, subcommand, apakah butuh nilai).
  2. LEARN     -> parse teks help menjadi profil tool (ToolProfile) dan cache
                  ke ~/.arc/tool_profiles/<tool>.json agar pemakaian berikutnya
                  instan.
  3. MAP       -> petakan INTENT (tujuan tinggi) + parameter semantik
                  (target/domain/url, output, wordlist, threads, ...) ke flag
                  yang BENAR sesuai profil -- berlaku untuk tool apa pun,
                  termasuk yang belum dikenal.
  4. EXECUTE   -> jalankan dengan argv berbasis LIST (bukan string.split),
                  timeout & parsing output terstruktur.
  5. SELF-HEAL -> bila gagal, coba bentuk flag alternatif secara heuristik.

Dengan ini, tool apa pun yang sudah di-download ARC (CLI / Kali / dependensi
maupun tool baru dari GitHub) BISA LANGSUNG DIGUNAKAN MANDIRI.
"""

import os
import sys
import re
import json
import time
import shlex
import shutil
import subprocess
from typing import Dict, List, Optional, Tuple, Any


class Flag:
    """Satu opsi/flag yang dipelajari dari help sebuah tool."""

    def __init__(self, long: str = None, short: str = None,
                 takes_value: bool = False, metavar: str = None,
                 help_text: str = ""):
        self.long = long or ""
        self.short = short or ""
        self.takes_value = takes_value
        self.metavar = (metavar or "").lower()
        self.help_text = help_text or ""
        self.alias = set()
        if self.long:
            self.alias.add(self.long)
        if self.short:
            self.alias.add(self.short)

    @property
    def tokens(self) -> List[str]:
        toks = []
        if self.long:
            toks.append(self.long)
        if self.short:
            toks.append(self.short)
        return toks

    def matches_semantic(self, *keywords) -> bool:
        """Cocokkan flag dengan kata kunci semantik (nama & bantuan)."""
        haystack = " ".join([
            self.long, self.short, self.metavar, self.help_text
        ]).lower()
        for kw in keywords:
            kwl = kw.lower()
            if kwl and kwl in haystack:
                return True
        return False

    def to_dict(self) -> Dict:
        return {
            'long': self.long,
            'short': self.short,
            'takes_value': self.takes_value,
            'metavar': self.metavar,
            'help_text': self.help_text
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "Flag":
        return cls(d.get('long'), d.get('short'), d.get('takes_value', False),
                   d.get('metavar'), d.get('help_text', ''))


class ToolProfile:
    """Profil antarmuka CLI sebuah tool hasil belajar dari help."""

    def __init__(self, name: str):
        self.name = name
        self.version = None
        self.description = None
        self.usage_lines: List[str] = []
        self.subcommands: Dict[str, str] = {}   # nama -> deskripsi
        self.flags: List[Flag] = []
        self.raw_help = ""
        self.help_sources: List[str] = []

    @property
    def has_subcommands(self) -> bool:
        return len(self.subcommands) > 0

    def flag_for(self, *keywords, fallbacks: List[str] = None) -> Optional[Flag]:
        """
        Pilih flag terbaik via sistem skor:
        nama panjang > nama pendek > metavar > teks bantuan.
        Ini membuat pilihan lebih akurat (mis. --url dipilih daripada --data
        yang kebetulan menyebut 'url' di bantuannya).
        """
        best, best_score = None, 0
        for flag in self.flags:
            scores = []
            for kw in keywords:
                kwl = (kw or '').lower().lstrip('-')
                if not kwl:
                    continue
                s = 0
                if flag.long and kwl == flag.long.lower():
                    s = 100
                elif flag.long and kwl in flag.long.lower():
                    s = 60
                if flag.short and kwl == flag.short.lower().lstrip('-'):
                    s = max(s, 80)
                if flag.metavar and kwl in flag.metavar:
                    s = max(s, 40)
                if kwl in flag.help_text.lower():
                    s = max(s, 10)
                scores.append(s)
            score = max(scores) if scores else 0
            if score > best_score:
                best, best_score = flag, score

        if best is not None and best_score > 0:
            return best

        # Fallback literal (misal "-u" / "--url")
        if fallbacks:
            wanted = set(fallbacks)
            for flag in self.flags:
                if flag.alias & wanted:
                    return flag
        return None

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'usage_lines': self.usage_lines,
            'subcommands': self.subcommands,
            'flags': [f.to_dict() for f in self.flags],
            'raw_help': self.raw_help,
            'help_sources': self.help_sources,
            'learned_at': time.time()
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "ToolProfile":
        p = cls(d.get('name', ''))
        p.version = d.get('version')
        p.description = d.get('description')
        p.usage_lines = d.get('usage_lines', [])
        p.subcommands = d.get('subcommands', {})
        p.flags = [Flag.from_dict(fd) for fd in d.get('flags', [])]
        p.raw_help = d.get('raw_help', '')
        p.help_sources = d.get('help_sources', [])
        return p

    def summarize(self) -> str:
        flag_names = ", ".join(f.tokens[0] for f in self.flags[:8])
        subs = ", ".join(list(self.subcommands.keys())[:6])
        return (f"[{self.name}] "
                f"flags({len(self.flags)}): {flag_names} | "
                f"subcommands({len(self.subcommands)}): {subs}")


class IntelligentToolCommander:
    """
    Komandan tool cerdas. Mempelajari, memetakan, dan mengeksekusi tool CLI
    apa pun secara mandiri (self-learning tool executor).
    """

    # Mapping intent (tujuan tinggi) ke kata kunci semantik + fallback.
    # Kata kunci dicocokkan ke help/nama flag dari tool YANG DIPELAJARI,
    # sehingga bekerja untuk tool masa depan tanpa hardcode perintah.
    INTENT_REGISTRY: Dict[str, Dict[str, Any]] = {
        'subdomain_enum': {
            'flags': {
                'target': (['domain', 'host', 'active', 'target', '-d'], ['--domain', '-d']),
                'output': (['output', 'file', 'write'], ['-o', '--output', '-f']),
                'recursive': (['recursive', 'subdomain', 'child'], []),
                'passive': (['passive', 'passive-only'], []),
            },
            'defaults': {'recursive': True}
        },
        'port_scan': {
            'flags': {
                'target': (['host', 'target', 'ip', 'scan'], ['-i', '--ip', '--target']),
                'ports': (['port', 'p'], ['-p', '--ports']),
                'top_ports': (['top', 'common'], ['--top-ports']),
                'fast': (['fast', 'top'], ['-F', '--fast']),
                'output': (['output', 'file'], ['-o', '--output']),
            },
            'defaults': {'fast': True}
        },
        'web_scan': {
            'flags': {
                'target': (['url', 'target', 'host', 'list', 'input'], ['-u', '--url', '--target', '-l']),
                'severity': (['severity', 'level', 'critical', 'high'], ['-severity', '--severity']),
                'templates': (['template', 't'], ['-t', '--template']),
                'rate': (['rate', 'rps', 'limit'], ['-rate-limit', '--rate-limit']),
                'output': (['output', 'file', 'json', 'export'], ['-o', '--output', '-json-export']),
            },
            'defaults': {}
        },
        'http_probe': {
            'flags': {
                'target': (['url', 'target', 'list', 'input', 'host'], ['-u', '-l', '--input', '--url']),
                'threads': (['thread', 'concurrence', 'parallel'], ['-t', '--threads', '-c']),
                'status': (['status', 'code', 'match'], ['-mc', '--status-code']),
                'output': (['output', 'file'], ['-o', '--output']),
            },
            'defaults': {}
        },
        'content_fuzz': {
            'flags': {
                'target': (['url', 'target', 'host'], ['-u', '--url', '--target']),
                'wordlist': (['wordlist', 'word', 'list', 'dict'], ['-w', '--wordlist']),
                'filter': (['filter', 'fc', 'hide', 'code'], ['-fc', '--filter-code']),
                'threads': (['thread', 'concurrence'], ['-t', '--threads']),
                'output': (['output', 'file'], ['-o', '--output']),
            },
            'defaults': {}
        },
        'sqli_check': {
            'flags': {
                'target': (['url', 'target', 'host'], ['-u', '--url', '--target']),
                'parameter': (['parameter', 'param'], ['-p', '--param']),
                'level': (['level'], ['--level']),
                'risk': (['risk'], ['--risk']),
                'batch': (['batch', 'non-interactive'], ['--batch']),
                'output': (['output', 'dir'], ['--output-dir', '--output']),
            },
            'defaults': {'batch': True, 'level': 3, 'risk': 2}
        },
        'generic': {
            'flags': {
                'target': (['url', 'target', 'host', 'domain', 'input', 'value'], ['-u', '-d', '-i', '--target', '--url']),
                'output': (['output', 'file', 'out'], ['-o', '--output', '-f']),
                'verbose': (['verbose'], ['-v', '--verbose']),
                'threads': (['thread', 'concurrence', 'parallel'], ['-t', '--threads', '-c']),
            },
            'defaults': {}
        }
    }

    def __init__(self, orchestrator=None, profile_dir: str = "~/.arc/tool_profiles"):
        self.orchestrator = orchestrator
        self.profile_dir = os.path.expanduser(profile_dir)
        os.makedirs(self.profile_dir, exist_ok=True)
        self._profiles: Dict[str, ToolProfile] = {}



    # ------------------------------------------------------------------
    # 1. DISCOVER — gali antarmuka CLI sebuah tool
    # ------------------------------------------------------------------
    @staticmethod
    def _help_invocations(tool_name: str, prefer_subcommand: Optional[str] = None):
        """Kombinasi invocation untuk menggali help, umum ke spesifik."""
        invocations = [
            ("version1", ['--version'], "--version"),
            ("version2", ['-version'], "-version"),
            ("version3", ['version'], "version"),
            ("help_all1", ['--help', 'all'], "--help all"),
            ("help_all2", ['--help-all'], "--help-all"),
            ("help_all3", ['help', 'all'], "help all"),
            ("help1", ['--help'], "--help"),
            ("help2", ['-h'], "-h"),
            ("help3", ['-help'], "-help"),
            ("help4", ['help'], "help"),
        ]
        if prefer_subcommand:
            invocations.insert(0, ("sub_help", [prefer_subcommand, '--help'],
                                   f"{prefer_subcommand} --help"))
            invocations.insert(1, ("sub_help2", [prefer_subcommand, '-h'],
                                   f"{prefer_subcommand} -h"))
        return invocations

    def discover_interface(self, tool_name: str,
                           prefer_subcommand: Optional[str] = None) -> ToolProfile:
        """Jalankan berbagai cara untuk membaca help tool & bangun profil."""
        profile = ToolProfile(tool_name)
        for _label, args, label in self._help_invocations(tool_name, prefer_subcommand):
            try:
                result = subprocess.run(
                    [tool_name] + args,
                    capture_output=True, text=True, timeout=30
                )
                text = (result.stdout or "") + "\n" + (result.stderr or "")
                if text.strip():
                    profile.help_sources.append(label)
                    profile.raw_help += f"\n===== {label} =====\n" + text
            except Exception:
                continue
        self._parse_profile(tool_name, profile)
        return profile

    # ------------------------------------------------------------------
    # 2. LEARN — parse teks help menjadi struktur
    # ------------------------------------------------------------------
    def _parse_profile(self, tool_name: str, profile: ToolProfile):
        text = profile.raw_help
        if not text.strip():
            profile.description = "no help available (tool may be library/interactive)"
            return profile

        m = re.search(r'[Vv]ersion[:\s]*([0-9][\w.\-]*)', text)
        if m:
            profile.version = m.group(1)

        # Deskripsi: baris pertama yang relevan
        for line in text.splitlines():
            line = line.strip()
            if not line or line.lower().startswith(("usage:", "usage ",
                                                    "options:", "command")):
                continue
            if re.match(r'^-', line):
                continue
            if re.match(r'(optional|positional|arguments):', line, re.I):
                continue
            profile.description = line[:200]
            break

        # Subcommand (tool multi-perintah)
        for line in text.splitlines():
            line = line.strip()
            m = re.match(r'^([a-z][a-z0-9\-_]{1,30})\s{2,}(\S.*)$', line, re.I)
            if m and not m.group(1).startswith('-'):
                name = m.group(1)
                if name.lower() not in ('yes', 'no', 'true', 'false'):
                    profile.subcommands.setdefault(name, m.group(2).strip())

        profile.flags = self._extract_flags(text)

        for line in text.splitlines():
            s = line.strip()
            if s.lower().startswith('usage'):
                profile.usage_lines.append(s)
        return profile

    @staticmethod
    def _extract_flags(help_text: str) -> List[Flag]:
        """Ekstrak daftar flag dari teks help secara generik."""
        flags: List[Flag] = []
        seen = set()
        pattern = re.compile(
            r'(?m)^\s*'
            r'(?P<short>-\w)?\s*,?\s*'
            r'(?P<long>--[\w][\w\-]*)'
            r'(?P<value>\s+(?:<[^>]+>|\[[^\]]+\]|\{[\w,| ]+\}|'
            r'(?:string|int|integer|bool|boolean|number|file|path|url|'
            r'domain|host|wordlist|dir|directory|list|json|http-url|'
            r'rate-limit|timeout|value|n|num|num int|f)\w*))?'
            r'(?P<desc>.*)$'
        )
        for m in pattern.finditer(help_text):
            long_opt = m.group('long')
            if not long_opt or long_opt in seen:
                continue
            short_opt = m.group('short')
            value_part = (m.group('value') or '').strip() if m.group('value') else ''
            metavar = ''
            takes_value = False
            if value_part:
                takes_value = True
                mm = re.search(r'<([^>]+)>|\[([^\]]+)\]|\{([^}]+)\}', value_part)
                if mm:
                    metavar = next(g for g in mm.groups() if g) or ''
                else:
                    metavar = value_part.split()[0]
            if long_opt.startswith('--') and re.match(r'--[\w\-]+$', long_opt):
                seen.add(long_opt)
                flags.append(Flag(
                    long=long_opt, short=short_opt,
                    takes_value=takes_value, metavar=metavar,
                    help_text=m.group('desc').strip()
                ))
        return flags

    # ------------------------------------------------------------------
    # Cache profil
    # ------------------------------------------------------------------
    def _profile_cache_path(self, tool_name: str) -> str:
        safe = re.sub(r'[^\w\-.]', '_', tool_name)
        return os.path.join(self.profile_dir, f"{safe}.json")

    def save_profile(self, profile: ToolProfile):
        try:
            with open(self._profile_cache_path(profile.name), 'w') as f:
                json.dump(profile.to_dict(), f, indent=2)
        except Exception:
            pass

    def load_profile(self, tool_name: str) -> Optional[ToolProfile]:
        path = self._profile_cache_path(tool_name)
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return ToolProfile.from_dict(json.load(f))
            except Exception:
                return None
        return None

    def get_profile(self, tool_name: str,
                    prefer_subcommand: Optional[str] = None) -> ToolProfile:
        """Ambil profil (cache dulu, baru discover)."""
        if tool_name in self._profiles:
            return self._profiles[tool_name]
        cached = self.load_profile(tool_name)
        if cached and cached.flags:
            self._profiles[tool_name] = cached
            return cached
        profile = self.discover_interface(tool_name, prefer_subcommand)
        if profile.flags or profile.subcommands:
            self.save_profile(profile)
        self._profiles[tool_name] = profile
        return profile


    # ------------------------------------------------------------------
    # 3. MAP — bangun command dari intent + parameter semantik
    # ------------------------------------------------------------------
    def _flag_token(self, flag: Flag) -> str:
        """Pilih token flag terbaik (long kalau ada, selainnya short)."""
        return flag.long or flag.short

    def attach_flags(self, argv: List[str], profile: ToolProfile,
                     params: Dict, flag_spec: Dict):
        """Tambahkan flag + nilainya ke argv berdasarkan spek & profil."""
        for semantic, (keywords, fallbacks) in flag_spec.items():
            if semantic not in params or params[semantic] is None:
                continue
            value = params[semantic]
            flag = profile.flag_for(*keywords, fallbacks=fallbacks)
            if not flag:
                continue
            token = self._flag_token(flag)
            if isinstance(value, bool):
                if value:
                    argv.append(token)
            else:
                argv.append(token)
                argv.append(str(value))

    def build_command(self, tool_name: str, intent: str = 'generic',
                      params: Optional[Dict] = None,
                      subcommand: Optional[str] = None) -> Dict:
        """
        Bangun command (argv list) untuk tool apa pun berdasarkan intent &
        parameter semantik, memakai profil yang dipelajari.
        """
        params = params or {}
        profile = self.get_profile(tool_name, prefer_subcommand=subcommand)

        argv = [tool_name]
        if subcommand:
            argv.append(subcommand)
        elif profile.has_subcommands and profile.subcommands.get('enum'):
            # heuristik: tool owasp/projectdiscovery biasa pakai subcommand enum
            argv.append('enum')

        registry = self.INTENT_REGISTRY.get(intent, self.INTENT_REGISTRY['generic'])
        if intent != 'generic':
            merged = dict(self.INTENT_REGISTRY['generic']['flags'])
            merged.update(registry['flags'])
            flag_spec = merged
        else:
            flag_spec = registry['flags']

        if 'defaults' in registry:
            for k, v in registry['defaults'].items():
                params.setdefault(k, v)

        self.attach_flags(argv, profile, params, flag_spec)

        raw_args = params.get('extra_args')
        if raw_args:
            if isinstance(raw_args, str):
                argv.extend(shlex.split(raw_args))
            else:
                argv.extend([str(a) for a in raw_args])

        return {
            'tool': tool_name,
            'intent': intent,
            'argv': argv,
            'profile': profile.summarize(),
            'subcommand': subcommand or (argv[1] if len(argv) > 1 else None)
        }


    # ------------------------------------------------------------------
    # 4. EXECUTE — jalankan dengan aman & robust
    # ------------------------------------------------------------------
    def run(self, argv: List[str], timeout: int = 600,
            cwd: Optional[str] = None) -> Dict:
        """Eksekusi argv berbasis list; kembalikan hasil terstruktur."""
        started = time.time()
        result = {
            'argv': argv,
            'returncode': None,
            'stdout': '',
            'stderr': '',
            'success': False,
            'execution_time': 0.0,
            'timed_out': False
        }
        try:
            proc = subprocess.run(
                argv, capture_output=True, text=True,
                timeout=timeout, cwd=cwd
            )
            result['returncode'] = proc.returncode
            result['stdout'] = (proc.stdout or '')[:200000]
            result['stderr'] = (proc.stderr or '')[:50000]
            result['success'] = proc.returncode == 0
        except subprocess.TimeoutExpired as e:
            result['timed_out'] = True
            result['stderr'] = f"Timeout after {timeout}s"
            out = getattr(e, 'stdout', None)
            if out:
                result['stdout'] = out.decode(errors='replace')[:200000] if isinstance(out, bytes) else out[:200000]
        except FileNotFoundError:
            result['stderr'] = f"Tool not found in PATH: {argv[0]}"
        except Exception as ex:
            result['stderr'] = f"Execution failed: {str(ex)}"
        result['execution_time'] = round(time.time() - started, 3)
        return result

    def ensure_available(self, tool_name: str) -> bool:
        """Pastikan tool tersedia; kalau tidak, auto-install via orchestrator."""
        if shutil.which(tool_name):
            return True
        if self.orchestrator is not None and hasattr(self.orchestrator, 'ensure_tool_available'):
            try:
                res = self.orchestrator.ensure_tool_available(tool_name)
                return bool(res.get('success'))
            except Exception:
                return False
        return False

    # ------------------------------------------------------------------
    # 5. SELF-HEAL — coba bentuk alternatif saat gagal
    # ------------------------------------------------------------------
    @staticmethod
    def _heal_alternatives(argv: List[str]) -> List[List[str]]:
        """Hasilkan beberapa alternatif perbaikan command (long<->short)."""
        alts = []
        tool = argv[0]
        for idx in range(1, len(argv)):
            token = argv[idx]
            if token.startswith('--'):
                alt = list(argv)
                alt[idx] = '-' + token[2:]
                alts.append(alt)
                if idx + 1 < len(argv) and not argv[idx + 1].startswith('-'):
                    alts.append(alt[:idx] + [alt[idx] + '=' + str(argv[idx + 1])]
                               + alt[idx + 2:])
        return alts[:10]

    def smart_execute(self, tool_name: str, intent: str = 'generic',
                      params: Optional[Dict] = None,
                      subcommand: Optional[str] = None,
                      timeout: int = 600) -> Dict:
        """
        API utama: pastikan tool tersedia -> pelajari antarmuka -> bangun
        command -> jalankan -> self-heal bila perlu.
        """
        params = params or {}
        result = {
            'tool': tool_name,
            'intent': intent,
            'available': False,
            'profile': None,
            'command': None,
            'output': None,
            'healed': False,
            'error': None
        }

        if not self.ensure_available(tool_name):
            result['error'] = f"Tool '{tool_name}' tidak tersedia & gagal di-install"
            return result
        result['available'] = True

        built = self.build_command(tool_name, intent, params, subcommand)
        result['profile'] = built['profile']
        result['command'] = built['argv']

        output = self.run(built['argv'], timeout=timeout)
        result['output'] = output

        # Self-heal bila gagal (dan bukan timeout)
        if not output['success'] and not output['timed_out']:
            for alt in self._heal_alternatives(built['argv']):
                healed = self.run(alt, timeout=timeout)
                if healed['success']:
                    result['healed'] = True
                    result['output'] = healed
                    result['command'] = alt
                    break

        return result


    # ------------------------------------------------------------------
    # API tinggi: jalankan per task (integrasi mudah dengan auto pilot)
    # ------------------------------------------------------------------
    def execute_task(self, task: Dict, timeout: int = 600) -> Dict:
        """Jalankan task dari dictionary: {tool, intent, params, subcommand}."""
        tool = task.get('tool')
        if not tool:
            intent = task.get('intent', 'generic')
            tool = self.recommend_tool(intent)
            if not tool:
                return {'success': False, 'error': 'No tool & no recommendation'}
        return self.smart_execute(
            tool_name=tool,
            intent=task.get('intent', 'generic'),
            params=task.get('params', {}),
            subcommand=task.get('subcommand'),
            timeout=task.get('timeout', timeout)
        )

    def recommend_tool(self, intent: str) -> Optional[str]:
        """Rekomendasikan tool yang tersedia untuk suatu intent."""
        mapping = {
            'subdomain_enum': ['amass', 'subfinder', 'assetfinder'],
            'port_scan': ['naabu', 'masscan', 'nmap'],
            'web_scan': ['nuclei', 'dalfox'],
            'http_probe': ['httpx'],
            'content_fuzz': ['ffuf'],
            'sqli_check': ['sqlmap'],
        }
        candidates = mapping.get(intent, [])
        for tool in candidates:
            if shutil.which(tool):
                return tool
        return candidates[0] if candidates else None


# ----------------------------------------------------------------------
# Utility factory untuk quick usage
# ----------------------------------------------------------------------
def create_smart_tool_commander(orchestrator=None) -> IntelligentToolCommander:
    """Buat commander + dengankan ke orchestrator tool ARC (jika ada)."""
    return IntelligentToolCommander(orchestrator=orchestrator)


if __name__ == "__main__":
    print("=== ARC Intelligent Tool Commander — self-test ===\n")
    commander = create_smart_tool_commander()

    candidate = None
    for t in ('nmap', 'curl', 'ffuf', 'httpx', 'nuclei', 'python3', 'ping'):
        if shutil.which(t):
            candidate = t
            break

    if candidate:
        prof = commander.get_profile(candidate)
        print(f"Diproses profil tool: {candidate}")
        print(f"  Deskripsi : {prof.description}")
        print(f"  Flags     : {len(prof.flags)} opsi terdeteksi")
        print(f"  Subcommand: {list(prof.subcommands.keys())[:5]}")
        for f_ in prof.flags[:10]:
            print(f"    - {f_.long or f_.short} {f_.metavar or ''}  (value={f_.takes_value})")
        print(prof.summarize())
    else:
        print("Tidak ada tool umum di PATH untuk self-test profil.")

    print("\n✅ IntelligentToolCommander siap digunakan ARC.")

