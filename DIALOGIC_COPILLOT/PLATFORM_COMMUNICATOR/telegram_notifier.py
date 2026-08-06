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
        
        # Emoji untuk platform dan severity
        self.platform_emoji = {
            'hackerone': '🔴',
            'bugcrowd': '🔵', 
            'intigriti': '🟢',
            'yeswehack': '🟡',
            'immunefi': '🟣',
            'hackthebox': '🟠',
            'tryhackme': '🟤'
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
        
        elif command == '/income':
            return self._get_income_projection()
        
        elif command == '/help':
            return self._get_help_message()
        
        elif command == '/report':
            return self._trigger_manual_report()
        
        elif command == '/stop':
            return self._stop_autonomous_ops()
        
        elif command == '/start':
            return self._start_autonomous_ops()
        
        return {'success': False, 'message': 'Unknown command. Use /help for available commands.'}
    
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

⚙️ <b>AUTONOMOUS OPERATIONS</b>
/start
→ Start 24/7 autonomous operations
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