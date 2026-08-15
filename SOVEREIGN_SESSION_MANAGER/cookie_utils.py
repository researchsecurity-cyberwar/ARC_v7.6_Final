"""Utility parsing & penerapan cookie ke sesi HTTP (ARC).

Menyatukan cara SEMUA scraper membaca kredensial ``session_cookie`` dari
config.yaml / confiq.yaml, sehingga formatnya konsisten antar platform.

Format yang didukung:
1. Raw cookie-string:   ``"nama1=value1; nama2=value2; ..."``
   (format yang dipakai config.example.yaml, mis. "SID=...; HSID=...")
2. Nilai tunggal:       ``"value_saja"``
   (kompatibilitas mundur: jika tidak ada '=', cookie dipasang dengan nama
   ``default`` yang diberikan -- menjaga perilaku lama scraper tertentu).

Catatan URL-encoding:
- Nilai cookie (mis. connect.sid ``s:<sid>.<sig>`` atau Laravel ``eyJpdiI6%3D``)
  dibiarkan apa adanya; requests/urllib akan mengurus encoding saat dikirim.
- JANGAN de-encode di sini agar signature/value tidak rusak.
"""
from typing import Dict, Optional


def parse_cookie_string(raw: str) -> Dict[str, str]:
    """Parse raw cookie-string ``'nama=value; nama2=value2'`` menjadi dict.

    Jika ``raw`` tidak mengandung ``=`` sama sekali (nilai tunggal / JWT mentah /
    token polos), dikembalikan dict kosong agar caller memakai jalur ``default``.
    """
    if not raw:
        return {}
    cookies: Dict[str, str] = {}
    for chunk in raw.split(';'):
        chunk = chunk.strip()
        if not chunk:
            continue
        if '=' in chunk:
            name, _, value = chunk.partition('=')
            name = name.strip()
            value = value.strip()
            if name:
                cookies[name] = value
    return cookies


def set_cookie_string(session, raw: str, default: Optional[str] = None) -> int:
    """Terapkan cookie-string ``raw`` ke ``session`` (objek requests.Session).

    Urutan:
    - Jika raw berbentuk ``nama=value; ...``  -> set semua pasangan (biasa dipakai
      platform yang butuh session + xsrf sekaligus, mis. Immunefi, Google).
    - Jika raw adalah nilai tunggal (tanpa '=') -> set sebagai cookie ``default``
      (kompatibilitas nilai-only lama, mis. BugCrowd / HTB / THM).

    Mengembalikan jumlah cookie yang berhasil terpasang.
    """
    parsed = parse_cookie_string(raw)
    if parsed:
        for name, value in parsed.items():
            session.cookies.set(name, value)
        return len(parsed)
    if default and raw:
        session.cookies.set(default, raw)
        return 1
    return 0


# Pemetaan nama header XSRF/CSRF per platform (dipakai untuk aksi POST/submit).
# Platform CTF (HTB/THM) dan Google umumnya tidak butuh header ini pada GET.
XSRF_HEADER_BY_PLATFORM = {
    "hackerone": "X-CSRF-Token",
    "bugcrowd": "X-CSRF-Token",
    "yeswehack": "X-CSRF-Token",
    "intigriti": "X-XSRF-TOKEN",
    "immunefi": "X-CSRF-Token",
}


def set_xsrf_token(session, token, platform=None, header=None) -> bool:
    """Set header XSRF/CSRF dari field opsional ``xsrf_token`` di config.

    Header yang dipakai tergantung platform:
      HackerOne / BugCrowd / YesWeHack / Immunefi -> X-CSRF-Token
      Intigriti                                   -> X-XSRF-TOKEN
    Bisa dipaksa dengan argumen ``header`` bila platform berbeda.

    Mengembalikan True jika sebuah header berhasil dipasang.
    """
    if not token:
        return False
    hname = header or XSRF_HEADER_BY_PLATFORM.get((platform or "").strip().lower())
    if not hname:
        return False
    session.headers[hname] = token
    return True
