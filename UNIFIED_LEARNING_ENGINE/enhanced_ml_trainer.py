"""
Enhanced ML Trainer - Machine Learning-based model training
Menggunakan scikit-learn dan XGBoost untuk success prediction yang lebih akurat
"""

import json
import os
import time
from typing import Dict, List, Any, Optional
from datetime import datetime


class EnhancedMLTrainer:
    """
    Enhanced ML trainer dengan scikit-learn dan XGBoost
    """

    def __init__(self, base_dir="~/.arc/ai_models"):
        self.base_dir = os.path.expanduser(base_dir)
        self.models_dir = os.path.join(self.base_dir, "ml_models")
        self.training_history_file = os.path.join(self.base_dir, "ml_training_history.json")
        
        os.makedirs(self.models_dir, exist_ok=True)
        
        self.models = {}
        self.training_history = []
        self.feature_importance = {}
        
        # Check ML library availability
        self.sklearn_available = False
        self.xgboost_available = False
        self.np_available = False
        
        self._check_ml_libraries()
        
        # Load training history
        self._load_training_history()
    
    def _check_ml_libraries(self):
        """Check availability of ML libraries"""
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
                print("✅ XGBoost loaded for advanced ML training")
            except ImportError:
                print("⚠️ XGBoost not available, using RandomForest and GradientBoosting")
            
            print("✅ Scikit-learn loaded for ML training")
            
        except ImportError as e:
            print(f"⚠️ ML libraries not available: {e}")
    
    def prepare_ml_features(self, experiences: List[Dict[str, Any]]) -> tuple:
        """
        Prepare features untuk ML training
        
        Args:
            experiences: List of experience dicts
            
        Returns:
            Tuple of (features_array, labels_array, feature_names)
        """
        if not self.sklearn_available or not experiences:
            return None, None, None
        
        features = []
        labels = []
        feature_names = []
        
        for exp in experiences:
            context = exp.get('context', {})
            outcome = exp.get('outcome', 'unknown')
            
            # Extract numeric and categorical features
            feature_vector = self._extract_feature_vector(context)
            features.append(feature_vector)
            
            # Label: 1 for success, 0 for failure
            labels.append(1 if outcome == 'success' else 0)
        
        if not feature_names:
            feature_names = list(self._get_feature_names())
        
        import numpy as np
        X = np.array(features)
        y = np.array(labels)
        
        return X, y, feature_names
    
    def _extract_feature_vector(self, context: Dict[str, Any]) -> List[float]:
        """Extract numeric feature vector dari context"""
        features = []
        
        # Feature 1: Severity (numeric encoding)
        severity_map = {'critical': 5, 'high': 4, 'medium': 3, 'low': 2, 'info': 1}
        features.append(severity_map.get(context.get('severity', 'medium').lower(), 3))
        
        # Feature 2: Has CVE
        features.append(1 if context.get('cve_id') else 0)
        
        # Feature 3: Has CWE
        features.append(1 if context.get('cwe_id') else 0)
        
        # Feature 4: Technique category (hash to numeric)
        technique = context.get('technique', 'unknown')
        features.append(hash(technique) % 1000)
        
        # Feature 5: Exploitability score (if available from AI features)
        features.append(context.get('exploitability_score', 0.5))
        
        # Feature 6: Remediation priority (if available)
        features.append(context.get('remediation_priority', 5))
        
        # Feature 7: User interaction required
        features.append(1 if context.get('user_interaction') == 'required' else 0)
        
        # Feature 8: Attack complexity
        complexity_map = {'low': 1, 'medium': 2, 'high': 3}
        features.append(complexity_map.get(context.get('attack_complexity', 'medium'), 2))
        
        # Feature 9: Required privileges
        privileges_map = {'none': 0, 'low': 1, 'high': 2}
        features.append(privileges_map.get(context.get('required_privileges', 'none'), 0))
        
        # Feature 10: Detection difficulty
        difficulty_map = {'easy': 1, 'medium': 2, 'hard': 3}
        features.append(difficulty_map.get(context.get('detection_difficulty', 'medium'), 2))
        
        return features
    
    def _get_feature_names(self) -> List[str]:
        """Get feature names untuk ML model"""
        return [
            'severity',
            'has_cve',
            'has_cwe',
            'technique_hash',
            'exploitability_score',
            'remediation_priority',
            'user_interaction_required',
            'attack_complexity',
            'required_privileges',
            'detection_difficulty'
        ]
    
    def train_models(self, experiences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Train ML models untuk success prediction
        
        Args:
            experiences: List of experience dicts
            
        Returns:
            Training results
        """
        if not self.sklearn_available:
            return {'error': 'Scikit-learn not available'}
        
        if len(experiences) < 10:
            return {'error': 'Insufficient data', 'min_required': 10}
        
        # Prepare features
        X, y, feature_names = self.prepare_ml_features(experiences)
        
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
            'best_accuracy': 0.0
        }
        
        # Train RandomForest
        if self.sklearn_available:
            rf_result = self._train_random_forest(X_train, X_test, y_train, y_test, feature_names)
            results['models_trained'].append(rf_result)
            
            if rf_result.get('accuracy', 0) > results['best_accuracy']:
                results['best_accuracy'] = rf_result.get('accuracy', 0)
                results['best_model'] = 'random_forest'
        
        # Train GradientBoosting
        if self.sklearn_available:
            gb_result = self._train_gradient_boosting(X_train, X_test, y_train, y_test, feature_names)
            results['models_trained'].append(gb_result)
            
            if gb_result.get('accuracy', 0) > results['best_accuracy']:
                results['best_accuracy'] = gb_result.get('accuracy', 0)
                results['best_model'] = 'gradient_boosting'
        
        # Train XGBoost
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
    
    def _train_random_forest(self, X_train, X_test, y_train, y_test, feature_names) -> Dict[str, Any]:
        """Train RandomForest model"""
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        # Feature importance
        importance = dict(zip(feature_names, model.feature_importances_.tolist()))
        self.feature_importance['random_forest'] = importance
        
        # Save model
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
        """Train GradientBoosting model"""
        from sklearn.ensemble import GradientBoostingClassifier
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        model = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        # Feature importance
        importance = dict(zip(feature_names, model.feature_importances_.tolist()))
        self.feature_importance['gradient_boosting'] = importance
        
        # Save model
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
        """Train XGBoost model"""
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
        
        # Evaluate
        y_pred_prob = model.predict(dtest)
        y_pred = (y_pred_prob > 0.5).astype(int)
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        # Feature importance
        importance = dict(zip(feature_names, model.get_score(importance_type='gain').values()))
        self.feature_importance['xgboost'] = importance
        
        # Save model
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
    
    def predict_success_probability(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict success probability menggunakan trained models
        
        Args:
            context: Vulnerability context
            
        Returns:
            Prediction results
        """
        if not self.models or not self.sklearn_available:
            return {
                'probability': 0.5,
                'confidence': 0.0,
                'model_used': 'none'
            }
        
        try:
            # Prepare features
            feature_vector = self._extract_feature_vector(context)
            import numpy as np
            X = np.array([feature_vector])
            
            # Get best model
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
            
            # Find model instance
            model = None
            model_key = None
            for key in self.models.keys():
                if best_model_name in key:
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
            
        except Exception as e:
            print(f"⚠️ Prediction failed: {e}")
            return {
                'probability': 0.5,
                'confidence': 0.0,
                'model_used': 'error',
                'error': str(e)
            }
    
    def get_feature_importance_analysis(self) -> Dict[str, Any]:
        """Get feature importance analysis dari semua models"""
        if not self.feature_importance:
            return {'error': 'No feature importance data available'}
        
        # Aggregate feature importance across models
        aggregated = {}
        
        for model_name, importance in self.feature_importance.items():
            for feature, score in importance.items():
                if feature not in aggregated:
                    aggregated[feature] = []
                aggregated[feature].append(score)
        
        # Calculate average importance
        avg_importance = {}
        for feature, scores in aggregated.items():
            avg_importance[feature] = {
                'average': sum(scores) / len(scores),
                'max': max(scores),
                'min': min(scores),
                'models_used': len(scores)
            }
        
        # Sort by average importance
        sorted_importance = dict(sorted(avg_importance.items(), key=lambda x: x[1]['average'], reverse=True))
        
        return {
            'feature_importance': sorted_importance,
            'top_features': list(sorted_importance.keys())[:5],
            'models_analyzed': list(self.feature_importance.keys())
        }
    
    def evaluate_model_performance(self) -> Dict[str, Any]:
        """Evaluate overall model performance"""
        if not self.training_history:
            return {'error': 'No training history available'}
        
        # Get latest training results
        latest = self.training_history[-1]
        
        return {
            'latest_training': {
                'timestamp': latest.get('timestamp'),
                'models_trained': len(latest.get('models_trained', [])),
                'best_model': latest.get('best_model'),
                'best_accuracy': latest.get('best_accuracy', 0.0)
            },
            'total_training_runs': len(self.training_history),
            'available_models': list(self.models.keys()),
            'feature_analysis': self.get_feature_importance_analysis()
        }
    
    def _save_training_history(self):
        """Save training history to disk"""
        try:
            with open(self.training_history_file, 'w') as f:
                json.dump(self.training_history, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save training history: {e}")
    
    def _load_training_history(self):
        """Load training history from disk"""
        try:
            if os.path.exists(self.training_history_file):
                with open(self.training_history_file, 'r') as f:
                    self.training_history = json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to load training history: {e}")
    
    def retrain_with_new_data(self, new_experiences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Retrain models dengan new data
        
        Args:
            new_experiences: New experiences to add
            
        Returns:
            Retraining results
        """
        if not new_experiences:
            return {'error': 'No new experiences provided'}
        
        print(f"🔄 Retraining ML models with {len(new_experiences)} new experiences...")
        
        # Combine with existing data (if any)
        all_experiences = new_experiences
        
        # Train models
        result = self.train_models(all_experiences)
        
        return result
    
    def export_model_metadata(self) -> Dict[str, Any]:
        """Export model metadata untuk documentation"""
        return {
            'available': self.sklearn_available,
            'xgboost_available': self.xgboost_available,
            'models_count': len(self.models),
            'training_runs': len(self.training_history),
            'feature_importance': self.feature_importance,
            'latest_performance': self.training_history[-1] if self.training_history else None,
            'exported_at': datetime.now().isoformat()
        }