#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Uji end-to-end: jalur poller Telegram -> session_approval_controller.handle_text
-> bridge -> human_in_the_loop_gate. Ini persis jalur yang dipakai di produksi
(arc_main auto-start_poller=True).
"""
import sys, os, io, importlib.util, threading, time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
BASE = os.path.dirname(os.path.abspath(__file__))

def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(BASE, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

tg = load("telegram_notifier", "DIALOGIC_COPILLOT/PLATFORM_COMMUNICATOR/telegram_notifier.py")
gate = load("human_in_the_loop_gate", "COGNITIVE_CORE/human_in_the_loop_gate.py")
sac = load("session_approval_controller",
           "TOOL_ORCHESTRATION/INTELLIGENT_TOOL_MANAGER/session_approval_controller.py")

notifier = tg.TelegramNotifier(config_path="c:/nonexistent/config.yaml")
sent = []
def fake_send(msg, parse_mode='HTML'):
    sent.append(msg)
    return {'success': True}
notifier.send_notification = fake_send

hitl = gate.HumanInTheLoopGate(telegram_notifier=notifier)
notifier.set_human_in_the_loop_gate(hitl)

# Controller dengan telegram, tanpa auto-start poller (kita tes handle_text langsung)
controller = sac.SessionApprovalController(telegram=notifier, bot_token="dummy",
                                           auto_start_poller=False)

print("=" * 72)
print("UJI E2E: poller -> handle_text -> bridge -> gate")
print("=" * 72)

# 1. Mulai request_approval di thread (mirip ARCOrchestrator._request_human_approval)
finding = {'id': 'e2e_1', 'operation_type': 'report_submission', 'risk_score': 0.95,
           'platform': 'hackerone', 'description': 'e2e test'}
res_holder = {}
def do_req():
    res_holder['r'] = hitl.request_approval(finding)
t = threading.Thread(target=do_req, daemon=True)
t.start()
time.sleep(0.5)

op_id = list(hitl.pending_approvals.keys())[0]
print(f"\nGate pending op: {op_id}")

# 2. Simulasikan balasan user di HP: "/approve_op_xxx"
#    Poller memanggil controller.handle_text(text, source='telegram')
reply = f"/approve_{op_id}"
print(f"User balas (diterima poller): {reply}")
result = controller.handle_text(reply, source='telegram')
print(f"handle_text result: {result}")

t.join(timeout=8)
print(f"\nrequest_approval return: {res_holder.get('r')}")

# 3. Verifikasi
ok = True
if res_holder.get('r') is not True:
    print("❌ Approval tidak sampai ke gate (handle_text tidak bridge)")
    ok = False
else:
    print("✅ APPROVAL BERHASIL sampai ke gate")

# 4. Uji /reject lewat handle_text juga
finding2 = {'id': 'e2e_2', 'operation_type': 'report_submission', 'risk_score': 0.9,
            'platform': 'bugcrowd', 'description': 'reject e2e'}
res2 = {}
def do_req2():
    res2['r'] = hitl.request_approval(finding2)
t2 = threading.Thread(target=do_req2, daemon=True)
t2.start()
time.sleep(0.5)
op2 = list(hitl.pending_approvals.keys())[0]
res_r = controller.handle_text(f"/reject_{op2}", source='telegram')
t2.join(timeout=8)
if res2.get('r') is not False:
    print("❌ Reject tidak sampai ke gate")
    ok = False
else:
    print("✅ REJECT BERHASIL sampai ke gate")

# 5. Uji command non-approval tetap jalan via handle_text (forward ke telegram)
r_help = controller.handle_text("/help", source='telegram')
print(f"\n/help via handle_text: success={r_help.get('success')}")
if r_help.get('success') is not True:
    print("❌ /help tidak forwarded ke telegram")
    ok = False
else:
    print("✅ /help diteruskan ke telegram_notifier")

print("\n" + "=" * 72)
print("HASIL E2E:", "SEMUA PASS ✅" if ok else "ADA GAGAL ❌")
print("=" * 72)
sys.exit(0 if ok else 1)
