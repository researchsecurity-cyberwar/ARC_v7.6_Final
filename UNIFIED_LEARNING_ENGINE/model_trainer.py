"""
Model Trainer - Training ML model dari collected data
Module ini menyediakan training sederhana untuk model prediksi
"""

import json
import os
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ModelMetrics:
    """Metrics untuk model evaluation"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    training_samples: int
    last_trained: float


class ModelTrainer:
    """
    Trainer untuk ML model yang belajar dari experience data
    """
    
    def __init__(self, model_dir="~/.arc/models"):
        self.model_dir = os.path.expanduser(model_dir)
        os.makedirs(self.model_dir, exist_ok=True)
        
        self.models: Dict[str, Dict] = {}
        self.training_history: List[Dict] = []
    
    def train_success_predictor(self, experiences: List[Dict]) -> Dict[str, Any]:
        """
        Train model untuk memprediksi success rate berdasarkan konteks
        """
        if not experiences:
            return {'error': 'No training data available'}
        
        # Ekstrak features dari experiences
        features = []
        labels = []
        
        for exp in experiences:
            feature_vector = self._extract_features(exp)
            label = 1 if exp.get('outcome') == 'success' else 0
            
            features.append(feature_vector)
            labels.append(label)
        
        # Hitung statistik sederhana (tanpa ML library)
        total_samples = len(features)
        successful = sum(labels)
        success_rate = successful / total_samples if total_samples > 0 else 0.0
        
        # Analisis feature importance
        feature_importance = self._analyze_feature_importance(features, labels)
        
        # Simpan model
        model_data = {
            'model_type': 'success_predictor',
            'training_samples': total_samples,
            'success_rate': success_rate,
            'feature_importance': feature_importance,
            'trained_at': time.time(),
            'metrics': {
                'accuracy': success_rate,
                'training_samples': total_samples
            }
        }
        
        model_id = f"success_predictor_{int(time.time())}"
        self.models[model_id] = model_data
        self._save_model(model_id, model_data)
        
        # Catat training history
        self.training_history.append({
            'model_id': model_id,
            'timestamp': time.time(),
            'samples': total_samples,
            'success_rate': success_rate
        })
        
        return {
            'model_id': model_id,
            'training_samples': total_samples,
            'success_rate': success_rate,
            'feature_importance': feature_importance,
            'status': 'trained'
        }
    
    def _extract_features(self, experience: Dict) -> Dict[str, Any]:
        """Ekstrak features dari experience"""
        features = {
            'experience_type': experience.get('experience_type', 'unknown'),
            'has_lessons_learned': len(experience.get('lessons_learned', [])) > 0,
            'num_actions': len(experience.get('actions_taken', [])),
            'has_metadata': bool(experience.get('metadata')),
            'context_complexity': len(json.dumps(experience.get('context', {})))
        }
        
        # Encode experience type
        exp_type = features['experience_type']
        features['is_vulnerability_scan'] = exp_type == 'vulnerability_scan'
        features['is_exploitation'] = exp_type == 'exploitation_attempt'
        features['is_ctf'] = exp_type == 'ctf_challenge'
        features['is_bug_bounty'] = exp_type == 'bug_bounty_submission'
        
        return features
    
    def _analyze_feature_importance(self, features: List[Dict], labels: List[int]) -> Dict[str, float]:
        """Analisis feature importance sederhana"""
        importance = {}
        total = len(features)
        
        if total == 0:
            return importance
        
        # Hitung correlation sederhana untuk setiap feature
        for key in features[0].keys():
            if isinstance(features[0][key], bool):
                # Untuk boolean features
                true_positive = sum(1 for f, l in zip(features, labels) if f[key] and l == 1)
                true_count = sum(1 for f in features if f[key])
                
                if true_count > 0:
                    importance[key] = (true_positive / true_count) if true_count > 0 else 0.0
            else:
                # Untuk numeric features
                importance[key] = 0.5  # Default importance
        
        return importance
    
    def predict_success_probability(self, context: Dict[str, Any], experience_type: str) -> float:
        """
        Prediksi probability of success berdasarkan konteks
        """
        # Cari model terbaik
        if not self.models:
            return 0.5  # Default
        
        # Gunakan model terbaru
        latest_model = max(self.models.values(), key=lambda m: m.get('trained_at', 0))
        
        # Ekstrak features dari context
        features = {
            'experience_type': experience_type,
            'has_lessons_learned': False,
            'num_actions': 0,
            'has_metadata': bool(context),
            'context_complexity': len(json.dumps(context))
        }
        
        exp_type = experience_type
        features['is_vulnerability_scan'] = exp_type == 'vulnerability_scan'
        features['is_exploitation'] = exp_type == 'exploitation_attempt'
        features['is_ctf'] = exp_type == 'ctf_challenge'
        features['is_bug_bounty'] = exp_type == 'bug_bounty_submission'
        
        # Hitung skor berdasarkan feature importance
        importance = latest_model.get('feature_importance', {})
        score = 0.0
        total_weight = 0.0
        
        for feature, value in features.items():
            if feature in importance:
                weight = importance[feature]
                score += weight * (1 if value else 0)
                total_weight += weight
        
        if total_weight > 0:
            score = score / total_weight
        
        # Normalize ke range 0-1
        base_rate = latest_model.get('success_rate', 0.5)
        prediction = base_rate + (score - 0.5) * 0.5
        prediction = max(0.0, min(1.0, prediction))
        
        return prediction
    
    def retrain_models(self, new_experiences: List[Dict]) -> Dict[str, Any]:
        """
        Retrain model dengan data baru
        """
        if not new_experiences:
            return {'message': 'No new experiences to train on'}
        
        results = []
        
        # Train success predictor
        success_result = self.train_success_predictor(new_experiences)
        results.append(success_result)
        
        return {
            'models_trained': len(results),
            'results': results,
            'timestamp': time.time()
        }
    
    def get_model_performance(self) -> Dict[str, Any]:
        """Dapatkan performa model"""
        if not self.models:
            return {'message': 'No models trained yet'}
        
        latest_model = max(self.models.values(), key=lambda m: m.get('trained_at', 0))
        
        return {
            'total_models': len(self.models),
            'latest_model': latest_model.get('model_type'),
            'training_samples': latest_model.get('training_samples'),
            'success_rate': latest_model.get('success_rate'),
            'last_trained': datetime.fromtimestamp(latest_model.get('trained_at', 0)).isoformat()
        }
    
    def _save_model(self, model_id: str, model_data: Dict):
        """Simpan model ke disk"""
        try:
            filepath = os.path.join(self.model_dir, f"{model_id}.json")
            with open(filepath, 'w') as f:
                json.dump(model_data, f, indent=2)
        except Exception as e:
            print(f"Failed to save model: {e}")
    
    def load_models(self):
        """Muat model dari disk"""
        try:
            for filename in os.listdir(self.model_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.model_dir, filename)
                    with open(filepath, 'r') as f:
                        model_data = json.load(f)
                        model_id = filename.replace('.json', '')
                        self.models[model_id] = model_data
        except Exception as e:
            print(f"Failed to load models: {e}")
