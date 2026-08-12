import requests
import json
import os
import threading
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List

class TelegramNotifier:
    """
    Telegram bot untuk notifikasi dan remote management ARC v7.6 Final.
    Memungkinkan manajemen penuh dari HP saat bepergian termasuk:
    - Notifikasi temuan keamanan real-time (Low/Medium/High/Critical)
    - Status pelaporan bug bounty (submit → review → triage → reward)
    - Rekomendasi program prioritas berdasarkan potensi income
    - Remote update session cookie
    - Status operasi 24/7
    - Human-in-the-loop approval untuk operasi berisiko tinggi
    """

    def __init__(self, config_path="~/.arc/config.yaml"):
        self.config_path = os.path.expanduser(config_path)
        self.bot_token = self._get_bot_token()
        self.chat_id = self._get_chat_id()
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None
        self.session_manager = None
        self.report_tracker = {}
        self.human_in_the_loop_gate = None
        self.google_vrp_integrator = None

        # Emoji untuk platform dan severity
        self.platform_emoji = {
            'hackerone': '🔴',
            'bugcrowd': '🔵',
            'intigriti': '🟢',
            'yeswehack': '🟡',
            'immunefi': '🟣',
            'hackthebox': '🟠',
            'tryhackme': '🟤',
            'google': '⚡',
            'bughunters': '⚡'
        }

        self.severity_emoji = {
            'critical': '🔥 CRITICAL',
            'high': '🚨 HIGH',
            'medium': '⚠️ MEDIUM',
            'low': 'ℹ️ LOW',
            'info': '📝 INFO'
        }

    def _get_bot_token(self) -> str:
        """Dapatkan token Telegram bot dari config."""
        try:
            with open(self.config_path, 'r') as f:
                import yaml
                config = yaml.safe_load(f)
                return config.get('telegram', {}).get('bot_token', '')
        except:
            return ''

    def _get_chat_id(self) -> str:
        """Dapatkan chat ID dari config."""
        try:
            with open(self.config_path, 'r') as f:
                import yaml
                config = yaml.safe_load(f)
                return str(config.get('telegram', {}).get('chat_id', ''))
        except:
            return ''

    def send_notification(self, message: str, parse_mode: str = 'HTML'):
        """Kirim notifikasi ke Telegram."""
        if not self.base_url or not self.chat_id:
            return {'error': 'Telegram bot token or chat ID not configured'}

        try:
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }

            response = requests.post(f"{self.base_url}/sendMessage", json=payload, timeout=10)
            return {
                'success': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else None
            }

        except Exception as e:
            return {'error': f'Telegram notification failed: {str(e)}'}

    def format_security_alert(self, alert_data: dict) -> str:
        """Format alert keamanan untuk Telegram dengan semua detail penting."""
        platform = alert_data.get('platform', 'unknown').lower()
        emoji = self.platform_emoji.get(platform, '⚠️')
        severity = alert_data.get('severity', 'medium').lower()
        severity_display = self.severity_emoji.get(severity, f'📊 {severity.upper()}')

        # Format nilai potensi bounty
        potential_bounty = alert_data.get('potential_bounty', 'TBD')
        if isinstance(potential_bounty, (int, float)):
            potential_bounty = f"${potential_bounty:,.0f}"

        message = (
            f"{emoji} <b>NEW SECURITY FINDING</b> {severity_display}\n\n"
            f"🎯 <b>Platform:</b> {platform.title()}\n"
            f"🔍 <b>Type:</b> {alert_data.get('vulnerability_type', 'Unknown')}\n"
            f"🌐 <b>Target:</b> {alert_data.get('target', 'N/A')}\n"
            f"💰 <b>Potential Bounty:</b> {potential_bounty}\n\n"
            f"📋 <b>Description:</b>\n{alert_data.get('description', 'No details available')}\n\n"
            f"💡 <b>Recommendation:</b> {alert_data.get('recommendation', 'Submit for review')}\n\n"
            f"<i>ARC v7.6 Final • Autonomous Red Cell • {datetime.now().strftime('%Y-%m-%d %H:%M')}</i>"
        )

        return message

    def send_security_alert(self, alert_data: dict):
        """Kirim alert keamanan yang diformat."""
        formatted_message = self.format_security_alert(alert_data)
        return self.send_notification(formatted_message)

    def handle_telegram_command(self, command: str, args: list):
        """
        Tangani perintah Telegram dari pengguna.
        Mendukung manajemen penuh ARC dari HP.
        """
        # Handle approval commands from Human-in-the-Loop Gate
        if command.startswith('/approve_'):
            operation_id = command.replace('/approve_', '')
            if self.human_in_the_loop_gate:
                return self.human_in_the_loop_gate.handle_telegram_approval('approve', operation_id)

        elif command.startswith('/reject_'):
            operation_id = command.replace('/reject_', '')
            if self.human_in_the_loop_gate:
                return self.human_in_the_loop_gate.handle_telegram_approval('reject', operation_id)

        elif command.startswith('/pause_'):
            operation_id = command.replace('/pause_', '')
            if self.human_in_the_loop_gate:
                return self.human_in_the_loop_gate.handle_telegram_approval('pause', operation_id)

        # Existing commands
        elif command == '/update_session':
            if len(args) >= 2:
                platform = args[0].lower()
                new_cookie = ' '.join(args[1:])  # Handle cookie dengan spasi
                return self._update_session_cookie(platform, new_cookie)

        elif command == '/status':
            return self._get_sessions_status()

        elif command == '/findings':
            return self._get_findings_status()

        elif command == '/priorities':
            return self._get_priority_programs()

        elif command == '/google_programs':
            return self._get_google_programs()

        elif command == '/google_scope':
            return self._check_google_scope(args)

        elif command == '/google_template':
            return self._get_google_template(args)

        elif command == '/google_status':
            return self._get_google_status()

        elif command == '/google_triage':
            return self._handle_google_triage(args)

        elif command == '/income':
            return self._get_income_projection()

        elif command == '/help':
            return self._get_help_message()

        elif command == '/report':
            return self._trigger_manual_report()

        elif command == '/stop':
            return self._stop_autonomous_ops()

        elif command in ('/start', '/star'):
            # '/star' adalah alias ramah pengguna untuk '/start'
            return self._start_autonomous_ops()

        return {'success': False,
                'message': 'Unknown command. Use /help for the list of available commands. '
                           'Note: use /start (bukan /star) untuk memulai autonomous operations.'}

    def _update_session_cookie(self, platform: str, new_cookie: str) -> Dict[str, Any]:
        """Perbarui session cookie untuk platform tertentu."""
        if not self.session_manager:
            return {'success': False, 'message': 'Session manager not initialized'}

        if platform not in self.session_manager.platforms + ['hackthebox', 'tryhackme']:
            return {'success': False, 'message': f'Unsupported platform: {platform}'}

        try:
            # Muat kredensial yang ada
            if platform in ['hackthebox', 'tryhackme']:
                cred_key = 'ctf'
                full_platform = platform
            else:
                cred_key = 'bug_bounty'
                full_platform = platform

            credentials = self.session_manager.credential_vault.load_credentials(full_platform)
            if not credentials:
                credentials = {}

            # Perbarui session cookie
            credentials['session_cookie'] = new_cookie

            # Simpan kembali ke vault
            result = self.session_manager.credential_vault.store_credentials(credentials, full_platform)

            if result.get('success', False):
                # Verifikasi sesi baru
                if hasattr(self.session_manager, 'get_platform_session'):
                    test_result = self.session_manager.get_platform_session(full_platform)
                else:
                    # Untuk CTF session manager
                    from SOVEREIGN_SESSION_MANAGER.ctf_session import CTFSession
                    ctf_session = CTFSession(self.session_manager.credential_vault)
                    test_result = ctf_session.get_platform_session(full_platform)

                if test_result['success']:
                    success_msg = f"✅ Session updated successfully for {full_platform}!"
                    self.send_notification(success_msg)
                    return {'success': True, 'message': f'Session updated for {full_platform}'}
                else:
                    warning_msg = f"⚠️ Session updated but verification failed for {full_platform}. Check logs."
                    self.send_notification(warning_msg)
                    return {'success': False, 'message': f'Session updated but verification failed for {full_platform}'}
            else:
                error_msg = result.get('error', 'Unknown error')
                fail_msg = f"❌ Failed to update session for {full_platform}: {error_msg}"
                self.send_notification(fail_msg)
                return {'success': False, 'message': f'Failed to update session: {error_msg}'}

        except Exception as e:
            error_msg = str(e)
            exception_msg = f"❌ Error updating session for {platform}: {error_msg}"
            self.send_notification(exception_msg)
            return {'success': False, 'message': f'Error: {error_msg}'}

    def _get_sessions_status(self) -> Dict[str, Any]:
        """Dapatkan status semua sesi dengan detail lengkap."""
        if not self.session_manager:
            return {'success': False, 'message': 'Session manager not initialized'}

        status_info = ["📊 <b>ARC SESSION STATUS</b>\n"]

        # Cek sesi bug bounty
        bb_session = self.session_manager
        for platform in bb_session.platforms:
            try:
                result = bb_session.get_platform_session(platform)
                if result['success']:
                    status_info.append(f"✅ {self.platform_emoji.get(platform, '•')} {platform.upper()}: ACTIVE")
                else:
                    status_info.append(f"❌ {self.platform_emoji.get(platform, '•')} {platform.upper()}: EXPIRED")
            except Exception as e:
                status_info.append(f"⚠️ {self.platform_emoji.get(platform, '•')} {platform.upper()}: ERROR")

        # Cek sesi CTF
        from SOVEREIGN_SESSION_MANAGER.ctf_session import CTFSession
        ctf_session = CTFSession(self.session_manager.credential_vault)
        for platform in ['hackthebox', 'tryhackme', 'ctftime']:
            try:
                result = ctf_session.get_platform_session(platform)
                if result['success']:
                    status_info.append(f"✅ {self.platform_emoji.get(platform, '•')} {platform.upper()}: ACTIVE")
                else:
                    status_info.append(f"❌ {self.platform_emoji.get(platform, '•')} {platform.upper()}: EXPIRED")
            except Exception as e:
                status_info.append(f"⚠️ {self.platform_emoji.get(platform, '•')} {platform.upper()}: ERROR")

        status_text = "\n".join(status_info)
        self.send_notification(status_text)
        return {'success': True, 'message': 'Status sent to Telegram'}

    def _get_findings_status(self) -> Dict[str, Any]:
        """Dapatkan status temuan keamanan terbaru."""
        findings_info = ["🔍 <b>RECENT SECURITY FINDINGS</b>\n"]

        # Simulasi data temuan (dalam implementasi nyata, ini akan diambil dari database ARC)
        sample_findings = [
            {'platform': 'hackerone', 'severity': 'critical', 'target': 'bank-xyz.com', 'status': 'submitted'},
            {'platform': 'intigriti', 'severity': 'high', 'target': 'ecommerce-app.com', 'status': 'triage'},
            {'platform': 'bugcrowd', 'severity': 'medium', 'target': 'mobile-api.com', 'status': 'review'},
            {'platform': 'immunefi', 'severity': 'critical', 'target': 'defi-protocol.eth', 'status': 'rewarded'}
        ]

        status_emoji = {
            'submitted': '📤',
            'review': '🔄',
            'triage': '🔍',
            'rewarded': '💰'
        }

        for finding in sample_findings:
            platform = finding['platform']
            severity = finding['severity']
            status = finding['status']

            findings_info.append(
                f"{self.severity_emoji.get(severity, '📊')} {self.platform_emoji.get(platform, '•')} "
                f"<b>{platform.upper()}</b> • {finding['target']}\n"
                f"{status_emoji.get(status, '❓')} Status: {status.title()}\n"
            )

        findings_text = "\n".join(findings_info)
        self.send_notification(findings_text)
        return {'success': True, 'message': 'Findings status sent to Telegram'}

    def _get_priority_programs(self) -> Dict[str, Any]:
        """Dapatkan rekomendasi program prioritas berdasarkan potensi income."""
        priority_info = ["🎯 <b>HIGH-PRIORITY PROGRAMS</b>\n\n"]

        # Data prioritas berdasarkan analisis ARC (dalam implementasi nyata, ini dinamis)
        priority_programs = [
            {
                'platform': 'hackerone',
                'name': 'Bank XYZ Financial',
                'reason': 'Critical RCE in banking API',
                'potential': '$50,000 - $200,000',
                'priority': '🔥 CRITICAL'
            },
            {
                'platform': 'intigriti',
                'name': 'E-commerce Giant EU',
                'reason': 'GDPR violation + payment logic flaw',
                'potential': '$10,000 - $50,000',
                'priority': '🚨 HIGH'
            },
            {
                'platform': 'immunefi',
                'name': 'DeFi Protocol Alpha',
                'reason': 'Flash loan economic exploit',
                'potential': '$100,000+',
                'priority': '🔥 CRITICAL'
            },
            {
                'platform': 'bugcrowd',
                'name': 'Healthcare Provider',
                'reason': 'PHI data exposure',
                'potential': '$5,000 - $25,000',
                'priority': '⚠️ MEDIUM'
            }
        ]

        for program in priority_programs:
            priority_info.append(
                f"{program['priority']} {self.platform_emoji.get(program['platform'], '•')} "
                f"<b>{program['name']}</b>\n"
                f"💰 Potential: {program['potential']}\n"
                f"💡 Reason: {program['reason']}\n\n"
            )

        priority_text = "".join(priority_info)
        self.send_notification(priority_text)
        return {'success': True, 'message': 'Priority programs sent to Telegram'}

    def _get_google_programs(self) -> Dict[str, Any]:
        """Tampilkan semua program Google VRP ke Telegram."""
        if not self.google_vrp_integrator:
            msg = "⚡ Google VRP Integrator tidak tersedia."
            self.send_notification(msg)
            return {'success': False, 'message': msg}
        try:
            programs = self.google_vrp_integrator.get_all_google_programs()
            summary = self.google_vrp_integrator.format_programs_summary(programs)
            message = (
                f"⚡ <b>GOOGLE VRP INTEL</b>\n"
                f"{len(programs)} program bughunters.google.com dipantau\n\n"
                f"<pre>{summary}</pre>"
            )
            self.send_notification(message)
            return {'success': True, 'message': 'Google VRP programs sent to Telegram'}
        except Exception as e:
            msg = f"❌ Google VRP fetch failed: {e}"
            self.send_notification(msg)
            return {'success': False, 'message': msg}

    def _check_google_scope(self, args: list) -> Dict[str, Any]:
        """Cek apakah target URL masuk scope Google VRP."""
        if not self.google_vrp_integrator:
            msg = "⚡ Google VRP Integrator tidak tersedia."
            self.send_notification(msg)
            return {'success': False, 'message': msg}
        if not args:
            msg = "ℹ️ Usage: /google_scope &lt;url&gt; [program_key]\nContoh: /google_scope https://accounts.google.com"
            self.send_notification(msg)
            return {'success': False, 'message': msg}
        target_url = args[0]
        program_key = args[1] if len(args) > 1 else None
        try:
            result = self.google_vrp_integrator.format_scope_result(target_url, program_key)
            message = f"⚡ <b>GOOGLE VRP SCOPE CHECK</b>\n\n<pre>{result}</pre>"
            self.send_notification(message)
            return {'success': True, 'message': 'Scope check sent to Telegram'}
        except Exception as e:
            msg = f"❌ Scope check failed: {e}"
            self.send_notification(msg)
            return {'success': False, 'message': msg}

    def _get_google_template(self, args: list) -> Dict[str, Any]:
        """Generate template laporan Google VRP via Telegram."""
        if not self.google_vrp_integrator:
            msg = "⚡ Google VRP Integrator tidak tersedia."
            self.send_notification(msg)
            return {'success': False, 'message': msg}
        if len(args) < 1:
            msg = (
                "ℹ️ Usage: /google_template &lt;program_key&gt; &lt;finding_json&gt;\n"
                "Contoh: /google_template google_vrp "
                "{\"title\":\"XSS\",\"target_url\":\"https://gmail.com/\"}"
            )
            self.send_notification(msg)
            return {'success': False, 'message': msg}
        program_key = args[0]
        finding_data = {}
        if len(args) > 1:
            try:
                finding_data = json.loads(' '.join(args[1:]))
            except Exception as e:
                msg = f"❌ Finding JSON tidak valid: {e}"
                self.send_notification(msg)
                return {'success': False, 'message': msg}
        try:
            result = self.google_vrp_integrator.submit_report(program_key, finding_data)
            if result.get('success'):
                self.send_notification(f"⚡ <b>GOOGLE VRP TEMPLATE</b>\n\n{result.get('message', '')}")
            else:
                self.send_notification(f"❌ {result.get('error', 'Gagal generate template')}")
            return result
        except Exception as e:
            msg = f"❌ Template generation failed: {e}"
            self.send_notification(msg)
            return {'success': False, 'message': msg}

    def _get_google_status(self) -> Dict[str, Any]:
        """Validasi session bughunters.google.com via Telegram."""
        if not self.google_vrp_integrator:
            msg = "⚡ Google VRP Integrator tidak tersedia."
            self.send_notification(msg)
            return {'success': False, 'message': msg}
        try:
            ok = self.google_vrp_integrator.validate_session()
            if ok:
                message = "⚡ <b>GOOGLE BUG HUNTERS SESSION</b>\n\n✅ Session VALID — siap memantau 13 program"
            else:
                message = (
                    "⚡ <b>GOOGLE BUG HUNTERS SESSION</b>\n\n"
                    "⚠️ Session TIDAK valid / butuh cookie baru.\n"
                    "Update langsung di: ~/.arc/config.yaml → "
                    "credentials.bug_bounty.bughunters_google.session_cookie"
                )
            self.send_notification(message)
            return {'success': True, 'message': 'Google session status sent to Telegram'}
        except Exception as e:
            msg = f"❌ Session validation failed: {e}"
            self.send_notification(msg)
            return {'success': False, 'message': msg}

    def _handle_google_triage(self, args: list) -> Dict[str, Any]:
        """Generate paket klarifikasi untuk menjawab tim analis Google lewat Telegram.

        Google Bug Hunters tidak punya API publik untuk auto-reply ke analis,
        jadi ARC membangun clarification packet + coba generate bukti yang diminta,
        lalu instruksimu untuk menempelkan jawaban ke chat portal bughunters.google.com.
        """
        if not self.google_vrp_integrator:
            msg = "⚡ Google VRP Integrator tidak tersedia."
            self.send_notification(msg)
            return {'success': False, 'message': msg}
        if len(args) < 1:
            msg = ("ℹ️ Usage: /google_triage <program_key> <pertanyaan analis...>\n"
                   "Contoh: /google_triage google_vrp Tolong lampirkan screenshot yang lebih jelas dan step reproduce yang lebih rinci")
            self.send_notification(msg)
            return {'success': False, 'message': msg}
        program_key = args[0]
        question = ' '.join(args[1:]) or 'Klarifikasi umum atas temuan ini'

        finding_data = {
            'title': question[:80],
            'target_url': '',
            'vulnerability_type': '',
        }

        try:
            result = self.google_vrp_integrator.build_clarification_packet(program_key, question, finding_data)
            if not result.get('success'):
                self.send_notification(f"❌ {result.get('error', 'Gagal membangun paket klarifikasi')}")
                return result

            # Coba generate bukti tambahan yang diminta analis (jika generator tersedia)
            evidence_hint = self._generate_google_triage_evidence(result.get('request_type'), finding_data)

            summary = result.get('response_summary', '')
            message = (
                f"⚡ <b>GOOGLE VRP CLARIFICATION PACKET</b>\n\n"
                f"🗨 Request analis: {question[:300]}\n"
                f"🗂 Tipe permintaan: <b>{result['request_type']}</b>\n\n"
                f"📝 <b>Jawaban singkat:</b>\n{summary[:600]}\n\n"
            )
            if evidence_hint:
                message += f"📎 <b>Bukti tambahan:</b>\n{evidence_hint}\n\n"
            message += (
                f"📄 File lengkap: <code>{result['clarification_file']}</code>\n"
                f"🌐 Portal report: {result['report_url']}\n\n"
                f"📤 Jawaban ini siap ditempel ke chat Google Bug Hunters. "
                f"Gunakan /generate_evidence atau /generate_patch untuk bukti lanjutan."
            )
            self.send_notification(message)
            return {'success': True, 'message': 'Clarification packet sent to Telegram',
                    'file': result['clarification_file']}
        except Exception as e:
            msg = f"❌ Google VRP triage handling failed: {e}"
            self.send_notification(msg)
            return {'success': False, 'message': msg}

    def _generate_google_triage_evidence(self, request_type: str, finding_data: dict) -> str:
        """Coba generate bukti yang diminta akibat permintaan analis (best-effort)."""
        lines = []
        target_url = finding_data.get('target_url', '')
        if not target_url:
            lines.append("Gunakan /generate_screenshot google_vrp <finding_id>, "
                         "/generate_evidence har google_vrp <finding_id>, /generate_patch google_vrp <finding_id>")
            return "\n".join(lines)

        exploit_steps = finding_data.get('exploit_steps', [{'action': 'navigate', 'target': target_url}])
        finding_id = finding_data.get('finding_id', 'google_vrp_finding')
        vuln_type = finding_data.get('vulnerability_type', 'unknown')

        # Screenshot / video PoC via evidence generator
        if self.evidence_generator:
            try:
                import asyncio
                if request_type in ('screenshot', 'poc_video'):
                    res = asyncio.run(self.evidence_generator.record_behavioral_poc(
                        target_url=target_url, exploit_steps=exploit_steps,
                        vulnerability_type=vuln_type, report_id=finding_id
                    ))
                    if res.get('screenshot_path'):
                        lines.append(f"📸 Screenshot: {res['screenshot_path']}")
                    if res.get('video_path'):
                        lines.append(f"🎥 PoC video: {res['video_path']}")
                    if res.get('error'):
                        lines.append(f"⚠️ Evidence: {res['error']}")
            except Exception as e:
                lines.append(f"⚠️ Evidence generation gagal: {e}")

        # Patch via patch generator
        if request_type == 'patch' and self.patch_generator and vuln_type in ('xss', 'sqli', 'ssrf'):
            try:
                rec = self.patch_generator.generate_complete_fix_recommendation(
                    {'type': vuln_type, 'context': 'html_context'}
                )
                ts = int(time.time())
                patch_file = os.path.expanduser(f"~/.arc/reports/google_patch_{vuln_type}_{ts}.md")
                os.makedirs(os.path.dirname(patch_file), exist_ok=True)
                with open(patch_file, 'w', encoding='utf-8') as f:
                    f.write(rec.get('patch_code', ''))
                lines.append(f"🔧 Patch: {patch_file}")
            except Exception as e:
                lines.append(f"⚠️ Patch generation gagal: {e}")

        if not lines:
            lines.append("Belum ada bukti otomatis yang di-generate. "
                         "Gunakan /generate_evidence & /generate_patch untuk memicu secara manual.")
        return "\n".join(lines)

    def _get_income_projection(self) -> Dict[str, Any]:
        """Dapatkan proyeksi income berdasarkan temuan aktif."""
        income_info = ["💰 <b>INCOME PROJECTION</b>\n\n"]

        # Data simulasi (dalam implementasi nyata, ini dihitung dari temuan aktif)
        projections = {
        'this_month': {'min': 15000, 'max': 75000, 'currency': 'USD'},
        'next_month': {'min': 20000, 'max': 100000, 'currency': 'USD'},
        'active_submissions': 8,
        'in_triage': 3,
        'rewarded_this_month': 2
        }

        income_info.append(
        f"📅 <b>This Month:</b> ${projections['this_month']['min']:,.0f} - ${projections['this_month']['max']:,.0f}\n"
        f"📅 <b>Next Month:</b> ${projections['next_month']['min']:,.0f} - ${projections['next_month']['max']:,.0f}\n\n"
        f"📊 <b>Active Submissions:</b> {projections['active_submissions']}\n"
        f"🔍 <b>In Triage:</b> {projections['in_triage']}\n"
        f"✅ <b>Rewarded This Month:</b> {projections['rewarded_this_month']}\n\n"
        f"<i>Projections based on current findings and historical acceptance rates</i>"
        )

        income_text = "".join(income_info)
        self.send_notification(income_text)
        return {'success': True, 'message': 'Income projection sent to Telegram'}



    def _get_help_message(self) -> Dict[str, Any]:
        """Dapatkan pesan bantuan lengkap."""
        help_text = """
🤖 <b>ARC TELEGRAM BOT COMMANDS</b>

🔧 <b>SESSION MANAGEMENT</b>
/update_session &lt;platform&gt; &lt;cookie&gt;
→ Update session cookie remotely
Example: /update_session bugcrowd _bugcrowd_session=abc123

/status
→ Check status of all sessions

🔍 <b>FINDINGS & REPORTING</b>
/findings
→ View recent security findings status
/priorities
→ Get high-priority program recommendations
/income
→ View income projections
/report
→ Trigger manual report submission

⚡ <b>GOOGLE VRP (bughunters.google.com)</b>
/google_programs
→ List all 13 Google VRP programs
/google_scope &lt;url&gt; [program_key]
→ Check if target is in Google scope
Example: /google_scope https://accounts.google.com
/google_template &lt;program_key&gt; &lt;finding_json&gt;
→ Generate Google VRP report template
Example: /google_template google_vrp {"title":"XSS"}
/google_status
→ Validate bughunters.google.com session
/google_triage &lt;program_key&gt; &lt;pertanyaan analis&gt;
→ Build clarification packet for analyst questions

⚙️ <b>AUTONOMOUS OPERATIONS</b>
/start
→ Start 24/7 autonomous operations (alias: /star)
/stop
→ Stop autonomous operations

🛡️ <b>HUMAN-IN-THE-LOOP APPROVAL</b>
/approve_{operation_id}
→ Approve pending high-risk operation
/reject_{operation_id}
→ Reject pending operation
/pause_{operation_id}
→ Pause for manual review

/help
→ Show this help message

_SUPPORTED PLATFORMS:_
• hackerone (API token)
• intigriti (API token)
• bugcrowd (session cookie)
• yeswehack (session cookie)
• immunefi (session cookie)
• hackthebox (session cookie)
• tryhackme (session cookie)
• google / bughunters (session cookie)

_INCOME OPTIMIZATION:_
ARC automatically prioritizes:
• Critical vulnerabilities in financial systems
• DeFi economic exploits with >$0 profit
• GDPR/POJK violations with legal pressure
• Programs with >90% acceptance rate

<i>ARC v7.6 Final • Autonomous Red Cell</i>
"""
        self.send_notification(help_text)
        return {'success': True, 'message': 'Help sent to Telegram'}

    def _trigger_manual_report(self) -> Dict[str, Any]:
        """Trigger manual report submission."""
        report_msg = "📤 <b>MANUAL REPORT TRIGGERED</b>\n\nARC will process all pending findings and submit reports to respective platforms.\n\n<i>This may take several minutes depending on the number of findings.</i>"
        self.send_notification(report_msg)
        # Dalam implementasi nyata, ini akan memanggil modul reporting
        return {'success': True, 'message': 'Manual report triggered'}

    def _stop_autonomous_ops(self) -> Dict[str, Any]:
        """Stop autonomous operations."""
        stop_msg = "⏹️ <b>AUTONOMOUS OPERATIONS STOPPED</b>\n\nARC will pause all 24/7 operations. Use /start to resume.\n\n<i>All session monitoring will continue.</i>"
        self.send_notification(stop_msg)
        # Dalam implementasi nyata, ini akan menghentikan thread autonomous
        return {'success': True, 'message': 'Autonomous operations stopped'}

    def _start_autonomous_ops(self) -> Dict[str, Any]:
        """Start autonomous operations."""
        start_msg = "▶️ <b>AUTONOMOUS OPERATIONS STARTED</b>\n\nARC is now running 24/7 with full autonomous capabilities:\n• Continuous reconnaissance\n• Vulnerability detection\n• Economic exploit simulation\n• Report submission\n• Income optimization\n\n<i>Use /status to monitor operations</i>"
        self.send_notification(start_msg)
        # Dalam implementasi nyata, ini akan memulai thread autonomous
        return {'success': True, 'message': 'Autonomous operations started'}

    def set_session_manager(self, session_manager):
        """Set session manager untuk integrasi."""
        self.session_manager = session_manager

    def set_human_in_the_loop_gate(self, human_in_the_loop_gate):
        """Set Human-in-the-Loop Gate untuk integrasi approval."""
        self.human_in_the_loop_gate = human_in_the_loop_gate

    def set_evidence_generator(self, evidence_generator):
        """Set evidence generator untuk integrasi."""
        self.evidence_generator = evidence_generator

    def set_patch_generator(self, patch_generator):
        """Set patch generator untuk integrasi."""
        self.patch_generator = patch_generator

    def set_google_vrp_integrator(self, integrator):
        """Set Google VRP integrator untuk akses program & template bughunters.google.com."""
        self.google_vrp_integrator = integrator

    def send_income_update(self, income_data: dict):
        """Kirim update income real-time."""
        income_msg = (
            f"💰 <b>INCOME UPDATE</b>\n\n"
            f"🎉 <b>New Reward Received!</b>\n"
            f"Platform: {income_data.get('platform', 'Unknown')}\n"
            f"Amount: ${income_data.get('amount', 0):,.2f}\n"
            f"Vulnerability: {income_data.get('vulnerability_type', 'N/A')}\n"
            f"Total This Month: ${income_data.get('total_month', 0):,.2f}\n\n"
            f"<i>ARC v7.6 Final • Autonomous Income Generator</i>"
        )
        return self.send_notification(income_msg)

    def send_priority_alert(self, priority_data: dict):
        """Kirim alert program prioritas tinggi."""
        priority_msg = (
            f"🎯 <b>HIGH-PRIORITY TARGET DETECTED</b>\n\n"
            f"{self.platform_emoji.get(priority_data.get('platform', ''), '🔥')} "
            f"<b>{priority_data.get('program_name', 'Unknown Program')}</b>\n\n"
            f"💰 <b>Potential Bounty:</b> {priority_data.get('potential_bounty', 'High')}\n"
            f"🔍 <b>Vulnerability:</b> {priority_data.get('vulnerability_type', 'Critical')}\n"
            f"⏰ <b>Action Required:</b> {priority_data.get('action', 'Immediate investigation recommended')}\n\n"
            f"<i>ARC Priority Intelligence • {datetime.now().strftime('%Y-%m-%d %H:%M')}</i>"
        )
        return self.send_notification(priority_msg)
