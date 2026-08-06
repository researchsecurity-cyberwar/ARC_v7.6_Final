class BusinessContextValidator:
    """
    Validate endpoints against business logic context.
    Wrap the standalone function-based implementation for class-based integration.
    """

    def __init__(self):
        self.context_rules = {
            'fintech': ['transfer', 'saldo', 'rekening', 'qr', 'qris', 'ewallet'],
            'government': ['layanan', 'penduduk', 'nik', 'npwp', 'perizinan'],
            'banking': ['transaction', 'balance', 'account'],
            'healthcare': ['patient', 'medical', 'record'],
            'ecommerce': ['payment', 'cart', 'checkout']
        }

    def validate(self, url, content, context_type='fintech'):
        """
        Validate business context for a given URL and content.
        Returns True if context validation passes.
        """
        if context_type not in self.context_rules:
            return True  # Unknown context, skip validation

        indicators = self.context_rules[context_type]
        content_lower = content.lower()
        found = [ind for ind in indicators if ind in content_lower]
        return len(found) >= 2

    def validate_fintech(self, url, content):
        """Validate fintech context (OJK/POJK compliance)."""
        return self.validate(url, content, 'fintech')

    def validate_government(self, url, content):
        """Validate government context (.go.id)."""
        return self.validate(url, content, 'government')

    def validate_banking(self, url, content):
        """Validate banking context."""
        return self.validate(url, content, 'banking')

    def validate_healthcare(self, url, content):
        """Validate healthcare context."""
        return self.validate(url, content, 'healthcare')

    def validate_ecommerce(self, url, content):
        """Validate ecommerce context."""
        return self.validate(url, content, 'ecommerce')


# Backward-compatible standalone functions
def validate_fintech_context(url, content):
    """
    Validasi konteks fintech (OJK/POJK compliance).
    """
    fintech_indicators = ['transfer', 'saldo', 'rekening', 'qr', 'qris', 'ewallet']
    content_lower = content.lower()

    found_indicators = [ind for ind in fintech_indicators if ind in content_lower]
    return len(found_indicators) >= 2


def validate_government_context(url, content):
    """
    Validasi konteks pemerintah (.go.id).
    """
    gov_indicators = ['layanan', 'penduduk', 'nik', 'npwp', 'perizinan']
    content_lower = content.lower()

    found_indicators = [ind for ind in gov_indicators if ind in content_lower]
    return len(found_indicators) >= 2
