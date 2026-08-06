class JurisdictionNavigator:
    """
    Resolve UU ITE + GDPR + CFAA conflicts.
    Menyelesaikan konflik yurisdiksi antara regulasi Indonesia dan internasional.
    """
    
    def __init__(self):
        self.jurisdiction_conflicts = {
            'uu_ite_vs_gdpr': {
                'conflict_area': 'Data breach notification timeline',
                'uu_ite_requirement': '72 hours (UU PDP No. 27/2022)',
                'gdpr_requirement': '72 hours (GDPR Article 33)',
                'resolution': 'Comply with stricter interpretation - report within 72 hours to both authorities',
                'priority_jurisdiction': 'Both equally important'
            },
            'uu_ite_vs_cfaa': {
                'conflict_area': 'Authorization for security testing',
                'uu_ite_requirement': 'Written authorization required (UU ITE Art. 30)',
                'cfaa_requirement': 'Explicit permission required (18 U.S.C. § 1030)',
                'resolution': 'Obtain written authorization from target owner before any testing',
                'priority_jurisdiction': 'Target location determines primary jurisdiction'
            },
            'gdpr_vs_cfaa': {
                'conflict_area': 'Data handling during security research',
                'gdpr_requirement': 'Minimize personal data processing (GDPR Art. 5)',
                'cfaa_requirement': 'No unauthorized access to protected computers',
                'resolution': 'Process only necessary data and ensure explicit authorization',
                'priority_jurisdiction': 'EU GDPR takes precedence for EU citizens data'
            }
        }
    
    def navigate_jurisdiction_conflicts(self, target_info: dict, operation_context: dict):
        """
        Navigasi konflik yurisdiksi untuk operasi keamanan.
        """
        results = {
            'target_info': target_info,
            'operation_context': operation_context,
            'applicable_jurisdictions': [],
            'identified_conflicts': [],
            'resolution_strategy': None,
            'compliance_pathway': None,
            'legal_risk_assessment': {}
        }
        
        try:
            # Identifikasi yurisdiksi yang berlaku
            jurisdictions = self._identify_applicable_jurisdictions(target_info, operation_context)
            results['applicable_jurisdictions'] = jurisdictions
            
            # Identifikasi konflik
            conflicts = self._identify_jurisdiction_conflicts(jurisdictions)
            results['identified_conflicts'] = conflicts
            
            # Bangun strategi resolusi
            resolution_strategy = self._build_resolution_strategy(conflicts, target_info)
            results['resolution_strategy'] = resolution_strategy
            
            # Bangun jalur kepatuhan
            compliance_pathway = self._build_compliance_pathway(jurisdictions, resolution_strategy)
            results['compliance_pathway'] = compliance_pathway
            
            # Nilai risiko hukum
            legal_risk = self._assess_legal_risk(jurisdictions, conflicts)
            results['legal_risk_assessment'] = legal_risk
        
        except Exception as e:
            results['error'] = f'Jurisdiction navigation failed: {str(e)}'
        
        return results
    
    def _identify_applicable_jurisdictions(self, target_info: dict, operation_context: dict) -> list:
        """Identifikasi yurisdiksi yang berlaku."""
        jurisdictions = []
        target_domain = target_info.get('domain', '').lower()
        researcher_location = operation_context.get('researcher_location', 'indonesia').lower()
        
        # Yurisdiksi Indonesia
        if target_domain.endswith(('.id', '.go.id', '.co.id')) or researcher_location == 'indonesia':
            jurisdictions.append('indonesia')
        
        # Yurisdiksi EU/GDPR
        eu_countries = ['.de', '.fr', '.it', '.es', '.nl', '.be', '.at', '.pt', '.fi', '.se', '.dk', '.ie', '.gr', '.lu', '.mt', '.cy', '.ee', '.lv', '.lt', '.si', '.sk', '.hr', '.bg', '.ro', '.hu', '.pl', '.cz', '.eu']
        if any(target_domain.endswith(country) for country in eu_countries):
            jurisdictions.append('eu_gdpr')
        
        # Yurisdiksi US/CFAA
        us_targets = ['.gov', '.mil', '.edu', '.us'] + ['usa', 'united states', 'america']
        if any(keyword in target_domain for keyword in us_targets) or target_info.get('hosted_in_us'):
            jurisdictions.append('us_cfaa')
        
        return jurisdictions
    
    def _identify_jurisdiction_conflicts(self, jurisdictions: list) -> list:
        """Identifikasi konflik yurisdiksi."""
        conflicts = []
        
        # Cek konflik spesifik
        if 'indonesia' in jurisdictions and 'eu_gdpr' in jurisdictions:
            conflicts.append(self.jurisdiction_conflicts['uu_ite_vs_gdpr'])
        
        if 'indonesia' in jurisdictions and 'us_cfaa' in jurisdictions:
            conflicts.append(self.jurisdiction_conflicts['uu_ite_vs_cfaa'])
        
        if 'eu_gdpr' in jurisdictions and 'us_cfaa' in jurisdictions:
            conflicts.append(self.jurisdiction_conflicts['gdpr_vs_cfaa'])
        
        return conflicts
    
    def _build_resolution_strategy(self, conflicts: list, target_info: dict) -> dict:
        """Bangun strategi resolusi."""
        if not conflicts:
            return {'strategy': 'single_jurisdiction_compliance', 'approach': 'Follow applicable jurisdiction requirements'}
        
        # Strategi untuk multiple jurisdiction
        strategy = {
            'strategy': 'harmonized_compliance',
            'approach': 'Apply the strictest requirement across all applicable jurisdictions',
            'key_principles': [
                'Obtain explicit written authorization before any testing',
                'Report data breaches within 72 hours to all relevant authorities',
                'Minimize data processing to essential information only',
                'Document all activities for legal defense purposes'
            ],
            'priority_order': self._determine_priority_order(target_info)
        }
        
        return strategy
    
    def _determine_priority_order(self, target_info: dict) -> list:
        """Tentukan urutan prioritas yurisdiksi."""
        # Prioritas berdasarkan lokasi target
        target_location = target_info.get('hosted_in', 'unknown').lower()
        
        if 'indonesia' in target_location:
            return ['indonesia', 'eu_gdpr', 'us_cfaa']
        elif 'europe' in target_location or 'eu' in target_location:
            return ['eu_gdpr', 'indonesia', 'us_cfaa']
        elif 'united states' in target_location or 'us' in target_location:
            return ['us_cfaa', 'indonesia', 'eu_gdpr']
        else:
            return ['indonesia', 'eu_gdpr', 'us_cfaa']  # Default untuk peneliti Indonesia
    
    def _build_compliance_pathway(self, jurisdictions: list, resolution_strategy: dict) -> dict:
        """Bangun jalur kepatuhan."""
        pathway = {
            'pre_operation': [],
            'during_operation': [],
            'post_operation': []
        }
        
        # Langkah pra-operasi
        pathway['pre_operation'] = [
            'Obtain written authorization from target owner',
            'Verify target scope and authorized testing methods',
            'Prepare incident response plan for data breach scenarios',
            'Document legal basis for security testing'
        ]
        
        # Langkah selama operasi
        pathway['during_operation'] = [
            'Limit data collection to essential information only',
            'Avoid accessing personal data unless absolutely necessary',
            'Maintain detailed logs of all testing activities',
            'Immediately stop testing if unauthorized access is detected'
        ]
        
        # Langkah pasca-operasi
        pathway['post_operation'] = [
            'Report findings within 72 hours if data breach occurred',
            'Provide complete documentation to target owner',
            'Cooperate with regulatory authorities if required',
            'Maintain records for minimum 3 years for legal defense'
        ]
        
        return pathway
    
    def _assess_legal_risk(self, jurisdictions: list, conflicts: list) -> dict:
        """Nilai risiko hukum."""
        if not jurisdictions:
            return {'risk_level': 'LOW', 'primary_concerns': ['None'], 'mitigation': 'Standard responsible disclosure'}
        
        if len(jurisdictions) > 1:
            risk_level = 'HIGH'
            primary_concerns = [
                'Conflicting legal requirements between jurisdictions',
                'Potential liability in multiple legal systems',
                'Complex compliance documentation requirements'
            ]
            mitigation = 'Engage legal counsel familiar with all applicable jurisdictions'
        else:
            risk_level = 'MEDIUM'
            primary_concerns = [f'Compliance with {jurisdictions[0].upper()} requirements']
            mitigation = 'Follow standard compliance procedures for single jurisdiction'
        
        return {
            'risk_level': risk_level,
            'primary_concerns': primary_concerns,
            'mitigation_strategy': mitigation
        }