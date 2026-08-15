import json
import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

class ConversationEngine:
    """
    Stateful dialogue with memory (per target/session).
    Menyediakan dialog berstatus dengan pemrosesan perintah alami dan integrasi penuh.
    Mendukung interaksi dengan peneliti manusia dan respon ke permintaan tim triage.
    
    REALITAS TEKNIS:
    - Hanya HackerOne & Intigriti yang mendukung API untuk auto-response
    - Platform lain (BugCrowd, YesWeHack, Immunefi) hanya support manual assistance
    - Tidak ada akses otomatis ke email/Gmail
    """
    
    def __init__(self, memory_dir="~/.arc/conversations"):
        self.memory_dir = os.path.expanduser(memory_dir)
        os.makedirs(self.memory_dir, exist_ok=True)
        self.current_conversation = None
        self.conversation_history = []
        
        # Komponen ARC yang akan diinjeksi
        self.evidence_generator = None
        self.patch_generator = None
        self.telegram_notifier = None
        self.human_in_the_loop_gate = None
        self.platform_submitters = {}  # {'hackerone': HackerOneSubmitter(), ...}

        # ProgramBrief handler (DIALOGIC_COPILLOT.program_brief) — di-inject dari ArcChatEngine
        self.brief_engine = None
        
        # Platform yang mendukung auto-response via API
        self.api_supported_platforms = ['hackerone', 'intigriti']
        
        # Pola regex untuk ekstraksi informasi
        self.patterns = {
            'platform': r'(hackerone|bugcrowd|intigriti|yeswehack|immunefi|hackthebox|tryhackme)',
            'finding_id': r'(finding|report|vuln)[-_]?(\w+)',
            'screenshot_type': r'(full[ -]?page|step[ -]?\d+|alert|popup|login|injection)',
            'vulnerability': r'(xss|sqli|ssrf|rce|idor|csrf|lfi|rfi|auth[ -]?bypass)',
            'evidence_type': r'(screenshot|har|pcap|video|script|log)'
        }
    
    def start_conversation(self, target_domain: str, session_id: str = None, finding_data: dict = None):
        """
        Mulai percakapan baru untuk target tertentu dengan data temuan opsional.
        """
        if session_id is None:
            # Nama file harus aman untuk path apa pun (target bisa berisi '/' dll.)
            safe_target = re.sub(r'[^\w\-.]', '_', target_domain)
            session_id = f"{safe_target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        conversation_file = os.path.join(self.memory_dir, f"{session_id}.json")
        self.current_conversation = {
            'session_id': session_id,
            'target_domain': target_domain,
            'start_time': datetime.now().isoformat(),
            'messages': [],
            'context': {
                'finding_data': finding_data or {},
                'platform': self._extract_platform_from_domain(target_domain),
                'conversation_type': 'researcher'  # atau 'triage_request'
            },
            'file_path': conversation_file
        }
        
        # Simpan ke file
        self._save_conversation()
        return session_id
    
    def add_message(self, role: str, content: str, metadata: dict = None):
        """
        Tambahkan pesan ke percakapan saat ini dan proses jika diperlukan.
        """
        if self.current_conversation is None:
            raise ValueError("No active conversation. Call start_conversation() first.")
        
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.current_conversation['messages'].append(message)
        self.conversation_history.append(message)
        
        # Proses pesan jika dari peneliti manusia
        if role == 'human':
            response = self.process_natural_command(content)
            if response:
                # Tambahkan respons ARC ke percakapan
                self.add_message('arc', response)
        
        # Simpan ke file
        self._save_conversation()
    
    def process_natural_command(self, user_message: str) -> Optional[str]:
        """
        Proses perintah bahasa alami dari peneliti atau permintaan triage.
        """
        user_message_lower = user_message.lower()
        
        # Deteksi jenis percakapan
        conversation_type = self.current_conversation['context'].get('conversation_type', 'researcher')
        
        if conversation_type == 'triage_request':
            return self._handle_triage_request(user_message)
        else:
            return self._handle_researcher_command(user_message)
    
    def _handle_researcher_command(self, user_message: str) -> Optional[str]:
        """Tangani perintah dari peneliti manusia."""
        user_message_lower = user_message.lower()

        # Delegasi ke ProgramBrief handler (program_brief.py) jika tersedia.
        # ArcChatEngine meng-inject dirinya sebagai brief_engine.
        if self.brief_engine is not None:
            try:
                brief_response = self.brief_engine.handle_brief_command(user_message)
                if brief_response:
                    return brief_response
            except Exception as e:
                return f"⚠️ Brief engine error (safe-fallback): {e}"

        # Ekstrak informasi konteks
        platform = self._extract_platform(user_message) or self.current_conversation['context'].get('platform')
        finding_id = self._extract_finding_id(user_message) or self.current_conversation['context'].get('finding_data', {}).get('id')
        
        # Perintah generate screenshot
        if any(keyword in user_message_lower for keyword in ['generate', 'buat', 'create']) and \
           any(keyword in user_message_lower for keyword in ['screenshot', 'tangkapan', 'gambar']):
            
            screenshot_type = self._extract_screenshot_type(user_message) or 'full_page'
            
            if self.evidence_generator:
                try:
                    new_evidence = self.evidence_generator.create_custom_screenshot(
                        platform=platform,
                        finding_id=finding_id,
                        screenshot_type=screenshot_type
                    )
                    
                    # Tentukan strategi berdasarkan platform
                    if platform in self.api_supported_platforms:
                        # Auto-submit untuk platform dengan API
                        submitter = self.platform_submitters.get(platform)
                        if submitter:
                            submitter._upload_h1_evidence_files(finding_id, [new_evidence])
                            action_msg = f"✅ Generated and automatically submitted {screenshot_type} screenshot"
                        else:
                            action_msg = f"✅ Generated {screenshot_type} screenshot (auto-submit ready)"
                    else:
                        # Manual upload untuk platform tanpa API
                        action_msg = (
                            f"✅ Generated {screenshot_type} screenshot for {platform} finding {finding_id}\n"
                            f"📤 File ready: {new_evidence}\n"
                            f"📋 Upload manually to {platform} report"
                        )
                    
                    # Kirim notifikasi ke Telegram jika tersedia
                    if self.telegram_notifier:
                        self.telegram_notifier.send_notification(
                            f"✅ <b>SCREENSHOT GENERATED</b>\n"
                            f"Platform: {platform}\n"
                            f"Finding: {finding_id}\n"
                            f"Type: {screenshot_type}"
                        )
                    
                    return action_msg
                    
                except Exception as e:
                    return f"❌ Error generating screenshot: {str(e)}"
            else:
                return "⚠️ Evidence generator not configured"
        
        # Perintah generate patch
        elif any(keyword in user_message_lower for keyword in ['create', 'buat', 'generate']) and \
             any(keyword in user_message_lower for keyword in ['patch', 'perbaikan', 'fix']):
            
            vulnerability = self._extract_vulnerability(user_message) or \
                           self.current_conversation['context'].get('finding_data', {}).get('vulnerability_type')
            
            if self.patch_generator and vulnerability:
                try:
                    patch = self.patch_generator.create_patch(vulnerability)
                    
                    # Simpan patch sebagai file sementara
                    patch_file = f"/tmp/arc_patch_{finding_id}_{int(datetime.now().timestamp())}.txt"
                    with open(patch_file, 'w') as f:
                        f.write(patch)
                    
                    # Tentukan strategi berdasarkan platform
                    if platform in self.api_supported_platforms:
                        submitter = self.platform_submitters.get(platform)
                        if submitter:
                            submitter._upload_h1_evidence_files(finding_id, [patch_file])
                            action_msg = f"✅ Generated and automatically submitted security patch for {vulnerability}"
                        else:
                            action_msg = f"✅ Generated security patch for {vulnerability} (auto-submit ready)"
                    else:
                        action_msg = (
                            f"✅ Generated security patch for {vulnerability}\n"
                            f"📤 File ready: {patch_file}\n"
                            f"📋 Upload manually to {platform} report"
                        )
                    
                    if self.telegram_notifier:
                        self.telegram_notifier.send_notification(
                            f"✅ <b>SECURITY PATCH GENERATED</b>\n"
                            f"Vulnerability: {vulnerability}\n"
                            f"Patch ready for submission"
                        )
                    
                    return action_msg
                    
                except Exception as e:
                    return f"❌ Error generating patch: {str(e)}"
            else:
                return "⚠️ Patch generator not configured or vulnerability not specified"
        
        # Perintah tambah bukti
        elif any(keyword in user_message_lower for keyword in ['add', 'tambah', 'generate']) and \
             any(keyword in user_message_lower for keyword in ['evidence', 'bukti', 'har', 'pcap', 'video']):
            
            evidence_type = self._extract_evidence_type(user_message) or 'screenshot'
            
            if self.evidence_generator:
                try:
                    new_evidence = self.evidence_generator.create_additional_evidence(
                        evidence_type=evidence_type,
                        platform=platform,
                        finding_id=finding_id
                    )
                    
                    # Strategi berdasarkan platform
                    if platform in self.api_supported_platforms:
                        submitter = self.platform_submitters.get(platform)
                        if submitter:
                            submitter._upload_h1_evidence_files(finding_id, [new_evidence])
                            action_msg = f"✅ Generated and automatically submitted {evidence_type} evidence"
                        else:
                            action_msg = f"✅ Generated {evidence_type} evidence (auto-submit ready)"
                    else:
                        action_msg = (
                            f"✅ Generated additional {evidence_type} evidence for {platform} finding {finding_id}\n"
                            f"📤 File ready: {new_evidence}\n"
                            f"📋 Upload manually to {platform} report"
                        )
                    
                    if self.telegram_notifier:
                        self.telegram_notifier.send_notification(
                            f"✅ <b>ADDITIONAL EVIDENCE GENERATED</b>\n"
                            f"Type: {evidence_type}\n"
                            f"Platform: {platform}\n"
                            f"Finding: {finding_id}"
                        )
                    
                    return action_msg
                    
                except Exception as e:
                    return f"❌ Error generating evidence: {str(e)}"
            else:
                return "⚠️ Evidence generator not configured"
        
        # Perintah bantuan
        elif any(keyword in user_message_lower for keyword in ['help', 'bantuan', 'bisa']):
            return (
                "🤖 <b>I can help with:</b>\n\n"
                "📸 <b>Screenshots:</b>\n"
                "- 'ARC generate full page screenshot for Bank XYZ'\n\n"
                "🔧 <b>Patches:</b>\n"
                "- 'ARC create patch for XSS vulnerability'\n\n"
                "📄 <b>Evidence:</b>\n"
                "- 'ARC add HAR file for SSRF finding'\n\n"
                "<b>PLATFORM SUPPORT:</b>\n"
                "✅ <b>HackerOne/Intigriti:</b> Auto-submit available\n"
                "⚠️ <b>BugCrowd/YesWeHack/Immunefi:</b> Manual upload required\n\n"
                "<i>Just mention what you need!</i>"
            )
        
        return None
    
    def _handle_triage_request(self, triage_message: str) -> str:
        """Tangani permintaan dari tim triage secara otomatis (HANYA UNTUK PLATFORM DENGAN API)."""
        platform = self.current_conversation['context'].get('platform')
        finding_id = self.current_conversation['context'].get('finding_data', {}).get('id')
        
        # HANYA PROSES OTOMATIS UNTUK PLATFORM DENGAN API
        if platform not in self.api_supported_platforms:
            return (
                f"ℹ️ Manual triage request detected for {platform}\n"
                f"📋 Please use Telegram commands to generate evidence:\n"
                f"/generate_screenshot {platform} {finding_id}\n"
                f"/generate_patch {platform} {finding_id}"
            )
        
        triage_lower = triage_message.lower()
        
        # Permintaan screenshot tambahan
        if any(keyword in triage_lower for keyword in ['screenshot', 'tangkapan', 'gambar', 'image']):
            screenshot_type = self._extract_screenshot_type(triage_message) or 'full_page'
            
            if self.evidence_generator:
                try:
                    new_evidence = self.evidence_generator.create_custom_screenshot(
                        platform=platform,
                        finding_id=finding_id,
                        screenshot_type=screenshot_type
                    )
                    
                    # Submit otomatis ke platform (HANYA UNTUK H1/INTIGRITI)
                    submitter = self.platform_submitters.get(platform)
                    if submitter:
                        submitter._upload_h1_evidence_files(finding_id, [new_evidence])
                    
                    return f"✅ Automatically generated and submitted {screenshot_type} screenshot as requested by triage team"
                except Exception as e:
                    return f"❌ Error handling triage request: {str(e)}"
        
        # Permintaan file jaringan (HAR/PCAP)
        elif any(keyword in triage_lower for keyword in ['har', 'pcap', 'network', 'jaringan', 'traffic']):
            evidence_type = self._extract_evidence_type(triage_message) or 'har'
            
            if self.evidence_generator:
                try:
                    new_evidence = self.evidence_generator.create_network_capture(
                        endpoints=[self.current_conversation['context'].get('target_domain')],
                        evidence_type=evidence_type
                    )
                    
                    submitter = self.platform_submitters.get(platform)
                    if submitter:
                        submitter._upload_h1_evidence_files(finding_id, [new_evidence])
                    
                    return f"✅ Automatically generated and submitted {evidence_type} file as requested by triage team"
                except Exception as e:
                    return f"❌ Error handling network capture request: {str(e)}"
        
        # Permintaan kode perbaikan
        elif any(keyword in triage_lower for keyword in ['patch', 'fix', 'perbaikan', 'remediation']):
            vulnerability = self.current_conversation['context'].get('finding_data', {}).get('vulnerability_type')
            
            if self.patch_generator and vulnerability:
                try:
                    patch = self.patch_generator.create_security_patch(
                        vulnerability_type=vulnerability,
                        affected_code=self.current_conversation['context'].get('finding_data', {}).get('affected_code', ''),
                        framework=self.current_conversation['context'].get('finding_data', {}).get('framework', 'unknown')
                    )
                    
                    # Simpan dan submit patch
                    patch_file = f"/tmp/h1_patch_{finding_id}_{int(datetime.now().timestamp())}.txt"
                    with open(patch_file, 'w') as f:
                        f.write(patch)
                    
                    submitter = self.platform_submitters.get(platform)
                    if submitter:
                        submitter._upload_h1_evidence_files(finding_id, [patch_file])
                    
                    return f"✅ Automatically generated and submitted security patch for {vulnerability} as requested by triage team"
                except Exception as e:
                    return f"❌ Error handling patch request: {str(e)}"
        
        # Permintaan umum
        else:
            if self.evidence_generator:
                try:
                    comprehensive_evidence = self.evidence_generator.generate_comprehensive_evidence(
                        finding_data=self.current_conversation['context'].get('finding_data', {})
                    )
                    
                    submitter = self.platform_submitters.get(platform)
                    if submitter:
                        submitter._upload_h1_evidence_files(finding_id, comprehensive_evidence.get('files', []))
                    
                    return "✅ Automatically generated and submitted comprehensive evidence package as requested by triage team"
                except Exception as e:
                    return f"❌ Error handling general triage request: {str(e)}"
        
        return "ℹ️ Request processed but no specific action taken"
    
    def initiate_triage_conversation(self, platform: str, finding_data: dict, triage_request: str):
        """
        Inisiasi percakapan khusus untuk menangani permintaan tim triage.
        HANYA AKTIF UNTUK PLATFORM DENGAN API (H1/INTIGRITI).
        """
        # Untuk platform tanpa API, cukup simpan sebagai referensi
        session_id = f"triage_{platform}_{finding_data.get('id', 'unknown')}_{int(datetime.now().timestamp())}"
        
        self.start_conversation(
            target_domain=finding_data.get('target', platform),
            session_id=session_id,
            finding_data=finding_data
        )
        
        # Update konteks
        self.current_conversation['context']['conversation_type'] = 'triage_request'
        self.current_conversation['context']['triage_request'] = triage_request
        self._save_conversation()
        
        # HANYA PROSES OTOMATIS UNTUK PLATFORM DENGAN API
        if platform in self.api_supported_platforms:
            response = self._handle_triage_request(triage_request)
            if response:
                self.add_message('arc', response)
        else:
            # Untuk platform tanpa API, beri instruksi manual
            manual_response = (
                f"⚠️ Triage request received for {platform}\n"
                f"📋 This platform doesn't support auto-response\n"
                f"📱 Use Telegram commands to generate evidence manually"
            )
            self.add_message('arc', manual_response)
        
        return session_id
    
    def get_conversation_context(self) -> dict:
        """
        Dapatkan konteks percakapan saat ini.
        """
        if self.current_conversation is None:
            return {}
        
        return {
            'target_domain': self.current_conversation['target_domain'],
            'message_count': len(self.current_conversation['messages']),
            'last_interaction': self.current_conversation['messages'][-1]['timestamp'] if self.current_conversation['messages'] else None,
            'context_data': self.current_conversation['context'],
            'conversation_type': self.current_conversation['context'].get('conversation_type', 'researcher'),
            'platform_supports_api': self.current_conversation['context'].get('platform') in self.api_supported_platforms
        }
    
    def update_context(self, context_data: dict):
        """
        Perbarui data konteks percakapan.
        """
        if self.current_conversation is None:
            raise ValueError("No active conversation.")
        
        self.current_conversation['context'].update(context_data)
        self._save_conversation()
    
    def load_conversation(self, session_id: str):
        """
        Muat percakapan yang sudah ada.
        """
        conversation_file = os.path.join(self.memory_dir, f"{session_id}.json")
        if not os.path.exists(conversation_file):
            raise FileNotFoundError(f"Conversation {session_id} not found.")
        
        with open(conversation_file, 'r') as f:
            self.current_conversation = json.load(f)
            self.conversation_history = self.current_conversation['messages']
    
    def _save_conversation(self):
        """Simpan percakapan ke file."""
        if self.current_conversation and 'file_path' in self.current_conversation:
            with open(self.current_conversation['file_path'], 'w') as f:
                json.dump(self.current_conversation, f, indent=2)
    
    def get_last_n_messages(self, n: int = 5) -> list:
        """Dapatkan n pesan terakhir dari percakapan."""
        if self.current_conversation is None:
            return []
        return self.current_conversation['messages'][-n:]
    
    def _extract_platform(self, text: str) -> Optional[str]:
        """Ekstrak platform dari teks."""
        match = re.search(self.patterns['platform'], text, re.IGNORECASE)
        return match.group(1).lower() if match else None
    
    def _extract_finding_id(self, text: str) -> Optional[str]:
        """Ekstrak ID temuan dari teks."""
        match = re.search(self.patterns['finding_id'], text, re.IGNORECASE)
        return match.group(2) if match else None
    
    def _extract_screenshot_type(self, text: str) -> str:
        """Ekstrak tipe screenshot dari teks."""
        match = re.search(self.patterns['screenshot_type'], text, re.IGNORECASE)
        return match.group(0).lower().replace(' ', '_') if match else 'full_page'
    
    def _extract_vulnerability(self, text: str) -> Optional[str]:
        """Ekstrak jenis kerentanan dari teks."""
        match = re.search(self.patterns['vulnerability'], text, re.IGNORECASE)
        return match.group(1).lower() if match else None
    
    def _extract_evidence_type(self, text: str) -> str:
        """Ekstrak tipe bukti dari teks."""
        match = re.search(self.patterns['evidence_type'], text, re.IGNORECASE)
        return match.group(1).lower() if match else 'screenshot'
    
    def _extract_platform_from_domain(self, domain: str) -> str:
        """Ekstrak platform dari domain target."""
        domain_lower = domain.lower()
        if 'hackerone' in domain_lower:
            return 'hackerone'
        elif 'bugcrowd' in domain_lower:
            return 'bugcrowd'
        elif 'intigriti' in domain_lower:
            return 'intigriti'
        elif 'yeswehack' in domain_lower:
            return 'yeswehack'
        elif 'immunefi' in domain_lower:
            return 'immunefi'
        elif 'hackthebox' in domain_lower:
            return 'hackthebox'
        elif 'tryhackme' in domain_lower:
            return 'tryhackme'
        else:
            return 'unknown'
    
    def set_evidence_generator(self, evidence_generator):
        """Set evidence generator untuk integrasi."""
        self.evidence_generator = evidence_generator
    
    def set_patch_generator(self, patch_generator):
        """Set patch generator untuk integrasi."""
        self.patch_generator = patch_generator
    
    def set_telegram_notifier(self, telegram_notifier):
        """Set Telegram notifier untuk integrasi."""
        self.telegram_notifier = telegram_notifier
    
    def set_human_in_the_loop_gate(self, human_in_the_loop_gate):
        """Set Human-in-the-Loop Gate untuk integrasi."""
        self.human_in_the_loop_gate = human_in_the_loop_gate
    
    def set_platform_submitters(self, submitters: dict):
        """Set platform submitters untuk integrasi auto-submit."""
        self.platform_submitters = submitters

    def set_brief_engine(self, brief_engine):
        """Set ProgramBrief handler (arc_chat_engine) agar perintah brief
        (set brief / tambah scope / manifest / dll) diproses dalam dialog."""
        self.brief_engine = brief_engine