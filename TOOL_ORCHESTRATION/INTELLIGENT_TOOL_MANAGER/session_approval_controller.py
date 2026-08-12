"""
ARC Session Approval Controller v7.6 Final
============================================
Approval/verifikasi MANUSIA untuk operasi yang butuh izin ARC, dengan
pendekatan NON-BLOCKING (tidak mengganggu ARC yang sedang berjalan).

Fitur:
  - Operasi (mis. install tool, sudo/PIN terminal, aksi berisiko) dibuatkan
    permintaan approval ber-ID unik.
  - Notifikasi cerdas via Telegram + CLI dengan perintah:
        /approve <id> <pin?>   -> menyetujui (opsional verifikasi PIN)
        /reject  <id>          -> menolak
        /status                -> daftar pending
  - Poller Telegram latar (thread) agar bisa di-approve dari HP tanpa laptop.
  - Verifikasi PIN untuk operasi yang sensitif.
  - Non-blocking: ARC terus berjalan; hanya task terkait yang menunggu
    keputusan (dengan timeout), lalu eksekusi lanjut di terminal.
"""

import os
import re
import time
import json
import threading
from datetime import datetime
from typing import Dict, List, Optional


class ApprovalRequest:
    """Satu permintaan persetujuan yang menunggu keputusan manusia."""

    LEVELS = {'info': 0.0, 'install': 0.4, 'sudo_pin': 0.7, 'high_risk': 0.9}

    def __init__(self, req_id: str, title: str, description: str,
                 level: str = 'install', pin: Optional[str] = None,
                 meta: Optional[Dict] = None, timeout: int = 600):
        self.id = req_id
        self.title = title
        self.description = description
        self.level = level if level in self.LEVELS else 'install'
        self.risk_score = self.LEVELS.get(self.level, 0.4)
        self.pin = pin                      # None = tanpa PIN
        self.pin_required = bool(pin)
        self.pin_attempts = 0
        self.max_pin_attempts = 3
        self.meta = meta or {}
        self.timeout = timeout
        self.status = 'pending'             # pending/approved/rejected/paused/timed_out
        self.created_at = time.time()
        self.decided_at = None
        self.decision_by = None             # 'cli' | 'telegram'

    @property
    def expired(self) -> bool:
        if self.status in ('approved', 'rejected', 'timed_out'):
            return False
        return (time.time() - self.created_at) > self.timeout

    def approve(self, pin: Optional[str] = None, source: str = 'cli'):
        if self.pin_required:
            if not pin or pin != self.pin:
                self.pin_attempts += 1
                return {'success': False,
                        'error': f'PIN salah (percobaan {self.pin_attempts}/{self.max_pin_attempts})'}
        self.status = 'approved'
        self.decided_at = time.time()
        self.decision_by = source
        return {'success': True, 'message': f'{self.id} disetujui'}

    def reject(self, source: str = 'cli'):
        self.status = 'rejected'
        self.decided_at = time.time()
        self.decision_by = source
        return {'success': True, 'message': f'{self.id} ditolak'}

    def pause(self, source: str = 'cli'):
        if self.status == 'pending':
            self.status = 'paused'
            self.decision_by = source
        return {'success': True, 'message': f'{self.id} dijeda'}

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'level': self.level,
            'risk_score': self.risk_score,
            'pin_required': self.pin_required,
            'status': self.status,
            'created_at': datetime.fromtimestamp(self.created_at).isoformat(),
            'decided_at': datetime.fromtimestamp(self.decided_at).isoformat()
                            if self.decided_at else None,
            'decision_by': self.decision_by,
            'meta': self.meta,
        }


