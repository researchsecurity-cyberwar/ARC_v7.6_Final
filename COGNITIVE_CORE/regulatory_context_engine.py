class RegulatoryContextEngine:
    """
    Auto-inject UU PDP/GDPR/OJK into reasoning based on target jurisdiction.
    Menyuntikkan konteks regulasi yang relevan ke dalam analisis.
    """
    
    REGULATORY_RULES = {
        'indonesia': {
            'name': 'UU PDP & POJK',
            'key_requirements': [
                'perlindungan data pribadi',
                'persetujuan eksplisit',
                'pelaporan insiden 72 jam',
                'audit keamanan berkala'
            ],
            'penalties': 'Denda hingga 2% dari pendapatan tahunan'
        },
        'eu': {
            'name': 'GDPR',
            'key_requirements': [
                'right to be forgotten',
                'data protection by design',
                '72-hour breach notification',
                'data protection officer'
            ],
            'penalties': 'Denda hingga €20 juta atau 4% dari omset global'
        },
        'usa': {
            'name': 'CCPA/State Laws',
            'key_requirements': [
                'right to know',
                'right to delete',
                'opt-out of sale',
                'non-discrimination'
            ],
            'penalties': 'Denda hingga $7,500 per pelanggaran'
        },
        'singapore': {
            'name': 'PDPA',
            'key_requirements': [
                'consent obligation',
                'notification obligation',
                'access and correction',
                'data protection policies'
            ],
            'penalties': 'Denda hingga SGD 1 juta'
        }
    }
    
    def __init__(self):
        pass
    
    def detect_jurisdiction(self, target_domain):
        """Deteksi yurisdiksi berdasarkan domain target."""
        domain_lower = target_domain.lower()
        
        if '.go.id' in domain_lower or '.mil.id' in domain_lower:
            return 'indonesia'
        elif '.gov.uk' in domain_lower or '.eu' in domain_lower:
            return 'eu'
        elif '.sg' in domain_lower or '.com.sg' in domain_lower:
            return 'singapore'
        elif '.gov' in domain_lower:
            return 'usa'
        else:
            # Coba deteksi dari konten atau IP nanti
            return 'international'
    
    def get_regulatory_context(self, target_domain):
        """Dapatkan konteks regulasi untuk target tertentu."""
        jurisdiction = self.detect_jurisdiction(target_domain)
        
        if jurisdiction in self.REGULATORY_RULES:
            return self.REGULATORY_RULES[jurisdiction]
        else:
            # Default untuk yurisdiksi internasional
            return {
                'name': 'International Standards',
                'key_requirements': ['data minimization', 'purpose limitation', 'security safeguards'],
                'penalties': 'Varies by jurisdiction'
            }
    
    def inject_regulatory_pressure(self, report_template, target_domain):
        """Suntikkan tekanan regulasi ke dalam template laporan."""
        regulatory_context = self.get_regulatory_context(target_domain)
        
        pressure_text = f"""
### Regulatory Context & Pressure

This vulnerability falls under **{regulatory_context['name']}** regulations, which mandates:

{chr(10).join([f"- {req}" for req in regulatory_context['key_requirements']])}

**Potential Penalties**: {regulatory_context['penalties']}

Given the 72-hour mandatory disclosure window for data breaches under these regulations, we strongly recommend immediate triage and remediation.
"""
        
        return report_template + pressure_text