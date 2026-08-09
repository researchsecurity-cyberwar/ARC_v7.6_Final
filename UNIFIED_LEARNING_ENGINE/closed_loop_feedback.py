"""
Closed-Loop Feedback System - Integrasi SovereignReasoner dengan Self-Learning
Menciptakan loop dimana AI reasoning dan learning saling memperkuat
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime


class ClosedLoopFeedback:
    """
    Closed-loop feedback system yang menghubungkan SovereignReasoner dengan Self-Learning
    """

    def __init__(self, base_dir="~/.arc/self_learning"):
        self.base_dir = os.path.expanduser(base_dir)
        self.feedback_log_file = os.path.join(self.base_dir, "closed_loop_feedback.json")
        
        self.sovereign_reasoner = None
        self.feature_extractor = None
        self.lesson_generator = None
        self.orchestrator = None
        
        self.feedback_loop_log = []
        
        # Initialize components
        self._init_components()
    
    def _init_components(self):
        """Initialize komponen yang dibutuhkan"""
        try:
            from COGNITIVE_CORE.sovereign_reasoner import SovereignReasoner
            self.sovereign_reasoner = SovereignReasoner()
            print("✅ ClosedLoopFeedback connected to SovereignReasoner")
        except Exception as e:
            print(f"⚠️ SovereignReasoner not available: {e}")
        
        try:
            from .ai_feature_extractor import AIFeatureExtractor
            self.feature_extractor = AIFeatureExtractor()
        except Exception as e:
            print(f"⚠️ AIFeatureExtractor not available: {e}")
        
        try:
            from .ai_lesson_generator import AILessonGenerator
            self.lesson_generator = AILessonGenerator()
        except Exception as e:
            print(f"⚠️ AILessonGenerator not available: {e}")
        
        # Load existing feedback log
        self._load_feedback_log()
    
    def integrate_with_orchestrator(self, orchestrator):
        """
        Integrate closed-loop feedback dengan SelfLearningOrchestrator
        
        Args:
            orchestrator: SelfLearningOrchestrator instance
        """
        self.orchestrator = orchestrator
        print("🔗 Closed-loop feedback integrated with orchestrator")
    
    def process_experience_with_ai(self, experience: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process experience menggunakan AI closed-loop
        
        Args:
            experience: Experience dict dari ExperienceCollector
            
        Returns:
            Enhanced experience dengan AI insights
        """
        if not self.sovereign_reasoner:
            return experience
        
        try:
            # Extract context dan outcome
            context = experience.get('context', {})
            outcome = experience.get('outcome', 'unknown')
            result_data = experience.get('result_data', {})
            
            # Step 1: AI Feature Extraction
            enhanced_context = self._ai_enhance_context(context)
            
            # Step 2: AI-Powered Analysis
            ai_analysis = self._ai_analyze_experience(enhanced_context, outcome, result_data)
            
            # Step 3: Generate AI Lessons
            ai_lessons = self._generate_ai_lessons(enhanced_context, outcome, result_data)
            
            # Step 4: Update predictions
            predictions = self._update_predictions(enhanced_context, outcome)
            
            # Combine everything
            enhanced_experience = {
                **experience,
                'context': enhanced_context,
                'ai_analysis': ai_analysis,
                'ai_lessons': ai_lessons,
                'predictions': predictions,
                'closed_loop_processed': True,
                'processed_at': datetime.now().isoformat()
            }
            
            # Log feedback
            self._log_feedback_activity('process_experience', {
                'experience_id': experience.get('experience_id'),
                'outcome': outcome,
                'ai_features_extracted': len(enhanced_context),
                'lessons_generated': len(ai_lessons)
            })
            
            return enhanced_experience
            
        except Exception as e:
            print(f"⚠️ Closed-loop processing failed: {e}")
            return experience
    
    def _ai_enhance_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance context dengan AI-extracted features"""
        if not self.feature_extractor:
            return context
        
        # Extract features menggunakan AI
        features = self.feature_extractor.extract_features(context)
        
        # Merge dengan original context
        enhanced = {**context, **features}
        
        return enhanced
    
    def _ai_analyze_experience(self, context: Dict, outcome: str, result_data: Dict) -> Dict[str, Any]:
        """Analyze experience menggunakan SovereignReasoner"""
        if not self.sovereign_reasoner:
            return {}
        
        try:
            vuln_type = context.get('technique', 'unknown')
            severity = context.get('impact_severity', context.get('severity', 'medium'))
            
            prompt = f"""<s>[INST]
