# -*- coding: utf-8 -*-
"""
Test sementara untuk COGNITIVE_CORE/sovereign_reasoner.py
Memakai fake llama_cpp sehingga bisa dijalankan tanpa GPU/model asli.
"""
import os
import shutil
import sys
import tempfile

# 1) Fake llama_cpp - dipasang sebelum import modul
FAKE_LLAMA_CALLS = []


class FakeLlama:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, prompt, max_tokens, temperature, top_p, repeat_penalty):
        FAKE_LLAMA_CALLS.append((prompt, max_tokens))
        return {"choices": [{"text": f"FAKE>>{prompt[:30]}... (max_tokens={max_tokens})"}]}


sys.modules["llama_cpp"] = type(sys)("llama_cpp")
sys.modules["llama_cpp"].Llama = FakeLlama

from COGNITIVE_CORE.sovereign_reasoner import SovereignReasoner  # noqa: E402

passed = 0
failed = 0


def check(name, cond, extra=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS: {name}")
    else:
        failed += 1
        print(f"  FAIL: {name} {extra}")


# 2) Siapkan direktori model palsu
tmp = tempfile.mkdtemp(prefix="arc_test_models_")
model_conf = os.path.join(tmp, "config.yaml")
try:
    models_dir = os.path.join(tmp, "models")
    os.makedirs(models_dir, exist_ok=True)

    print("== Test 1: explicit model_path ==")
    explicit_model = os.path.join(models_dir, "explicit.gguf")
    open(explicit_model, "wb").write(b"dummy")
    sr = SovereignReasoner(model_path=explicit_model)
    check("is_ready dengan explicit path", sr.is_ready, sr.status())
    check("path tersimpan", sr.model_path == explicit_model, sr.model_path)
    check("n_threads auto-detect", isinstance(sr._n_threads, int) and sr._n_threads >= 1, sr._n_threads)

    print("== Test 2: env var ARC_LLM_MODEL_PATH ==")
    env_model = os.path.join(models_dir, "env_model.gguf")
    open(env_model, "wb").write(b"dummy")
    os.environ["ARC_LLM_MODEL_PATH"] = env_model
    sr2 = SovereignReasoner()
    check("is_ready via env var", sr2.is_ready, sr2.status())
    check("path dari env var", sr2.model_path == env_model, sr2.model_path)
    del os.environ["ARC_LLM_MODEL_PATH"]

    print("== Test 3: auto-discovery + ARC_LLM_MODEL_DIRS ==")
    discover_model = os.path.join(models_dir, "z_discover.gguf")
    open(discover_model, "wb").write(b"dummy")
    os.environ["ARC_LLM_MODEL_DIRS"] = models_dir
    sr3 = SovereignReasoner()
    check("is_ready via auto-discovery", sr3.is_ready, sr3.status())
    check("path dari auto-discovery", sr3.model_path is not None and sr3.model_path.startswith(models_dir) and sr3.model_path.endswith(".gguf"), sr3.model_path)
    found = sr3._discover_models()
    check("_discover_models menemukan file", any(m for m in found if m.endswith("z_discover.gguf")), found[:3])
    del os.environ["ARC_LLM_MODEL_DIRS"]

    print("== Test 4: model tidak ditemukan (fallback) ==")
    sr4 = SovereignReasoner(model_path=os.path.join(models_dir, "nope.gguf"))
    check("fallback saat model tidak ada", not sr4.is_ready and sr4.llm is None)

    print("== Test 5: require_model=True melempar FileNotFoundError ==")
    try:
        SovereignReasoner(model_path=os.path.join(models_dir, "nope.gguf"), require_model=True)
        check("require_model melempar FileNotFoundError", False)
    except FileNotFoundError as e:
        check("require_model melempar FileNotFoundError", "Model AI tidak ditemukan" in str(e), e)

    print("== Test 6: config yaml ~/.arc/config.yaml ==")
    arc_cfg_dir = os.path.expanduser("~/.arc")
    backup = None
    cfg_file_full = os.path.join(arc_cfg_dir, "config.yaml")
    if os.path.exists(cfg_file_full):
        backup = open(cfg_file_full, "rb").read()
    os.makedirs(arc_cfg_dir, exist_ok=True)
    cfg_model = os.path.join(models_dir, "cfg_model.gguf")
    open(cfg_model, "wb").write(b"dummy")
    with open(cfg_file_full, "w", encoding="utf-8") as fh:
        fh.write(f"llm:\n  model_path: \"{cfg_model.replace(os.sep, '/')}\"\n")
    sr5 = SovereignReasoner()
    check("is_ready via config yaml", sr5.is_ready, sr5.status())
    check("path dari config yaml", sr5.model_path == cfg_model, sr5.model_path)

    # Path Windows ber-backslash -> fallback parse manual harus menanganinya
    with open(cfg_file_full, "w", encoding="utf-8") as fh:
        fh.write(f"llm:\n  model_path: \"{cfg_model}\"\n")
    sr5b = SovereignReasoner()
    check("config yaml backslash (fallback parse)", sr5b.model_path == cfg_model, sr5b.model_path if sr5b.model_path else sr5b.status())

    if backup is not None:
        with open(cfg_file_full, "wb") as fh:
            fh.write(backup)
    else:
        os.remove(cfg_file_full)

    print("== Test 7: _complete / analyze_vulnerability / generate_report_section ==")
    sr6 = SovereignReasoner(model_path=os.path.join(models_dir, "explicit.gguf"))
    txt = sr6._complete("Hello model", max_tokens=64)
    check("_complete mengembalikan teks", txt.startswith("FAKE>>"), txt[:60])

    analysis = sr6.analyze_vulnerability("https://target.local/api?id=1", "IDOR")
    check("analyze_vulnerability berjalan", "FAKE>>" in analysis, analysis[:80])

    report = sr6.generate_report_section("Temuan IDOR di endpoint /api/v1/user")
    check("generate_report_section berjalan", "FAKE>>" in report, report[:80])

finally:
    shutil.rmtree(tmp, ignore_errors=True)

print(f"\nRESULT: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)