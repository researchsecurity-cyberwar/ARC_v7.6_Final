class RegulatoryLeverageEngine:
    """
    GDPR 72h clock, OJK POJK No.13/2023 pressure.
    Memberikan tekanan regulasi berdasarkan yurisdiksi target.
    """
    
    def __init__(self):
        self.regulatory_frameworks = {
            'indonesia': {
                'name': 'UU PDP No. 27/2022 & POJK No. 13/2023',
                'disclosure_window': '72 hours',
                'requirements': [
                    'Pelaporan insiden kegiatan pelanggaran data pribadi',
                    'Notifikasi kepada pemilik data yang terdampak',
                    'Audit forensik wajib untuk insiden kritis'
                ],
                'penalties': 'Denda hingga 2% dari pendapatan tahunan atau Rp5 miliar',
                'enforcement_body': 'Kominfo & OJK'
            },
            'eu': {
                'name': 'GDPR (General Data Protection Regulation)',
                'disclosure_window': '72 hours',
                'requirements': [
                    'Report to supervisory authority',
                    'Document nature, scope, and impact',
                    'Implement appropriate security measures'
                ],
                'penalties': 'Fines up to €20 million or 4% of global annual turnover',
                'enforcement_body': 'European Data Protection Board'
            },
            'usa': {
                'name': 'State-specific Data Breach Laws',
                'disclosure_window': 'Varies by state (typically 30-60 days)',
                'requirements': [
                    'Notify affected residents',
                    'Report to state attorney general',
                    'Provide credit monitoring if SSN exposed'
                ],
                'penalties': 'Fines vary by state, typically $100-$750 per record',
                'enforcement_body': 'State Attorney General'
            },
            'singapore': {
                'name': 'PDPA (Personal Data Protection Act)',
                'disclosure_window': '72 hours if significant harm likely',
                'requirements': [
                    'Notify PDPC and affected individuals',
                    'Assess likelihood of significant harm',
                    'Implement preventive measures'
                ],
                'penalties': 'Fines up to SGD 1 million',
                'enforcement_body': 'Personal Data Protection Commission'
            }
        }
    
    def apply_regulatory_pressure(self, vulnerability_data: dict) -> dict:
        """
        Terapkan tekanan regulasi berdasarkan yurisdiksi target.
        """
        jurisdiction = vulnerability_data.get('jurisdiction', 'international')
        framework = self.regulatory_frameworks.get(jurisdiction, self.regulatory_frameworks['international'])
        
        pressure_text = f"""
### Regulatory Pressure & Legal Leverage

This vulnerability falls under **{framework['name']}**, which mandates:

**Disclosure Timeline**: {framework['disclosure_window']}

**Key Requirements**:
{chr(10).join([f"- {req}" for req in framework['requirements']])}

**Potential Penalties**: {framework['penalties']}

**Enforcement Body**: {framework['enforcement_body']}

Given the {framework['disclosure_window']} mandatory disclosure window, we strongly recommend immediate triage and remediation to avoid regulatory penalties and reputational damage.
"""
        
        return {
            'jurisdiction': jurisdiction,
            'framework': framework['name'],
            'disclosure_window': framework['disclosure_window'],
            'pressure_text': pressure_text,
            'penalties': framework['penalties']
        }
    
    def get_disclosure_deadline(self, discovery_date: str, jurisdiction: str) -> str:
        """Dapatkan tenggat waktu pelaporan berdasarkan yurisdiksi."""
        from datetime import datetime, timedelta
        
        try:
            discovery_dt = datetime.fromisoformat(discovery_date.replace('Z', '+00:00'))
            
            if jurisdiction in ['indonesia', 'eu', 'singapore']:
                deadline = discovery_dt + timedelta(hours=72)
            elif jurisdiction == 'usa':
                deadline = discovery_dt + timedelta(days=30)
            else:
                deadline = discovery_dt + timedelta(days=7)  # Default reasonable timeframe
            
            return deadline.isoformat()
        except:
            return 'Unable to calculate deadline'