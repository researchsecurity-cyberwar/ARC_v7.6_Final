"""
Dynamic Knowledge Base
"""

import json
import os
import time
from typing import Dict, List, Any, Optional


class DynamicKnowledgeBase:
    """Knowledge base yang berkembang"""
    
    def __init__(self, kb_dir="~/.arc/knowledge_base"):
        self.kb_dir = os.path.expanduser(kb_dir)
        os.makedirs(self.kb_dir, exist_ok=True)
        
        self.knowledge = {
            'techniques': {},
            'patterns': {},
            'lessons': {},
            'best_practices': {},
            'failure_modes': {}
        }
        
        self.load_knowledge()
    
    def add_technique_knowledge(self, technique: str, knowledge: Dict[str, Any]):
        """Tambah pengetahuan tentang teknik"""
        if technique not in self.knowledge['techniques']:
            self.knowledge['techniques'][technique] = {
                'name': technique,
                'created_at': time.time(),
                'updated_at': time.time(),
                'success_count': 0,
                'failure_count': 0,
                'data': {}
            }
        
        tech = self.knowledge['techniques'][technique]
        tech['updated_at'] = time.time()
        tech['data'].update(knowledge)
        self.save_knowledge()
    
    def record_technique_outcome(self, technique: str, outcome: str):
        """Rekam outcome dari eksekusi teknik"""
        if technique not in self.knowledge['techniques']:
            self.add_technique_knowledge(technique, {})
        
        tech = self.knowledge['techniques'][technique]
        
        if outcome == 'success':
            tech['success_count'] += 1
        elif outcome == 'failure':
            tech['failure_count'] += 1
        
        self.save_knowledge()
    
    def get_technique_confidence(self, technique: str) -> float:
        """Dapatkan confidence score"""
        if technique not in self.knowledge['techniques']:
            return 0.5
        
        tech = self.knowledge['techniques'][technique]
        total = tech['success_count'] + tech['failure_count']
        
        if total == 0:
            return 0.5
        
        return tech['success_count'] / total
    
    def add_pattern(self, pattern_name: str, pattern_data: Dict[str, Any]):
        """Tambah pattern"""
        if pattern_name not in self.knowledge['patterns']:
            self.knowledge['patterns'][pattern_name] = {
                'name': pattern_name,
                'created_at': time.time(),
                'updated_at': time.time(),
                'occurrences': 0,
                'data': pattern_data
            }
        
        self.knowledge['patterns'][pattern_name]['occurrences'] += 1
        self.save_knowledge()
    
    def add_lesson(self, lesson: str, context: Dict[str, Any], importance: float = 0.5):
        """Tambah lesson learned"""
        lesson_id = f"lesson_{int(time.time())}"
        
        self.knowledge['lessons'][lesson_id] = {
            'lesson': lesson,
            'context': context,
            'importance': importance,
            'created_at': time.time(),
            'applied_count': 0
        }
        
        self.save_knowledge()
        return lesson_id
    
    def get_relevant_lessons(self, context: Dict[str, Any], min_importance: float = 0.3) -> List[Dict]:
        """Dapatkan lesson yang relevan"""
        relevant = []
        
        for lesson_id, lesson_data in self.knowledge['lessons'].items():
            if lesson_data['importance'] >= min_importance:
                relevant.append({
                    'lesson_id': lesson_id,
                    'lesson': lesson_data['lesson'],
                    'importance': lesson_data['importance']
                })
        
        relevant.sort(key=lambda x: x['importance'], reverse=True)
        return relevant
    
    def add_best_practice(self, practice: str, category: str, description: str):
        """Tambah best practice"""
        if category not in self.knowledge['best_practices']:
            self.knowledge['best_practices'][category] = []
        
        self.knowledge['best_practices'][category].append({
            'practice': practice,
            'description': description,
            'created_at': time.time(),
            'usage_count': 0
        })
        
        self.save_knowledge()
    
    def record_failure_mode(self, failure_type: str, context: Dict[str, Any], recovery: str):
        """Rekam failure mode"""
        if failure_type not in self.knowledge['failure_modes']:
            self.knowledge['failure_modes'][failure_type] = {
                'failure_type': failure_type,
                'occurrences': 0,
                'contexts': [],
                'recovery_strategies': []
            }
        
        failure = self.knowledge['failure_modes'][failure_type]
        failure['occurrences'] += 1
        failure['contexts'].append(context)
        
        if recovery not in failure['recovery_strategies']:
            failure['recovery_strategies'].append(recovery)
        
        self.save_knowledge()
    
    def get_recovery_strategy(self, failure_type: str) -> Optional[str]:
        """Dapatkan strategi recovery"""
        if failure_type not in self.knowledge['failure_modes']:
            return None
        
        failure = self.knowledge['failure_modes'][failure_type]
        if failure['recovery_strategies']:
            return failure['recovery_strategies'][0]
        
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Statistik knowledge base"""
        return {
            'total_techniques': len(self.knowledge['techniques']),
            'total_patterns': len(self.knowledge['patterns']),
            'total_lessons': len(self.knowledge['lessons']),
            'total_best_practices': sum(len(practices) for practices in self.knowledge['best_practices'].values()),
            'total_failure_modes': len(self.knowledge['failure_modes'])
        }
    
    def save_knowledge(self):
        """Simpan ke disk"""
        try:
            filepath = os.path.join(self.kb_dir, "knowledge_base.json")
            with open(filepath, 'w') as f:
                json.dump(self.knowledge, f, indent=2)
        except Exception as e:
            print(f"Failed to save: {e}")
    
    def load_knowledge(self):
        """Muat dari disk"""
        try:
            filepath = os.path.join(self.kb_dir, "knowledge_base.json")
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    self.knowledge.update(data)
        except Exception as e:
            print(f"Failed to load: {e}")
