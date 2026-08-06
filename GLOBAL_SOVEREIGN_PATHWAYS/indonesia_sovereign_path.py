import os
import json
from datetime import datetime

class IndonesiaSovereignPath:
    """
    .go.id → OJK → BUMN → private programs.
    Membangun jalur kedaulatan Indonesia dari sektor publik ke swasta.
    """
    
    def __init__(self, sovereign_dir="~/.arc/sovereign"):
        self.sovereign_dir = os.path.expanduser(sovereign_dir)
        os.makedirs(self.sovereign_dir, exist_ok=True)
        self.indonesian_domains = {
            'government': ['.go.id', '.mil.id', '.polri.go.id'],
            'financial': ['.ojk.go.id', '.bi.go.id', '.idx.co.id'],
            'bumn': ['.telkom.co.id', '.pln.co.id', '.bumn.go.id'],
            'private': ['.id', '.co.id']
        }
    
    def map_sovereign_pathway(self, target_domain: str):
        """
        Petakan jalur kedaulatan untuk domain target Indonesia.
        """
        results = {
            'target_domain': target_domain,
            'sovereign_tier': None,
            'regulatory_framework': None,
            'compliance_requirements': [],
            'pathway_strategy': None,
            'success_probability': 0.0
        }
        
        try:
            # Tentukan tier kedaulatan
            sovereign_tier = self._determine_sovereign_tier(target_domain)
            results['sovereign_tier'] = sovereign_tier
            
            # Dapatkan kerangka regulasi
            regulatory_framework = self._get_regulatory_framework(sovereign_tier)
            results['regulatory_framework'] = regulatory_framework
            
            # Bangun persyaratan kepatuhan
            compliance_reqs = self._build_compliance_requirements(sovereign_tier, regulatory_framework)
            results['compliance_requirements'] = compliance_reqs
            
            # Rekomendasikan strategi jalur
            pathway_strategy = self._recommend_pathway_strategy(sovereign_tier, target_domain)
            results['pathway_strategy'] = pathway_strategy
            
            # Hitung probabilitas keberhasilan
            success_prob = self._calculate_success_probability(sovereign_tier, compliance_reqs)
            results['success_probability'] = success_prob
        
        except Exception as e:
            results['error'] = f'Sovereign pathway mapping failed: {str(e)}'
        
        return results
    
    def _determine_sovereign_tier(self, domain: str) -> str:
        """Tentukan tier kedaulatan berdasarkan domain."""
        domain_lower = domain.lower()
        
        for tier, domains in self.indonesian_domains.items():
            if any(domain_lower.endswith(d) for d in domains):
                return tier
        
        # Jika domain Indonesia tapi tidak cocok, anggap private
        if domain_lower.endswith(('.id', '.co.id')):
            return 'private'
        
        return 'international'
    
    def _get_regulatory_framework(self, tier: str) -> dict:
        """Dapatkan kerangka regulasi berdasarkan tier."""
        frameworks = {
            'government': {
                'primary_law': 'UU ITE No. 19/2016',
                'secondary_regulations': ['Perpres No. 75/2014', 'SE Menkominfo No. 3/2020'],
                'oversight_body': 'Kominfo & BSSN'
            },
            'financial': {
                'primary_law': 'POJK No. 13/2023',
                'secondary_regulations': ['POJK No. 12/2018', 'PBI No. 23/2/2021'],
                'oversight_body': 'OJK & Bank Indonesia'
            },
            'bumn': {
                'primary_law': 'PP No. 72/2019',
                'secondary_regulations': ['Permen BUMN No. PER-01/MBU/2021'],
                'oversight_body': 'Kementerian BUMN'
            },
            'private': {
                'primary_law': 'UU PDP No. 27/2022',
                'secondary_regulations': ['Peraturan PDP Pelaksana'],
                'oversight_body': 'Kominfo'
            }
        }
        
        return frameworks.get(tier, {
            'primary_law': 'International Standards',
            'secondary_regulations': ['ISO/IEC 27001', 'NIST CSF'],
            'oversight_body': 'Self-regulated'
        })
    
    def _build_compliance_requirements(self, tier: str, framework: dict) -> list:
        """Bangun persyaratan kepatuhan."""
        requirements = []
        
        # Persyaratan umum untuk semua tier Indonesia
        requirements.extend([
            'Laporan insiden dalam 72 jam (UU PDP)',
            'Notifikasi kepada pemilik data yang terdampak',
            'Audit forensik wajib untuk insiden kritis',
            'Dokumentasi lengkap untuk regulator'
        ])
        
        # Persyaratan spesifik tier
        if tier == 'government':
            requirements.extend([
                'Koordinasi dengan BSSN untuk insiden kritis',
                'Pelaporan ke Kominfo sesuai SE No. 3/2020',
                'Dokumentasi dalam format SPBE'
            ])
        elif tier == 'financial':
            requirements.extend([
                'Pelaporan ke OJK dalam 2x24 jam (POJK 13/2023)',
                'Notifikasi ke Bank Indonesia untuk insiden sistem pembayaran',
                'Audit oleh auditor independen terakreditasi OJK'
            ])
        elif tier == 'bumn':
            requirements.extend([
                'Pelaporan ke Kementerian BUMN',
                'Koordinasi dengan tim keamanan siber BUMN',
                'Dokumentasi sesuai standar BUMN'
            ])
        
        return requirements
    
    def _recommend_pathway_strategy(self, tier: str, target_domain: str) -> dict:
        """Rekomendasikan strategi jalur kedaulatan."""
        strategies = {
            'government': {
                'approach': 'official_channel_first',
                'primary_contact': 'cert@kominfo.go.id',
                'backup_contact': 'incident@bssn.go.id',
                'documentation_standard': 'SPBE Security Incident Format',
                'timeline_expectation': '7-14 days for initial response'
            },
            'financial': {
                'approach': 'ojk_coordinated_disclosure',
                'primary_contact': f'security@{target_domain}',
                'backup_contact': 'bounty@intigriti.com',
                'documentation_standard': 'POJK 13/2023 Incident Report',
                'timeline_expectation': '3-7 days for triage'
            },
            'bumn': {
                'approach': 'bumn_security_team_coordination',
                'primary_contact': f'csirt@{target_domain}',
                'backup_contact': 'security@telkom.co.id',
                'documentation_standard': 'BUMN Cyber Incident Format',
                'timeline_expectation': '5-10 days for response'
            },
            'private': {
                'approach': 'direct_responsible_disclosure',
                'primary_contact': f'security@{target_domain}',
                'backup_contact': 'bugcrowd or hackerone if available',
                'documentation_standard': 'Standard VDP Report',
                'timeline_expectation': '1-30 days depending on company size'
            }
        }
        
        return strategies.get(tier, {
            'approach': 'international_standards',
            'primary_contact': f'security@{target_domain}',
            'backup_contact': 'responsible disclosure platforms',
            'documentation_standard': 'ISO/IEC 30111 format',
            'timeline_expectation': 'varies by jurisdiction'
        })
    
    def _calculate_success_probability(self, tier: str, requirements: list) -> float:
        """Hitung probabilitas keberhasilan berdasarkan tier dan kepatuhan."""
        base_probabilities = {
            'government': 0.6,
            'financial': 0.8,
            'bumn': 0.7,
            'private': 0.5,
            'international': 0.4
        }
        
        base_prob = base_probabilities.get(tier, 0.4)
        
        # Penyesuaian berdasarkan kompleksitas kepatuhan
        if len(requirements) > 6:
            # Semakin banyak persyaratan, semakin rendah probabilitas
            adjustment = -0.1 * (len(requirements) - 6)
            base_prob += adjustment
        
        return max(0.1, min(0.9, base_prob))