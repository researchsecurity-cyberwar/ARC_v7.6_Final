import time
import os

class HumanInTheLoopGate:
    """
    Mandatory approval gate for high-risk operations and chain reactions.
    Memastikan operasi berisiko tinggi mendapat persetujuan manusia via Telegram atau CLI.
    """
    
    HIGH_RISK_OPERATIONS = [
        'chain_exploitation',
        'data_exfiltration', 
        'account_takeover',
        'financial_impact',
        'report_submission',
        'scope_expansion'
    ]
    
    def __init__(self, auto_approve_low_risk=True, telegram_notifier=None):
        self.auto_approve_low_risk = auto_approve_low_risk
        self.telegram_notifier = telegram_notifier
        self.pending_approvals = {}  # Menyimpan operasi yang menunggu approval
    
    def requires_approval(self, operation_type, risk_score):
        """
        Tentukan apakah operasi memerlukan persetujuan manusia.
        """
        if operation_type in self.HIGH_RISK_OPERATIONS:
            return True
        
        # Risk score > 0.7 memerlukan persetujuan (sedikit lebih longgar)
        if risk_score > 0.7:
            return True
            
        return False
    
    def request_approval(self, operation_details):
        """
        Minta persetujuan manusia untuk operasi berisiko via Telegram + CLI.
        """
        operation_id = f"op_{int(time.time())}_{hash(str(operation_details)) % 10000}"
        operation_details['id'] = operation_id
        
        # Simpan operasi yang menunggu approval
        self.pending_approvals[operation_id] = operation_details
        
        # Kirim notifikasi ke Telegram jika tersedia
        if self.telegram_notifier:
            approval_message = self._format_telegram_approval_message(operation_details)
            self.telegram_notifier.send_notification(approval_message)
            
            print(f"\n📱 Approval request sent to Telegram!")
            print(f"   Operation ID: {operation_id}")
            print(f"   Check your Telegram for approval options.")
        
        # Tampilkan di CLI juga
        self._show_cli_approval_prompt(operation_details)
        
        # Tunggu approval (bisa dari Telegram atau CLI)
        return self._wait_for_approval(operation_id)
    
    def _format_telegram_approval_message(self, operation_details):
        """Format pesan approval untuk Telegram."""
        platform_emoji = {
            'hackerone': '🔴',
            'bugcrowd': '🔵',
            'intigriti': '🟢',
            'immunefi': '🟣',
            'hackthebox': '🟠'
        }
        
        platform = operation_details.get('platform', 'unknown')
        emoji = platform_emoji.get(platform, '⚠️')
        
        risk_level = "🔥 CRITICAL" if operation_details.get('risk_score', 0) > 0.9 else \
                    "🚨 HIGH" if operation_details.get('risk_score', 0) > 0.8 else \
                    "⚠️ MEDIUM"
        
        message = (
            f"{emoji} <b>HUMAN APPROVAL REQUIRED</b> {risk_level}\n\n"
            f"🎯 <b>Operation:</b> {operation_details.get('operation_type', 'Unknown')}\n"
            f"🌐 <b>Target:</b> {operation_details.get('target', 'N/A')}\n"
            f"💰 <b>Potential Impact:</b> {operation_details.get('potential_impact', 'N/A')}\n\n"
            f"📋 <b>Description:</b>\n{operation_details.get('description', 'No details')}\n\n"
            f"<b>Commands:</b>\n"
            f"/approve_{operation_details['id']} → ✅ Approve\n"
            f"/reject_{operation_details['id']} → ❌ Reject\n"
            f"/pause_{operation_details['id']} → ⏸️ Pause for review\n\n"
            f"<i>ARC v7.6 Final • Autonomous Red Cell</i>"
        )
        return message
    
    def _show_cli_approval_prompt(self, operation_details):
        """Tampilkan prompt approval di CLI."""
        print("\n" + "="*60)
        print("⚠️  HUMAN-IN-THE-LOOP APPROVAL REQUIRED")
        print("="*60)
        print(f"Operation ID: {operation_details['id']}")
        print(f"Operation: {operation_details.get('operation_type', 'Unknown')}")
        print(f"Target: {operation_details.get('target', 'Unknown')}")
        print(f"Risk Score: {operation_details.get('risk_score', 0):.2f}")
        print(f"Potential Impact: {operation_details.get('potential_impact', 'N/A')}")
        print(f"Description: {operation_details.get('description', 'No description')}")
        print("\nOptions:")
        print("1. ✅ Approve")
        print("2. ⏸️  Pause for review") 
        print("3. ❌ Reject")
        print(f"\nYou can also approve via Telegram with: /approve_{operation_details['id']}")
    
    def _wait_for_approval(self, operation_id, timeout=3600):
        """
        Tunggu approval dari Telegram atau CLI.
        Timeout: 1 jam default.
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Cek apakah sudah ada approval dari Telegram
            if operation_id in self.pending_approvals:
                operation_details = self.pending_approvals[operation_id]
                if operation_details.get('approved') is not None:
                    result = operation_details['approved']
                    del self.pending_approvals[operation_id]
                    return result
            
            # Untuk CLI, kita asumsikan approval langsung dari input
            # (Dalam implementasi nyata, ini akan menggunakan threading atau polling)
            try:
                # Ini adalah placeholder - dalam implementasi nyata,
                # CLI akan menggunakan input() terpisah atau sistem antrian
                time.sleep(5)
            except KeyboardInterrupt:
                print("\n❌ Operation cancelled by user.")
                if operation_id in self.pending_approvals:
                    del self.pending_approvals[operation_id]
                return False
        
        # Timeout - reject otomatis
        print(f"\n⏰ Approval timeout for operation {operation_id}. Operation rejected.")
        if operation_id in self.pending_approvals:
            del self.pending_approvals[operation_id]
        return False
    
    def handle_telegram_approval(self, command, operation_id):
        """
        Tangani approval dari perintah Telegram.
        Dipanggil oleh TelegramNotifier saat menerima /approve_XYZ.
        """
        if operation_id not in self.pending_approvals:
            return {'success': False, 'message': f'No pending operation with ID: {operation_id}'}
        
        operation_details = self.pending_approvals[operation_id]
        
        if command == 'approve':
            operation_details['approved'] = True
            self.pending_approvals[operation_id] = operation_details
            
            # Kirim konfirmasi ke Telegram
            if self.telegram_notifier:
                confirm_msg = f"✅ <b>APPROVED</b>\nOperation {operation_id} approved and will proceed."
                self.telegram_notifier.send_notification(confirm_msg)
            
            return {'success': True, 'message': f'Operation {operation_id} approved'}
            
        elif command == 'reject':
            operation_details['approved'] = False
            self.pending_approvals[operation_id] = operation_details
            
            if self.telegram_notifier:
                confirm_msg = f"❌ <b>REJECTED</b>\nOperation {operation_id} rejected by human operator."
                self.telegram_notifier.send_notification(confirm_msg)
            
            return {'success': True, 'message': f'Operation {operation_id} rejected'}
            
        elif command == 'pause':
            operation_details['approved'] = None  # Tetap menunggu
            self.pending_approvals[operation_id] = operation_details
            
            if self.telegram_notifier:
                confirm_msg = f"⏸️ <b>PAUSED</b>\nOperation {operation_id} paused for manual review."
                self.telegram_notifier.send_notification(confirm_msg)
            
            return {'success': True, 'message': f'Operation {operation_id} paused'}
        
        return {'success': False, 'message': 'Invalid approval command'}
    
    def auto_approve_if_safe(self, operation_type, risk_score):
        """
        Otomatis menyetujui operasi jika dianggap aman.
        """
        if not self.requires_approval(operation_type, risk_score):
            if self.auto_approve_low_risk:
                print(f"✅ Auto-approved low-risk operation: {operation_type}")
                return True
        return False
    
    def set_telegram_notifier(self, telegram_notifier):
        """Set Telegram notifier untuk integrasi."""
        self.telegram_notifier = telegram_notifier
    
    def set_evidence_generator(self, evidence_generator):
        """Set evidence generator untuk integrasi."""
        self.evidence_generator = evidence_generator
    
    def set_patch_generator(self, patch_generator):
        """Set patch generator untuk integrasi."""
        self.patch_generator = patch_generator
