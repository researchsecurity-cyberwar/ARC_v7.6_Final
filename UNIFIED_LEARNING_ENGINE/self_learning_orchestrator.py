"""
Self-Learning Orchestrator - Koordinator utama sistem pembelajaran
Module ini mengkoordinasikan semua komponen self-learning
"""

import time
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

from .experience_collector import ExperienceCollector, ExperienceType, OutcomeType
from .feedback_loop import FeedbackLoop
from .unified_model_trainer import UnifiedModelTrainer
from .dynamic_knowledge_base import DynamicKnowledgeBase


class SelfLearningOrchestrator:
    """
    Koordinator utama sistem pembelajaran mandiri
    Mengintegrasikan experience collection, feedback loop, model training, dan knowledge base
    """
    
    def __init__(self, base_dir="~/.arc/self_learning"):
        self.base_dir = os.path.expanduser(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)
        
        # Inisialisasi komponen
        self.experience_collector = ExperienceCollector()
        self.feedback_loop = FeedbackLoop()
        self.model_trainer = UnifiedModelTrainer()
        self.knowledge_base = DynamicKnowledgeBase()
        
        # State tracking
        self.learning_enabled = True
        self.auto_retrain_threshold = 10  # Retrain setelah 10 experience baru
        self.experiences_since_last_train = 0
        
        print("✅ Self-Learning Orchestrator initialized")
    
    def record_and_learn(self, experience_type: str, outcome: str,
                         context: Dict[str, Any], actions_taken: List[Dict],
                         result_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rekam experience dan trigger learning process
        
        Returns:
            Hasil learning process
        """
        result = {
            'experience_recorded': False,
            'feedback_generated': False,
            'model_updated': False,
            'knowledge_updated': False
        }
        
        try:
            # 1. Record experience
            experience_id = self.experience_collector.record_experience(
                experience_type=experience_type,
                outcome=outcome,
                context=context,
                actions_taken=actions_taken,
                result_data=result_data
            )
            result['experience_recorded'] = True
            result['experience_id'] = experience_id
            
            # 2. Generate feedback
            feedback_id = self._generate_feedback(experience_id, outcome, context, result_data)
            result['feedback_generated'] = True
            result['feedback_id'] = feedback_id
            
            # 3. Update knowledge base
            self._update_knowledge_base(experience_type, outcome, context, result_data)
            result['knowledge_updated'] = True
            
            # 4. Check if retraining needed
            self.experiences_since_last_train += 1
            if self.experiences_since_last_train >= self.auto_retrain_threshold:
                train_result = self.retrain_models()
                result['model_updated'] = train_result.get('models_trained', 0) > 0
                self.experiences_since_last_train = 0
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _generate_feedback(self, experience_id: str, outcome: str,
                           context: Dict[str, Any], result_data: Dict[str, Any]) -> str:
        """Generate feedback dari experience"""
        # Tentukan feedback type berdasarkan outcome
        if outcome == OutcomeType.SUCCESS.value:
            feedback_type = 'success'
            original_outcome = 'success'
            actual_outcome = 'success'
            impact_score = 0.8
        elif outcome == OutcomeType.FAILURE.value:
            feedback_type = 'failure'
            original_outcome = 'success'  # Expected success
            actual_outcome = 'failure'
            impact_score = 1.0
        else:
            feedback_type = 'improvement'
            original_outcome = outcome
            actual_outcome = outcome
            impact_score = 0.5
        
        correction_data = {
            'action': 'record_lesson',
            'lesson': result_data.get('lesson', 'No lesson identified'),
            'context': context
        }
        
        feedback_id = self.feedback_loop.record_feedback(
            experience_id=experience_id,
            feedback_type=feedback_type,
            original_outcome=original_outcome,
            actual_outcome=actual_outcome,
            context=context,
            correction_data=correction_data,
            impact_score=impact_score
        )
        
        return feedback_id
    
    def _update_knowledge_base(self, experience_type: str, outcome: str,
                               context: Dict[str, Any], result_data: Dict[str, Any]):
        """Update knowledge base dengan data baru"""
        # Record technique outcome
        technique = context.get('technique', experience_type)
        self.knowledge_base.record_technique_outcome(technique, outcome)
        
        # Add lesson jika ada
        if 'lesson' in result_data:
            self.knowledge_base.add_lesson(
                lesson=result_data['lesson'],
                context=context,
                importance=0.7 if outcome == OutcomeType.SUCCESS.value else 0.9
            )
        
        # Record CVE/CWE context if available
        if 'cve_id' in context or 'cwe_id' in context:
            vuln_info = {
                'cve_id': context.get('cve_id'),
                'cwe_id': context.get('cwe_id'),
                'severity': context.get('severity'),
                'exploitability': context.get('exploitability')
            }
            self.knowledge_base.add_technique_knowledge(technique, {'vulnerability_context': vuln_info})
        
        # Record failure mode jika gagal
        if outcome == OutcomeType.FAILURE.value:
            failure_type = result_data.get('error_type', 'unknown_failure')
            recovery = result_data.get('recovery', 'retry_with_different_params')
            self.knowledge_base.record_failure_mode(failure_type, context, recovery)
    
    def retrain_models(self) -> Dict[str, Any]:
        """Retrain model dengan experience terbaru"""
        # Dapatkan semua experiences
        experiences = self.experience_collector.experiences
        
        if not experiences:
            return {'message': 'No experiences to train on'}
        
        # Convert ke dict
        exp_dicts = [exp.to_dict() for exp in experiences]
        
        # Train model
        result = self.model_trainer.retrain_models(exp_dicts)
        
        return result
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """Dapatkan statistik pembelajaran"""
        exp_stats = self.experience_collector.analyze_patterns()
        feedback_stats = self.feedback_loop.analyze_feedback_patterns()
        model_stats = self.model_trainer.get_model_performance()
        kb_stats = self.knowledge_base.get_statistics()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'learning_enabled': self.learning_enabled,
            'experiences': exp_stats,
            'feedback': feedback_stats,
            'model': model_stats,
            'knowledge_base': kb_stats
        }
    
    def get_learning_recommendations(self, context: Dict[str, Any], 
                                     experience_type: str) -> Dict[str, Any]:
        """Dapatkan rekomendasi berdasarkan pembelajaran"""
        recommendations = {
            'success_probability': 0.5,
            'relevant_lessons': [],
            'suggested_techniques': [],
            'potential_failures': []
        }

        # Prediction: predict_success_probability() may return a dict
        # OR a float in various shapes. Normalize to a plain float here so
        # ALL downstream consumers (arc_main, closed_loop_feedback,
        # learning_mixin, xss_detector, dst) never see a dict. This is the
        # defense-in-depth fix for "TypeError: unsupported operand type(s)
        # for '*': 'dict' and 'int'".
        recommendations['success_probability'] = self._normalize_probability(
            self.model_trainer.predict_success_probability(context, experience_type)
        )

        # Get relevant lessons
        recommendations['relevant_lessons'] = self.knowledge_base.get_relevant_lessons(context)

        # Get potential failure modes
        failure_modes = self.knowledge_base.knowledge.get('failure_modes', {})
        if failure_modes:
            recommendations['potential_failures'] = list(failure_modes.keys())[:5]

        # Get suggested techniques from knowledge graph (safe fallback)
        try:
            techs = self.knowledge_base.knowledge.get('techniques', {})
            if isinstance(techs, dict):
                recommendations['suggested_techniques'] = list(techs.keys())[:5]
        except Exception:
            recommendations['suggested_techniques'] = []

        return recommendations
    
    @staticmethod
    def _normalize_probability(value: Any) -> float:
        """Konversi probabilitas apa pun (float, dict, str, None) menjadi float aman.

        Menangani berbagai bentuk yang mungkin dikembalikan oleh model trainer:
        - float / int langsung (0.7)
        - dict {'probability': 0.7}
        - dict {'success_probability': 0.7}
        - dict bersarang {'success_probability': {'probability': 0.7}}
        - None / string non-numeric -> default 0.5

        Ini mencegah TypeError "dict * int" di konsumen hilir (arc_main dkk).
        """
        default = 0.5
        def _extract(v):
            # Telusuri dict bertingkat sampai menemukan angka float/int
            depth = 0
            while isinstance(v, dict) and depth < 10:
                depth += 1
                if isinstance(v.get('probability'), (int, float)) and not isinstance(v.get('probability'), bool):
                    v = v['probability']
                elif isinstance(v.get('success_probability'), (int, float)) and not isinstance(v.get('success_probability'), bool):
                    v = v['success_probability']
                elif v.get('probability') is not None:
                    v = v['probability']
                elif v.get('success_probability') is not None:
                    v = v['success_probability']
                else:
                    return default
            return v

        extracted = _extract(value)
        try:
            prob = float(extracted)
            if prob < 0.0:
                return 0.0
            if prob > 1.0:
                return 1.0
            return prob
        except (TypeError, ValueError):
            return default
    
    def enable_learning(self):
        """Aktifkan self-learning"""
        self.learning_enabled = True
        print("✅ Self-learning enabled")
    
    def disable_learning(self):
        """Matikan self-learning"""
        self.learning_enabled = False
        print("⚠️ Self-learning disabled")
    
    def integrate_threat_intelligence(self, threat_data: Dict[str, Any]):
        """Integrasikan data ancaman (CVE/CWE) ke knowledge base"""
        if not threat_data:
            return
            
        print(f"📥 Integrating {len(threat_data.get('vulnerabilities', []))} threats into knowledge base")
        
        for vuln in threat_data.get('vulnerabilities', []):
            cve = vuln.get('cve', {})
            cve_id = cve.get('id')
            descriptions = cve.get('descriptions', [])
            desc_text = descriptions[0].get('value', '') if descriptions else ""
            
            # Map description to potential techniques
            potential_techniques = self._map_description_to_techniques(desc_text)
            
            for tech in potential_techniques:
                self.knowledge_base.add_technique_knowledge(tech, {
                    'related_cve': cve_id,
                    'threat_description': desc_text,
                    'last_seen_in_intel': time.time()
                })

    def _map_description_to_techniques(self, description: str) -> List[str]:
        """Mapping deskripsi CVE ke teknik internal (diperluas untuk semua bidang keamanan)"""
        tech_map = {
            # Web Security
            'xss': ['cross-site scripting', 'xss', 'reflected xss', 'stored xss', 'dom-based xss'],
            'sqli': ['sql injection', 'sqli', 'database query', 'blind sql'],
            'rce': ['remote code execution', 'rce', 'arbitrary code', 'code execution'],
            'ssrf': ['server-side request forgery', 'ssrf', 'request forgery'],
            'idor': ['insecure direct object reference', 'idor', 'access control bypass', 'broken access control'],
            'csrf': ['cross-site request forgery', 'csrf', 'xsrf'],
            'lfi': ['local file inclusion', 'lfi', 'file inclusion', 'path traversal'],
            'rfi': ['remote file inclusion', 'rfi'],
            'command_injection': ['command injection', 'os command', 'shell injection'],
            'backdoor': ['backdoor', 'webshell', 'hidden access'],
            'open_redirect': ['open redirect', 'url redirect'],
            'clickjacking': ['clickjacking', 'ui redress'],
            'file_upload': ['file upload', 'unrestricted upload'],
            'deserialization': ['deserialization', 'insecure deserialization'],
            'xxe': ['xml external entity', 'xxe', 'xml injection'],
            'ssti': ['server-side template injection', 'ssti', 'template injection'],
            'http_smuggling': ['request smuggling', 'http smuggling'],
            'host_header': ['host header injection', 'host header'],
            'cors': ['cross-origin resource sharing', 'cors misconfiguration'],
            'subdomain_takeover': ['subdomain takeover', 'dangling dns'],
            
            # API Security
            'bola': ['broken object level authorization', 'bola', 'object level authorization'],
            'bfa': ['broken function level authorization', 'bfa', 'function level authorization'],
            'mass_assignment': ['mass assignment', 'parameter binding'],
            'jwt': ['jwt', 'json web token', 'token validation'],
            'oauth': ['oauth', 'authorization flow', 'token leakage'],
            'rate_limiting': ['rate limiting', 'brute force', 'credential stuffing'],
            'api_key_leak': ['api key', 'secret key', 'credential exposure'],
            
            # Cloud Security
            's3_misconfig': ['s3 bucket', 'aws s3', 'cloud storage'],
            'gcp_bucket': ['gcp bucket', 'google cloud storage'],
            'azure_blob': ['azure blob', 'azure storage'],
            'cloud_metadata': ['cloud metadata', 'metadata service', 'imds'],
            'iam_misconfig': ['iam', 'identity and access management', 'privilege escalation'],
            'k8s': ['kubernetes', 'k8s', 'container orchestration'],
            'serverless': ['serverless', 'lambda', 'cloud function'],
            
            # Mobile Security
            'insecure_storage': ['insecure storage', 'data storage', 'sensitive data'],
            'hardcoded_secret': ['hardcoded', 'embedded secret', 'hardcoded credential'],
            'binary_analysis': ['binary analysis', 'reverse engineering', 'obfuscation'],
            'root_detection': ['root detection', 'jailbreak detection'],
            'ssl_pinning': ['ssl pinning', 'certificate pinning'],
            
            # Web3 / Smart Contract
            'reentrancy': ['reentrancy', 'smart contract', 'solidity'],
            'flash_loan': ['flash loan', 'price manipulation', 'oracle manipulation'],
            'integer_overflow': ['integer overflow', 'arithmetic overflow', 'underflow'],
            'access_control': ['access control', 'onlyowner', 'authorization bypass'],
            'tx_origin': ['tx.origin', 'transaction origin'],
            'delegatecall': ['delegatecall', 'proxy contract', 'upgradeable'],
            'gas_issue': ['gas limit', 'gas griefing', 'denial of service'],
            'front_running': ['front running', 'transaction ordering', 'mev'],
            'governance': ['governance attack', 'voting manipulation', 'proposal'],
            
            # AI Security
            'prompt_injection': ['prompt injection', 'jailbreak', 'instruction bypass'],
            'model_inversion': ['model inversion', 'training data extraction'],
            'data_leak': ['data leakage', 'information disclosure', 'sensitive information'],
            'llm_abuse': ['llm abuse', 'ai abuse', 'model abuse'],
            
            # Supply Chain
            'dependency': ['dependency', 'supply chain', 'package'],
            'typosquatting': ['typosquatting', 'malicious package', 'imposter package'],
            'logic_bomb': ['logic bomb', 'malicious code', 'backdoor code'],
            
            # Realtime / SPA
            'websocket': ['websocket', 'realtime', 'socket injection'],
            'prototype_pollution': ['prototype pollution', 'object pollution'],
            'dom_xss': ['dom xss', 'dom-based', 'client-side'],
            'session_fixation': ['session fixation', 'session hijacking', 'session management'],
            
            # MFA
            'mfa_bypass': ['mfa bypass', 'two-factor', '2fa', 'otp bypass'],
            
            # General
            'information_disclosure': ['information disclosure', 'information leak', 'sensitive data exposure'],
            'privilege_escalation': ['privilege escalation', 'permission bypass', 'authorization bypass'],
            'denial_of_service': ['denial of service', 'dos', 'resource exhaustion'],
            'buffer_overflow': ['buffer overflow', 'stack overflow', 'heap overflow'],
            'memory_corruption': ['memory corruption', 'use-after-free', 'double free'],
            'crypto_weakness': ['weak encryption', 'crypto weakness', 'insecure cipher'],
            'default_credentials': ['default credential', 'default password', 'weak password'],
            'misconfiguration': ['misconfiguration', 'security misconfiguration', 'improper configuration']
        }
        
        found = []
        desc_lower = description.lower()
        for tech, keywords in tech_map.items():
            if any(k in desc_lower for k in keywords):
                found.append(tech)
        return found
    
    def integrate_cwe_data(self, cwe_data: Dict[str, Any]):
        """Integrasikan data CWE ke knowledge base untuk memperkaya pemahaman teknik."""
        if not cwe_data:
            return
        
        weaknesses = cwe_data.get('weaknesses', [])
        if not weaknesses and cwe_data.get('error'):
            print(f"⚠️ CWE data has error: {cwe_data['error']} — 0 entries integrated")
        print(f"📥 Integrating {len(weaknesses)} CWE entries into knowledge base")
        
        for weakness in weaknesses:
            cwe_id = weakness.get('id', '')
            name = weakness.get('name', '')
            description = weakness.get('description', '')
            
            # Map CWE description to techniques
            potential_techniques = self._map_description_to_techniques(description)
            
            for tech in potential_techniques:
                self.knowledge_base.add_technique_knowledge(tech, {
                    'related_cwe': cwe_id,
                    'cwe_name': name,
                    'cwe_description': description[:500],
                    'last_seen_in_cwe': time.time()
                })
    
    def connect_detector_findings(self, detector_name: str, findings: List[Dict[str, Any]]):
        """
        Hubungkan temuan dari semua detektor ke self-learning.
        Setiap temuan direkam sebagai experience untuk pembelajaran berkelanjutan.
        """
        if not findings:
            return
        
        for finding in findings:
            # Extract vulnerability info
            vuln_type = finding.get('type', detector_name)
            cve_id = finding.get('cve_id')
            cwe_id = finding.get('cwe_id')
            severity = finding.get('severity', 'unknown')
            parameter = finding.get('parameter', '')
            payload = finding.get('payload', '')
            
            # Build context
            context = {
                'technique': vuln_type,
                'detector': detector_name,
                'severity': severity,
                'parameter': parameter,
                'cve_id': cve_id,
                'cwe_id': cwe_id
            }
            
            # Record as experience
            self.record_and_learn(
                experience_type="vulnerability_scan",
                outcome="success",
                context=context,
                actions_taken=[{
                    'type': 'detect',
                    'detector': detector_name,
                    'vulnerability_type': vuln_type
                }],
                result_data={
                    'finding': finding,
                    'lesson': f"Found {vuln_type} vulnerability via {detector_name}"
                }
            )
    
    def get_cve_context_for_technique(self, technique: str) -> List[Dict[str, Any]]:
        """Dapatkan konteks CVE yang relevan untuk teknik tertentu."""
        tech_data = self.knowledge_base.knowledge.get('techniques', {}).get(technique, {})
        data = tech_data.get('data', {})
        
        related_cves = []
        if 'related_cve' in data:
            related_cves.append({
                'cve_id': data['related_cve'],
                'description': data.get('threat_description', '')
            })
        
        return related_cves

    def save_state(self):
        """Simpan state semua komponen"""
        self.experience_collector.save_experiences()
        self.feedback_loop.save_feedback()
        self.knowledge_base.save_knowledge()
        print("💾 Self-learning state saved")
    
    def load_state(self):
        """Muat state semua komponen"""
        self.experience_collector.load_persistent_experiences()
        self.feedback_loop.load_feedback()
        self.model_trainer.load_models()
        self.knowledge_base.load_knowledge()
        print("📂 Self-learning state loaded")
