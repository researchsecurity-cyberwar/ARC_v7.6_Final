import json
import os
from datetime import datetime

class DialogicMemory:
    """
    Long-term contextual memory for per-target and global sessions.
    Menyimpan riwayat interaksi dan konteks untuk setiap target.
    """
    
    def __init__(self, memory_dir="~/.arc/memory"):
        self.memory_dir = os.path.expanduser(memory_dir)
        os.makedirs(self.memory_dir, exist_ok=True)
        self.global_memory_file = os.path.join(self.memory_dir, "global_memory.json")
        self.load_global_memory()
    
    def load_global_memory(self):
        """Muat memori global dari file."""
        if os.path.exists(self.global_memory_file):
            with open(self.global_memory_file, 'r') as f:
                self.global_memory = json.load(f)
        else:
            self.global_memory = {
                "targets": {},
                "lessons_learned": [],
                "successful_strategies": []
            }
    
    def save_global_memory(self):
        """Simpan memori global ke file."""
        with open(self.global_memory_file, 'w') as f:
            json.dump(self.global_memory, f, indent=2)
    
    def get_target_memory(self, target_domain):
        """Dapatkan memori spesifik untuk target tertentu."""
        if target_domain not in self.global_memory["targets"]:
            self.global_memory["targets"][target_domain] = {
                "interactions": [],
                "vulnerabilities_found": [],
                "failed_attempts": [],
                "last_interaction": None
            }
        return self.global_memory["targets"][target_domain]
    
    def add_interaction(self, target_domain, interaction_data):
        """Tambahkan interaksi baru ke memori target."""
        target_mem = self.get_target_memory(target_domain)
        interaction_record = {
            "timestamp": datetime.now().isoformat(),
            "data": interaction_data
        }
        target_mem["interactions"].append(interaction_record)
        target_mem["last_interaction"] = datetime.now().isoformat()
        self.save_global_memory()
    
    def add_vulnerability(self, target_domain, vuln_data):
        """Catat kerentanan yang ditemukan pada target."""
        target_mem = self.get_target_memory(target_domain)
        target_mem["vulnerabilities_found"].append({
            "timestamp": datetime.now().isoformat(),
            "vulnerability": vuln_data
        })
        self.save_global_memory()
    
    def add_lesson_learned(self, lesson):
        """Tambahkan pelajaran yang dipelajari dari pengalaman."""
        self.global_memory["lessons_learned"].append({
            "timestamp": datetime.now().isoformat(),
            "lesson": lesson
        })
        self.save_global_memory()