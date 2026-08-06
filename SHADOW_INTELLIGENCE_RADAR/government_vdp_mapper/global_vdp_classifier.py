import re

class GlobalVDPClassifier:
    """
    Auto-tag jurisdiction + legal framework.
    Mengklasifikasikan program VDP berdasarkan yurisdiksi dan kerangka hukum.
    """
    
    JURISDICTION_RULES = {
        r'\.go\.id$': {'jurisdiction': 'indonesia', 'framework': 'UU PDP No. 27/2022'},
        r'\.gov$': {'jurisdiction': 'usa', 'framework': 'CISA Binding Operational Directive 22-01'},
        r'\.gouv\.fr$': {'jurisdiction': 'france', 'framework': 'ANSSI Security Guidelines'},
        r'\.bund\.de$': {'jurisdiction': 'germany', 'framework': 'BSI IT-Sicherheitsgesetz'},
        r'\.gov\.sg$': {'jurisdiction': 'singapore', 'framework': 'Singapore Cybersecurity Act'},
        r'\.gov\.uk$': {'jurisdiction': 'uk', 'framework': 'UK Government SPF'},
        r'\.mil$': {'jurisdiction': 'usa_military', 'framework': 'DoD VDP DTM-19-007'}
    }
    
    def __init__(self):
        pass
    
    def classify_vdp_program(self, vdp_url):
        """Klasifikasikan program VDP berdasarkan URL."""
        for pattern, classification in self.JURISDICTION_RULES.items():
            if re.search(pattern, vdp_url, re.IGNORECASE):
                return classification
        
        # Default untuk yurisdiksi internasional
        return {
            'jurisdiction': 'international',
            'framework': 'ISO/IEC 30111'
        }
    
    def get_legal_requirements(self, jurisdiction):
        """Dapatkan persyaratan hukum untuk yurisdiksi tertentu."""
        legal_requirements = {
            'indonesia': {
                'disclosure_window': 'no mandatory timeframe',
                'required_info': ['vulnerability details', 'affected systems', 'potential impact'],
                'contact_method': 'official security contact or form',
                'note': 'UU PDP mengatur insiden data pribadi, bukan kerentanan teknis'
            },
            'usa': {
                'disclosure_window': 'varies by agency (typically 90 days)',
                'required_info': ['CVE if available', 'technical details', 'proof of concept', 'remediation suggestion'],
                'contact_method': 'security@agency.gov or official VDP portal'
            },
            'usa_military': {
                'disclosure_window': '90 days (DoD VDP policy)',
                'required_info': ['detailed technical report', 'PoC video', 'affected systems'],
                'contact_method': 'HackerOne DoD portal only',
                'note': 'Only authorized via official DoD VDP platform'
            },
            'singapore': {
                'disclosure_window': 'reasonable timeframe',
                'required_info': ['vulnerability description', 'impact assessment', 'suggested fix'],
                'contact_method': 'SingCERT portal or email'
            },
            'international': {
                'disclosure_window': 'reasonable timeframe (typically 60-90 days)',
                'required_info': ['vulnerability description', 'affected versions', 'impact assessment', 'remediation steps'],
                'contact_method': 'security contact or official disclosure channel'
            }
        }
        
        return legal_requirements.get(jurisdiction, legal_requirements['international'])