You are an expert analyst reviewing a vulnerability detection experience.

Experience Details:
- Vulnerability Type: {vuln_type}
- Severity: {severity}
- Outcome: {outcome}
- Context: {json.dumps(context, indent=2)}

Provide a brief strategic analysis:
1. What went well or wrong
2. Key insights for future detections
3. Patterns to watch for

Keep it concise (max 200 words).
[/INST]"""
            
            response = self.sovereign_reasoner.llm(
                prompt,
                max_tokens=256,
                temperature=0.3,
                top_p=0.9
            )
            
            analysis_text = response["choices"][0]["text"].strip()
            
            return {
                'strategic_analysis': analysis_text,
                'analyzed_at': datetime.now().isoformat(),
                'model_used': 'mistral-7b-instruct'
            }
            
        except Exception as e:
            print(f"⚠️ AI analysis failed: {e}")
            return {}
    
    def _generate_ai_lessons(self, context: Dict, outcome: str, result_data: Dict) -> List[Dict]:
        """Generate lessons menggunakan AI"""
        if not self.lesson_generator:
            return []
        
        lessons = []
        
        try:
            if outcome == 'failure':
                # Generate lesson dari failure
                failure_data = {**context, **result_data}
                lesson = self.lesson_generator.generate_lesson_from_failure(failure_data)
                lessons.append(lesson)
            elif outcome == 'success':
                # Generate best practice dari success
                success_data = {**context, **result_data}
                lesson = self.lesson_generator.generate_lesson_from_success(success_data)
                lessons.append(lesson)
        except Exception as e:
            print(f"⚠️ AI lesson generation failed: {e}")
        
        return lessons
    
    def _update_predictions(self, context: Dict, outcome: str) -> Dict[str, Any]:
        """Update predictions berdasarkan experience"""
        vuln_type = context.get('technique', 'unknown')
        
        predictions = {
            'future_success_probability': 0.5,
            'confidence': 0.0,
            'recommendations': []
        }
        
        # Simple prediction logic
        if outcome == 'success':
            predictions['future_success_probability'] = 0.8
            predictions['confidence'] = 0.7
            predictions['recommendations'].append(f"Continue using current approach for {vuln_type}")
        else:
            predictions['future_success_probability'] = 0.4
            predictions['confidence'] = 0.6
            predictions['recommendations'].append(f"Review and adjust approach for {vuln_type}")
        
        return predictions
    
    def ai_guided_detection(self, detector_name: str, target_info: Dict) -> Dict[str, Any]:
        """
        Get AI guidance untuk detection
        
        Args:
            detector_name: Name of detector
            target_info: Target information
            
        Returns:
            AI guidance dict
        """
        if not self.sovereign_reasoner or not self.orchestrator:
            return {'error': 'AI or orchestrator not available'}
        
        try:
            # Get relevant lessons dari orchestrator
            recommendations = self.orchestrator.get_learning_recommendations(
                target_info, detector_name
            )
            
            # Build prompt untuk AI guidance
            prompt = f"""<s>[INST]
You are an expert bug bounty hunter advising a detection system.

Detector: {detector_name}
Target Info: {json.dumps(target_info, indent=2)}

Historical Recommendations:
- Success Probability: {recommendations.get('success_probability', 0.5)}
- Relevant Lessons: {', '.join(recommendations.get('relevant_lessons', [])[:3])}
- Potential Failures: {', '.join(recommendations.get('potential_failures', [])[:3])}

Provide tactical guidance:
1. Recommended approach
2. Payload strategies
3. Things to watch out for
4. Success indicators

