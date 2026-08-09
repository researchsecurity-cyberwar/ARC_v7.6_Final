"""
Unified Model Trainer - Consolidated trainer untuk semua ML/statistical training needs
Menggabungkan ModelTrainer, AIModelTrainer, dan EnhancedMLTrainer menjadi satu interface
"""
import json
import os
import time
import warnings
import hashlib
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class UnifiedModelTrainer:
    """
    Unified trainer yang menggabungkan semua capabilities:
    - Basic statistical analysis (dari ModelTrainer)
    - sklearn-based training (dari AIModelTrainer)
    - Advanced ML dengan XGBoost (dari EnhancedMLTrainer)
    
    Auto-selects best available training method based on installed libraries.
    """
    
    def __init__(self, base_dir: str = "~/.arc/ai_models"):
        # Validate and sanitize base directory
        expanded = os.path.expanduser(base_dir)
        
        # Security: Prevent path traversal
        if ".." in expanded or not os.path.isabs(expanded):
            raise ValueError(f"Invalid base_dir: must be absolute path without '..' (got: {base_dir})")
        
        # Security: Validate path format
        # Catatan: spasi diizinkan karena nama user Windows bisa mengandung spasi
        # (contoh: "C:\\Users\\Ryzen 7 Pro 4750"). ".." sudah dicek di atas.
        if not re.match(r'^[a-zA-Z0-9_\-./\\:~ ]+$', expanded):
            raise ValueError(f"Invalid characters in base_dir: {base_dir}")
        
        self.base_dir = expanded
        self.models_dir = os.path.join(self.base_dir, "unified_models")
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Storage
        self.models: Dict[str, Any] = {}
        self.training_history: List[Dict] = []
        self.feature_importance: Dict[str, Dict] = {}
        
        # Detect available backends
        self._detect_capabilities()
        
        # Load existing models
        self._load_models()
        
        # Security: Don't leak capability information
        print(f"✅ UnifiedModelTrainer initialized")
    
    def _detect_capabilities(self):
        """Detect available ML libraries"""
        self.basic_available = True  # Always available
        
        self.sklearn_available = False
        self.xgboost_available = False
        self.llama_available = False
        
        # Check sklearn
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
            from sklearn.preprocessing import StandardScaler
            import numpy as np
            import pandas as pd
            
            self.sklearn_available = True
            self.np_available = True
            self.pd_available = True
            
            # Check XGBoost
            try:
                import xgboost as xgb
                self.xgboost_available = True
            except ImportError:
                pass
                
        except ImportError:
            pass
        
        # Check llama.cpp
        try:
            from llama_cpp import Llama
            self.llama_available = True
        except ImportError:
            pass
    
    def _get_capabilities_string(self) -> str:
        """Get human-readable capabilities string"""
        caps = ["basic"]
        if self.sklearn_available:
            caps.append("sklearn")
        if self.xgboost_available:
            caps.append("xgboost")
        if self.llama_available:
            caps.append("llama")
        return ", ".join(caps)
    
    def _extract_features(self, experience_or_context: Dict) -> Dict[str, Any]:
        """
        Extract features from experience or context dict
        Supports both old (ModelTrainer) and new (EnhancedMLTrainer) formats
        """
        # Handle both experience dict and context dict
        if 'context' in experience_or_context:
            # It's an experience dict
            context = experience_or_context.get('context', {})
        else:
            # It's already a context dict
            context = experience_or_context
        
        features = {}
        
        # Basic features (from ModelTrainer)
        features['experience_type'] = experience_or_context.get('experience_type', context.get('technique', 'unknown'))
        features['has_lessons_learned'] = len(experience_or_context.get('lessons_learned', [])) > 0
        features['num_actions'] = len(experience_or_context.get('actions_taken', []))
        features['has_metadata'] = bool(experience_or_context.get('metadata', context))
        features['context_complexity'] = len(json.dumps(context))
        
        # Encode experience type
        exp_type = features['experience_type']
        features['is_vulnerability_scan'] = exp_type == 'vulnerability_scan'
        features['is_exploitation'] = exp_type == 'exploitation_attempt'
        features['is_ctf'] = exp_type == 'ctf_challenge'
        features['is_bug_bounty'] = exp_type == 'bug_bounty_submission'
        
        # Advanced features (from EnhancedMLTrainer)
        severity_map = {'critical': 5, 'high': 4, 'medium': 3, 'low': 2, 'info': 1}
        # Security: Validate severity is string before calling .lower()
        severity = context.get('severity', 'medium')
        if not isinstance(severity, str):
            severity = 'medium'
        features['severity'] = severity_map.get(severity.lower(), 3)
        features['has_cve'] = 1 if context.get('cve_id') else 0
        features['has_cwe'] = 1 if context.get('cwe_id') else 0
        # Security: Use cryptographic hash instead of Python's hash()
        technique_str = str(context.get('technique', 'unknown'))
        features['technique_hash'] = int(hashlib.sha256(technique_str.encode()).hexdigest(), 16) % 1000
        
        # Security: Validate numeric inputs
        exploitability = context.get('exploitability_score', 0.5)
        features['exploitability_score'] = float(exploitability) if isinstance(exploitability, (int, float)) else 0.5
        
        remediation = context.get('remediation_priority', 5)
        features['remediation_priority'] = int(remediation) if isinstance(remediation, (int, float)) else 5
        
        features['user_interaction_required'] = 1 if context.get('user_interaction') == 'required' else 0
        
        # Security: Validate string inputs
        complexity = context.get('attack_complexity', 'medium')
        if not isinstance(complexity, str):
            complexity = 'medium'
        complexity_map = {'low': 1, 'medium': 2, 'high': 3}
        features['attack_complexity'] = complexity_map.get(complexity.lower(), 2)
        
        privileges = context.get('required_privileges', 'none')
        if not isinstance(privileges, str):
            privileges = 'none'
        privileges_map = {'none': 0, 'low': 1, 'high': 2}
        features['required_privileges'] = privileges_map.get(privileges.lower(), 0)
        
        difficulty = context.get('detection_difficulty', 'medium')
        if not isinstance(difficulty, str):
            difficulty = 'medium'
        difficulty_map = {'easy': 1, 'medium': 2, 'hard': 3}
        features['detection_difficulty'] = difficulty_map.get(difficulty.lower(), 2)
        
        return features
    
    def train_success_predictor(self, experiences: List[Dict]) -> Dict[str, Any]:
        """
        Train success predictor (backward compatible dengan ModelTrainer)
        
        Args:
            experiences: List of experience dicts
            
        Returns:
            Training results
        """
        if not experiences:
            return {'error': 'No training data available'}
        
        if len(experiences) < 5:
            return {'error': 'Insufficient data', 'min_required': 5}
        
        # Extract features and labels
        features = []
        labels = []
        
        for exp in experiences:
            feature_vector = self._extract_features(exp)
            features.append(feature_vector)
            labels.append(1 if exp.get('outcome') == 'success' else 0)
        
        # Calculate statistics
        total_samples = len(features)
        successful = sum(labels)
        success_rate = successful / total_samples if total_samples > 0 else 0.0
        
        # Analyze feature importance
        feature_importance = self._analyze_feature_importance(features, labels)
        
        # Save model
        model_data = {
            'model_type': 'success_predictor_unified',
            'training_samples': total_samples,
            'success_rate': success_rate,
            'feature_importance': feature_importance,
            'trained_at': time.time(),
            'backend': 'basic',
            'metrics': {
                'accuracy': success_rate,
                'training_samples': total_samples
            }
        }
        
        model_id = f"success_predictor_{int(time.time())}"
        self.models[model_id] = model_data
        self._save_model(model_id, model_data)
        
        # Record training history
        self.training_history.append({
            'model_id': model_id,
            'timestamp': time.time(),
            'backend': 'basic',
            'samples': total_samples,
            'success_rate': success_rate
        })
        
        return {
            'model_id': model_id,
            'training_samples': total_samples,
            'success_rate': success_rate,
            'feature_importance': feature_importance,
            'status': 'trained',
            'backend': 'basic'
        }
    
    def _analyze_feature_importance(self, features: List[Dict], labels: List[int]) -> Dict[str, float]:
        """Analyze feature importance (basic version)"""
        importance = {}
        total = len(features)
        
        if total == 0:
            return importance
        
        for key in features[0].keys():
            if isinstance(features[0][key], bool):
                true_positive = sum(1 for f, l in zip(features, labels) if f[key] and l == 1)
                true_count = sum(1 for f in features if f[key])
                importance[key] = (true_positive / true_count) if true_count > 0 else 0.0
            else:
                importance[key] = 0.5
        
        return importance
    
    def train_models(self, experiences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Train ML models (from EnhancedMLTrainer)
        
        Args:
            experiences: List of experience dicts
            
        Returns:
            Training results
        """
        if not self.sklearn_available:
            return {'error': 'Scikit-learn not available', 'fallback': 'basic'}
        
        if len(experiences) < 10:
            return {'error': 'Insufficient data', 'min_required': 10}
        
        # Prepare features
        X, y, feature_names = self._prepare_ml_features(experiences)
        
        if X is None or len(X) < 10:
            return {'error': 'Failed to prepare features'}
        
        # Split data
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_samples': len(experiences),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'models_trained': [],
            'best_model': None,
            'best_accuracy': 0.0,
            'backend': 'sklearn'
        }
        
        # Train RandomForest
        rf_result = self._train_random_forest(X_train, X_test, y_train, y_test, feature_names)
        results['models_trained'].append(rf_result)
        
        if rf_result.get('accuracy', 0) > results['best_accuracy']:
            results['best_accuracy'] = rf_result.get('accuracy', 0)
            results['best_model'] = 'random_forest'
        
        # Train GradientBoosting
        gb_result = self._train_gradient_boosting(X_train, X_test, y_train, y_test, feature_names)
        results['models_trained'].append(gb_result)
        
        if gb_result.get('accuracy', 0) > results['best_accuracy']:
            results['best_accuracy'] = gb_result.get('accuracy', 0)
            results['best_model'] = 'gradient_boosting'
        
        # Train XGBoost if available
        if self.xgboost_available:
            xgb_result = self._train_xgboost(X_train, X_test, y_train, y_test, feature_names)
            results['models_trained'].append(xgb_result)
            
            if xgb_result.get('accuracy', 0) > results['best_accuracy']:
                results['best_accuracy'] = xgb_result.get('accuracy', 0)
                results['best_model'] = 'xgboost'
        
        # Save training history
        self.training_history.append(results)
        self._save_training_history()
        
        return results
    
    def _prepare_ml_features(self, experiences: List[Dict[str, Any]]) -> Tuple[Optional[Any], Optional[Any], List[str]]:
        """Prepare features for ML training"""
        if not self.sklearn_available or not experiences:
            return None, None, []
        
        features = []
        labels = []
        feature_names = []
        
        for exp in experiences:
            context = exp.get('context', {})
            feature_vector = self._extract_feature_vector(context)
            features.append(feature_vector)
            labels.append(1 if exp.get('outcome') == 'success' else 0)
        
        if not feature_names:
            feature_names = list(self._get_feature_names())
        
        import numpy as np
        X = np.array(features)
        y = np.array(labels)
        
        return X, y, feature_names
    
    def _extract_feature_vector(self, context: Dict[str, Any]) -> List[float]:
        """Extract numeric feature vector"""
        features = []
        
        # Security: Validate and sanitize inputs
        severity = context.get('severity', 'medium')
        if not isinstance(severity, str):
            severity = 'medium'
        severity = severity.lower()
        
        severity_map = {'critical': 5, 'high': 4, 'medium': 3, 'low': 2, 'info': 1}
        features.append(severity_map.get(severity, 3))
        
        features.append(1 if context.get('cve_id') else 0)
        features.append(1 if context.get('cwe_id') else 0)
        
        # Security: Use cryptographic hash
        technique_str = str(context.get('technique', 'unknown'))
        features.append(int(hashlib.sha256(technique_str.encode()).hexdigest(), 16) % 1000)
        
        # Security: Validate numeric inputs
        exploitability = context.get('exploitability_score', 0.5)
        features.append(float(exploitability) if isinstance(exploitability, (int, float)) else 0.5)
        
        remediation = context.get('remediation_priority', 5)
        features.append(int(remediation) if isinstance(remediation, (int, float)) else 5)
        
        features.append(1 if context.get('user_interaction') == 'required' else 0)
        
        complexity = context.get('attack_complexity', 'medium')
        if not isinstance(complexity, str):
            complexity = 'medium'
        complexity_map = {'low': 1, 'medium': 2, 'high': 3}
        features.append(complexity_map.get(complexity.lower(), 2))
        
        privileges = context.get('required_privileges', 'none')
        if not isinstance(privileges, str):
            privileges = 'none'
        privileges_map = {'none': 0, 'low': 1, 'high': 2}
        features.append(privileges_map.get(privileges.lower(), 0))
        
        difficulty = context.get('detection_difficulty', 'medium')
        if not isinstance(difficulty, str):
            difficulty = 'medium'
        difficulty_map = {'easy': 1, 'medium': 2, 'hard': 3}
        features.append(difficulty_map.get(difficulty.lower(), 2))
        
        return features
    
    def _get_feature_names(self) -> List[str]:
        """Get feature names"""
        return [
            'severity', 'has_cve', 'has_cwe', 'technique_hash',
            'exploitability_score', 'remediation_priority',
            'user_interaction_required', 'attack_complexity',
            'required_privileges', 'detection_difficulty'
        ]
    
    def _train_random_forest(self, X_train, X_test, y_train, y_test, feature_names) -> Dict[str, Any]:
        """Train RandomForest"""
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        importance = dict(zip(feature_names, model.feature_importances_.tolist()))
        self.feature_importance['random_forest'] = importance
        
        model_id = f"rf_model_{int(time.time())}"
        self.models[model_id] = model
        
        return {
            'model_id': model_id,
            'model_type': 'random_forest',
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'feature_importance': importance
        }
    
    def _train_gradient_boosting(self, X_train, X_test, y_train, y_test, feature_names) -> Dict[str, Any]:
        """Train GradientBoosting"""
        from sklearn.ensemble import GradientBoostingClassifier
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        model = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        importance = dict(zip(feature_names, model.feature_importances_.tolist()))
        self.feature_importance['gradient_boosting'] = importance
        
        model_id = f"gb_model_{int(time.time())}"
        self.models[model_id] = model
        
        return {
            'model_id': model_id,
            'model_type': 'gradient_boosting',
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'feature_importance': importance
        }
    
    def _train_xgboost(self, X_train, X_test, y_train, y_test, feature_names) -> Dict[str, Any]:
        """Train XGBoost"""
        import xgboost as xgb
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        dtrain = xgb.DMatrix(X_train, label=y_train)
        dtest = xgb.DMatrix(X_test, label=y_test)
        
        params = {
            'max_depth': 5,
            'eta': 0.1,
            'objective': 'binary:logistic',
            'eval_metric': 'logloss',
            'seed': 42
        }
        
        model = xgb.train(params, dtrain, num_boost_round=100, verbose_eval=False)
        
        y_pred_prob = model.predict(dtest)
        y_pred = (y_pred_prob > 0.5).astype(int)
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        importance = dict(zip(feature_names, model.get_score(importance_type='gain').values()))
        self.feature_importance['xgboost'] = importance
        
        model_id = f"xgb_model_{int(time.time())}"
        self.models[model_id] = model
        
        return {
            'model_id': model_id,
            'model_type': 'xgboost',
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'feature_importance': importance
        }
    
    def predict_success_probability(self, context: Dict[str, Any], experience_type: str = None) -> Dict[str, Any]:
        """
        Predict success probability (unified interface)
        
        Args:
            context: Vulnerability context
            experience_type: Optional experience type (for backward compatibility)
            
        Returns:
            Prediction results dict
        """
        # Try sklearn models first
        if self.sklearn_available and self.models:
            try:
                return self._predict_with_ml(context)
            except Exception as e:
                print(f"⚠️ ML prediction failed, falling back to basic: {e}")
        
        # Fallback to basic prediction
        return self._predict_basic(context, experience_type)
    
    def _predict_with_ml(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Predict using trained ML models"""
        feature_vector = self._extract_feature_vector(context)
        import numpy as np
        X = np.array([feature_vector])
        
        # Find best model
        best_model_name = None
        best_accuracy = 0.0
        
        for hist in reversed(self.training_history):
            if hist.get('best_model'):
                best_model_name = hist['best_model']
                best_accuracy = hist.get('best_accuracy', 0.0)
                break
        
        if not best_model_name:
            return {
                'probability': 0.5,
                'confidence': 0.0,
                'model_used': 'none'
            }
        
        # Find model instance (exact match to prevent wrong model selection)
        model = None
        model_key = None
        for key in self.models.keys():
            # Security: Exact match or prefix match to prevent substring attacks
            if best_model_name == key or key.startswith(f"{best_model_name}_"):
                model = self.models[key]
                model_key = key
                break
        
        if not model:
            return {
                'probability': 0.5,
                'confidence': 0.0,
                'model_used': 'none'
            }
        
        # Predict
        if best_model_name == 'xgboost':
            import xgboost as xgb
            dtest = xgb.DMatrix(X)
            prob = float(model.predict(dtest)[0])
        else:
            prob = float(model.predict_proba(X)[0][1])
        
        return {
            'probability': round(prob, 3),
            'confidence': round(best_accuracy, 3),
            'model_used': best_model_name,
            'model_key': model_key
        }
    
    def _predict_basic(self, context: Dict, experience_type: str = None) -> Dict[str, Any]:
        """Basic prediction fallback"""
        score = 0.5
        
        if context.get('cve_id') or context.get('cwe_id'):
            score += 0.2
        if context.get('severity') in ['critical', 'high']:
            score += 0.1
        if experience_type:
            score += 0.05  # Small boost for having type info
        
        prediction = max(0.0, min(1.0, score))
        
        return {
            'probability': round(prediction, 3),
            'confidence': 0.5,
            'model_used': 'basic_heuristic'
        }
    
    def retrain_models(self, new_experiences: List[Dict]) -> Dict[str, Any]:
        """Retrain with new data"""
        if not new_experiences:
            return {'message': 'No new experiences to train on'}
        
        # Use best available backend
        if self.sklearn_available and len(new_experiences) >= 10:
            return self.train_models(new_experiences)
        else:
            return self.train_success_predictor(new_experiences)
    
    def get_model_performance(self) -> Dict[str, Any]:
        """Get model performance"""
        if not self.training_history:
            return {'message': 'No models trained yet'}
        
        latest = self.training_history[-1]
        
        return {
            'total_models': len(self.models),
            'total_training_runs': len(self.training_history),
            'latest_model': latest.get('backend', 'unknown'),
            'training_samples': latest.get('training_samples', 0),
            'success_rate': latest.get('success_rate', 0.0),
            'last_trained': datetime.fromtimestamp(latest.get('timestamp', 0)).isoformat(),
            'capabilities': self._get_capabilities_string()
        }
    
    def evaluate_model_performance(self) -> Dict[str, Any]:
        """Evaluate model performance (from EnhancedMLTrainer)"""
        if not self.training_history:
            return {'error': 'No training history available'}
        
        latest = self.training_history[-1]
        
        return {
            'latest_training': {
                'timestamp': latest.get('timestamp'),
                'backend': latest.get('backend'),
                'models_trained': len(latest.get('models_trained', [])),
                'best_model': latest.get('best_model'),
                'best_accuracy': latest.get('best_accuracy', 0.0)
            },
            'total_training_runs': len(self.training_history),
            'available_models': list(self.models.keys()),
            'feature_analysis': self.get_feature_importance_analysis()
        }
    
    def get_feature_importance_analysis(self) -> Dict[str, Any]:
        """Get feature importance analysis"""
        if not self.feature_importance:
            return {'error': 'No feature importance data available'}
        
        aggregated = {}
        for model_name, importance in self.feature_importance.items():
            for feature, score in importance.items():
                if feature not in aggregated:
                    aggregated[feature] = []
                aggregated[feature].append(score)
        
        avg_importance = {}
        for feature, scores in aggregated.items():
            avg_importance[feature] = {
                'average': sum(scores) / len(scores),
                'max': max(scores),
                'min': min(scores),
                'models_used': len(scores)
            }
        
        sorted_importance = dict(sorted(avg_importance.items(), key=lambda x: x[1]['average'], reverse=True))
        
        return {
            'feature_importance': sorted_importance,
            'top_features': list(sorted_importance.keys())[:5],
            'models_analyzed': list(self.feature_importance.keys())
        }
    
    def _save_model(self, model_id: str, model_data: Dict):
        """Save model metadata with validation"""
        try:
            # Security: Validate model_id to prevent injection
            if not re.match(r'^[a-zA-Z0-9_-]+$', model_id):
                raise ValueError(f"Invalid model_id format: {model_id}")
            
            filepath = os.path.join(self.models_dir, f"{model_id}.json")
            
            # Security: Atomic write with temp file
            temp_filepath = filepath + '.tmp'
            with open(temp_filepath, 'w') as f:
                json.dump(model_data, f, indent=2)
            
            # Atomic rename
            os.replace(temp_filepath, filepath)
            
        except Exception as e:
            # Security: Raise exception instead of silent failure
            raise RuntimeError(f"Failed to save model: {e}") from e
    
    def _save_training_history(self):
        """Save training history with atomic write"""
        try:
            history_file = os.path.join(self.base_dir, "training_history.json")
            
            # Security: Atomic write
            temp_filepath = history_file + '.tmp'
            with open(temp_filepath, 'w') as f:
                json.dump(self.training_history, f, indent=2)
            
            os.replace(temp_filepath, history_file)
            
        except Exception as e:
            raise RuntimeError(f"Failed to save training history: {e}") from e
    
    def _load_models(self):
        """Load models from disk with validation"""
        try:
            if not os.path.exists(self.models_dir):
                return
            
            for filename in os.listdir(self.models_dir):
                if filename.endswith('.json'):
                    # Security: Validate filename
                    model_id = filename.replace('.json', '')
                    if not re.match(r'^[a-zA-Z0-9_-]+$', model_id):
                        print(f"⚠️ Skipping invalid model file: {filename}")
                        continue
                    
                    filepath = os.path.join(self.models_dir, filename)
                    
                    # Security: Validate file size
                    file_size = os.path.getsize(filepath)
                    if file_size > 10 * 1024 * 1024:  # 10MB limit
                        print(f"⚠️ Skipping oversized model: {filename}")
                        continue
                    
                    with open(filepath, 'r') as f:
                        model_data = json.load(f)
                        self.models[model_id] = model_data
                        
        except Exception as e:
            print(f"⚠️ Failed to load models: {e}")
    
    def _load_training_history(self):
        """Load training history from disk with validation"""
        try:
            history_file = os.path.join(self.base_dir, "training_history.json")
            if os.path.exists(history_file):
                # Security: Validate file size
                file_size = os.path.getsize(history_file)
                if file_size > 10 * 1024 * 1024:  # 10MB limit
                    print(f"⚠️ Skipping oversized training history")
                    return
                
                with open(history_file, 'r') as f:
                    self.training_history = json.load(f)
                    
                    # Security: Validate structure
                    if not isinstance(self.training_history, list):
                        print(f"⚠️ Invalid training history format")
                        self.training_history = []
                        
        except Exception as e:
            print(f"⚠️ Failed to load training history: {e}")
    
    def export_model_metadata(self) -> Dict[str, Any]:
        """Export model metadata"""
        return {
            'available': True,
            'sklearn_available': self.sklearn_available,
            'xgboost_available': self.xgboost_available,
            'llama_available': self.llama_available,
            'models_count': len(self.models),
            'training_runs': len(self.training_history),
            'feature_importance': self.feature_importance,
            'latest_performance': self.training_history[-1] if self.training_history else None,
            'exported_at': datetime.now().isoformat()
        }
    
    @classmethod
    def is_available(cls) -> bool:
        """Check if trainer is available"""
        return True  # Always available (basic mode)


# Backward compatibility wrappers with deprecation warnings
class ModelTrainer(UnifiedModelTrainer):
    """
    Deprecated: Use UnifiedModelTrainer instead.
    Kept for backward compatibility.
    """
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "ModelTrainer is deprecated, use UnifiedModelTrainer",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)


class AIModelTrainer(UnifiedModelTrainer):
    """
    Deprecated: Use UnifiedModelTrainer instead.
    This was dead code, now consolidated.
    """
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "AIModelTrainer is deprecated and was unused, use UnifiedModelTrainer",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)


class EnhancedMLTrainer(UnifiedModelTrainer):
    """
    Deprecated: Use UnifiedModelTrainer instead.
    Kept for backward compatibility.
    """
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "EnhancedMLTrainer is deprecated, use UnifiedModelTrainer",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)