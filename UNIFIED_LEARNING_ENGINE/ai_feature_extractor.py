"""
AI Feature Extractor - Extract intelligent features using SovereignReasoner
Menggunakan Mistral AI untuk extract features dari vulnerability context
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime


class AIFeatureExtractor:
    """
    AI-powered feature extraction menggunakan SovereignReasoner
    """

    def __init__(self, base_dir="~/.arc/self_learning"):
        self.base_dir = os.path.expanduser(base_dir)
        self.sovereign_reasoner = None
        self.feature_cache = {}
        self.cache_file = os.path.join(self.base_dir, "feature_cache.json")
        
        # Try to initialize SovereignReasoner
        self._init_reasoner()
    
    def _init_reasoner(self):
        """Initialize SovereignReasoner jika tersedia"""
        try:
            from COGNITIVE_CORE.sovereign_reasoner import SovereignReasoner
            self.sovereign_reasoner = SovereignReasoner()
            print("✅ AI Feature Extractor connected to SovereignReasoner")
        except Exception as e:
            print(f"⚠️ SovereignReasoner not available: {e}")
            self.sovereign_reasoner = None
    
    def extract_features(self, vulnerability_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract features dari vulnerability context menggunakan AI
        
        Args:
            vulnerability_context: Dict berisi info vulnerability
            
        Returns:
            Dict berisi features yang diextract
        """
        if not self.sovereign_reasoner:
            return self._fallback_feature_extraction(vulnerability_context)
        
        # Check cache dulu
        cache_key = self._generate_cache_key(vulnerability_context)
        if cache_key in self.feature_cache:
            return self.feature_cache[cache_key]
        
        # Extract features menggunakan AI
        features = self._ai_extract_features(vulnerability_context)
        
        # Cache hasil
        self.feature_cache[cache_key] = features
        self._save_cache()
        
        return features
    
    def _ai_extract_features(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features menggunakan SovereignReasoner"""
        try:
            # Build prompt untuk feature extraction
            prompt = self._build_feature_extraction_prompt(context)
            
            # Call AI
            response = self.sovereign_reasoner.llm(
                prompt,
                max_tokens=512,
                temperature=0.3,  # Low temperature untuk consistent output
                top_p=0.9,
                repeat_penalty=1.1
            )
            
            # Parse response
            ai_output = response["choices"][0]["text"].strip()
            features = self._parse_ai_features(ai_output, context)
            
            return features
            
        except Exception as e:
            print(f"⚠️ AI feature extraction failed: {e}")
            return self._fallback_feature_extraction(context)
    
    def _build_feature_extraction_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt untuk AI feature extraction"""
        vuln_type = context.get('technique', 'unknown')
        severity = context.get('severity', 'unknown')
        target_info = context.get('target_info', 'N/A')
        description = context.get('description', context.get('lesson', ''))
        
        prompt = f"""<s>[INST]
You are an expert vulnerability analyst. Analyze this vulnerability and extract structured features.

Vulnerability Type: {vuln_type}
Severity: {severity}
Target: {target_info}
Description: {description}

Extract and provide ONLY a JSON object with these exact fields:
{{
    "technique_category": "web/api/cloud/mobile/web3/ai/supply_chain/realtime/mfa/general",
    "exploitability_score": 0.0-1.0,
    "impact_severity": "critical/high/medium/low/info",
    "attack_complexity": "low/medium/high",
    "required_privileges": "none/low/high",
    "user_interaction": "none/required",
    "detection_difficulty": "easy/medium/hard",
    "remediation_priority": 1-10,
    "business_impact_areas": ["confidentiality", "integrity", "availability", "financial", "reputation"],
    "attack_vector": "network/adjacent/physical/local",
    "affected_components": ["component1", "component2"],
    "root_cause": "brief technical root cause",
    "key_weakness": "OWASP/CWE category"
}}

Provide ONLY valid JSON, no explanations.
[/INST]"""
        
        return prompt
    
    def _parse_ai_features(self, ai_output: str, original_context: Dict) -> Dict[str, Any]:
        """Parse AI output into structured features"""
        try:
            # Extract JSON dari response
            json_start = ai_output.find('{')
            json_end = ai_output.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = ai_output[json_start:json_end]
                ai_features = json.loads(json_str)
            else:
                ai_features = {}
            
            # Combine dengan original context
            features = {
                # Original context
                'original_technique': original_context.get('technique'),
                'original_severity': original_context.get('severity'),
                'detector': original_context.get('detector'),
                
                # AI-extracted features
                'technique_category': ai_features.get('technique_category', self._categorize_technique(original_context.get('technique', ''))),
                'exploitability_score': ai_features.get('exploitability_score', self._estimate_exploitability(original_context)),
                'impact_severity': ai_features.get('impact_severity', original_context.get('severity', 'medium')),
                'attack_complexity': ai_features.get('attack_complexity', 'medium'),
                'required_privileges': ai_features.get('required_privileges', 'none'),
                'user_interaction': ai_features.get('user_interaction', 'none'),
                'detection_difficulty': ai_features.get('detection_difficulty', 'medium'),
                'remediation_priority': ai_features.get('remediation_priority', 5),
                'business_impact_areas': ai_features.get('business_impact_areas', ['confidentiality']),
                'attack_vector': ai_features.get('attack_vector', 'network'),
                'affected_components': ai_features.get('affected_components', []),
                'root_cause': ai_features.get('root_cause', ''),
                'key_weakness': ai_features.get('key_weakness', ''),
                
                # Metadata
                'extraction_method': 'ai',
                'extracted_at': datetime.now().isoformat()
            }
            
            return features
            
        except Exception as e:
            print(f"⚠️ Failed to parse AI features: {e}")
            return self._fallback_feature_extraction(original_context)
    
    def _fallback_feature_extraction(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback feature extraction tanpa AI"""
        technique = context.get('technique', 'unknown')
        severity = context.get('severity', 'medium')
        
        return {
            'original_technique': technique,
            'original_severity': severity,
            'detector': context.get('detector'),
            'technique_category': self._categorize_technique(technique),
            'exploitability_score': self._estimate_exploitability(context),
            'impact_severity': severity,
            'attack_complexity': 'medium',
            'required_privileges': 'none',
            'user_interaction': 'none',
            'detection_difficulty': 'medium',
            'remediation_priority': self._severity_to_priority(severity),
            'business_impact_areas': ['confidentiality', 'integrity'],
            'attack_vector': 'network',
            'affected_components': context.get('affected_components', []),
            'root_cause': '',
            'key_weakness': '',
            'extraction_method': 'fallback',
            'extracted_at': datetime.now().isoformat()
        }
    
    def _categorize_technique(self, technique: str) -> str:
        """Categorize technique into category"""
        technique_lower = technique.lower()
        
        categories = {
            'web': ['xss', 'sqli', 'lfi', 'rfi', 'csrf', 'ssrf', 'command_injection', 'ssti', 'xxe'],
            'api': ['bola', 'bfa', 'mass_assignment', 'jwt', 'oauth', 'rate_limiting'],
            'cloud': ['s3_misconfig', 'gcp_bucket', 'azure_blob', 'cloud_metadata', 'iam_misconfig', 'k8s', 'serverless'],
            'mobile': ['insecure_storage', 'hardcoded_secret', 'binary_analysis', 'root_detection', 'ssl_pinning'],
            'web3': ['reentrancy', 'flash_loan', 'integer_overflow', 'access_control', 'delegatecall'],
            'ai': ['prompt_injection', 'model_inversion', 'data_leak', 'llm_abuse'],
            'supply_chain': ['dependency', 'typosquatting', 'logic_bomb'],
            'realtime': ['websocket', 'prototype_pollution', 'dom_xss', 'session_fixation'],
            'mfa': ['mfa_bypass'],
            'general': ['information_disclosure', 'privilege_escalation', 'denial_of_service', 'buffer_overflow']
        }
        
        for category, keywords in categories.items():
            if any(kw in technique_lower for kw in keywords):
                return category
        
        return 'general'
    
    def _estimate_exploitability(self, context: Dict) -> float:
        """Estimate exploitability score (0.0-1.0)"""
        score = 0.5  # Base score
        
        # Adjust based on severity
        severity = context.get('severity', 'medium').lower()
        severity_scores = {
            'critical': 0.9,
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4,
            'info': 0.2
        }
        score = severity_scores.get(severity, 0.5)
        
        # Adjust based on CVE/CWE availability
        if context.get('cve_id') or context.get('cwe_id'):
            score += 0.1
        
        return min(1.0, max(0.0, score))
    
    def _severity_to_priority(self, severity: str) -> int:
        """Convert severity to remediation priority (1-10)"""
        mapping = {
            'critical': 10,
            'high': 8,
            'medium': 5,
            'low': 3,
            'info': 1
        }
        return mapping.get(severity.lower(), 5)
    
    def _generate_cache_key(self, context: Dict) -> str:
        """Generate cache key from context"""
        technique = context.get('technique', 'unknown')
        target = context.get('target_info', 'N/A')[:50]
        return f"{technique}:{target}"
    
    def _save_cache(self):
        """Save feature cache to disk"""
        try:
            os.makedirs(self.base_dir, exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.feature_cache, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save feature cache: {e}")
    
    def load_cache(self):
        """Load feature cache from disk"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    self.feature_cache = json.load(f)
                print(f"📂 Loaded {len(self.feature_cache)} cached features")
        except Exception as e:
            print(f"⚠️ Failed to load feature cache: {e}")
    
    def batch_extract_features(self, contexts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract features untuk multiple contexts
        
        Args:
            contexts: List of vulnerability contexts
            
        Returns:
            List of extracted features
        """
        features_list = []
        
        for context in contexts:
            features = self.extract_features(context)
            features_list.append(features)
        
        return features_list
    
    def get_feature_statistics(self) -> Dict[str, Any]:
        """Get statistics tentang feature extraction"""
        return {
            'cached_features': len(self.feature_cache),
            'ai_available': self.sovereign_reasoner is not None,
            'cache_file': self.cache_file
        }