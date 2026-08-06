class CloudBlastRadiusAnalyzer:
    """
    Full ecosystem impact scoring (data, services, accounts).
    Menghitung skor dampak ledakan penuh di ekosistem cloud.
    """
    
    def __init__(self):
        self.impact_categories = {
            'data_exposure': {
                'weight': 0.4,
                'factors': ['sensitive_data_volume', 'data_classification', 'encryption_status']
            },
            'service_disruption': {
                'weight': 0.3,
                'factors': ['critical_services_affected', 'sla_impact', 'customer_facing']
            },
            'financial_loss': {
                'weight': 0.2,
                'factors': ['direct_costs', 'regulatory_fines', 'reputation_damage']
            },
            'compliance_violation': {
                'weight': 0.1,
                'factors': ['gdpr', 'hipaa', 'pci_dss', 'sox']
            }
        }
    
    def analyze_cloud_blast_radius(self, compromised_resources: Dict, cloud_platform: str):
        """
        Analisis radius dampak ledakan di lingkungan cloud.
        """
        results = {
            'cloud_platform': cloud_platform,
            'compromised_resources': compromised_resources,
            'impact_scores': {},
            'total_blast_radius_score': 0.0,
            'risk_assessment': {},
            'mitigation_strategies': []
        }
        
        try:
            # Hitung skor untuk setiap kategori dampak
            impact_scores = {}
            total_weighted_score = 0.0
            
            for category, config in self.impact_categories.items():
                category_score = self._calculate_category_score(category, compromised_resources, cloud_platform)
                weighted_score = category_score * config['weight']
                impact_scores[category] = {
                    'raw_score': category_score,
                    'weighted_score': weighted_score,
                    'factors_analyzed': config['factors']
                }
                total_weighted_score += weighted_score
            
            results['impact_scores'] = impact_scores
            results['total_blast_radius_score'] = min(total_weighted_score, 1.0)
            
            # Buat penilaian risiko
            results['risk_assessment'] = self._generate_risk_assessment(results['total_blast_radius_score'])
            
            # Buat strategi mitigasi
            results['mitigation_strategies'] = self._generate_mitigation_strategies(
                impact_scores, cloud_platform
            )
        
        except Exception as e:
            results['error'] = f'Cloud blast radius analysis failed: {str(e)}'
        
        return results
    
    def _calculate_category_score(self, category: str, resources: Dict, platform: str) -> float:
        """Hitung skor untuk kategori dampak tertentu."""
        if category == 'data_exposure':
            # Estimasi volume data sensitif
            sensitive_data_types = ['pii', 'financial', 'healthcare', 'credentials']
            sensitive_count = sum(
                1 for resource in resources.get('data_stores', [])
                if any(data_type in str(resource).lower() for data_type in sensitive_data_types)
            )
            total_data_stores = len(resources.get('data_stores', []))
            return min(sensitive_count / max(total_data_stores, 1), 1.0)
        
        elif category == 'service_disruption':
            # Estimasi layanan kritis yang terdampak
            critical_services = ['api', 'database', 'authentication', 'payment']
            critical_count = sum(
                1 for resource in resources.get('services', [])
                if any(service in str(resource).lower() for service in critical_services)
            )
            total_services = len(resources.get('services', []))
            return min(critical_count / max(total_services, 1), 1.0)
        
        elif category == 'financial_loss':
            # Estimasi kerugian finansial berdasarkan sumber daya
            high_value_resources = ['production', 'customer_facing', 'revenue_generating']
            high_value_count = sum(
                1 for resource in resources.get('all_resources', [])
                if any(val in str(resource).lower() for val in high_value_resources)
            )
            total_resources = len(resources.get('all_resources', []))
            return min(high_value_count / max(total_resources, 1), 1.0)
        
        elif category == 'compliance_violation':
            # Cek pelanggaran compliance
            regulated_industries = ['healthcare', 'finance', 'government']
            if any(industry in resources.get('organization_type', '').lower() for industry in regulated_industries):
                return 1.0
            return 0.0
        
        return 0.0
    
    def _generate_risk_assessment(self, total_score: float) -> Dict:
        """Hasilkan penilaian risiko berdasarkan skor total."""
        if total_score >= 0.7:
            severity = 'CRITICAL'
            description = 'Catastrophic ecosystem impact - immediate executive attention required'
        elif total_score >= 0.4:
            severity = 'HIGH'
            description = 'Significant business impact - urgent remediation needed'
        elif total_score >= 0.2:
            severity = 'MEDIUM'
            description = 'Moderate impact - scheduled remediation recommended'
        else:
            severity = 'LOW'
            description = 'Limited impact - monitor and document'
        
        return {
            'severity': severity,
            'description': description,
            'estimated_financial_impact': self._estimate_financial_impact(severity, total_score),
            'recommended_response_time': self._get_response_time(severity)
        }
    
    def _estimate_financial_impact(self, severity: str, score: float) -> str:
        """Estimasi dampak finansial."""
        if severity == 'CRITICAL':
            return f"${int(score * 1000000):,} - ${int(score * 10000000):,}"
        elif severity == 'HIGH':
            return f"${int(score * 100000):,} - ${int(score * 1000000):,}"
        elif severity == 'MEDIUM':
            return f"${int(score * 10000):,} - ${int(score * 100000):,}"
        else:
            return "$0 - $10,000"
    
    def _get_response_time(self, severity: str) -> str:
        """Dapatkan waktu respon yang direkomendasikan."""
        times = {
            'CRITICAL': 'IMMEDIATE (within 1 hour)',
            'HIGH': 'URGENT (within 24 hours)',
            'MEDIUM': 'STANDARD (within 7 days)',
            'LOW': 'MONITOR (monthly review)'
        }
        return times.get(severity, 'ASSESS MANUALLY')
    
    def _generate_mitigation_strategies(self, impact_scores: Dict, platform: str) -> List[str]:
        """Hasilkan strategi mitigasi berdasarkan skor dampak."""
        strategies = []
        
        # Strategi berdasarkan kategori dengan skor tertinggi
        highest_category = max(impact_scores.keys(), key=lambda k: impact_scores[k]['weighted_score'])
        
        if highest_category == 'data_exposure':
            strategies.extend([
                'Implement data encryption at rest and in transit',
                'Apply data loss prevention (DLP) controls',
                'Classify and label sensitive data automatically'
            ])
        elif highest_category == 'service_disruption':
            strategies.extend([
                'Implement high availability and disaster recovery',
                'Deploy circuit breakers and rate limiting',
                'Conduct regular chaos engineering tests'
            ])
        elif highest_category == 'financial_loss':
            strategies.extend([
                'Implement cost anomaly detection',
                'Set up budget alerts and spending limits',
                'Use reserved instances for predictable workloads'
            ])
        elif highest_category == 'compliance_violation':
            strategies.extend([
                'Implement compliance as code',
                'Conduct regular security and compliance audits',
                'Use cloud provider compliance reporting tools'
            ])
        
        # Strategi spesifik platform
        if platform == 'aws':
            strategies.append('Use AWS Security Hub for centralized security findings')
        elif platform == 'azure':
            strategies.append('Implement Microsoft Defender for Cloud')
        elif platform == 'gcp':
            strategies.append('Use Security Command Center for threat detection')
        
        return strategies