Keep it actionable and concise.
[/INST]"""
            
            response = self.sovereign_reasoner.llm(
                prompt,
                max_tokens=512,
                temperature=0.4,
                top_p=0.9
            )
            
            ai_guidance = response["choices"][0]["text"].strip()
            
            return {
                'detector': detector_name,
                'target': target_info,
                'ai_guidance': ai_guidance,
                'historical_recommendations': recommendations,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ AI-guided detection failed: {e}")
            return {'error': str(e)}
    
    def closed_loop_learning_cycle(self, new_experiences: List[Dict]) -> Dict[str, Any]:
        """
        Execute closed-loop learning cycle
        
        Args:
            new_experiences: List of new experiences to process
            
        Returns:
            Learning cycle results
        """
        if not self.orchestrator:
            return {'error': 'Orchestrator not integrated'}
        
        print("🔄 Starting closed-loop learning cycle...")
        
        results = {
            'processed': 0,
            'enhanced': 0,
            'lessons_generated': 0,
            'models_updated': False,
            'feedback_loops_closed': 0
        }
        
        # Process each experience
        for exp in new_experiences:
            # Enhance with AI
            enhanced = self.process_experience_with_ai(exp)
            results['processed'] += 1
            
            if enhanced.get('closed_loop_processed'):
                results['enhanced'] += 1
                results['lessons_generated'] += len(enhanced.get('ai_lessons', []))
        
        # Trigger retraining if needed
        if self.orchestrator:
            train_result = self.orchestrator.retrain_models()
            results['models_updated'] = train_result.get('models_trained', 0) > 0
            results['model_details'] = train_result
        
        # Export feedback
        results['exported_training_data'] = self.export_training_data()
        
        # Log cycle
        self._log_feedback_activity('learning_cycle', results)
        
        print(f"✅ Closed-loop cycle completed: {results['processed']} processed, {results['lessons_generated']} lessons")
        
        return results
    
    def export_training_data(self) -> str:
        """Export closed-loop enhanced data untuk training"""
        if not self.feedback_loop_log:
            return ""
        
        timestamp = int(datetime.now().timestamp())
        export_file = os.path.join(self.base_dir, f"closed_loop_training_{timestamp}.jsonl")
        
        try:
            with open(export_file, 'w') as f:
                for entry in self.feedback_loop_log:
                    if entry.get('activity') == 'process_experience':
                        training_example = {
                            'experience_id': entry.get('data', {}).get('experience_id'),
                            'outcome': entry.get('data', {}).get('outcome'),
                            'timestamp': entry.get('timestamp'),
                            'type': 'closed_loop_processed'
                        }
                        f.write(json.dumps(training_example) + '\n')
            
            return export_file
        except Exception as e:
            print(f"⚠️ Failed to export training data: {e}")
            return ""
    
    def _log_feedback_activity(self, activity: str, data: Dict):
        """Log feedback activity"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'activity': activity,
            'data': data
        }
        
        self.feedback_loop_log.append(log_entry)
        self._save_feedback_log()
    
    def _save_feedback_log(self):
        """Save feedback log to disk"""
        try:
            os.makedirs(self.base_dir, exist_ok=True)
            with open(self.feedback_log_file, 'w') as f:
                json.dump(self.feedback_loop_log, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save feedback log: {e}")
    
    def _load_feedback_log(self):
        """Load feedback log from disk"""
        try:
            if os.path.exists(self.feedback_log_file):
                with open(self.feedback_log_file, 'r') as f:
                    self.feedback_loop_log = json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to load feedback log: {e}")
    
    def get_closed_loop_statistics(self) -> Dict[str, Any]:
        """Get closed-loop statistics"""
        total_processed = len([l for l in self.feedback_loop_log if l.get('activity') == 'process_experience'])
        total_cycles = len([l for l in self.feedback_loop_log if l.get('activity') == 'learning_cycle'])
        
        return {
            'total_experiences_processed': total_processed,
            'total_learning_cycles': total_cycles,
            'sovereign_reasoner_available': self.sovereign_reasoner is not None,
            'feature_extractor_available': self.feature_extractor is not None,
            'lesson_generator_available': self.lesson_generator is not None,
            'orchestrator_integrated': self.orchestrator is not None,
            'feedback_log_size': len(self.feedback_loop_log)
        }
    
    def validate_closed_loop_effectiveness(self) -> Dict[str, Any]:
        """
        Validate effectiveness of closed-loop feedback
        
        Returns:
            Validation metrics
        """
        # Calculate metrics dari feedback log
        experiences = [l for l in self.feedback_loop_log if l.get('activity') == 'process_experience']
        
        if not experiences:
            return {
                'status': 'no_data',
                'message': 'No closed-loop data available yet'
            }
        
        # Calculate improvement over time
        total = len(experiences)
        ai_enhanced = len([e for e in experiences if e.get('data', {}).get('ai_features_extracted', 0) > 0])
        
        return {
            'status': 'active',
            'total_experiences': total,
            'ai_enhanced': ai_enhanced,
            'enhancement_rate': ai_enhanced / total if total > 0 else 0.0,
            'feedback_loop_health': 'healthy' if self.sovereign_reasoner else 'degraded'
        }