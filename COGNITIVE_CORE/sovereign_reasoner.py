import argparse
import json
import os

try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except Exception as e:  # ImportError ATAU native library (.so/.dll) gagal di-load
    Llama = None
    LLAMA_CPP_AVAILABLE = False
    print(f"WARNING: llama-cpp-python tidak tersedia ({e}) - SovereignReasoner akan berjalan dalam mode fallback")

# Path default (dipakai hanya jika semua sumber lain tidak menemukan model)
DEFAULT_MODEL_PATH = "~/.arc/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"

# Direktori yang di-scan otomatis untuk mencari file *.gguf
MODEL_CANDIDATE_DIRS = [
    "~/.arc/models",
    "~/models",
    "~/.cache/llama.cpp/models",
    "~/.local/share/llama.cpp/models",
    "./models",
    "/usr/share/llama.cpp/models",
    "/opt/llama.cpp/models",
]


def _env_int(name: str, default: int) -> int:
    """Baca integer dari environment variable, fallback ke `default` bila gagal."""
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return default


def _env_bool(name: str, default: bool = False) -> bool:
    """Baca boolean dari environment variable ("1/true/yes/on")."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


class SovereignReasoner:
    """
    Elite-grade reasoning engine via llama.cpp (model GGUF: Mistral, Llama 3, Qwen, dll).
    Bertindak sebagai otak strategis ARC: analisis kerentanan, perencanaan serangan
    bug bounty / CTF, dan bantuan penulisan laporan.

    Cara menentukan path model (urutan prioritas):
      1. Argumen konstruktor          model_path="..."
      2. Environment variable         ARC_LLM_MODEL_PATH=/path/ke/model.gguf
      3. Config file                  ~/.arc/config.yaml  ->  llm.model_path
      4. Auto-discovery               *.gguf di direktori model umum
      5. Path default                 ~/.arc/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
    """

    def __init__(
        self,
        model_path: str = None,
        n_ctx: int = None,
        n_threads: int = None,
        n_gpu_layers: int = None,
        verbose: bool = None,
        temperature: float = None,
        require_model: bool = False,
    ):
        self.model_path = None
        self.llm = None
        self.model_name = "unknown"
        self.loaded = False

        # Konfigurasi runtime (bisa override lewat env var)
        self._n_ctx = n_ctx if n_ctx is not None else _env_int("ARC_LLM_N_CTX", 4096)
        self._n_threads = n_threads if n_threads is not None else _env_int("ARC_LLM_N_THREADS", os.cpu_count() or 4)
        self._n_gpu_layers = n_gpu_layers if n_gpu_layers is not None else _env_int("ARC_LLM_GPU_LAYERS", 0)
        self._verbose = verbose if verbose is not None else _env_bool("ARC_LLM_VERBOSE", False)
        self._temperature = temperature if temperature is not None else float(os.environ.get("ARC_LLM_TEMPERATURE", "0.7"))

        if not LLAMA_CPP_AVAILABLE:
            print("⚠️ SovereignReasoner dalam mode fallback (llama-cpp-python belum terpasang).")
            print("   Install di Kali Linux dengan:  pip install llama-cpp-python")
            return

        # Resolusi path model sesuai urutan prioritas di atas
        resolved = self._resolve_model_path(model_path)

        if resolved is None or not os.path.exists(resolved):
            message = self._model_missing_message(resolved)
            if require_model:
                raise FileNotFoundError(message)
            print(f"⚠️ {message}")
            return

        self.model_path = resolved
        self.model_name = os.path.basename(resolved)

        print(f"🧠 Initializing Sovereign Reasoner: {self.model_name}")
        self.llm = Llama(
            model_path=self.model_path,
            n_ctx=self._n_ctx,          # Panjang konteks memori
            n_threads=self._n_threads,  # Auto-detect jumlah core CPU
            n_gpu_layers=self._n_gpu_layers,  # 0 = CPU only (lebih stabil)
            verbose=self._verbose,
        )
        self.loaded = True
        print(f"✅ Sovereign Reasoner siap untuk tactical analysis. (threads={self._n_threads}, gpu_layers={self._n_gpu_layers})")

    # ------------------------------------------------------------------ #
    # Resolusi & deteksi model
    # ------------------------------------------------------------------ #
    def _resolve_model_path(self, explicit):
        """Temukan path model: argumen > env var > config yaml > auto-discovery > default."""
        if explicit:
            return os.path.expanduser(explicit)

        env_path = os.environ.get("ARC_LLM_MODEL_PATH")
        if env_path and os.path.exists(os.path.expanduser(env_path)):
            return os.path.expanduser(env_path)

        cfg_path = self._load_config_model_path()
        if cfg_path and os.path.exists(cfg_path):
            return cfg_path

        found = self._discover_models()
        if found:
            return found[0]

        return os.path.expanduser(DEFAULT_MODEL_PATH)

    def _load_config_model_path(self):
        """Baca path model dari ~/.arc/config.yaml bagian `llm.model_path`."""
        cfg_file = os.path.expanduser("~/.arc/config.yaml")
        if not os.path.exists(cfg_file):
            return None
        raw_value = None
        try:
            with open(cfg_file, "r", encoding="utf-8") as fh:
                content = fh.read()
            try:
                import yaml
                cfg = yaml.safe_load(content) or {}
                raw_value = (cfg.get("llm") or {}).get("model_path")
            except Exception:
                # Fallback manual: parse baris per baris (mis. path Windows ber-backslash
                # yang dianggap escape oleh YAML double-quoted string).
                for line in content.splitlines():
                    stripped = line.strip()
                    if stripped.startswith("model_path:"):
                        raw_value = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                        break
            if raw_value:
                return os.path.normpath(os.path.expanduser(raw_value))
        except Exception:
            pass
        return None

    def _discover_models(self):
        """Scan direktori model umum + ARC_LLM_MODEL_DIRS untuk file *.gguf."""
        dirs_to_scan = list(MODEL_CANDIDATE_DIRS)
        extra = os.environ.get("ARC_LLM_MODEL_DIRS", "")
        if extra:
            # Pisahkan list direktori sesuai platform:
            # Windows pakai ';' (biarkan ':' milik huruf drive seperti C:\...),
            # Linux/macOS pakai ':' (standar PATH).
            separator = ";" if os.name == "nt" else ":"
            for chunk in extra.split(separator):
                if chunk.strip():
                    dirs_to_scan.append(chunk.strip())
        found = []
        seen = set()
        for directory in dirs_to_scan:
            dir_path = os.path.expanduser(directory)
            if not os.path.isdir(dir_path):
                continue
            try:
                for name in sorted(os.listdir(dir_path)):
                    if name.lower().endswith(".gguf"):
                        full = os.path.join(dir_path, name)
                        if full not in seen:
                            seen.add(full)
                            found.append(full)
            except OSError:
                continue
        return found

    def _model_missing_message(self, resolved):
        """Buat pesan bantuan yang jelas ketika model tidak ditemukan."""
        lines = [
            f"Model AI tidak ditemukan di: {resolved}",
            "Cara perbaiki (pilih salah satu):",
            "  1) export ARC_LLM_MODEL_PATH=/path/ke/model.gguf",
            "  2) python COGNITIVE_CORE/sovereign_reasoner.py --model /path/ke/model.gguf --interactive",
            "  3) Letakkan file .gguf di ~/.arc/models/",
        ]
        discovered = self._discover_models()
        if discovered:
            lines.append("Model .gguf terdeteksi di direktori model:")
            for path in discovered:
                lines.append(f"      - {path}")
        else:
            dirs = ", ".join(os.path.expanduser(d) for d in MODEL_CANDIDATE_DIRS[:3])
            lines.append(f"Direktori model yang dicek: {dirs}")
            lines.append("Download contoh model: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF")
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    # Status
    # ------------------------------------------------------------------ #
    @property
    def is_ready(self):
        """True jika model berhasil dimuat dan siap dipakai."""
        return self.llm is not None and self.loaded

    def status(self):
        """Ringkasan status LLM untuk debugging."""
        if not self.is_ready:
            return {
                "ready": False,
                "reason": "llama_cpp_missing" if not LLAMA_CPP_AVAILABLE else "model_not_found",
            }
        return {
            "ready": True,
            "model": self.model_name,
            "path": self.model_path,
            "n_ctx": self._n_ctx,
            "n_threads": self._n_threads,
            "n_gpu_layers": self._n_gpu_layers,
            "temperature": self._temperature,
        }

    # ------------------------------------------------------------------ #
    # Inti inference (aman di semua mode)
    # ------------------------------------------------------------------ #
    def _complete(self, prompt, max_tokens=512, temperature=None, top_p=0.95,
                  repeat_penalty=1.1, fallback=""):
        """Generate teks dari prompt. Aman dipanggil dalam fallback mode."""
        if not self.is_ready:
            return fallback
        try:
            response = self.llm(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature if temperature is not None else self._temperature,
                top_p=top_p,
                repeat_penalty=repeat_penalty,
            )
            return response["choices"][0]["text"].strip()
        except Exception as e:
            print(f"⚠️ AI generation error: {e}")
            return fallback
    
    def analyze_vulnerability(self, target_info, vulnerability_type):
        """
        Menganalisis kerentanan spesifik pada target.
        """
        if not self.is_ready:
            return "⚠️ AI reasoning not available - llama_cpp tidak terpasang / model tidak ditemukan. Gunakan static analysis fallback."

        prompt = f"""[INST]
