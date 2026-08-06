"""
Experience Collector - Mengumpulkan data dari eksekusi nyata
"""

import json
import time
import os
from typing import Dict, List, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


class ExperienceType(Enum):
    VULNERABILITY_SCAN = "vulnerability_scan"
    EXPLOITATION_ATTEMPT = "exploitation_attempt"
    CTF_CHALLENGE = "ctf_challenge"
    BUG_BOUNTY_SUBMISSION = "bug_bounty_submission"
    PLAYBOOK_EXECUTION = "playbook_execution"


class OutcomeType(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL_SUCCESS = "partial_success"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class Experience:
    experience_id: str
    experience_type: str
    outcome: str
    timestamp: float
    context: Dict[str, Any]
    actions_taken: List[Dict[str, Any]]
    result_data: Dict[str, Any]
    lessons_learned: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)


class ExperienceCollector:
    """Mengumpulkan experience data dari eksekusi nyata agent"""
    
    def __init__(self, storage_dir="~/.arc/experiences"):
        self.storage_dir = os.path.expanduser(storage_dir)
        os.makedirs(self.storage_dir, exist_ok=True)
        self.experiences: List[Experience] = []
        self.load_persistent_experiences()
    
    def record_experience(self, experience_type: str, outcome: str, 
                         context: Dict[str, Any], actions_taken: List[Dict],
                         result_data: Dict[str, Any], lessons_learned: List[str] = None,
                         metadata: Dict[str, Any] = None) -> str:
        """Rekam experience baru"""
        experience_id = f"exp_{int(time.time())}_{len(self.experiences)}"
        
        experience = Experience(
            experience_id=experience_id,
            experience_type=experience_type,
            outcome=outcome,
            timestamp=time.time(),
            context=context,
            actions_taken=actions_taken,
            result_data=result_data,
            lessons_learned=lessons_learned or [],
            metadata=metadata or {}
        )
        
        self.experiences.append(experience)
        
        if len(self.experiences) % 10 == 0:
            self.save_experiences()
        
        return experience_id
    
    def get_successful_experiences(self, experience_type: str = None) -> List[Experience]:
        """Dapatkan experience yang sukses"""
        successful = [exp for exp in self.experiences if exp.outcome == OutcomeType.SUCCESS.value]
        if experience_type:
            successful = [exp for exp in successful if exp.experience_type == experience_type]
        return successful
    
    def get_failed_experiences(self, experience_type: str = None) -> List[Experience]:
        """Dapatkan experience yang gagal"""
        failed = [exp for exp in self.experiences if exp.outcome == OutcomeType.FAILURE.value]
        if experience_type:
            failed = [exp for exp in failed if exp.experience_type == experience_type]
        return failed
    
    def analyze_patterns(self, experience_type: str = None) -> Dict[str, Any]:
        """Analisis pola dari experiences"""
        experiences = self.experiences
        if experience_type:
            experiences = [exp for exp in experiences if exp.experience_type == experience_type]
        
        if not experiences:
            return {'error': 'No experiences to analyze'}
        
        total = len(experiences)
        successful = len([exp for exp in experiences if exp.outcome == OutcomeType.SUCCESS.value])
        failed = len([exp for exp in experiences if exp.outcome == OutcomeType.FAILURE.value])
        
        return {
            'total_experiences': total,
            'successful': successful,
            'failed': failed,
            'success_rate': successful / total if total > 0 else 0.0
        }
    
    def save_experiences(self):
        """Simpan experiences ke disk"""
        try:
            data = [exp.to_dict() for exp in self.experiences]
            filepath = os.path.join(self.storage_dir, "experiences.json")
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save experiences: {e}")
    
    def load_persistent_experiences(self):
        """Muat experiences yang tersimpan"""
        try:
            filepath = os.path.join(self.storage_dir, "experiences.json")
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    self.experiences = [Experience.from_dict(exp_data) for exp_data in data]
        except Exception as e:
            print(f"Failed to load experiences: {e}")
            self.experiences = []