class BusinessImpactEnhancer:
    """
    Calculate financial/reputational impact.
    Menghitung dampak finansial dan reputasi dari temuan keamanan.
    """
    
    def __init__(self):
        self.industry_multipliers = {
            'finance': 5.0,
            'healthcare': 4.0,
            'ecommerce': 3.0,
            'social_media': 2.5,
            'government': 4.5,
            'education': 2.0,
            'technology': 3.5
        }
    
    def enhance_business_impact(self, finding: dict, target_info: dict):
        """
        Tingkatkan analisis dampak bisnis dari temuan.
        """
        results = {
            'finding': finding,
            'target_info': target_info,
            'financial_impact_usd': 0,
            'reputational_impact_score': 0,
            'regulatory_risk': 'low',
            'enhanced_impact_analysis': {},
            'impact_enhancement_successful': False
        }
        
        try:
            # Hitung dampak finansial
            financial_impact = self._calculate_financial_impact(finding, target_info)
            results['financial_impact_usd'] = financial_impact
            
            # Hitung dampak reputasi
            reputational_impact = self._calculate_reputational_impact(finding, target_info)
            results['reputational_impact_score'] = reputational_impact
            
            # Nilai risiko regulasi
            regulatory_risk = self._assess_regulatory_risk(finding, target_info)
            results['regulatory_risk'] = regulatory_risk
            
            # Bangun analisis dampak yang ditingkatkan
            enhanced_analysis = self._build_enhanced_impact_analysis(
                financial_impact, reputational_impact, regulatory_risk, target_info
            )
            results['enhanced_impact_analysis'] = enhanced_analysis
            
            results['impact_enhancement_successful'] = True
        
        except Exception as e:
            results['error'] = f'Business impact enhancement failed: {str(e)}'
        
        return results
    
    def _calculate_financial_impact(self, finding: dict, target_info: dict) -> float:
        """Hitung dampak finansial."""
        base_impact = 10000  # USD
        
        # Faktor berdasarkan tipe kerentanan
        vuln_type = finding.get('type', '').lower()
        vuln_multipliers = {
            'rce': 10.0,
            'sqli': 8.0,
            'ssrf': 6.0,
            'xss': 3.0,
            'idor': 5.0,
            'auth_bypass': 7.0
        }
        vuln_multiplier = vuln_multipliers.get(vuln_type, 2.0)
        
        # Faktor berdasarkan industri
        industry = target_info.get('industry', 'technology').lower()
        industry_multiplier = self.industry_multipliers.get(industry, 1.0)
        
        # Faktor berdasarkan jumlah pengguna yang terdampak
        affected_users = finding.get('affected_users', 1000)
        user_multiplier = min(affected_users / 1000, 100.0)
        
        financial_impact = base_impact * vuln_multiplier * industry_multiplier * user_multiplier
        
        return min(financial_impact, 10000000)  # Batas maksimum $10 juta
    
    def _calculate_reputational_impact(self, finding: dict, target_info: dict) -> float:
        """Hitung dampak reputasi."""
        base_score = 50.0
        
        # Faktor berdasarkan visibilitas
        visibility = finding.get('visibility', 'internal')
        if visibility == 'public':
            base_score += 30.0
        elif visibility == 'semi_public':
            base_score += 15.0
        
        # Faktor berdasarkan sensitivitas data
        data_sensitivity = finding.get('data_sensitivity', 'low')
        sensitivity_scores = {'high': 25.0, 'medium': 15.0, 'low': 5.0}
        base_score += sensitivity_scores.get(data_sensitivity, 0)
        
        # Faktor berdasarkan ukuran perusahaan
        company_size = target_info.get('company_size', 'medium')
        size_scores = {'large': 10.0, 'medium': 5.0, 'small': 0.0}
        base_score += size_scores.get(company_size, 0)
        
        return min(base_score, 100.0)
    
    def _assess_regulatory_risk(self, finding: dict, target_info: dict) -> str:
        """Nilai risiko regulasi."""
        industry = target_info.get('industry', '').lower()
        data_involved = finding.get('data_involved', [])
        
        # Industri yang diatur ketat
        regulated_industries = ['finance', 'healthcare', 'government']
        
        # Data yang diatur
        regulated_data = ['pii', 'financial', 'health', 'children']
        
        if any(industry == reg_ind for reg_ind in regulated_industries) and \
           any(data in regulated_data for data in data_involved):
            return 'high'
        elif industry in regulated_industries or any(data in regulated_data for data in data_involved):
            return 'medium'
        else:
            return 'low'
    
    def _build_enhanced_impact_analysis(self, financial_impact: float, 
                                      reputational_impact: float, 
                                      regulatory_risk: str,
                                      target_info: dict) -> dict:
        """Bangun analisis dampak yang ditingkatkan."""
        return {
            'executive_summary': f"This vulnerability could result in ${financial_impact:,.0f} in financial losses and a {reputational_impact:.0f}/100 reputational damage score.",
            'financial_breakdown': {
                'direct_costs': financial_impact * 0.4,
                'indirect_costs': financial_impact * 0.35,
                'regulatory_fines': financial_impact * 0.25 if regulatory_risk == 'high' else financial_impact * 0.1
            },
            'reputational_consequences': {
                'customer_trust_loss': f"{min(reputational_impact * 0.6, 60):.0f}% estimated customer trust loss",
                'media_attention': 'High' if reputational_impact > 70 else 'Medium' if reputational_impact > 50 else 'Low',
                'stock_price_impact': f"-{min(reputational_impact * 0.3, 15):.0f}% potential stock price impact" if target_info.get('public_company') else 'N/A'
            },
            'regulatory_implications': {
                'risk_level': regulatory_risk,
                'potential_fines': self._estimate_regulatory_fines(regulatory_risk, target_info),
                'compliance_requirements': self._get_compliance_requirements(regulatory_risk, target_info)
            },
            'business_continuity_impact': {
                'service_disruption': 'Possible' if financial_impact > 100000 else 'Unlikely',
                'customer_churn_risk': 'High' if reputational_impact > 60 else 'Medium' if reputational_impact > 40 else 'Low'
            }
        }
    
    def _estimate_regulatory_fines(self, risk_level: str, target_info: dict) -> str:
        """Perkirakan denda regulasi."""
        if risk_level == 'high':
            industry = target_info.get('industry', '')
            if industry == 'finance':
                return 'Up to 2% of annual revenue or $5M (whichever is higher)'
            elif industry == 'healthcare':
                return 'Up to $1.5M per violation under HIPAA'
            elif industry == 'government':
                return 'Contract termination and civil penalties'
            else:
                return 'Up to $2M in regulatory fines'
        elif risk_level == 'medium':
            return 'Up to $500K in regulatory fines'
        else:
            return 'Minimal regulatory risk'
    
    def _get_compliance_requirements(self, risk_level: str, target_info: dict) -> list:
        """Dapatkan persyaratan kepatuhan."""
        if risk_level == 'high':
            industry = target_info.get('industry', '')
            if industry == 'finance':
                return ['GDPR Article 33', 'POJK No. 13/2023', 'PCI DSS Requirement 12']
            elif industry == 'healthcare':
                return ['HIPAA Breach Notification Rule', 'GDPR Article 33']
            elif industry == 'government':
                return ['UU PDP No. 27/2022', 'SPBE Security Incident Reporting']
            else:
                return ['GDPR Article 33', 'CCPA Breach Notification']
        elif risk_level == 'medium':
            return ['Internal security policy reporting', 'Voluntary disclosure frameworks']
        else:
            return ['Best practice disclosure']