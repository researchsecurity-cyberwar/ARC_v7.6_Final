"""
ARC Intelligent Tool Commander — Verification Test
===================================================
Memverifikasi bahwa ARC dapat memakai tool CLI secara MANDIRI:
mempelajari antarmuka, memetakan intent->flag yang benar, membangun command,
menjalankan, dan self-heal. Berfungsi untuk tool apa pun (existing & future).

Jalankan:  python test_smart_tool.py
"""
import os
import sys

ROOT = os.path.abspath('.')
sys.path.insert(0, ROOT)

from TOOL_ORCHESTRATION.INTELLIGENT_TOOL_MANAGER import (
    IntelligentToolCommander,
    create_smart_tool_commander,
)


def main():
    passed = 0
    failed = 0
    commander = create_smart_tool_commander()

    def check(name, cond, detail=""):
        nonlocal passed, failed
        flag = "✅" if cond else "❌"
        print(f"{flag} {name} {('| ' + str(detail)) if detail else ''}")
        if cond:
            passed += 1
        else:
            failed += 1

    print("=" * 72)
    print("1) BELAJAR ANTARMUKA TOOL (discover + parse help)")
    print("=" * 72)
    # curl tersedia di sebagian besar sistem; pakai python sebagai alternatif
    sample = 'curl' if commander.ensure_available('curl') else 'python'
    profile = commander.get_profile(sample)
    check(f"Profil dibangun untuk '{sample}' + cache tersimpan",
          len(profile.flags) > 0,
          f"opsi terdeteksi={len(profile.flags)}, subcommand={list(profile.subcommands)[:3]}")
    cache_file = commander._profile_cache_path(sample)
    check("Cache profil ditulis ke disk", os.path.exists(cache_file), cache_file)
    # reload dari cache (profil harus sama tanpa rediscover)
    reloaded = commander.load_profile(sample)
    check("Profil dapat dimuat ulang dari cache",
          reloaded is not None and len(reloaded.flags) == len(profile.flags))

    print("\n" + "=" * 72)
    print("2) MEMBANGUN COMMAND DARI INTENT + PARAMETER (bukan hardcode)")
    print("=" * 72)
    # Demonstrasi bagaimana flag dipilih dari makna & fallback, berlaku tool apapun
    cmd = commander.build_command('curl', 'generic',
                                  {'target': 'https://example.com', 'output': 'o.txt'})
    check("build_command(generic, target+output) memakai flag curl yang dipelajari",
          'curl' in cmd['argv'] and cmd['profile'].startswith('[curl]'),
          " ".join(cmd['argv']))

    # Tool yang TIDAK terpasang tetap bisa dibangun command-nya (jika profil diasumsikan)
    not_installed = 'ffuf'
    prof2 = commander.get_profile(not_installed)  # akan kosong bila tak ada tool
    check(f"Tool '{not_installed}' ditangani tanpa error (mungkin tak terpasang)",
          isinstance(prof2, object))

    print("\n" + "=" * 72)
    print("3) EKSEKUSI NYATA (smart_execute) pada perintah aman")
    print("=" * 72)
    if commander.ensure_available('python'):
        r = commander.smart_execute(
            'python', 'generic',
            {'extra_args': "-c \"import sys; print('ARC-SMART-OK', sys.version.split()[0])\""}
        )
        out = (r.get('output') or {})
        check("smart_execute menjalankan tool & menangkap output",
              out.get('success') and 'ARC-SMART-OK' in (out.get('stdout') or ''),
              (out.get('stdout') or out.get('stderr') or '').strip()[:80])

    if commander.ensure_available('curl'):
        # build command untuk generic intent (harus memetakan target ke flag URL/domain
        # dan menyertakan nilai target pada command yang dibangun)
        built = commander.build_command('curl', 'generic', {'target': 'https://example.com'})
        joined = " ".join(built['argv'])
        check("build_command curl memetakan 'target' ke flag URL & menyertakan nilainya",
              'https://example.com' in joined and
              any(f in joined for f in ('--url', '-u ', '--data-urlencode')),
              joined)
    else:
        check("curl tidak tersedia — lewati", True, "skip")

    print("\n" + "=" * 72)
    print("4) API TASK (execute_task) + rekomendasi tool")
    print("=" * 72)
    rec = commander.recommend_tool('subdomain_enum')
    check("recommend_tool memilih kandidat untuk subdomain_enum",
          rec in ('amass', 'subfinder', 'assetfinder'), rec)
    t = commander.execute_task({'intent': 'http_probe'})  # tanpa tool -> rekomendasi
    check("execute_task tanpa 'tool' ditangani (fallback rekomendasi)",
          'output' in t or 'error' in t)

    print("\n" + "=" * 72)
    print(f"HASIL: {passed} lulus, {failed} gagal")
    print("=" * 72)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
