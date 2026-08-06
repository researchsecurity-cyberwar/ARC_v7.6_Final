"""
Feedback Loop - Belajar dari kesalahan dan keberhasilan
"""

import time
import json
import os
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class FeedbackRecord:
    feedback_id: str
    experience_id: str
    feedback_type: str
    timestamp: float
    original_outcome: str
    actual_outcome: str
    context: Dict[str, Any]
    correction_data: Dict[str, Any]
    impact_score: float
    applied: bool = False


class FeedbackLoop:
    """Mekanisme feedback loop untuk belajar dari kesalahan dan keberhasilan"""
    
    def __init__(self, storage_dir="~/.arc/feedback"):
        self.storage_dir = os.path.expanduser(storage_dir)
        os.makedirs(self.storage_dir, exist_ok=True)
        self.feedback_records: List[FeedbackRecord] = []
        self.pending_feedback: List[FeedbackRecord] = []
    
    def record_feedback(self, experience_id: str, feedback_type: str,
                       original_outcome: str, actual_outcome: str,
                       context: Dict[str, Any], correction_data: Dict[str, Any],
                       impact_score: float = 1.0) -> str:
        """Rekam feedback untuk experience tertentu"""
        feedback_id = f"fb_{int(time.time())}_{len(self.feedback_records)}"
        
        feedback = FeedbackRecord(
            feedback_id=feedback_id,
            experience_id=experience_id,
            feedback_type=feedback_type,
            timestamp=time.time(),
            original_outcome=original_outcome,
            actual_outcome=actual_outcome,
            context=context,
            correction_data=correction_data,
            impact_score=impact_score
        )
        
        self.feedback_records.append(feedback)
        if impact_score >= 0.5:
            self.pending_feedback.append(feedback)
        
        return feedback_id
    
    def analyze_feedback_patterns(self) -> Dict[str, Any]:
        """Analisis pola dari feedback yang diterima"""
        if not self.feedback_records:
            return {'error': 'No feedback records'}
        
        total = len(self.feedback_records)
        success = len([fb for fb in self.feedback_records if fb.feedback_type == 'success'])
        failure = len([fb for fb in self.feedback_records if fb.feedback_type == 'failure'])
        
        return {
            'total_feedback': total,
            'success_feedback': success,
            'failure_feedback': failure,
            'pending_corrections': len(self.pending_feedback)
        }
    
    def get_corrections_to_apply(self, min_impact: float = 0.5) -> List[Dict]:
        """Dapatkan koreksi yang perlu diterapkan"""
        corrections = []
        for fb in self.pending_feedback:
            if not fb.applied and fb.impact_score >= min_impact:
                corrections.append({
                    'feedback_id': fb.feedback_id,
                    'correction': fb.correction_data,
                    'impact_score': fb.impact_score
                })
        corrections.sort(key=lambda x: x['impact_score'], reverse=True)
        return corrections
    
    def apply_correction(self, feedback_id: str) -> Dict[str, Any]:
        """Terapkan koreksi dari feedback"""
        result = {'feedback_id': feedback_id, 'applied': False}
        
        for fb in self.feedback_records:
            if fb.feedback_id == feedback_id and not fb.applied:
                fb.applied = True
                if fb in self.pending_feedback:
                    self.pending_feedback.remove(fb)
                result['applied'] = True
                break
        
        return result
    
    def learn_from_mistakes(self) -> Dict[str, Any]:
        """Belajar dari kesalahan yang terjadi"""
        failures = [fb for fb in self.feedback_records if fb.feedback_type == 'failure']
        
        if not failures:
            return {'message': 'No failures to learn from'}
        
        lessons = []
        for fb in failures:
            lessons.append({
                'experience_id': fb.experience_id,
                'mistake': f"Expected {fb.original_outcome}, got {fb.actual_outcome}",
                'correction': fb.correction_data
            })
        
        return {'total_mistakes': len(failures), 'lessons': lessons}
    
    def save_feedback(self):
        """Simpan feedback ke disk"""
        try:
            data = [fb.__dict__ for fb in self.feedback_records]
            filepath = os.path.join(self.storage_dir, "feedback.json")
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save feedback: {e}")
    
    def load_feedback(self):
        """Muat feedback dari disk"""
        try:
            filepath = os.path.join(self.storage_dir, "feedback.json")
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    self.feedback_records = [FeedbackRecord(**fb) for fb in data]
        except Exception as e:
            print(f"Failed to load feedback: {e}")
