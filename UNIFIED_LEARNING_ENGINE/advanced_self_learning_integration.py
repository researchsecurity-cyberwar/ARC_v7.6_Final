"""
Advanced Self-Learning Integration - Integrasi semua komponen AI-enhanced
Module ini menghubungkan semua komponen baru ke sistem yang sudah ada
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime


class AdvancedSelfLearningIntegration:
    """
    Integrasi semua komponen AI-enhanced self-learning
    """

    def __init__(self, base_dir="~/.arc/self_learning"):
        self.base_dir = os.path.expanduser(base_dir)
        
        # Initialize all components
        self.feature_extractor = None
        self.fine_tuning_pipeline = None
        self.lesson_generator = None
        self.closed_loop_feedback = None
        self.ml_trainer = None
        self.rl_learner = None
        self.orchestrator = None
        
        # Initialize components
        self._init_components()
    
    def _init_components(self):
        """Initialize semua komponen AI-enhanced"""
        print("🧠 Initializing Advanced Self-Learning Integration...")
        
        # 1. AI Feature Extractor
        try:
            from .ai_feature_extractor import AIFeatureExtractor
            self.feature_extractor = AIFeatureExtractor(self.base_dir)
            print("  ✅ AI Feature Extractor loaded")
        except Exception as e:
            print(f"  ⚠️ AI Feature Extractor failed: {e}")
        
        # 2. AI Fine-Tuning Pipeline
        try:
            from .ai_fine_tuning_pipeline import AIFineTuningPipeline
            self.fine_tuning_pipeline = AIFineTuningPipeline()
            print("  ✅ AI Fine-Tuning Pipeline loaded")
        except Exception as e:
            print(f"  ⚠️ AI Fine-Tuning Pipeline failed: {e}")
        
        # 3. AI Lesson Generator
        try:
            from .ai_lesson_generator import AILessonGenerator
            self.lesson_generator = AILessonGenerator(self.base_dir)
            print("  ✅ AI Lesson Generator loaded")
        except Exception as e:
            print(f"  ⚠️ AI Lesson Generator failed: {e}")
        
        # 4. Closed-Loop Feedback
        try:
            from .closed_loop_feedback import ClosedLoopFeedback
            self.closed_loop_feedback = ClosedLoopFeedback(self.base_dir)
            print("  ✅ Closed-Loop Feedback loaded")
        except Exception as e:
            print(f"  ⚠️ Closed-Loop Feedback failed: {e}")
        
        # 5. Unified ML Trainer (replaces EnhancedMLTrainer)
        try:
            from .unified_model_trainer import UnifiedModelTrainer
            self.ml_trainer = UnifiedModelTrainer()
            print("  ✅ Unified ML Trainer loaded")
        except Exception as e:
            print(f"  ⚠️ Unified ML Trainer failed: {e}")
        
        # 6. Reinforcement Learner
        try:
            from .reinforcement_learning import ReinforcementLearner
            self.rl_learner = ReinforcementLearner(self.base_dir)
            print("  ✅ Reinforcement Learner loaded")
        except Exception as e:
            print(f"  ⚠️ Reinforcement Learner failed: {e}")
        
        print("✅ Advanced Self-Learning Integration initialized\n")
    
    def integrate_with_arc_main(self, arc_main_instance):
        """
        Integrate dengan ARC main system
        
        Args:
            arc_main_instance: Instance dari ARCMain class
        """
        self.orchestrator = arc_main_instance.self_learning_orchestrator
        
        # Integrate closed-loop feedback dengan orchestrator
        if self.closed_loop_feedback and self.orchestrator:
            self.closed_loop_feedback.integrate_with_orchestrator(self.orchestrator)
        
        # Integrate RL dengan closed-loop
        if self.rl_learner and self.closed_loop_feedback:
            self.rl_learner.integrate_with_closed_loop(self.closed_loop_feedback)
        
        print("🔗 Advanced Self-Learning integrated with ARC Main")
    
    def process_experience_advanced(self, experience: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process experience dengan semua AI enhancements
        
        Args:
            experience: Experience dict
            
        Returns:
            Enhanced experience
        """
        enhanced = experience
        
        # Step 1: Feature Extraction
        if self.feature_extractor:
            try:
                features = self.feature_extractor.extract_features(experience.get('context', {}))
                enhanced['context'] = {**experience.get('context', {}), **features}
            except Exception as e:
                print(f"⚠️ Feature extraction failed: {e}")
        
        # Step 2: Closed-Loop Processing
        if self.closed_loop_feedback:
            try:
                enhanced = self.closed_loop_feedback.process_experience_with_ai(enhanced)
            except Exception as e:
                print(f"⚠️ Closed-loop processing failed: {e}")
        
        # Step 3: Reinforcement Learning
        if self.rl_learner:
            try:
                self.rl_learner.learn_from_experience(enhanced)
            except Exception as e:
                print(f"⚠️ RL learning failed: {e}")
        
        return enhanced
    
    def get_ai_recommendations(self, context: Dict[str, Any], detector_name: str) -> Dict[str, Any]:
        """
        Get comprehensive AI recommendations
        
        Args:
            context: Vulnerability context
            detector_name: Detector name
            
        Returns:
            AI recommendations
        """
        recommendations = {
            'detector': detector_name,
            'context': context,
            'timestamp': datetime.now().isoformat()
        }
        
        # 1. ML-based success prediction
        if self.ml_trainer:
            try:
                ml_pred = self.ml_trainer.predict_success_probability(context)
                recommendations['ml_prediction'] = ml_pred
            except Exception as e:
                print(f"⚠️ ML prediction failed: {e}")
        
        # 2. RL-based strategy
        if self.rl_learner:
            try:
                rl_strategy = self.rl_learner.get_best_strategy(context)
                recommendations['rl_strategy'] = rl_strategy
            except Exception as e:
                print(f"⚠️ RL strategy failed: {e}")
        
        # 3. AI-guided detection
        if self.closed_loop_feedback and self.orchestrator:
            try:
                ai_guidance = self.closed_loop_feedback.ai_guided_detection(detector_name, context)
                recommendations['ai_guidance'] = ai_guidance
            except Exception as e:
                print(f"⚠️ AI guidance failed: {e}")
        
        # 4. Learning recommendations
        if self.orchestrator:
            try:
                learning_recs = self.orchestrator.get_learning_recommendations(context, detector_name)
                recommendations['learning_recommendations'] = learning_recs
            except Exception as e:
                print(f"⚠️ Learning recommendations failed: {e}")
        
        return recommendations
    
    def auto_improvement_cycle(self) -> Dict[str, Any]:
        """
        Execute automatic improvement cycle
        
        Returns:
            Cycle results
        """
        print("🔄 Starting Auto-Improvement Cycle...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'steps_completed': [],
            'improvements': {}
        }
        
        # Step 1: Closed-loop learning cycle
        if self.closed_loop_feedback and self.orchestrator:
            try:
                experiences = self.orchestrator.experience_collector.experiences[-50:]  # Last 50
                cycle_result = self.closed_loop_feedback.closed_loop_learning_cycle(experiences)
                results['improvements']['closed_loop'] = cycle_result
                results['steps_completed'].append('closed_loop_cycle')
            except Exception as e:
                print(f"⚠️ Closed-loop cycle failed: {e}")
        
        # Step 2: ML retraining
        if self.ml_trainer and self.orchestrator:
            try:
                experiences = self.orchestrator.experience_collector.experiences
                if len(experiences) >= 10:
                    ml_result = self.ml_trainer.train_models(experiences)
                    results['improvements']['ml_training'] = ml_result
                    results['steps_completed'].append('ml_retraining')
            except Exception as e:
                print(f"⚠️ ML retraining failed: {e}")
        
        # Step 3: RL batch learning
        if self.rl_learner and self.orchestrator:
            try:
                experiences = self.orchestrator.experience_collector.experiences[-100:]  # Last 100
                self.rl_learner.batch_learn(experiences)
                rl_stats = self.rl_learner.get_learning_statistics()
                results['improvements']['rl_learning'] = rl_stats
                results['steps_completed'].append('rl_batch_learning')
            except Exception as e:
                print(f"⚠️ RL batch learning failed: {e}")
        
        # Step 4: Fine-tuning preparation
        if self.fine_tuning_pipeline and self.orchestrator:
            try:
                experiences = self.orchestrator.experience_collector.experiences
                if len(experiences) >= 20:
                    ft_result = self.fine_tuning_pipeline.auto_fine_tune_loop(self.orchestrator)
                    results['improvements']['fine_tuning'] = ft_result
                    results['steps_completed'].append('fine_tuning_preparation')
            except Exception as e:
                print(f"⚠️ Fine-tuning preparation failed: {e}")
        
        print(f"✅ Auto-Improvement Cycle completed: {len(results['steps_completed'])} steps")
        
        return results
    
    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics dari semua komponen"""
        stats = {
            'timestamp': datetime.now().isoformat(),
            'components': {}
        }
        
        # Feature Extractor stats
        if self.feature_extractor:
            try:
                stats['components']['feature_extractor'] = self.feature_extractor.get_feature_statistics()
            except Exception as e:
                stats['components']['feature_extractor'] = {'error': str(e)}
        
        # Fine-Tuning Pipeline stats
        if self.fine_tuning_pipeline:
            try:
                stats['components']['fine_tuning_pipeline'] = self.fine_tuning_pipeline.get_pipeline_statistics()
            except Exception as e:
                stats['components']['fine_tuning_pipeline'] = {'error': str(e)}
        
        # Lesson Generator stats
        if self.lesson_generator:
            try:
                stats['components']['lesson_generator'] = self.lesson_generator.get_lesson_statistics()
            except Exception as e:
                stats['components']['lesson_generator'] = {'error': str(e)}
        
        # Closed-Loop Feedback stats
        if self.closed_loop_feedback:
            try:
                stats['components']['closed_loop_feedback'] = self.closed_loop_feedback.get_closed_loop_statistics()
            except Exception as e:
                stats['components']['closed_loop_feedback'] = {'error': str(e)}
        
        # ML Trainer stats
        if self.ml_trainer:
            try:
                stats['components']['ml_trainer'] = self.ml_trainer.evaluate_model_performance()
            except Exception as e:
                stats['components']['ml_trainer'] = {'error': str(e)}
        
        # RL Learner stats
        if self.rl_learner:
            try:
                stats['components']['rl_learner'] = self.rl_learner.get_learning_statistics()
            except Exception as e:
                stats['components']['rl_learner'] = {'error': str(e)}
        
        return stats
    
    def export_all_ai_artifacts(self, output_dir: str = None) -> Dict[str, str]:
        """
        Export semua AI artifacts untuk backup/analysis
        
        Args:
            output_dir: Output directory (optional)
            
        Returns:
            Dict of exported file paths
        """
        if not output_dir:
            timestamp = int(datetime.now().timestamp())
            output_dir = os.path.join(self.base_dir, f"ai_export_{timestamp}")
        
        os.makedirs(output_dir, exist_ok=True)
        exported = {}
        
        # Export lessons
        if self.lesson_generator:
            try:
                lesson_file = os.path.join(output_dir, "ai_lessons.jsonl")
                result = self.lesson_generator.export_lessons_for_training(lesson_file)
                exported['lessons'] = result
            except Exception as e:
                print(f"⚠️ Failed to export lessons: {e}")
        
        # Export RL policy
        if self.rl_learner:
            try:
                rl_policy_file = os.path.join(output_dir, "rl_policy.json")
                policy = self.rl_learner.export_policy()
                with open(rl_policy_file, 'w') as f:
                    json.dump(policy, f, indent=2)
                exported['rl_policy'] = rl_policy_file
            except Exception as e:
                print(f"⚠️ Failed to export RL policy: {e}")
        
        # Export ML metadata
        if self.ml_trainer:
            try:
                ml_metadata_file = os.path.join(output_dir, "ml_metadata.json")
                metadata = self.ml_trainer.export_model_metadata()
                with open(ml_metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
                exported['ml_metadata'] = ml_metadata_file
            except Exception as e:
                print(f"⚠️ Failed to export ML metadata: {e}")
        
        # Export closed-loop data
        if self.closed_loop_feedback:
            try:
                cl_data_file = os.path.join(output_dir, "closed_loop_data.jsonl")
                result = self.closed_loop_feedback.export_training_data()
                exported['closed_loop_data'] = result
            except Exception as e:
                print(f"⚠️ Failed to export closed-loop data: {e}")
        
        print(f"📦 AI artifacts exported to: {output_dir}")
        
        return exported
    
    def validate_system_health(self) -> Dict[str, Any]:
        """
        Validate health of all AI components
        
        Returns:
            Health check results
        """
        health = {
            'timestamp': datetime.now().isoformat(),
            'overall_health': 'healthy',
            'components': {},
            'issues': []
        }
        
        # Check each component
        components = {
            'feature_extractor': self.feature_extractor,
            'fine_tuning_pipeline': self.fine_tuning_pipeline,
            'lesson_generator': self.lesson_generator,
            'closed_loop_feedback': self.closed_loop_feedback,
            'ml_trainer': self.ml_trainer,
            'rl_learner': self.rl_learner
        }
        
        for name, component in components.items():
            if component:
                health['components'][name] = 'operational'
            else:
                health['components'][name] = 'unavailable'
                health['issues'].append(f"{name} not initialized")
        
        # Overall health
        if len(health['issues']) > 3:
            health['overall_health'] = 'degraded'
        elif len(health['issues']) > 0:
            health['overall_health'] = 'partial'
        
        return health