class SessionApprovalController:
    """
    Pusat persetujuan non-blocking. Mengelola permintaan, notifikasi Telegram+CLI,
    polling Telegram latar, dan verifikasi PIN.
    """

    def __init__(self, telegram=None, bot_token: str = '',
                 chat_id: str = '', config_path: str = "~/.arc/config.yaml",
                 auto_start_poller: bool = True):
        self.telegram = telegram
        self.requests: Dict[str, ApprovalRequest] = {}
        self.events: Dict[str, threading.Event] = {}

        self.bot_token = bot_token or self._read_config(config_path, 'bot_token')
        self.chat_id = chat_id or self._read_config(config_path, 'chat_id')

        self._polling = False
        self._poller_thread = None
        self._cli_thread = None
        self._lock = threading.RLock()
        self._cli_reader_running = False
        self._last_update_id = 0

        if auto_start_poller and self.bot_token:
            self.start_poller()
        if auto_start_poller:
            self.start_cli_listener()

    # ------------------------------------------------------------------
    # config helper
    # ------------------------------------------------------------------
    @staticmethod
    def _read_config(path: str, key: str) -> str:
        try:
            import yaml
            with open(os.path.expanduser(path), 'r') as f:
                cfg = yaml.safe_load(f) or {}
            return str(cfg.get('telegram', {}).get(key, ''))
        except Exception:
            return ''

    # ------------------------------------------------------------------
    # request lifecycle
    # ------------------------------------------------------------------
    def request(self, title: str, description: str, level: str = 'install',
                pin: Optional[str] = None, meta: Optional[Dict] = None,
                timeout: int = 600) -> ApprovalRequest:
        req_id = f"ap_{int(time.time())}_{len(self.requests) % 10000}"
        req = ApprovalRequest(req_id, title, description, level, pin, meta, timeout)
        with self._lock:
            self.requests[req_id] = req
            self.events[req_id] = threading.Event()
        self.notify(req)
        return req

    def notify(self, req: ApprovalRequest):
        """Kirim notifikasi approval via Telegram dan CLI (perintah cerdas)."""
        print("\n" + "=" * 64)
        print("HUMAN APPROVAL REQUIRED")
        print("=" * 64)
        print(f"  ID        : {req.id}")
        print(f"  Operasi   : {req.title}")
        print(f"  Deskripsi : {req.description}")
        if req.pin_required:
            print("  PIN       : Diperlukan (verifikasi)")
        print("  Perintah:")
        print(f"    /approve {req.id} <pin>   -> setujui & lanjutkan")
        print(f"    /reject  {req.id}        -> tolak")
        print(f"    /status                  -> daftar pending")
        print("=" * 64)

        if self.telegram is not None and hasattr(self.telegram, 'send_notification'):
            try:
                self.telegram.send_notification(self.format_telegram(req))
            except Exception as e:
                print(f"(Telegram notif gagal: {e})")

    def format_telegram(self, req: ApprovalRequest) -> str:
        emoji = {'info': 'ℹ️', 'install': '📦', 'sudo_pin': '🔐',
                 'high_risk': '🚨'}.get(req.level, '✋')
        lines = [
            f"{emoji} <b>HUMAN APPROVAL REQUIRED</b>",
            "",
            f"🆔 <b>ID:</b> <code>{req.id}</code>",
            f"📌 <b>Operasi:</b> {req.title}",
            f"📝 <b>Deskripsi:</b> {req.description}",
        ]
        if req.pin_required:
            lines.append("🔐 <b>PIN:</b> Diperlukan")
        lines += [
            "",
            "<b>Perintah (balas pesan ini):</b>",
            f"/approve {req.id}{' &lt;PIN&gt;' if req.pin_required else ''}  -> Approve",
            f"/reject {req.id}  -> Tolak",
            f"/status  -> Daftar pending",
            "",
            "<i>ARC akan lanjut otomatis di terminal setelah disetujui.</i>",
        ]
        return "\n".join(lines)



    # ------------------------------------------------------------------
    # decision (dari CLI / Telegram) + verifikasi PIN
    # ------------------------------------------------------------------
    def _resolve(self, req_id: str) -> Optional[ApprovalRequest]:
        with self._lock:
            return self.requests.get(req_id)

    def approve(self, req_id: str, pin: Optional[str] = None,
                source: str = 'cli') -> Dict:
        req = self._resolve(req_id)
        if req is None:
            return {'success': False, 'error': f'Tidak ada permintaan {req_id}'}
        result = req.approve(pin, source)
        if result.get('success'):
            ev = self.events.get(req_id)
            if ev:
                ev.set()
        else:
            print(f"PIN salah utk {req_id}")
        return result

    def reject(self, req_id: str, source: str = 'cli') -> Dict:
        req = self._resolve(req_id)
        if req is None:
            return {'success': False, 'error': f'Tidak ada permintaan {req_id}'}
        result = req.reject(source)
        ev = self.events.get(req_id)
        if ev:
            ev.set()
        return result

    def pause(self, req_id: str, source: str = 'cli') -> Dict:
        req = self._resolve(req_id)
        if req is None:
            return {'success': False, 'error': f'Tidak ada permintaan {req_id}'}
        return req.pause(source)

    def get_decision(self, req_id: str) -> Optional[str]:
        req = self._resolve(req_id)
        return req.status if req else None

    def await_decision(self, req_id: str, poll_interval: float = 1.0) -> str:
        """
        Tunggu keputusan untuk task TERTENTU saja (bukan seluruh proses).
        ARC lain tetap berjalan; task ini lanjut sendiri saat ada keputusan.
        """
        req = self._resolve(req_id)
        if req is None:
            return 'not_found'
        ev = self.events.get(req_id)
        while True:
            if req.expired:
                req.status = 'timed_out'
                return 'timed_out'
            if ev is not None and ev.is_set():
                return req.status
            time.sleep(poll_interval)

    # ------------------------------------------------------------------
    # command parser (teks dari CLI maupun Telegram)
    # ------------------------------------------------------------------
    @staticmethod
    def parse_command(text: str):
        """Parse perintah approval. Return (cmd, id, pin).
        Mendukung 2 format yang dihasilkan notify()/format_telegram():
          - /approve_<id> [pin]   (underscore, dipakai pesan telegram)
          - /approve <id> [pin]   (spasi, dipakai prompt CLI)
        """
        text = (text or '').strip()
        m = re.match(r'^/(approve|reject|pause|status)(?:_(\w+))?\s*(.*)$', text, re.I)
        if m:
            cmd = m.group(1).lower()
            rid = m.group(2)            # dari format /approve_<id>
            rest = m.group(3).strip()   # sisa teks setelah command
            tokens = rest.split() if rest else []
            if cmd == 'approve':
                if not rid and tokens:
                    # format /approve <id> [pin]
                    rid = tokens[0]
                    pin = tokens[1] if len(tokens) > 1 else None
                else:
                    # format /approve_<id> [pin]
                    pin = tokens[0] if tokens else None
            else:
                # reject / pause / status
                if not rid and tokens:
                    rid = tokens[0]
                pin = None
            return cmd, rid, pin
        return None, None, None

    def handle_text(self, text: str, source: str = 'cli') -> Dict:
        cmd, rid, pin = self.parse_command(text)
        if not cmd:
            # Forward non-approval commands (e.g. /help, /start, /stop) to TelegramNotifier
            if (source == 'telegram' and self.telegram is not None and
                    hasattr(self.telegram, 'handle_telegram_command')):
                parts = text.strip().split()
                command = parts[0].lower() if parts else ''
                args = parts[1:] if len(parts) > 1 else []
                result = self.telegram.handle_telegram_command(command, args)
                # handle_telegram_command already sends its own notification
                # via send_notification, so flag to skip double-send in poll loop
                result['_already_notified'] = True
                return result
            return {'success': False, 'error': 'perintah tidak dikenali'}
        if cmd == 'status':
            pending = [r.id for r in self.requests.values() if r.status == 'pending']
            msg = f"Pending: {len(pending)} — " + (", ".join(pending) if pending else "tidak ada")
            if self.telegram is not None and hasattr(self.telegram, 'send_notification'):
                self.telegram.send_notification(msg)
            print(msg)
            return {'success': True, 'pending': pending}
        if not rid:
            return {'success': False, 'error': 'perlu ID permintaan'}
        req = self._resolve(rid)

        # --- BRIDGE ke Human-in-the-Loop Gate ---
        # Approval dari ARCOrchestrator.human_in_the_loop_gate disimpan di
        # gate.pending_approvals (ID 'op_...'), SEDANGKAN session_approval_controller
        # menyimpan di self.requests (ID 'ap_...'). Karena keduanya terpisah,
        # perintah /approve_op_... dari notifikasi gate TIDAK akan ditemukan di
        # self.requests. Jika tidak ditemukan, teruskan ke TelegramNotifier yang
        # akan merutekan ke human_in_the_loop_gate.handle_telegram_approval().
        if req is None and source == 'telegram' and self.telegram is not None and \
                hasattr(self.telegram, 'handle_telegram_command'):
            parts = text.strip().split()
            command = parts[0].lower() if parts else ''
            args = parts[1:] if len(parts) > 1 else []
            result = self.telegram.handle_telegram_command(command, args)
            result['_already_notified'] = True
            return result

        if cmd == 'approve':
            needed = req.pin if (req and req.pin_required) else None
            return self.approve(rid, pin, source)
        elif cmd == 'reject':
            return self.reject(rid, source)
        elif cmd == 'pause':
            return self.pause(rid, source)
        return {'success': False, 'error': 'perintah tidak dikenali'}



    # ------------------------------------------------------------------
    # Poller Telegram latar (approve dari HP tanpa laptop) + CLI listener
    # ------------------------------------------------------------------
    def start_poller(self, interval: float = 2.0):
        """Mulai thread latar yang membaca pesan Telegram (getUpdates)."""
        if self._polling or not self.bot_token:
            return
        self._polling = True
        self._poller_thread = threading.Thread(
            target=self._poll_telegram_loop, args=(interval,),
            daemon=True, name='arc-tg-approval-poller')
        self._poller_thread.start()

    def _poll_telegram_loop(self, interval: float):
        import requests
        base = f"https://api.telegram.org/bot{self.bot_token}"
        while self._polling:
            try:
                url = f"{base}/getUpdates"
                if self._last_update_id:
                    url += f"?offset={self._last_update_id + 1}"
                r = requests.get(url, timeout=15)
                if r.status_code == 200:
                    for upd in r.json().get('result', []):
                        self._last_update_id = max(self._last_update_id, upd.get('update_id', 0))
                        msg = upd.get('message') or upd.get('callback_query', {}).get('message')
                        text = upd.get('message', {}).get('text')
                        if text and text.strip().startswith('/'):
                            result = self.handle_text(text, source='telegram')
                            if not result.get('_already_notified') and self.telegram is not None:
                                self.telegram.send_notification(
                                    self._fmt_result(result))
            except Exception:
                pass  # polling dilanjutkan di iterasi berikutnya
            time.sleep(interval)

    def start_cli_listener(self):
        """Thread latar membaca perintah dari CLI (stdin) bila ada baris."""
        if self._cli_reader_running:
            return
        self._cli_reader_running = True
        self._cli_thread = threading.Thread(
            target=self._cli_read_loop, daemon=True, name='arc-cli-approval')
        self._cli_thread.start()

    def _cli_read_loop(self):
        try:
            while True:
                line = input()
                if line and line.strip().startswith('/'):
                    self.handle_text(line, source='cli')
        except (EOFError, KeyboardInterrupt):
            pass

    def _fmt_result(self, result: Dict) -> str:
        if result.get('success'):
            return f"✅ {result.get('message', 'OK')}"
        return f"⚠️ {result.get('error', 'gagal')}"

    def stop(self):
        self._polling = False
        self._cli_reader_running = False

