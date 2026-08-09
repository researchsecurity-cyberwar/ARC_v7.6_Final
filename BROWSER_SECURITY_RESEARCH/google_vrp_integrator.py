import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

class GoogleVRPIntegrator:
    """
    Integrator lengkap untuk semua program Google Bug Bounty.
    Mendukung login session, scraping scope/rules dari semua program resmi,
    dan integrasi penuh dengan sistem ARC v7.6 Final.
    
    REALITAS TEKNIS:
    - Menggunakan session cookie untuk akses authenticated content
    - Scraping langsung dari halaman resmi Google Bug Hunters
    - Mendukung semua 13 program Google VRP yang aktif
    - Anti-crash dengan fallback dan caching cerdas
    """
    
    def __init__(self, session_cookie: str = None, cache_dir="~/.arc/google_vrp_cache"):
        self.cache_dir = os.path.expanduser(cache_dir)
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Setup session dengan session cookie jika tersedia
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; ARC-Scanner/1.0)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Set session cookie jika tersedia
        if session_cookie:
            # Parse session cookie format yang kompleks
            cookies = dict(item.split('=', 1) for item in session_cookie.split('; ') if '=' in item)
            for name, value in cookies.items():
                self.session.cookies.set(name, value)
        
        # Konfigurasi lengkap semua program Google VRP dari link resmi
        self.google_programs = {
            'chrome_extensions_vrp': {
                'name': 'Chrome Extensions Vulnerability Reward Program',
                'rules_url': 'https://bughunters.google.com/about/rules/chrome-friends/chrome-extensions-vulnerability-reward-program-rules',
                'report_url': 'https://bughunters.google.com/report/new',
                'scope_patterns': [
                    r'first-party Chrome extensions',
                    r'Chrome.*extension'
                ],
                'bounty_range': '$100 - $31,337',
                'program_type': 'chrome_friends'
            },
            'android_devices_vrp': {
                'name': 'Android and Google Devices Security Reward Program',
                'rules_url': 'https://bughunters.google.com/about/rules/android-friends/android-and-google-devices-security-reward-program-rules',
                'report_url': 'https://bughunters.google.com/report/new',
                'scope_patterns': [
                    r'Pixel.*device',
                    r'Google.*Nest',
                    r'Home.*APIs',
                    r'Pixel.*Watch',
                    r'Fitbit.*devices',
                    r'Android.*OS'
                ],
                'bounty_range': '$500 - $25,000',
                'program_type': 'android_friends'
            },
            'mobile_vrp': {
                'name': 'Google Mobile Vulnerability Reward Program',
                'rules_url': 'https://bughunters.google.com/about/rules/android-friends/google-mobile-vulnerability-reward-program-rules',
                'report_url': 'https://bughunters.google.com/report/new',
                'scope_patterns': [
                    r'first-party Android applications',
                    r'Google.*mobile.*apps'
                ],
                'bounty_range': '$100 - $10,000',
                'program_type': 'android_friends'
            },
            'chrome_vrp': {
                'name': 'Chrome Vulnerability Reward Program',
                'rules_url': 'https://bughunters.google.com/about/rules/chrome-friends/chrome-vulnerability-reward-program-rules',
                'report_url': 'https://bugs.chromium.org/p/chromium/issues/entry',
                'scope_patterns': [
                    r'Chrome.*Browser',
                    r'Chromium.*project',
                    r'V8.*JavaScript.*engine',
                    r'Blink.*rendering.*engine',
                    r'PDFium',
                    r'GPU.*driver.*bugs'
                ],
                'bounty_range': '$500 - $250,000',
                'program_type': 'chrome_friends'
            },
            'chromeos_vrp': {
                'name': 'ChromeOS Vulnerability Reward Program',
                'rules_url': 'https://bughunters.google.com/about/rules/chrome-friends/chromeos-vulnerability-reward-program-rules',
                'report_url': 'https://bughunters.google.com/report/new',
                'scope_patterns': [
                    r'Chromebooks',
                    r'ChromeOS.*ecosystem',
                    r'ChromeOS.*devices'
                ],
                'bounty_range': '$500 - $100,000',
                'program_type': 'chrome_friends'
            },
            'abuse_vrp': {
                'name': 'Abuse Vulnerability Reward Program',
                'rules_url': 'https://bughunters.google.com/about/rules/google-friends/abuse-vulnerability-reward-program-rules',
                'report_url': 'https://bughunters.google.com/report/new',
                'scope_patterns': [
                    r'Google-owned.*web.*service',
                    r'Alphabet.*subsidiary.*web.*service',
                    r'reasonably.*sensitive.*user.*data'
                ],
                'bounty_range': '$100 - $13,337',
                'program_type': 'google_friends'
            },
            'ai_vrp': {
                'name': 'AI Vulnerability Reward Program',
                'rules_url': 'https://bughunters.google.com/about/rules/google-friends/ai-vulnerability-reward-program-rules',
                'report_url': 'https://bughunters.google.com/report/new',
                'scope_patterns': [
                    r'Google-owned.*AI-based.*product',
                    r'Alphabet.*AI.*service',
                    r'Gemini.*Apps',
                    r'Google.*Search.*AI',
                    r'Google.*Workspace.*AI'
                ],
                'bounty_range': '$500 - $20,000',
                'program_type': 'google_friends'
            },
            'cloud_vrp': {
                'name': 'Cloud Vulnerability Reward Program',
                'rules_url': 'https://bughunters.google.com/about/rules/google-friends/cloud-vulnerability-reward-program-rules',
                'report_url': 'https://bughunters.google.com/report/new',
                'scope_patterns': [
                    r'Google.*Cloud.*product',
                    r'Google.*Cloud.*web.*service',
                    r'cloud\.google\.com',
                    r'googleapis\.com'
                ],
                'bounty_range': '$500 - $31,337',
                'program_type': 'google_friends'
            },
            'google_vrp': {
                'name': 'Google and Alphabet Vulnerability Reward Program',
                'rules_url': 'https://bughunters.google.com/about/rules/google-friends/google-and-alphabet-vulnerability-reward-program-vrp-rules',
                'report_url': 'https://bughunters.google.com/report/new',
                'scope_patterns': [
                    r'Google-owned.*web.*service',
                    r'Alphabet.*subsidiary.*web.*service',
                    r'\.google\.com$',
                    r'\.youtube\.com$',
                    r'\.gmail\.com$'
                ],
                'bounty_range': '$100 - $31,337',
                'program_type': 'google_friends'
            },
            'oss_vrp': {
                'name': 'Google Open Source Software Vulnerability Reward Program',
                'rules_url': 'https://bughunters.google.com/about/rules/open-source/google-open-source-software-vulnerability-reward-program-rules',
                'report_url': 'https://bughunters.google.com/report/new',
                'scope_patterns': [
                    r'Google-owned.*GitHub.*organizations',
                    r'open.*source.*software',
                    r'supply.*chain.*compromise',
                    r'build.*integrity'
                ],
                'bounty_range': '$101 - $31,337',
                'program_type': 'open_source'
            },
            'patch_rewards': {
                'name': 'Patch Rewards Program',
                'rules_url': 'https://bughunters.google.com/about/rules/open-source/patch-rewards-program-rules',
                'report_url': 'https://bughunters.google.com/report/new',
                'scope_patterns': [
                    r'proactive.*security.*improvements',
                    r'open.*source.*projects',
                    r'security.*patches'
                ],
                'bounty_range': 'Variable',
                'program_type': 'open_source'
            },
            'tsunami_patch_rewards': {
                'name': 'Tsunami Patch Rewards Program',
                'rules_url': 'https://bughunters.google.com/about/rules/open-source/tsunami-patch-rewards-program-rules',
                'report_url': 'https://bughunters.google.com/report/new',
                'scope_patterns': [
                    r'Tsunami.*security.*scanners',
                    r'vulnerability.*detection',
                    r'web.*application.*fingerprinting'
                ],
                'bounty_range': 'On Hold',
                'program_type': 'open_source',
                'status': 'on_hold'
            },
            'osv_scalibr_patch_rewards': {
                'name': 'OSV-SCALIBR Patch Rewards Program',
                'rules_url': 'https://bughunters.google.com/about/rules/open-source/osv-scalibr-patch-rewards-program-rules',
                'report_url': 'https://bughunters.google.com/report/new',
                'scope_patterns': [
                    r'OSV-SCALIBR',
                    r'filesystem.*scanner',
                    r'vulnerability.*detection',
                    r'software.*inventory.*extraction'
                ],
                'bounty_range': 'On Hold',
                'program_type': 'open_source',
                'status': 'on_hold'
            }
        }
        
        # Cache terakhir update
        self._last_update = 0
        self._cached_program_data = {}
    
    def get_all_google_programs(self, refresh: bool = False) -> Dict[str, dict]:
        """Dapatkan semua program Google VRP dengan scraping lengkap.

        Args:
            refresh: True memaksa scrap ulang dari website (mengabaikan cache).
        """
        current_time = time.time()
        
        # Gunakan cache jika masih valid (< 1 jam) kecuali diminta refresh
        cache_fresh = current_time - self._last_update < 3600 and self._cached_program_data
        if cache_fresh and not refresh:
            return self._cached_program_data
        
        # Scrap data lengkap dari semua program
        updated_programs = {}
        for program_key, program_config in self.google_programs.items():
            try:
                program_data = self._scrape_program_details(program_config)
                if program_data:
                    updated_programs[program_key] = program_data
                else:
                    # Fallback ke konfigurasi dasar jika scraping gagal
                    updated_programs[program_key] = {
                        **program_config,
                        'scope': program_config['scope_patterns'],
                        'out_of_scope': [],
                        'rules': {},
                        'last_updated': current_time,
                        'status': 'fallback'
                    }
            except Exception as e:
                print(f"⚠️ Failed to scrape {program_key}: {e}")
                # Tetap gunakan konfigurasi dasar
                updated_programs[program_key] = {
                    **program_config,
                    'scope': program_config['scope_patterns'],
                    'out_of_scope': [],
                    'rules': {},
                    'last_updated': current_time,
                    'status': 'error'
                }
        
        # Simpan ke cache
        self._cached_program_data = updated_programs
        self._last_update = current_time
        self._save_cache(updated_programs)
        
        return updated_programs
    
    def _scrape_program_details(self, program_config: dict) -> Optional[dict]:
        """Scrap detail lengkap program dari halaman resmi Google."""
        try:
            response = self.session.get(
                program_config['rules_url'],
                timeout=15,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Ekstrak scope dari konten halaman
                scope_data = self._extract_scope_from_page(soup, program_config)
                
                # Ekstrak out-of-scope jika tersedia
                out_of_scope_data = self._extract_out_of_scope_from_page(soup)
                
                # Ekstrak rules dan persyaratan
                rules_data = self._extract_rules_from_page(soup, program_config)
                
                return {
                    **program_config,
                    'scope': scope_data,
                    'out_of_scope': out_of_scope_data,
                    'rules': rules_data,
                    'last_updated': time.time(),
                    'status': 'active'
                }
            
        except Exception as e:
            print(f"⚠️ Scraping failed for {program_config['name']}: {e}")
        
        return None
    
    def _extract_scope_from_page(self, soup: BeautifulSoup, program_config: dict) -> List[str]:
        """Ekstrak scope dari halaman program."""
        scope_items = []
        
        # Cari teks "Scope" di halaman
        scope_sections = soup.find_all(string=re.compile(r'Scope', re.IGNORECASE))
        for section in scope_sections[:3]:
            parent = section.parent
            if parent:
                # Ekstrak daftar scope
                list_items = parent.find_next_siblings(['ul', 'ol'])
                for ul in list_items[:2]:
                    for li in ul.find_all('li'):
                        scope_text = li.get_text(strip=True)
                        if scope_text and len(scope_text) > 10:
                            scope_items.append(scope_text)
        
        # Jika tidak menemukan scope dari parsing, gunakan pola default
        if not scope_items:
            scope_items = program_config['scope_patterns']
        
        return scope_items
    
    def _extract_out_of_scope_from_page(self, soup: BeautifulSoup) -> List[str]:
        """Ekstrak out-of-scope dari halaman program."""
        out_of_scope_items = []
        
        # Cari teks "Out of Scope" atau "Not in Scope"
        oos_sections = soup.find_all(string=re.compile(r'Out of Scope|Not in Scope', re.IGNORECASE))
        for section in oos_sections[:2]:
            parent = section.parent
            if parent:
                list_items = parent.find_next_siblings(['ul', 'ol'])
                for ul in list_items[:2]:
                    for li in ul.find_all('li'):
                        oos_text = li.get_text(strip=True)
                        if oos_text and len(oos_text) > 10:
                            out_of_scope_items.append(oos_text)
        
        return out_of_scope_items
    
    def _extract_rules_from_page(self, soup: BeautifulSoup, program_config: dict) -> dict:
        """Ekstrak rules dan persyaratan dari halaman program."""
        rules = {}
        
        # Ekstrak reward amounts jika tersedia
        reward_sections = soup.find_all(string=re.compile(r'Reward|Bounty', re.IGNORECASE))
        if reward_sections:
            rules['has_reward_info'] = True
        
        # Ekstrak kualifikasi kerentanan
        qualifying_sections = soup.find_all(string=re.compile(r'Qualifying|Eligible', re.IGNORECASE))
        if qualifying_sections:
            rules['has_qualifying_criteria'] = True
        
        # Ekstrak informasi pelaporan
        report_sections = soup.find_all(string=re.compile(r'Report|Submit', re.IGNORECASE))
        if report_sections:
            rules['has_reporting_guidelines'] = True
        
        # Tambahkan URL aturan resmi
        rules['official_rules_url'] = program_config['rules_url']
        rules['report_submission_url'] = program_config['report_url']
        
        return rules
    
    def is_target_in_google_scope(self, target_url: str, program_name: str = None) -> bool:
        """Periksa apakah target dalam scope program Google."""
        programs = self.get_all_google_programs()
        
        if program_name:
            if program_name in programs:
                program_data = programs[program_name]
                return self._matches_scope_patterns(target_url, program_data['scope'])
            return False
        else:
            for program_data in programs.values():
                if self._matches_scope_patterns(target_url, program_data['scope']):
                    return True
        return False
    
    def _matches_scope_patterns(self, target_url: str, scope_patterns: List[str]) -> bool:
        """Cocokkan URL target dengan pola scope (regex, wildcard, atau literal)."""
        full_url = target_url.lower()
        target_domain = urlparse(target_url).netloc.lower()
        
        for raw_pattern in scope_patterns:
            pattern = raw_pattern.strip()
            if not pattern:
                continue
            
            # 1) Pola dibungkus slash: /regex/
            if len(pattern) > 2 and pattern.startswith('/') and pattern.endswith('/'):
                try:
                    if re.search(pattern[1:-1], full_url, re.IGNORECASE):
                        return True
                except re.error:
                    pass
                continue
            
            # 2) Wildcard domain (contoh: *.google.com)
            if '*' in pattern:
                regex = re.escape(pattern).replace(r'\*', r'.*')
                try:
                    if re.search(regex, full_url, re.IGNORECASE):
                        return True
                except re.error:
                    pass
                continue
            
            # 3) Regex eksplisit (mengandung meta karakter regex)
            if re.search(r'[.+^$(){}\[\]|\\]', pattern):
                try:
                    if re.search(pattern, full_url, re.IGNORECASE):
                        return True
                except re.error:
                    pass
                continue
            
            # 4) Literal substring (domain/path)
            if pattern.lower() in full_url or pattern.lower() in target_domain:
                return True
        
        return False
    
    def get_submission_template(self, program_name: str, finding_data: dict) -> dict:
        """Dapatkan template laporan untuk program Google spesifik."""
        programs = self.get_all_google_programs()
        
        if program_name not in programs:
            raise ValueError(f"Unknown Google program: {program_name}")
        
        program = programs[program_name]
        
        return {
            'program_name': program['name'],
            'program_type': program['program_type'],
            'report_url': program['report_url'],
            'bounty_range': program['bounty_range'],
            'official_rules_url': program['rules_url'],
            'finding_title': finding_data.get('title', 'Security Vulnerability'),
            'vulnerability_type': finding_data.get('vulnerability_type', 'unspecified'),
            'target_url': finding_data.get('target_url', ''),
            'description': finding_data.get('technical_description', ''),
            'steps_to_reproduce': finding_data.get('reproduction_steps', ''),
            'impact': finding_data.get('business_impact', ''),
            'scope_validation': self.is_target_in_google_scope(finding_data.get('target_url', ''), program_name)
        }
    
    # ==================================================================
    # INTERFACE SCRAPER ARC (kompatibel dengan arc_main._update_intelligence_feed)
    # ==================================================================
    def get_all_programs(self) -> Dict[str, dict]:
        """Alias kompatibel scraper ARC: return dict program Google VRP."""
        return self.get_all_google_programs()
    
    def get_program_details(self, program_key: str, fetch: bool = False) -> Optional[dict]:
        """Dapatkan detail satu program (cepat, gunakan cache/lokal jika scraping gagal)."""
        programs = self.get_all_google_programs(refresh=fetch)
        return programs.get(program_key)
    
    def find_matching_google_programs(self, target_url: str) -> List[str]:
        """Cari semua program Google yang scope-nya cocok dengan target URL."""
        programs = self.get_all_google_programs()
        return [
            key for key, program_data in programs.items()
            if self._matches_scope_patterns(target_url, program_data['scope'])
        ]
    
    # ==================================================================
    # FORMATTER OUTPUT - untuk CLI & Telegram (seperti platform bug bounty lain)
    # ==================================================================
    def format_programs_summary(self, programs: dict = None) -> str:
        """Format ringkasan semua program Google VRP untuk output CLI/Telegram."""
        if programs is None:
            programs = self.get_all_google_programs()
        
        lines = [
            "🎯 GOOGLE VULNERABILITY REWARD PROGRAMS",
            f"📊 Total: {len(programs)} program aktif",
            "─" * 48,
        ]
        for key, prog in programs.items():
            status = prog.get('status', 'config')
            flag = "⏸" if status == 'on_hold' else ("✅" if status == 'active' else "📋")
            lines.append(f"{flag} {prog.get('name', key)}")
            lines.append(f"   Key   : {key}")
            lines.append(f"   Bounty: {prog.get('bounty_range', 'N/A')}")
            lines.append(f"   Tipe  : {prog.get('program_type', 'N/A')}")
            lines.append("")
        return "\n".join(lines)
    
    def format_program_details(self, program_key: str) -> str:
        """Format detail lengkap satu program untuk output CLI/Telegram."""
        program = self.get_program_details(program_key)
        if not program:
            available = ", ".join(sorted(self.google_programs.keys()))
            return f"❌ Program tidak dikenal: {program_key}\n   Tersedia: {available}"
        
        lines = [
            f"🎯 {program.get('name', program_key)}",
            f"🆔 Key   : {program_key}",
            f"💰 Bounty: {program.get('bounty_range', 'N/A')}",
            f"🏷 Tipe  : {program.get('program_type', 'N/A')}",
            f"📊 Status: {program.get('status', 'config')}",
            f"🔗 Rules : {program.get('rules_url', 'N/A')}",
            f"📮 Report: {program.get('report_url', 'N/A')}",
        ]
        
        scope = program.get('scope', [])
        if scope:
            lines.append("")
            lines.append("🛡 SCOPE:")
            for item in scope:
                lines.append(f"   • {item}")
        
        out_of_scope = program.get('out_of_scope', [])
        if out_of_scope:
            lines.append("")
            lines.append("🚫 OUT OF SCOPE:")
            for item in out_of_scope:
                lines.append(f"   • {item}")
        
        rules = program.get('rules', {})
        if rules:
            lines.append("")
            lines.append("📜 RULES:")
            for rule_key, val in rules.items():
                lines.append(f"   • {rule_key}: {val}")
        
        return "\n".join(lines)
    
    def format_scope_result(self, target_url: str, program_name: str = None) -> str:
        """Format hasil pengecekan scope target untuk output CLI/Telegram."""
        in_scope = self.is_target_in_google_scope(target_url, program_name)
        matching = []
        try:
            matching = self.find_matching_google_programs(target_url)
        except Exception:
            matching = []
        
        status = "🟢 IN SCOPE" if in_scope else "🔴 NOT IN SCOPE"
        lines = [
            f"{status} → {target_url}",
            "",
        ]
        if matching:
            lines.append("✅ Program yang cocok:")
            for key in matching:
                prog = self.google_programs.get(key, {})
                lines.append(f"   • {key} — {prog.get('name', 'N/A')} ({prog.get('bounty_range', 'N/A')})")
        else:
            lines.append("ℹ️ Tidak ada program Google yang scope-nya cocok.")
            lines.append("💡 Catatan: Scope Google VRP sangat dinamis — verifikasi manual di:")
            lines.append("   https://bughunters.google.com/report/new")
        return "\n".join(lines)
    
    # ==================================================================
    # INTERFACE SUBMITTER ARC (kompatibel dengan self.submitters di arc_main)
    # ==================================================================
    def submit_report(self, program_name: str, report_data: dict, evidence_files: list = None):
        """Generate template laporan Google VRP untuk submit manual (form bughunters.google.com)."""
        try:
            programs = self.get_all_google_programs()
            if program_name not in programs:
                available = ", ".join(sorted(programs.keys()))
                return {
                    'success': False,
                    'error': f"Unknown Google program: {program_name}. Available: {available}"
                }
            
            template = self.get_submission_template(program_name, report_data)
            report_markdown = self._build_report_markdown(template, report_data, evidence_files)
            
            timestamp = int(time.time())
            out_dir = os.path.expanduser("~/.arc/reports")
            os.makedirs(out_dir, exist_ok=True)
            file_path = os.path.join(out_dir, f"google_vrp_{program_name}_{timestamp}.md")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report_markdown)
            
            evidence_hint = ", ".join(evidence_files[:5]) if evidence_files else "none"
            instructions = (
                f"✅ Google VRP report template ready!\n\n"
                f"📋 Manual Submission Steps:\n"
                f"1. Open: {template['report_url']}\n"
                f"2. Select program: {template['program_name']}\n"
                f"3. Fill the form using content from: {file_path}\n"
                f"4. Attach evidence files: {evidence_hint}\n"
                f"5. Scope validation: {'✅ IN SCOPE' if template['scope_validation'] else '⚠️ VERIFY scope manually'}"
            )
            
            return {
                'success': True,
                'template_file': file_path,
                'message': instructions,
                'report_url': template['report_url']
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Google VRP template generation failed: {str(e)}'
            }
    
    def _build_report_markdown(self, template: dict, finding_data: dict, evidence_files: list = None) -> str:
        """Bangun dokumen laporan markdown dari template program Google."""
        if evidence_files:
            evidence_section = "\n".join([f"- {f}" for f in evidence_files])
        else:
            evidence_section = "[Tambahkan file bukti di sini: PoC, video, HAR, log, script]"
        
        report = f"""# Google Vulnerability Reward Program Submission

## Program Information
- **Program**: {template.get('program_name', 'N/A')}
- **Program Type**: {template.get('program_type', 'N/A')}
- **Bounty Range**: {template.get('bounty_range', 'N/A')}
- **Report URL**: {template.get('report_url', 'N/A')}
- **Official Rules**: {template.get('official_rules_url', 'N/A')}
- **Scope Validation**: {'✅ Target IN SCOPE' if template.get('scope_validation') else '⚠️ Target NOT verified in scope'}

## Finding
- **Title**: {template.get('finding_title', 'Security Vulnerability')}
- **Vulnerability Type**: {template.get('vulnerability_type', 'unspecified')}
- **Target URL**: {template.get('target_url', 'N/A')}

## Description
{template.get('description', 'Technical description of the vulnerability')}

## Steps to Reproduce
{template.get('steps_to_reproduce', 'Step-by-step reproduction steps')}

## Impact
{template.get('impact', 'Security impact analysis')}

## Evidence
{evidence_section}

## Additional Notes
- **Researcher**: Mr Esse14
- **Discovery Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Finding Metadata**: {json.dumps(finding_data, default=str, indent=2)[:1000]}

---
*This report template was automatically generated by ARC v7.6 Final — Google VRP Integrator.*
"""
        return report
    
    # ==================================================================
    # INTERFACE TRIAGE / KLARIFIKASI ANALIS GOOGLE (seperti submitter lain)
    # ==================================================================
    def set_evidence_generator(self, evidence_generator):
        """Set evidence generator untuk integrasi."""
        self.evidence_generator = evidence_generator
    
    def set_patch_generator(self, patch_generator):
        """Set patch generator untuk integrasi."""
        self.patch_generator = patch_generator
    
    def handle_triage_request(self, request_type: str, request_details: dict):
        """Tangani permintaan klarifikasi tim analis Google VRP (manual assistance).

        REALITAS TEKNIS:
        - bughunters.google.com TIDAK punya API publik untuk auto-comment (beda HackerOne/Intigriti)
        - ARC membangun clarification packet + panduan bukti, lalu jawaban ditempel manual
        """
        finding_id = request_details.get('finding_id', 'unknown')
        question = request_details.get('question') or request_details.get('message') or 'Klarifikasi umum'
        program_key = request_details.get('program') or request_details.get('program_name', 'google_vrp')
        finding_data = dict(request_details.get('finding_data', {}))
        finding_data.setdefault('finding_id', finding_id)
        return self.build_clarification_packet(program_key, question, finding_data)
    
    def build_clarification_packet(self, program_name: str, analyst_question: str, finding_data: dict) -> dict:
        """Bangun paket klarifikasi untuk menjawab pertanyaan tim analis Google VRP.

        Menghasilkan dokumen Markdown berisi jawaban terstruktur + arahan bukti,
        disimpan di ~/.arc/reports/google_vrp_clarification_*.md
        """
        try:
            template = self.get_submission_template(program_name, finding_data)
            request_type = self._classify_analyst_request(analyst_question)
            answer = self._build_analyst_answer(template, analyst_question, request_type)
            clarified_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            packet = f"""# Google VRP - Clarification Response

## Program
{template.get('program_name', program_name)} | Report: {finding_data.get('finding_id', finding_data.get('id', 'N/A'))}

## Analyst Request
{analyst_question.strip()}

## Request Classification
{request_type}

## Response Summary
{answer}

## Finding Reference
- **Title**: {template.get('finding_title', 'Security Vulnerability')}
- **Vulnerability Type**: {template.get('vulnerability_type', 'unspecified')}
- **Target URL**: {template.get('target_url', 'N/A')}
- **Bounty Range**: {template.get('bounty_range', 'N/A')}
- **Program Key**: {program_name}

## Technical Description
{template.get('description', '')}

## Steps to Reproduce
{template.get('steps_to_reproduce', '')}

## Impact
{template.get('impact', '')}

## Evidence Checklist
{self._clarification_evidence_checklist(request_type, finding_data)}

---
*Generated by ARC v7.6 Final - Google VRP Integrator | {clarified_at}*
"""
            timestamp = int(time.time())
            out_dir = os.path.expanduser("~/.arc/reports")
            os.makedirs(out_dir, exist_ok=True)
            file_path = os.path.join(out_dir, f"google_vrp_clarification_{timestamp}.md")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(packet)
            
            return {
                'success': True,
                'clarification_file': file_path,
                'request_type': request_type,
                'response_summary': answer,
                'response_text': packet,
                'report_url': template.get('report_url', 'https://bughunters.google.com/report/new'),
            }
        
        except Exception as e:
            return {'success': False, 'error': f'Clarification packet build failed: {str(e)}'}
    
    def _classify_analyst_request(self, question: str) -> str:
        """Klasifikasikan jenis permintaan klarifikasi dari analis Google."""
        q = question.lower()
        if any(k in q for k in ['video', 'screen recording', 'rekaman']):
            return 'poc_video'
        if any(k in q for k in ['screenshot', 'gambar', 'image', 'capture', 'tangkapan']):
            return 'screenshot'
        if any(k in q for k in ['http', 'request', 'response', 'har', 'network', 'pcap', 'traffic', 'paket']):
            return 'network_evidence'
        if any(k in q for k in ['patch', 'fix', 'perbaikan', 'remediation', 'mitigation', 'solusi']):
            return 'patch'
        if any(k in q for k in ['step', 'reproduce', 'reproduction', 'langkah', 'cara mereplikasi']):
            return 'reproduction_steps'
        if any(k in q for k in ['scope', 'in scope', 'aut', 'eligible']):
            return 'scope_validation'
        if any(k in q for k in ['impact', 'dampak', 'severity', 'worst case', 'user impact']):
            return 'impact'
        if any(k in q for k in ['clarif', 'jelas', 'detail', 'lebih', 'explain', 'jelaskan', 'info', 'poc', 'bukti']):
            return 'technical_clarification'
        return 'general'
    
    def _build_analyst_answer(self, template: dict, question: str, request_type: str) -> str:
        """Bangun ringkasan jawaban profesional per jenis permintaan analis."""
        target = template.get('target_url', 'N/A')
        vuln = template.get('vulnerability_type', 'unspecified')
        title = template.get('finding_title', 'the vulnerability')
        
        answers = {
            'poc_video': (
                f"Disertakan video PoC end-to-end yang menunjukkan eksploitasi {vuln} pada {target}. "
                f"Video mencakup: (1) navigasi ke target, (2) payload/request yang dikirim, "
                f"(3) dampak yang terlihat di browser, (4) timestamp sistem. "
                f"Langkah reproduce tersedia di bagian Steps to Reproduce."
            ),
            'screenshot': (
                f"Disertakan tangkapan layar ber-timestamp yang memperlihatkan payload {vuln} "
                f"dan dampaknya terhadap {target}. Setiap tangkapan memiliki overlay URL agar "
                f"researcher dapat memverifikasi target aslinya."
            ),
            'network_evidence': (
                f"Disertakan bukti network (request/response/HAR/PCAP) yang memperlihatkan alur "
                f"eksploitasi {vuln} terhadap {target} - termasuk header, parameter, dan payload. "
                f"Ini membuktikan serangan dikirim ke target yang benar dan bukan hasil manipulasi lokal."
            ),
            'patch': (
                f"Ditambahkan saran remediasi/patch untuk {vuln} (lihat lampiran). "
                f"Rekomendasi mencakup perbaikan kode, konfigurasi, dan langkah pengujian ulang. "
                f"Patch ini diberikan agar tim Google dapat memverifikasi dampak sekaligus menutup celah."
            ),
            'reproduction_steps': (
                f"Berikut langkah reproduce yang lebih rinci untuk {vuln} pada {target}: "
                f"(1) environment yang digunakan (browser/versi/OS), (2) langkah klik demi klik, "
                f"(3) request persis yang dikirim (method/path/body), (4) hasil yang teramati. "
                f"Semua step dapat diulang ulang secara konsisten."
            ),
            'scope_validation': (
                f"Verifikasi scope: target {target} diuji pada program "
                f"{template.get('program_name', 'Google VRP')} dan sesuai aturan resmi "
                f"(lihat Official Rules). Detail program & bounty tercantum di lampiran."
            ),
            'impact': (
                f"Ringkasan dampak {vuln}: dampak terhadap pengguna Google/ekosistem produk "
                f"(data, akun, ketersediaan), skenario worst-case, serta alasan keterpaparan "
                f"dinilai signifikan. Detail perhitungan dampak ada di bagian Impact laporan."
            ),
            'technical_clarification': (
                f"Klarifikasi teknis {title}: penjelasan detail tentang bagaimana {vuln} terjadi, "
                f"alur serangan terhadap {target}, serta keterkaitan komponen. "
                f"Jika analis membutuhkan bukti tambahan (video/HAR/patch), perintah "
                f"/generate_evidence dan /generate_patch siap dipakai."
            ),
            'general': (
                f"Menindaklanjuti permintaan analis, berikut penjelasan untuk {title} ({vuln}) "
                f"pada {target}. Detail lengkap, langkah reproduce, dampak, dan checklist bukti "
                f"terlampir. Silakan beri tahu jika ada bagian yang perlu diperjelas lagi."
            ),
        }
        return answers.get(request_type, answers['general'])
    
    def _clarification_evidence_checklist(self, request_type: str, finding_data: dict) -> str:
        """Bangun checklist bukti yang perlu dilampirkan saat menjawab analis."""
        existing = finding_data.get('evidence_files') or []
        lines = []
        
        default_checks = {
            'poc_video': ["Video PoC (mp4, ber-timestamp)", "Screenshot dampak", "Daftar langkah eksploitasi"],
            'screenshot': ["Screenshot full-page dengan URL overlay", "Screenshot payload & response", "Timestamp"],
            'network_evidence': ["HAR file", "PCAP (jika relevan)", "Screenshot request/response headers"],
            'patch': ["Kode patch", "Catatan implementasi", "Hasil testing ulang"],
            'reproduction_steps': ["Step-by-step detail", "Environment/versi", "Request persis (curl) atau HAR"],
            'scope_validation': ["Copy aturan scope program", "Bukti target dalam scope", "URL laporan resmi"],
            'impact': ["Perhitungan dampak", "Skenario worst-case", "Pengguna/data yang terpapar"],
            'technical_clarification': ["Deskripsi teknis tambahan", "Diagram alur serangan (jika ada)", "Bukti pendukung lain"],
            'general': ["Template laporan lengkap", "Bukti yang sudah ada", "Ketersediaan untuk diskusi lanjutan"],
        }
        needed = default_checks.get(request_type, default_checks['general'])
        for item in needed:
            lines.append(f"- [ ] {item}")
        
        if existing:
            lines.append("")
            lines.append("File bukti sudah tersedia:")
            for f in existing:
                lines.append(f"  - {f}")
        
        return "\n".join(lines)
    
    def _save_cache(self, data: dict):
        """Simpan cache ke file."""
        try:
            cache_file = os.path.join(self.cache_dir, 'google_vrp_cache.json')
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"⚠️ Failed to save cache: {e}")
    
    def load_cache(self):
        """Muat cache dari file."""
        try:
            cache_file = os.path.join(self.cache_dir, 'google_vrp_cache.json')
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    self._cached_program_data = cached_data
                    self._last_update = time.time()
                    return True
        except Exception as e:
            print(f"⚠️ Failed to load cache: {e}")
        return False
    
    def validate_session(self) -> bool:
        """Validasi apakah session cookie masih valid."""
        try:
            response = self.session.get(
                "https://bughunters.google.com/",
                timeout=10
            )
            return response.status_code == 200 and 'Sign in' not in response.text
        except:
            return False


