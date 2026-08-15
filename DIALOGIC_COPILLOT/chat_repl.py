# -*- coding: utf-8 -*-
"""
ARC Chat REPL — chat dengan ARC langsung dari terminal (tanpa browser).

Cara jalan:
    python DIALOGIC_COPILLOT/chat_repl.py
    ketik 'exit' / 'quit' / Ctrl+C untuk keluar.

Menggunakan ArcChatEngine yang sama dengan WebUI -> data brief & percakapan
tersimpan konsisten di ~/.arc.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from DIALOGIC_COPILLOT.arc_chat_engine import ArcChatEngine  # noqa: E402


def run_repl(engine: ArcChatEngine):
    """Loop chat terminal (blocking). Dipakai oleh chat_repl maupun arc_main --chat."""
    print("=" * 56)
    print("  ARC Chat v7.6 (terminal) — tukar informasi bug bounty")
    print("  Ketik /bantuan untuk daftar perintah, 'exit' untuk keluar.")
    print("=" * 56)

    while True:
        conv = engine.conversation.current_conversation
        cur = conv["target_domain"] if conv else None
        prompt = f"[{cur or 'belum ada'}] Kamu> "
        try:
            msg = input("\n" + prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSampai jumpa!")
            break
        if not msg:
            continue
        if msg.lower() in ("exit", "quit", "keluar", "bye"):
            print("ARC> Sampai jumpa! 👋")
            break
        print("ARC> " + engine.handle(msg))


def main():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    engine = ArcChatEngine()
    run_repl(engine)


if __name__ == "__main__":
    main()