You are an elite cybersecurity researcher working on an authorized bug bounty program.
Analyze the following potential vulnerability:

Target Info: {target_info}
Vulnerability Type: {vulnerability_type}

Provide a technical analysis including:
1. Potential exploitation path.
2. Business impact estimation.
3. Recommended proof-of-concept steps.
Keep the response professional and technical.
[/INST]"""

        return self._complete(
            prompt,
            max_tokens=1024,
            temperature=0.7,
            top_p=0.95,
            repeat_penalty=1.1,
            fallback="⚠️ AI reasoning output tidak tersedia (fallback).",
        )
    
    def generate_report_section(self, finding_details):
        """
        Membantu menulis bagian teknis dari laporan bug bounty.
        """
        if not self.is_ready:
            return "⚠️ AI report generation not available - llama_cpp tidak terpasang / model tidak ditemukan. Gunakan template fallback."

        prompt = f"""[INST]
Draft a professional 'Technical Description' section for a bug bounty report based on these details:
{finding_details}

Use clear, concise, and professional language suitable for a CSIRT team.
[/INST]"""

        return self._complete(
            prompt,
            max_tokens=512,
            fallback="⚠️ AI report output tidak tersedia (fallback).",
        )


# ------------------------------------------------------------------ #
# CLI - untuk menguji model AI yang sudah didownload
# ------------------------------------------------------------------ #
def _cli_interactive(reasoner):
    """Loop chat sederhana untuk menguji model."""
    print("\n" + "=" * 60)
    print("  SOVEREIGN REASONER - Interactive Mode")
    print("=" * 60)
    if not reasoner.is_ready:
        print("⚠️ Model BELUM siap. Pakai --model /path/model.gguf atau set ARC_LLM_MODEL_PATH.")
        print("   (Fallback static analysis digunakan untuk metode analisis.)\n")
    else:
        print(f"✅ Model: {reasoner.model_name}")
        print(f"   Path : {reasoner.model_path}\n")
    print("Ketik prompt untuk bertanya (exit/quit untuk keluar):\n")

    while True:
        try:
            user_input = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSampai jumpa.")
            break
        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q", "keluar", "exit()"):
            break
        if user_input.lower() in ("status", "info"):
            print(json.dumps(reasoner.status(), indent=2))
            continue
        print(reasoner._complete(user_input, max_tokens=1024))
        print()


def main():
    parser = argparse.ArgumentParser(
        description="SovereignReasoner - Cognitive Core ARC (llama.cpp). "
                    "Cara cek model: python COGNITIVE_CORE/sovereign_reasoner.py --status"
    )
    parser.add_argument("--model", "-m", default=None, help="Path ke file model .gguf")
    parser.add_argument("--interactive", "-i", action="store_true", help="Mode chat interaktif")
    parser.add_argument("--prompt", "-p", default=None, help="Prompt sekali-jalan (single shot)")
    parser.add_argument("--analyze", action="store_true", help="Demo analisis kerentanan")
    parser.add_argument("--report", action="store_true", help="Demo penulisan laporan")
    parser.add_argument("--list-models", action="store_true", help="Tampilkan model .gguf yang terdeteksi")
    parser.add_argument("--status", action="store_true", help="Tampilkan status LLM")
    parser.add_argument("--n-ctx", type=int, default=None, dest="n_ctx", help="Panjang konteks (token)")
    parser.add_argument("--threads", type=int, default=None, dest="n_threads", help="Jumlah CPU thread")
    parser.add_argument("--gpu-layers", type=int, default=None, dest="n_gpu_layers", help="Layer GPU yang dioffload (0 = CPU only)")
    args = parser.parse_args()

    if args.list_models:
        probe = SovereignReasoner()
        found = probe._discover_models()
        if not found:
            print("Tidak ada model .gguf terdeteksi. Set ARC_LLM_MODEL_PATH atau letakkan di ~/.arc/models/")
        else:
            print("Model .gguf yang terdeteksi:")
            for path in found:
                print(f"  - {path}")
        return

    reasoner = SovereignReasoner(
        model_path=args.model,
        n_ctx=args.n_ctx,
        n_threads=args.n_threads,
        n_gpu_layers=args.n_gpu_layers,
    )

    if args.status:
        print(json.dumps(reasoner.status(), indent=2))

    if args.prompt:
        print(reasoner._complete(args.prompt, max_tokens=1024))

    if args.analyze:
        print("\n--- DEMO: analyze_vulnerability ---")
        print(reasoner.analyze_vulnerability(
            "https://example.com/api/v1/user?id=1",
            "IDOR (Insecure Direct Object Reference)",
        ))

    if args.report:
        print("\n--- DEMO: generate_report_section ---")
        print(reasoner.generate_report_section(
            "IDOR di endpoint /api/v1/user memungkinkan akses data pengguna lain tanpa otorisasi."
        ))

    if args.interactive:
        _cli_interactive(reasoner)

    if not any([args.interactive, args.prompt, args.analyze, args.report, args.status]):
        parser.print_help()


if __name__ == "__main__":
    main()