class ASEANBridge:
    """
    Leverage ID rep for SG/MY/TH programs.
    Memanfaatkan reputasi Indonesia untuk program ASEAN.
    """
    
    def __init__(self):
        self.asean_programs = {
            'singapore': {
                'platforms': ['hackerone', 'bugcrowd'],
                'regulations': ['PDPA Singapore'],
                'reputation_leverage': 'Indonesian researcher with OJK compliance experience',
                'contact_strategy': 'Emphasize ASEAN cybersecurity cooperation'
            },
            'malaysia': {
                'platforms': ['yeswehack', 'intigriti'],
                'regulations': ['Personal Data Protection Act 2010'],
                'reputation_leverage': 'Experience with UU PDP and financial sector compliance',
                'contact_strategy': 'Highlight ASEAN digital economy integration'
            },
            'thailand': {
                'platforms': ['hackerone', 'private programs'],
                'regulations': ['Personal Data Protection Act B.E. 2562'],
                'reputation_leverage': 'Proven track record in government and financial security',
                'contact_strategy': 'Reference ASEAN Cybersecurity Cooperation Framework'
            }
        }
    
    def build_asean_bridge_strategy(self, target_country: str, indonesian_credentials: dict):
        """
        Bangun strategi jembatan ASEAN berdasarkan kredensial Indonesia.
        """
        results = {
            'target_country': target_country,
            'indonesian_credentials': indonesian_credentials,
            'bridge_strategy': None,
            'credibility_factors': [],
            'recommended_approach': None,
            'success_probability': 0.0
        }
        
        try:
            if target_country not in self.asean_programs:
                results['error'] = f'No ASEAN bridge strategy for {target_country}'
                return results
            
            country_strategy = self.asean_programs[target_country]
            
            # Bangun strategi jembatan
            bridge_strategy = {
                'country': target_country,
                'platforms_to_target': country_strategy['platforms'],
                'regulatory_alignment': self._align_regulations(
                    indonesian_credentials.get('regulations', []),
                    country_strategy['regulations']
                ),
                'reputation_narrative': country_strategy['reputation_leverage'],
                'contact_approach': country_strategy['contact_strategy']
            }
            
            results['bridge_strategy'] = bridge_strategy
            
            # Identifikasi faktor kredibilitas
            credibility_factors = self._identify_credibility_factors(
                indonesian_credentials, country_strategy
            )
            results['credibility_factors'] = credibility_factors
            
            # Rekomendasikan pendekatan
            recommended_approach = self._recommend_approach(
                indonesian_credentials, country_strategy
            )
            results['recommended_approach'] = recommended_approach
            
            # Hitung probabilitas keberhasilan
            success_prob = self._calculate_asean_success_probability(
                credibility_factors, recommended_approach
            )
            results['success_probability'] = success_prob
        
        except Exception as e:
            results['error'] = f'ASEAN bridge strategy failed: {str(e)}'
        
        return results
    
    def _align_regulations(self, id_regs: list, asean_regs: list) -> dict:
        """Sejajarkan regulasi Indonesia dengan ASEAN."""
        alignment = {
            'common_ground': [],
            'differences': [],
            'leverage_points': []
        }
        
        # Temukan kesamaan
        for id_reg in id_regs:
            if any(asean_reg.lower() in id_reg.lower() for asean_reg in asean_regs):
                alignment['common_ground'].append(id_reg)
        
        # Identifikasi perbedaan
        for asean_reg in asean_regs:
            if not any(asean_reg.lower() in id_reg.lower() for id_reg in id_regs):
                alignment['differences'].append(asean_reg)
        
        # Titik leverage
        if 'UU PDP' in str(id_regs) and 'PDPA' in str(asean_regs):
            alignment['leverage_points'].append('Experience with comprehensive data protection laws')
        
        if 'POJK' in str(id_regs):
            alignment['leverage_points'].append('Financial sector regulatory compliance experience')
        
        return alignment
    
    def _identify_credibility_factors(self, id_creds: dict, country_strategy: dict) -> list:
        """Identifikasi faktor kredibilitas."""
        factors = []
        
        # Faktor berdasarkan pengalaman regulasi
        if id_creds.get('ojk_experience'):
            factors.append('Proven experience with financial sector regulations (OJK POJK 13/2023)')
        
        if id_creds.get('government_experience'):
            factors.append('Experience working with Indonesian government security standards')
        
        if id_creds.get('pdp_compliance'):
            factors.append('Demonstrated compliance with UU PDP No. 27/2022')
        
        # Faktor berdasarkan reputasi
        acceptance_rate = id_creds.get('acceptance_rate', 0)
        if acceptance_rate >= 0.8:
            factors.append(f'High acceptance rate ({acceptance_rate*100:.0f}%) in Indonesian programs')
        
        return factors
    
    def _recommend_approach(self, id_creds: dict, country_strategy: dict) -> dict:
        """Rekomendasikan pendekatan."""
        approach = {
            'initial_contact': f"Hello, I'm an Indonesian security researcher with experience in {country_strategy['reputation_leverage'].lower()}.",
            'credibility_statement': self._build_credibility_statement(id_creds),
            'regulatory_reference': f"I understand your {country_strategy['regulations'][0]} requirements and have similar experience with Indonesian regulations.",
            'collaboration_proposal': country_strategy['contact_strategy']
        }
        
        return approach
    
    def _build_credibility_statement(self, id_creds: dict) -> str:
        """Bangun pernyataan kredibilitas."""
        statements = []
        
        if id_creds.get('ojk_experience'):
            statements.append('OJK POJK No. 13/2023 compliance')
        
        if id_creds.get('government_experience'):
            statements.append('Indonesian government security standards')
        
        if id_creds.get('acceptance_rate', 0) >= 0.8:
            statements.append(f'{id_creds["acceptance_rate"]*100:.0f}% acceptance rate')
        
        if statements:
            return f"My experience includes: {', '.join(statements)}."
        else:
            return "I am an experienced security researcher familiar with ASEAN cybersecurity standards."
    
    def _calculate_asean_success_probability(self, credibility_factors: list, approach: dict) -> float:
        """Hitung probabilitas keberhasilan ASEAN."""
        base_prob = 0.6  # Probabilitas dasar untuk peneliti ASEAN
        
        # Tambahkan berdasarkan faktor kredibilitas
        credibility_bonus = len(credibility_factors) * 0.1
        base_prob += credibility_bonus
        
        # Batasi maksimum
        return min(0.9, base_prob)