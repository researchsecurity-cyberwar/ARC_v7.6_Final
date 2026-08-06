"""
Zero Trust Verifier Package
"Trust nothing" validator for headers, responses, and scopes.
"""
import re
from urllib.parse import urlparse

from .canarytoken_detector import CanarytokenDetector
from .business_context_validator import BusinessContextValidator


class ZeroTrustVerifier:
    """
    "Trust nothing" validator for headers, responses, and scopes.
    Memastikan setiap asumsi diverifikasi sebelum eksploitasi.
    """

    def __init__(self):
        self.canary_patterns = [
            r'canarytoken',
            r'honeypot',
            r'deception',
            r'fake.*data',
            r'test.*account'
        ]

        self.business_context_rules = {
            'banking': ['transaction', 'balance', 'account'],
            'healthcare': ['patient', 'medical', 'record'],
            'ecommerce': ['payment', 'cart', 'checkout']
        }

        # Sub-validators
        self.canarytoken_detector = CanarytokenDetector()
        self.business_context_validator = BusinessContextValidator()

    def verify_scope(self, target_url, allowed_domains):
        """
        Verifikasi apakah target URL berada dalam scope yang diizinkan.
        """
        parsed_url = urlparse(target_url)
        target_domain = parsed_url.netloc.lower()

        for allowed_domain in allowed_domains:
            if allowed_domain.startswith('*.'):
                # Wildcard subdomain
                base_domain = allowed_domain[2:]
                if target_domain.endswith(base_domain):
                    return True
            elif target_domain == allowed_domain.lower():
                return True

        return False

    def detect_canarytokens(self, response_content):
        """
        Deteksi Canarytokens atau marker penipuan dalam respons.
        """
        content_lower = response_content.lower()
        detected_tokens = []

        for pattern in self.canary_patterns:
            if re.search(pattern, content_lower):
                detected_tokens.append(pattern)

        # Also use the dedicated detector
        dedicated = self.canarytoken_detector.detect(response_content)
        if dedicated:
            detected_tokens.extend(dedicated)

        return list(set(detected_tokens))

    def validate_business_context(self, target_url, response_content, expected_context):
        """
        Validasi apakah konten respons sesuai dengan konteks bisnis target.
        """
        if expected_context not in self.business_context_rules:
            return True  # Konteks tidak dikenal, lewati validasi

        keywords = self.business_context_rules[expected_context]
        content_lower = response_content.lower()

        # Minimal 2 keyword harus ditemukan
        found_keywords = sum(1 for keyword in keywords if keyword in content_lower)
        return found_keywords >= 2