import os

try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    Llama = None
    LLAMA_CPP_AVAILABLE = False
    print("⚠️ llama-cpp-python tidak tersedia - SovereignReasoner akan berjalan dalam mode fallback")

class SovereignReasoner:
    """
    Elite-grade reasoning engine using Mistral-7B via llama.cpp.
    Bertindak sebagai otak strategis ARC untuk analisis kerentanan dan perencanaan serangan.
    """
    
    def __init__(self):
        # Path ke model AI yang sudah didownload di Kali Linux
        model_path = os.path.expanduser("~/.arc/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf")
        
        if not LLAMA_CPP_AVAILABLE:
            print("⚠️ SovereignReasoner initialized in fallback mode (no llama_cpp)")
            self.llm = None
            return

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model AI tidak ditemukan di: {model_path}")

        print("🧠 Initializing Sovereign Reasoner (Mistral-7B)...")
        
        # Inisialisasi LLM dengan konfigurasi optimal
        self.llm = Llama(
            model_path=model_path,
            n_ctx=4096,          # Panjang konteks memori
            n_threads=8,         # Sesuaikan dengan jumlah core CPU kamu
            n_gpu_layers=0,      # 0 = CPU only (lebih stabil)
            verbose=False        # Matikan log verbose agar output bersih
        )
        print("✅ Sovereign Reasoner is ready for tactical analysis.")
    
    def analyze_vulnerability(self, target_info, vulnerability_type):
        """
        Menganalisis kerentanan spesifik pada target.
        """
        if self.llm is None:
            return "⚠️ AI reasoning not available - llama_cpp not installed. Using static analysis fallback."
        
        prompt = f"""<s>[INST]
You are an elite cybersecurity researcher working on a authorized bug bounty program.
Analyze the following potential vulnerability:

Target Info: {target_info}
Vulnerability Type: {vulnerability_type}

Provide a technical analysis including:
1. Potential exploitation path.
2. Business impact estimation.
3. Recommended proof-of-concept steps.
Keep the response professional and technical.
[/INST]"""

        response = self.llm(
            prompt, 
            max_tokens=1024, 
            temperature=0.7, 
            top_p=0.95, 
            repeat_penalty=1.1
        )
        
        return response["choices"][0]["text"].strip()
    
    def generate_report_section(self, finding_details):
        """
        Membantu menulis bagian teknis dari laporan bug bounty.
        """
        if self.llm is None:
            return "⚠️ AI report generation not available - llama_cpp not installed. Using template fallback."
        
        prompt = f"""<s>[INST]
Draft a professional 'Technical Description' section for a bug bounty report based on these details:
{finding_details}

Use clear, concise, and professional language suitable for a CSIRT team.
[/INST]"""

        response = self.llm(prompt, max_tokens=512)
        return response["choices"][0]["text"].strip()