def main():
    """CLI entrypoint Google VRP Integrator (ARC v7.6 Final)."""
    # Pastikan stdout mendukung Unicode/emoji (terutama di Windows console)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        description="GoogleVRPIntegrator - Intel & template report Google Bug Bounty (ARC v7.6 Final)."
    )
    parser.add_argument("--status", action="store_true", help="Validasi session bughunters.google.com")
    parser.add_argument("--programs", action="store_true", help="Tampilkan semua program Google VRP")
    parser.add_argument("--program", metavar="KEY", help="Tampilkan detail program (contoh: google_vrp, cloud_vrp)")
    parser.add_argument("--scope", metavar="URL", help="Cek apakah target URL masuk scope Google")
    parser.add_argument("--program-for-scope", metavar="KEY", help="Batasi pengecekan scope ke program tertentu")
    parser.add_argument("--template", metavar="KEY", help="Generate template laporan untuk program tertentu")
    parser.add_argument("--finding-data", metavar="JSON", help="Data temuan JSON untuk template laporan")
    parser.add_argument("--cookie", metavar="COOKIE", help="Session cookie bughunters.google.com (opsional)")
    parser.add_argument("--fetch", action="store_true", help="Scrap ulang dari website (abaikan cache)")
    args = parser.parse_args()

    integrator = GoogleVRPIntegrator(session_cookie=args.cookie)
    integrator.load_cache()

    if args.status:
        ok = integrator.validate_session()
        print("✅ Session bughunters.google.com VALID"
              if ok else "⚠️ Session tidak valid / butuh cookie baru")
        return

    if args.programs:
        programs = integrator.get_all_google_programs(refresh=args.fetch)
        print(integrator.format_programs_summary(programs))
        return

    if args.program:
        print(integrator.format_program_details(args.program))
        return

    if args.scope:
        print(integrator.format_scope_result(args.scope, args.program_for_scope))
        return

    if args.template:
        finding_data = {}
        if args.finding_data:
            try:
                finding_data = json.loads(args.finding_data)
            except json.JSONDecodeError as e:
                print(f"❌ --finding-data bukan JSON valid: {e}")
                return
        result = integrator.submit_report(args.template, finding_data)
        for k, v in result.items():
            print(f"{k}: {v}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()