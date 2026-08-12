#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Uji komprehensif fitur bot Telegram ARC v7.6 Final.
Memverifikasi: semua command handle_telegram_command, alias /star,
dan alur Human-in-the-Loop approval (feedback) dari Telegram.
Menggunakan mock (tanpa jaringan Telegram asli).
"""
import sys, os, io, importlib.util, types

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
BASE = os.path.dirname(os.path.abspath(__file__))
results = []

def report(name, ok, detail=""):
    results.append(ok)
    print(f"  {'✅' if ok else '❌'} {name}" + (f" — {detail}" if detail else ""))

def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(BASE, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

print("=" * 72)
print("UJI BOT TELEGRAM ARC — command & human-in-the-loop")
print("=" * 72)

# ---- Load TelegramNotifier & HumanInTheLoopGate ----
tg = load("telegram_notifier", "DIALOGIC_COPILLOT/PLATFORM_COMMUNICATOR/telegram_notifier.py")
gate = load("human_in_the_loop_gate", "COGNITIVE_CORE/human_in_the_loop_gate.py")

# Mock telegram notifier tanpa token (base_url None)
notifier = tg.TelegramNotifier(config_path="c:/nonexistent/config.yaml")

# Override send_notification agar tidak kena HTTP (record pesan)
sent_msgs = []
def fake_send(msg, parse_mode='HTML'):
    sent_msgs.append(msg)
    return {'success': True, 'response': None}
notifier.send_notification = fake_send

# Human-in-the-loop gate
hitl = gate.HumanInTheLoopGate(telegram_notifier=notifier)
notifier.set_human_in_the_loop_gate(hitl)
print("\n[1] COMMAND BOT TELEGRAM LANGSUNG")
print("-" * 60)
# Alias /star
r = notifier.handle_telegram_command('/star', [])
report("/star -> _start_autonomous_ops", r.get('success') is True,
       str(r.get('message')))
# /start
r = notifier.handle_telegram_command('/start', [])
report("/start", r.get('success') is True)
# /stop
r = notifier.handle_telegram_command('/stop', [])
report("/stop", r.get('success') is True)
# /help
r = notifier.handle_telegram_command('/help', [])
report("/help", r.get('success') is True)
# /status (butuh session_manager -> akan gagal karena belum set, tapi TIDAK crash)
r = notifier.handle_telegram_command('/status', [])
report("/status (tanpa session_manager, tidak crash)", 'success' in r or 'message' in r,
       str(r.get('error') or r.get('message')))
# /findings
r = notifier.handle_telegram_command('/findings', [])
report("/findings (tidak crash)", isinstance(r, dict))
# /income
r = notifier.handle_telegram_command('/income', [])
report("/income (tidak crash)", isinstance(r, dict))
# /report
r = notifier.handle_telegram_command('/report', [])
report("/report -> _trigger_manual_report", r.get('success') is True)
# Unknown
r = notifier.handle_telegram_command('/unknown_cmd', [])
report("/unknown_cmd -> error ramah", r.get('success') is False and 'Unknown' in r.get('message',''),
       r.get('message'))
# /update_session tanpa arg
r = notifier.handle_telegram_command('/update_session', [])
report("/update_session tanpa args (tidak crash)", isinstance(r, dict))

print("\n[2] ALUR HUMAN-IN-THE-LOOP")
print("-" * 60)
finding = {
    'id': 'find_001',
    'operation_type': 'report_submission',
    'risk_score': 0.95,
    'platform': 'hackerone',
    'target': 'example.com',
    'description': 'Test high-risk submission'
}
report("requires_approval(report_submission, 0.95) = True",
       hitl.requires_approval('report_submission', 0.95) is True)

import threading, time
approval_thread_result = {}
def do_request():
    approval_thread_result['result'] = hitl.request_approval(finding)
t = threading.Thread(target=do_request, daemon=True)
t.start()
time.sleep(0.5)

op_ids = list(hitl.pending_approvals.keys())
report("request_approval membuat pending op_... ID", len(op_ids) > 0,
       op_ids[:1])
op_id = op_ids[0] if op_ids else 'op_unknown'

print("\n[3] BALASAN TELEGRAM /approve_op_... (via gate)")
print("-" * 60)
r = notifier.handle_telegram_command(f'/approve_{op_id}', [])
report(f"/approve_{op_id} via gate", r.get('success') is True, str(r.get('message')))

# Pastikan handle_telegram_approval sudah set approved=True di gate
approved_val = hitl.pending_approvals.get(op_id, {}).get('approved')
report("gate.pending_approvals[op].approved == True (diproses gate)",
       approved_val is True, f"approved={approved_val}")

t.join(timeout=8)
res = approval_thread_result.get('result')
report("request_approval() return mengikuti approval manusia",
       res is True, f"return={res}")
report("Pending approval dibersihkan setelah diputuskan",
       op_id not in hitl.pending_approvals)

# --- Uji reject path ---
finding2 = {'id': 'find_002', 'operation_type': 'report_submission',
            'risk_score': 0.9, 'platform': 'bugcrowd', 'description': 'reject test'}
def do_request2():
    approval_thread_result['r2'] = hitl.request_approval(finding2)
t2 = threading.Thread(target=do_request2, daemon=True)
t2.start()
time.sleep(0.5)
op2 = list(hitl.pending_approvals.keys())[0]
r = notifier.handle_telegram_command(f'/reject_{op2}', [])
report(f"/reject_{op2} -> gate reject", r.get('success') is True, str(r.get('message')))
t2.join(timeout=8)
report("request_approval() return False setelah reject",
       approval_thread_result.get('r2') is False)

print("\n" + "=" * 72)
passed = sum(1 for x in results if x)
total = len(results)
print(f"HASIL: {passed}/{total} PASS")
print("=" * 72)
sys.exit(0 if passed == total else 1)

