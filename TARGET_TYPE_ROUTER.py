"""
Target Type Router - Sistem routing otomatis target → modul ARC v7.6
"""

import re
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class TargetProfile:
    """Profile terdeteksi dari target."""
    target_type: str
    confidence: float
    indicators: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)
    cloud_providers: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class TargetTypeRouter:
    """Router otomatis untuk menentukan modul ARC mana yang harus dijalankan."""
    
    def __init__(self):
        self.target_patterns = {
            'chromium': {'keywords': ['chromium', 'chrome', 'blink', 'v8'], 'file_extensions': ['.crx'], 'weight': 1.0},
            'android': {'keywords': ['android', 'apk', 'mobile'], 'file_extensions': ['.apk', '.dex'], 'weight': 1.0},
            'ios': {'keywords': ['ios', 'iphone', 'ipa'], 'file_extensions': ['.ipa'], 'weight': 1.0},
            'cloud': {'keywords': ['aws', 's3', 'lambda', 'gcp', 'azure', 'kubernetes'], 'file_extensions': ['.yaml', '.tf'], 'weight': 1.0},
            'crypto': {'keywords': ['ethereum', 'web3', 'solidity', 'blockchain'], 'file_extensions': ['.sol'], 'weight': 1.0},
            'ai': {'keywords': ['llm', 'gpt', 'claude', 'prompt injection'], 'file_extensions': ['.ipynb'], 'weight': 1.0},
            'web': {'keywords': ['website', 'web'], 'file_extensions': ['.html', '.php'], 'weight': 0.8},
            'api': {'keywords': ['api', 'rest', 'graphql'], 'file_extensions': ['.json'], 'weight': 0.9}
        }
    def detect_target_type(self, target_url="", target_hint="", content="", headers=None):
        """Deteksi tipe target."""
        scores = {t: 0.0 for t in self.target_patterns}
        all_indicators = []
        
        # 1. Hint eksplisit (prioritas tertinggi)
        if target_hint:
            hint_lower = target_hint.lower().strip()
            if hint_lower in scores:
                scores[hint_lower] += 10.0
                all_indicators.append(f"hint:{hint_lower}")
        
        # 2. Analisis URL
        if target_url:
            url_lower = target_url.lower()
            for ttype, patterns in self.target_patterns.items():
                for kw in patterns['keywords']:
                    if kw in url_lower:
                        scores[ttype] += 2.0 * patterns['weight']
                        all_indicators.append(f"url:{kw}")
                for ext in patterns['file_extensions']:
                    if target_url.endswith(ext):
                        scores[ttype] += 3.0 * patterns['weight']
                        all_indicators.append(f"ext:{ext}")
        
        # 3. Analisis konten
        if content:
            content_lower = content.lower()
            for ttype, patterns in self.target_patterns.items():
                for kw in patterns['keywords']:
                    if kw in content_lower:
                        scores[ttype] += 1.5 * patterns['weight']
        
        # 4. Mobile khusus
        if target_url.endswith('.apk'):
            scores['android'] += 10.0
            all_indicators.append("file:apk")
        elif target_url.endswith('.ipa'):
            scores['ios'] += 10.0
            all_indicators.append("file:ipa")
        
        # 5. Fallback ke web
        if max(scores.values()) == 0:
            scores['web'] = 1.0
            all_indicators.append("fallback:web")
        
        # Normalisasi
        max_score = max(scores.values())
        if max_score > 0:
            for t in scores:
                scores[t] = scores[t] / max_score
        
        best = max(scores, key=scores.get)
        confidence = min(scores[best], 1.0)
        
        return TargetProfile(
            target_type=best,
            confidence=confidence,
            indicators=list(set(all_indicators)),
            metadata={'scores': scores}
        )

        self._module_cache = {}

    
    def route_to_modules(self, profile, available_modules=None):
        """Route target ke modul yang sesuai."""
        if available_modules is None:
            available_modules = self._get_available_modules()
        
        routing_map = {
            'chromium': ['browser_security'],
            'android': ['mobile_security'],
            'ios': ['mobile_security'],
            'cloud': ['cloud_security'],
            'crypto': ['crypto_web3_security'],
            'ai': ['ai_security'],
            'web': ['web_security'],
            'api': ['api_security']
        }
        
        categories = routing_map.get(profile.target_type, ['web_security'])
        routed = {c: available_modules[c] for c in categories if c in available_modules}
        
        return {
            'target_profile': profile,
            'routed_modules': routed,
            'detector_names': self._get_detector_names(profile.target_type)
        }
    
    def _get_detector_names(self, target_type):
        """Dapatkan nama detector untuk target type."""
        detector_map = {
            'chromium': ['chromium_fuzz', 'domato', 'fuzzilli'],
            'android': ['apk_static_analyzer', 'binary_analyzer'],
            'ios': ['ios_ipa_analyzer', 'binary_analyzer'],
            'cloud': ['aws_s3_checker', 'gcp_bucket_scanner', 'cloud_metadata_prober'],
            'crypto': ['smart_contract_analyzer', 'reentrancy_simulator'],
            'ai': ['advanced_llm_attacker', 'prompt_injection_detector'],
            'web': ['xss', 'sqli', 'ssrf', 'idor'],
            'api': ['bola', 'jwt', 'mass_assignment']
        }
        return detector_map.get(target_type, detector_map['web'])
    
    def _get_available_modules(self):
        """Dapatkan modul yang tersedia dengan error handling."""
        available = {}
        
        # Browser Security
        try:
            from BROWSER_SECURITY_RESEARCH.chromium_fuzz_orchestrator import ChromiumFuzzOrchestrator
            available['browser_security'] = {'chromium_fuzz_orchestrator': ChromiumFuzzOrchestrator}
        except ImportError as e:
            logger.debug(f"Browser Security not available: {e}")
        
        # Mobile Security
        try:
            from VULNERABILITY_DETECTORS.mobile_security.apk_static_analyzer import APKStaticAnalyzer
            from VULNERABILITY_DETECTORS.mobile_security.ios_ipa_analyzer import IOSIPAAnalyzer
            available['mobile_security'] = {
                'apk_static_analyzer': APKStaticAnalyzer,
                'ios_ipa_analyzer': IOSIPAAnalyzer
            }
        except ImportError as e:
            logger.debug(f"Mobile Security not available: {e}")
        
        # Cloud Security
        try:
            from VULNERABILITY_DETECTORS.cloud_security.aws_s3_checker import AWSS3Checker
            from VULNERABILITY_DETECTORS.cloud_security.gcp_bucket_scanner import GCPBucketScanner
            available['cloud_security'] = {
                'aws_s3_checker': AWSS3Checker,
                'gcp_bucket_scanner': GCPBucketScanner
            }
        except ImportError as e:
            logger.debug(f"Cloud Security not available: {e}")
        
        # Crypto/Web3 Security
        try:
            from VULNERABILITY_DETECTORS.crypto_web3_security.smart_contract_analyzer import SmartContractAnalyzer
            from VULNERABILITY_DETECTORS.crypto_web3_security.reentrancy_simulator import ReentrancySimulator
            available['crypto_web3_security'] = {
                'smart_contract_analyzer': SmartContractAnalyzer,
                'reentrancy_simulator': ReentrancySimulator
            }
        except ImportError as e:
            logger.debug(f"Crypto/Web3 Security not available: {e}")
        
        # AI Security
        try:
            from VULNERABILITY_DETECTORS.ai_security.advanced_llm_attacker import AdvancedLLMAttacker
            from VULNERABILITY_DETECTORS.ai_security.prompt_injection_detector import PromptInjectionDetector
            available['ai_security'] = {
                'advanced_llm_attacker': AdvancedLLMAttacker,
                'prompt_injection_detector': PromptInjectionDetector
            }
        except ImportError as e:
            logger.debug(f"AI Security not available: {e}")
        
        # Web Security
        try:
            from VULNERABILITY_DETECTORS.web_security.xss_detector import XSSDetector
            from VULNERABILITY_DETECTORS.web_security.sqli_scanner import SQLiScanner
            from VULNERABILITY_DETECTORS.web_security.ssrf_hunter import SSRFHunter
            available['web_security'] = {
                'xss': XSSDetector,
                'sqli': SQLiScanner,
                'ssrf': SSRFHunter
            }
        except ImportError as e:
            logger.debug(f"Web Security not available: {e}")
        
        # API Security
        try:
            from VULNERABILITY_DETECTORS.api_security.bola_scanner import BOLAScanner
            available['api_security'] = {'bola': BOLAScanner}
        except ImportError as e:
            logger.debug(f"API Security not available: {e}")
        
        return available


    
    def get_architecture_fingerprint(self, target_url):
        """Gunakan ArchitectureFingerprinter untuk deteksi mendalam."""
        try:
            from ENTERPRISE_ATTACK_SURFACE.architecture_fingerprinter import ArchitectureFingerprinter
            fingerprinter = ArchitectureFingerprinter()
            return fingerprinter.fingerprint_target(target_url)
        except ImportError as e:
            logger.debug(f"ArchitectureFingerprinter not available: {e}")
            return {}
        except Exception as e:
            logger.warning(f"Architecture fingerprinting failed: {e}")
            return {}


def create_target_router():
    """Factory function untuk membuat TargetTypeRouter instance."""
    return TargetTypeRouter()


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    router = create_target_router()
    
    print("\n" + "="*60)
    print("TARGET TYPE ROUTER DEMO")
    print("="*60)
    
    test_cases = [
        ("https://example.com", "web", ""),
        ("https://api.example.com/v1/users", "api", ""),
        ("https://chromium.googlesource.com", "chromium", ""),
        ("https://play.google.com/store/apps", "android", ""),
        ("https://aws.amazon.com/s3", "cloud", ""),
        ("https://etherscan.io", "crypto", ""),
        ("https://chat.openai.com", "ai", ""),
    ]
    
    for url, hint, content in test_cases:
        profile = router.detect_target_type(url, hint, content)
        routing = router.route_to_modules(profile)
        
        print(f"\nTarget: {url}")
        print(f"  Hint: {hint or '(none)'}")
        print(f"  Detected: {profile.target_type.upper()} ({profile.confidence:.1%})")
        print(f"  Routed to: {list(routing['routed_modules'].keys())}")
    
    print("\n" + "="*60)
    print("Demo completed!")
    print("="*60)
