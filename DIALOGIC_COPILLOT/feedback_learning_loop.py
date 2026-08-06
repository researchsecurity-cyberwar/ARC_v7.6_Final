import json
import os
from datetime import datetime

class FeedbackLearningLoop:
    """
    Your validation → updates confidence thresholds.
    Memperbarui ambang batas kepercayaan berdasarkan validasi pengguna.
    """
    
    def __init__(self, learning_dir="~/.arc/learning"):
        self.learning_dir = os.path.expanduser(learning_dir)
        os.makedirs(self.learning_dir, exist_ok=True)
        self.confidence_thresholds = self._load_confidence_thresholds()
    
    def process_feedback(self, finding_id: str, user_validation: dict):
        """
        Proses umpan balik validasi dari pengguna.
        """
        feedback_record = {
            'finding_id': finding_id,
            'user_validation': user_validation,
            'timestamp': datetime.now().isoformat(),
            'impact_on_thresholds': self._calculate_threshold_impact(user_validation)
        }
        
        # Simpan catatan umpan balik
        feedback_file = os.path.join(self.learning_dir, f"feedback_{finding_id}.json")
        with open(feedback_file, 'w') as f:
            json.dump(feedback_record, f, indent=2)
        
        # Perbarui ambang batas kepercayaan
        self._update_confidence_thresholds(feedback_record['impact_on_thresholds'])
        
        return {
            'feedback_processed': True,
            'finding_id': finding_id,
            'threshold_updates': feedback_record['impact_on_thresholds'],
            'learning_applied': True
        }
    
    def _calculate_threshold_impact(self, validation: dict) -> dict:
        """Hitung dampak pada ambang batas kepercayaan."""
        impact = {}
        finding_type = validation.get('finding_type', 'unknown')
        was_correct = validation.get('correct', False)
        confidence_score = validation.get('confidence_score', 0.5)
        
        # Sesuaikan ambang batas berdasarkan akurasi
        if was_correct:
            # Jika benar, turunkan ambang batas sedikit (lebih percaya diri)
            impact[f'{finding_type}_threshold'] = -0.05
        else:
            # Jika salah, naikkan ambang batas (lebih hati-hati)
            impact[f'{finding_type}_threshold'] = 0.1
        
        # Batasi perubahan
        for key in impact:
            impact[key] = max(-0.2, min(0.2, impact[key]))
        
        return impact
    
    def _update_confidence_thresholds(self, threshold_impacts: dict):
        """Perbarui ambang batas kepercayaan."""
        for threshold_key, adjustment in threshold_impacts.items():
            current_value = self.confidence_thresholds.get(threshold_key, 0.7)
            new_value = max(0.3, min(0.95, current_value + adjustment))
            self.confidence_thresholds[threshold_key] = new_value
        
        # Simpan ke file
        thresholds_file = os.path.join(self.learning_dir, "confidence_thresholds.json")
        with open(thresholds_file, 'w') as f:
            json.dump(self.confidence_thresholds, f, indent=2)
    
    def _load_confidence_thresholds(self) -> dict:
        """Muat ambang batas kepercayaan dari file."""
        thresholds_file = os.path.join(self.learning_dir, "confidence_thresholds.json")
        if os.path.exists(thresholds_file):
            with open(thresholds_file, 'r') as f:
                return json.load(f)
        else:
            # Nilai default
            return {
                'xss_threshold': 0.7,
                'sqli_threshold': 0.7,
                'ssrf_threshold': 0.7,
                'idor_threshold': 0.7,
                'rce_threshold': 0.8,
                'lfi_threshold': 0.7,
                'csrf_threshold': 0.6
            }
    
    def get_confidence_threshold(self, finding_type: str) -> float:
        """Dapatkan ambang batas kepercayaan untuk tipe temuan."""
        return self.confidence_thresholds.get(f'{finding_type}_threshold', 0.7)