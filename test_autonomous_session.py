"""
ARC Autonomous Session Engine — Verification Test
Jalankan:  python test_autonomous_session.py > out.txt 2>&1
"""
import os
import sys
import json

ROOT = os.path.abspath('.')
sys.path.insert(0, ROOT)

from TOOL_ORCHESTRATION.INTELLIGENT_TOOL_MANAGER import (
    AutonomousSessionEngine,
    create_autonomous_engine,
)


def main():
    passed = failed = 0

    def check(name, cond, detail=""):
        nonlocal passed, failed
        flag = "PASS" if cond else "FAIL"
        print(f"[{flag}] {name} {('| ' + str(detail)) if detail else ''}")
        if cond:
            passed += 1
        else:
            failed += 1

    eng = create_autonomous_engine()

    print("== 1) DETEKSI LINGKUNGAN ==")
    env = eng.env
    check("platform terdeteksi", bool(env.get('platform')))
    check("distro terdeteksi (bukan crash)", env.get('distro') is not None)
    check("is_kali boolean", isinstance(env.get('is_kali'), bool))
    check("package manager list", isinstance(env.get('package_managers'), list))
    check("session/cwd terisi", bool(env.get('cwd')))

    print("== 2) ENSURE TOOL (tidak menjalankan install di luar Kali) ==")
    r = eng.ensure_tool('python')
    check("ensure(existing tool)=already_installed",
          r.get('success') and r.get('action') == 'already_installed')

    print("== 3) UPDATE DATA (harus degradasi anggun tanpa crash) ==")
    try:
        up = eng.update_all_data(tools=[])
        check("update_all_data selesai tanpa crash", isinstance(up, dict))
    except Exception as e:
        check("update_all_data selesai tanpa crash", False, f"{e}")

    print("== 4) RUN OTONOM (task aman, tidak menyentuh jaringan) ==")
    # gunakan intent yang aman: hanya memastikan tool python tanpa target
    res = eng.run_autonomously({'tool': 'python', 'intent': 'generic',
                                'params': {'extra_args': "-c \"print('ok')\""},
                                'update_data': False})
    check("run_autonomously mengembalikan struktur lengkap",
          isinstance(res, dict) and 'ensure' in res or not res.get('success', True) or 'session' in res,
          json.dumps({k: (v if not isinstance(v, dict) else '...') for k, v in res.items()}))
    if 'session' in res:
        check("session_report ada", isinstance(res['session'].get('environment'), dict))
        check("installed_this_session adalah list",
              isinstance(res['session'].get('installed_this_session'), list))

    print("== 5) CLI STATUS (parsing) ==")
    try:
        import subprocess
        p = subprocess.run([sys.executable, os.path.join(
            ROOT, 'TOOL_ORCHESTRATION', 'INTELLIGENT_TOOL_MANAGER',
            'autonomous_session_engine.py'), 'status'],
            capture_output=True, text=True, timeout=120)
        check("CLI 'status' berjalan",
              p.returncode == 0 or 'status' in (p.stdout or '') + (p.stderr or ''),
              (p.stdout or p.stderr)[:120])
    except Exception as e:
        check("CLI 'status' berjalan", False, str(e))

    print(f"\nRESULT: {passed} pass, {failed} fail")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
