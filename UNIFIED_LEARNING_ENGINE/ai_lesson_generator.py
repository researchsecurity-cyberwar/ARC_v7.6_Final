"""
AI Lesson Generator - Generate intelligent lessons using SovereignReasoner
Menggunakan Mistral AI untuk generate actionable lessons dari failures dan successes
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime


class AILessonGenerator:
    """
    AI-powered lesson generation menggunakan SovereignReasoner
    """

    def __init__(self, base_dir="~/.arc/self_learning"):
        self.base_dir = os.path.expanduser(base_dir)
        self.sovereign_reasoner = None
        self.lesson_history = []
        self.lesson_cache_file = os.path.join(self.base_dir, "ai_generated_lessons.json")
        
        # Try to initialize SovereignReasoner
        self._init_reasoner()
    
    def _init_reasoner(self):
        """Initialize SovereignReasoner jika tersedia"""
        try:
            from COGNITIVE_CORE.sovereign_reasoner import SovereignReasoner
            self.sovereign_reasoner = SovereignReasoner()
            print("✅ AI Lesson Generator connected to SovereignReasoner")
        except Exception as e:
            print(f"⚠️ SovereignReasoner not available: {e}")
            self.sovereign_reasoner = None
    
    def generate_lesson_from_failure(self, failure_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate actionable lesson dari failure data menggunakan AI
        
        Args:
            failure_data: Dict berisi info tentang failure
            
        Returns:
            Dict berisi lesson yang di-generate
        """
        if not self.sovereign_reasoner:
            return self._fallback_lesson_generation(failure_data)
        
        try:
            # Build prompt untuk lesson generation
            prompt = self._build_lesson_prompt(failure_data)
            
            # Call AI
            response = self.sovereign_reasoner.llm(
                prompt,
                max_tokens=768,
                temperature=0.4,
                top_p=0.9,
                repeat_penalty=1.1
            )
            
            # Parse response
            ai_output = response["choices"][0]["text"].strip()
            lesson = self._parse_ai_lesson(ai_output, failure_data)
            
            # Cache lesson
            self._cache_lesson(lesson)
            
            return lesson
            
        except Exception as e:
            print(f"⚠️ AI lesson generation failed: {e}")
            return self._fallback_lesson_generation(failure_data)
    
    def _build_lesson_prompt(self, failure_data: Dict) -> str:
        """Build prompt untuk AI lesson generation"""
        vuln_type = failure_data.get('technique', 'unknown')
        error_type = failure_data.get('error_type', 'unknown_error')
        detector = failure_data.get('detector', 'unknown')
        target = failure_data.get('target_info', 'N/A')
        severity = failure_data.get('severity', 'medium')
        
        prompt = f"""<s>[INST]
You are an expert cybersecurity analyst and educator. A bug bounty detection system (ARC) failed to detect a vulnerability. Analyze this failure and generate an actionable lesson.

Failure Details:
- Vulnerability Type: {vuln_type}
- Error Type: {error_type}
- Detector Used: {detector}
- Target: {target}
- Severity: {severity}

Generate a comprehensive lesson in JSON format:
{{
    "lesson_title": "Brief descriptive title",
    "root_cause": "Technical explanation of why the detection failed",
    "corrective_actions": [
        "Action 1: Specific step to fix",
        "Action 2: Another specific step"
    ],
    "detection_strategy_improvements": [
        "Improvement 1: How to enhance detection",
        "Improvement 2: Alternative approach"
    ],
    "preventive_measures": [
        "Measure 1: How to avoid this failure in future",
        "Measure 2: Testing/validation approach"
    ],
    "related_techniques": ["technique1", "technique2"],
    "severity_impact": "low/medium/high",
    "remediation_priority": 1-10,
    "example_payload_or_approach": "Concrete example of improved detection",
    "references": ["CWE-XXX", "OWASP-XXX"]
}}

Provide ONLY valid JSON, no explanations.
[/INST]"""
        
        return prompt
    
    def _parse_ai_lesson(self, ai_output: str, failure_data: Dict) -> Dict[str, Any]:
        """Parse AI output into structured lesson"""
        try:
            # Extract JSON dari response
            json_start = ai_output.find('{')
            json_end = ai_output.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = ai_output[json_start:json_end]
                ai_lesson = json.loads(json_str)
            else:
                ai_lesson = {}
            
            # Structure lesson
            lesson = {
                # Core lesson data
                'lesson_id': f"lesson_{int(datetime.now().timestamp())}",
                'generated_at': datetime.now().isoformat(),
                'generation_method': 'ai',
                
                # Content
                'lesson_title': ai_lesson.get('lesson_title', f"Lesson: {failure_data.get('technique', 'unknown')}"),
                'root_cause': ai_lesson.get('root_cause', 'Detection failed due to unknown reason'),
                'corrective_actions': ai_lesson.get('corrective_actions', []),
                'detection_strategy_improvements': ai_lesson.get('detection_strategy_improvements', []),
                'preventive_measures': ai_lesson.get('preventive_measures', []),
                'related_techniques': ai_lesson.get('related_techniques', []),
                'severity_impact': ai_lesson.get('severity_impact', 'medium'),
                'remediation_priority': ai_lesson.get('remediation_priority', 5),
                'example_payload_or_approach': ai_lesson.get('example_payload_or_approach', ''),
                'references': ai_lesson.get('references', []),
                
                # Context
                'source_failure': failure_data,
                'technique': failure_data.get('technique'),
                'detector': failure_data.get('detector'),
                'error_type': failure_data.get('error_type'),
                
                # Metadata
                'applied_count': 0,
                'success_count': 0,
                'effectiveness_score': 0.0
            }
            
            return lesson
            
        except Exception as e:
            print(f"⚠️ Failed to parse AI lesson: {e}")
            return self._fallback_lesson_generation(failure_data)
    
    def _fallback_lesson_generation(self, failure_data: Dict) -> Dict[str, Any]:
        """Fallback lesson generation tanpa AI"""
        vuln_type = failure_data.get('technique', 'unknown')
        error_type = failure_data.get('error_type', 'unknown')
        detector = failure_data.get('detector', 'unknown')
        
        return {
            'lesson_id': f"lesson_{int(datetime.now().timestamp())}",
            'generated_at': datetime.now().isoformat(),
            'generation_method': 'fallback',
            
            'lesson_title': f"Detection Failure: {vuln_type} via {detector}",
            'root_cause': f"Failed to detect {vuln_type}. Error: {error_type}",
            'corrective_actions': [
                f"Review {detector} configuration parameters",
                f"Adjust payload generation for {vuln_type}",
                "Check for WAF/IDS evasion requirements"
            ],
            'detection_strategy_improvements': [
                f"Implement adaptive payloads for {vuln_type}",
                "Add context-aware detection logic",
                "Enhance error handling and retry mechanisms"
            ],
            'preventive_measures': [
                "Add pre-detection validation",
                "Implement multi-vector detection",
                "Test with various payload encodings"
            ],
            'related_techniques': [vuln_type],
            'severity_impact': 'medium',
            'remediation_priority': 5,
            'example_payload_or_approach': 'N/A',
            'references': [],
            
            'source_failure': failure_data,
            'technique': vuln_type,
            'detector': detector,
            'error_type': error_type,
            
            'applied_count': 0,
            'success_count': 0,
            'effectiveness_score': 0.0
        }
    
    def generate_lesson_from_success(self, success_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate best practice lesson dari successful detection
        
        Args:
            success_data: Dict berisi info tentang successful detection
            
        Returns:
            Dict berisi best practice lesson
        """
        if not self.sovereign_reasoner:
            return self._fallback_success_lesson(success_data)
        
        try:
            prompt = self._build_success_lesson_prompt(success_data)
            
            response = self.sovereign_reasoner.llm(
                prompt,
                max_tokens=512,
                temperature=0.3,
                top_p=0.9,
                repeat_penalty=1.1
            )
            
            ai_output = response["choices"][0]["text"].strip()
            lesson = self._parse_success_lesson(ai_output, success_data)
            
            self._cache_lesson(lesson)
            return lesson
            
        except Exception as e:
            print(f"⚠️ AI success lesson generation failed: {e}")
            return self._fallback_success_lesson(success_data)
    
    def _build_success_lesson_prompt(self, success_data: Dict) -> str:
        """Build prompt untuk success lesson generation"""
        vuln_type = success_data.get('technique', 'unknown')
        detector = success_data.get('detector', 'unknown')
        target = success_data.get('target_info', 'N/A')
        payload = success_data.get('payload', 'N/A')
        
        prompt = f"""<s>[INST]
You are an expert cybersecurity analyst. A bug bounty detection system (ARC) successfully detected a vulnerability. Analyze this success and extract best practices.

Success Details:
- Vulnerability Type: {vuln_type}
- Detector Used: {detector}
- Target: {target}
- Payload/Approach: {payload}

Generate best practices in JSON format:
{{
    "best_practice_title": "Brief title",
    "key_success_factors": [
        "Factor 1: What made this detection successful",
        "Factor 2: Critical element"
    ],
    "replicable_patterns": [
        "Pattern 1: How to replicate this success",
        "Pattern 2: Detection strategy"
    ],
    "optimal_conditions": [
        "Condition 1: When this approach works best",
        "Condition 2: Target characteristics"
    ],
    "generalization_advice": "How to apply this to other targets",
    "confidence_score": 0.0-1.0,
    "reusability": "high/medium/low"
}}

Provide ONLY valid JSON, no explanations.
[/INST]"""
        
        return prompt
    
    def _parse_success_lesson(self, ai_output: str, success_data: Dict) -> Dict[str, Any]:
        """Parse AI success lesson output"""
        try:
            json_start = ai_output.find('{')
            json_end = ai_output.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = ai_output[json_start:json_end]
                ai_lesson = json.loads(json_str)
            else:
                ai_lesson = {}
            
            return {
                'lesson_id': f"best_practice_{int(datetime.now().timestamp())}",
                'generated_at': datetime.now().isoformat(),
                'generation_method': 'ai',
                'lesson_type': 'best_practice',
                
                'best_practice_title': ai_lesson.get('best_practice_title', f"Success: {success_data.get('technique')}"),
                'key_success_factors': ai_lesson.get('key_success_factors', []),
                'replicable_patterns': ai_lesson.get('replicable_patterns', []),
                'optimal_conditions': ai_lesson.get('optimal_conditions', []),
                'generalization_advice': ai_lesson.get('generalization_advice', ''),
                'confidence_score': ai_lesson.get('confidence_score', 0.8),
                'reusability': ai_lesson.get('reusability', 'high'),
                
                'source_success': success_data,
                'technique': success_data.get('technique'),
                'detector': success_data.get('detector'),
                
                'applied_count': 0,
                'success_count': 0,
                'effectiveness_score': 0.0
            }
            
        except Exception as e:
            print(f"⚠️ Failed to parse success lesson: {e}")
            return self._fallback_success_lesson(success_data)
    
    def _fallback_success_lesson(self, success_data: Dict) -> Dict[str, Any]:
        """Fallback success lesson generation"""
        vuln_type = success_data.get('technique', 'unknown')
        detector = success_data.get('detector', 'unknown')
        
        return {
            'lesson_id': f"best_practice_{int(datetime.now().timestamp())}",
            'generated_at': datetime.now().isoformat(),
            'generation_method': 'fallback',
            'lesson_type': 'best_practice',
            
            'best_practice_title': f"Successful {vuln_type} Detection",
            'key_success_factors': [
                f"Effective use of {detector}",
                f"Proper payload selection for {vuln_type}"
            ],
            'replicable_patterns': [
                f"Apply {detector} for similar {vuln_type} vulnerabilities",
                "Use context-aware payload generation"
            ],
            'optimal_conditions': [
                f"Target uses {vuln_type} vulnerable patterns",
                "Standard web application stack"
            ],
            'generalization_advice': f"Apply {detector} to similar targets with {vuln_type} potential",
            'confidence_score': 0.7,
            'reusability': 'high',
            
            'source_success': success_data,
            'technique': vuln_type,
            'detector': detector,
            
            'applied_count': 0,
            'success_count': 0,
            'effectiveness_score': 0.0
        }
    
    def batch_generate_lessons(self, experiences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate lessons untuk batch of experiences
        
        Args:
            experiences: List of experience dicts
            
        Returns:
            List of generated lessons
        """
        lessons = []
        
        for exp in experiences:
            outcome = exp.get('outcome', 'unknown')
            context = exp.get('context', {})
            result_data = exp.get('result_data', {})
            
            # Combine context dan result_data
            data = {**context, **result_data}
            
            if outcome == 'failure':
                lesson = self.generate_lesson_from_failure(data)
                lessons.append(lesson)
            elif outcome == 'success':
                lesson = self.generate_lesson_from_success(data)
                lessons.append(lesson)
        
        return lessons
    
    def _cache_lesson(self, lesson: Dict[str, Any]):
        """Cache lesson untuk avoid regeneration"""
        self.lesson_history.append(lesson)
        
        # Save to disk periodically
        if len(self.lesson_history) % 10 == 0:
            self._save_lesson_history()
    
    def _save_lesson_history(self):
        """Save lesson history to disk"""
        try:
            os.makedirs(self.base_dir, exist_ok=True)
            with open(self.lesson_cache_file, 'w') as f:
                json.dump(self.lesson_history, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save lesson history: {e}")
    
    def load_lesson_history(self):
        """Load lesson history from disk"""
        try:
            if os.path.exists(self.lesson_cache_file):
                with open(self.lesson_cache_file, 'r') as f:
                    self.lesson_history = json.load(f)
                print(f"📂 Loaded {len(self.lesson_history)} cached lessons")
        except Exception as e:
            print(f"⚠️ Failed to load lesson history: {e}")
    
    def update_lesson_effectiveness(self, lesson_id: str, applied: bool, success: bool):
        """
        Update lesson effectiveness based on real-world application
        
        Args:
            lesson_id: ID of the lesson
            applied: Whether the lesson was applied
            success: Whether application led to success
        """
        for lesson in self.lesson_history:
            if lesson.get('lesson_id') == lesson_id:
                lesson['applied_count'] += 1
                if success:
                    lesson['success_count'] += 1
                
                # Update effectiveness score
                if lesson['applied_count'] > 0:
                    lesson['effectiveness_score'] = lesson['success_count'] / lesson['applied_count']
                
                break
    
    def get_top_lessons(self, technique: str = None, min_effectiveness: float = 0.0,
                       limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top lessons berdasarkan effectiveness
        
        Args:
            technique: Filter by technique (optional)
            min_effectiveness: Minimum effectiveness score
            limit: Maximum number of lessons to return
            
        Returns:
            List of top lessons
        """
        filtered = self.lesson_history
        
        # Filter by technique
        if technique:
            filtered = [l for l in filtered if l.get('technique') == technique]
        
        # Filter by effectiveness
        filtered = [l for l in filtered if l.get('effectiveness_score', 0.0) >= min_effectiveness]
        
        # Sort by effectiveness
        sorted_lessons = sorted(filtered, key=lambda x: x.get('effectiveness_score', 0.0), reverse=True)
        
        return sorted_lessons[:limit]
    
    def get_lesson_statistics(self) -> Dict[str, Any]:
        """Get statistics tentang generated lessons"""
        total = len(self.lesson_history)
        ai_generated = len([l for l in self.lesson_history if l.get('generation_method') == 'ai'])
        fallback = len([l for l in self.lesson_history if l.get('generation_method') == 'fallback'])
        
        avg_effectiveness = 0.0
        if self.lesson_history:
            avg_effectiveness = sum(l.get('effectiveness_score', 0.0) for l in self.lesson_history) / total
        
        return {
            'total_lessons': total,
            'ai_generated': ai_generated,
            'fallback_generated': fallback,
            'average_effectiveness': avg_effectiveness,
            'most_effective': self.get_top_lessons(limit=1)[0] if self.lesson_history else None,
            'least_effective': self.get_top_lessons(limit=1)[-1] if self.lesson_history else None
        }
    
    def export_lessons_for_training(self, output_file: str = None) -> str:
        """
        Export lessons untuk use dalam training data
        
        Args:
            output_file: Output file path (optional)
            
        Returns:
            Path ke exported file
        """
        if not output_file:
            timestamp = int(datetime.now().timestamp())
            output_file = os.path.join(self.base_dir, f"exported_lessons_{timestamp}.jsonl")
        
        try:
            with open(output_file, 'w') as f:
                for lesson in self.lesson_history:
                    # Convert to training format
                    training_example = {
                        "instruction": f"Generate a lesson for {lesson.get('technique', 'unknown')} failure",
                        "output": f"Title: {lesson.get('lesson_title')}\n\n"
                                  f"Root Cause: {lesson.get('root_cause')}\n\n"
                                  f"Corrective Actions: {'; '.join(lesson.get('corrective_actions', []))}\n\n"
                                  f"Strategy Improvements: {'; '.join(lesson.get('detection_strategy_improvements', []))}"
                    }
                    f.write(json.dumps(training_example) + '\n')
            
            return output_file
            
        except Exception as e:
            print(f"⚠️ Failed to export lessons: {e}")
            return ""