class QualityOverQuantityEnforcer:
    """
    Only act if confidence ≥0.95 (reduce false positives).
    Menegakkan standar kualitas dengan threshold kepercayaan tinggi.
    """
    
    def __init__(self, confidence_threshold=0.95):
        self.confidence_threshold = confidence_threshold
        self.quality_metrics = {
            'technical_validation': 0.4,
            'business_impact_verification': 0.3,
            'reproduction_reliability': 0.2,
            'ethical_compliance': 0.1
        }
    
    def enforce_quality_standards(self, finding_data: dict):
        """
        Tegakkan standar kualitas untuk temuan keamanan.
        """
        results = {
            'finding_data': finding_data,
            'quality_score': 0.0,
            'confidence_threshold': self.confidence_threshold,
            'meets_quality_standards': False,
            'validation_details': {},
            'recommendation': None
        }
        
        try:
            # Hitung skor kualitas
            quality_score = self._calculate_quality_score(finding_data)
            results['quality_score'] = quality_score
            
            # Periksa apakah memenuhi standar
            meets_standards = quality_score >= self.confidence_threshold
            results['meets_quality_standards'] = meets_standards
            
            # Detail validasi
            validation_details = self._get_validation_details(finding_data)
            results['validation_details'] = validation_details
            
            # Rekomendasi
            recommendation = self._generate_recommendation(meets_standards, quality_score, finding_data)
            results['recommendation'] = recommendation
        
        except Exception as e:
            results['error'] = f'Quality enforcement failed: {str(e)}'
        
        return results
    
    def _calculate_quality_score(self, finding_data: dict) -> float:
        """Hitung skor kualitas berdasarkan metrik."""
        total_score = 0.0
        
        # Validasi teknis
        technical_score = finding_data.get('technical_validation_score', 0.5)
        total_score += technical_score * self.quality_metrics['technical_validation']
        
        # Verifikasi dampak bisnis
        impact_score = finding_data.get('business_impact_score', 0.5)
        total_score += impact_score * self.quality_metrics['business_impact_verification']
        
        # Keandalan reproduksi
        reproduction_score = finding_data.get('reproduction_reliability_score', 0.5)
        total_score += reproduction_score * self.quality_metrics['reproduction_reliability']
        
        # Kepatuhan etis
        ethical_score = finding_data.get('ethical_compliance_score', 0.5)
        total_score += ethical_score * self.quality_metrics['ethical_compliance']
        
        return min(1.0, total_score)
    
    def _get_validation_details(self, finding_data: dict) -> dict:
        """Dapatkan detail validasi."""
        return {
            'technical_validation': {
                'score': finding_data.get('technical_validation_score', 0.5),
                'method': finding_data.get('validation_method', 'automated'),
                'evidence_quality': finding_data.get('evidence_quality', 'medium')
            },
            'business_impact': {
                'score': finding_data.get('business_impact_score', 0.5),
                'impact_severity': finding_data.get('impact_severity', 'medium'),
                'affected_systems': finding_data.get('affected_systems', [])
            },
            'reproduction': {
                'score': finding_data.get('reproduction_reliability_score', 0.5),
                'success_rate': finding_data.get('reproduction_success_rate', 0.0),
                'environment_consistency': finding_data.get('environment_consistency', 'variable')
            },
            'ethics': {
                'score': finding_data.get('ethical_compliance_score', 0.5),
                'scope_compliance': finding_data.get('scope_compliant', True),
                'data_minimization': finding_data.get('data_minimized', True)
            }
        }
    
    def _generate_recommendation(self, meets_standards: bool, quality_score: float, finding_data: dict) -> str:
        """Hasilkan rekomendasi berdasarkan skor kualitas."""
        if meets_standards:
            return f"PROCEED: Finding meets quality standards (score: {quality_score:.2f})"
        elif quality_score >= 0.8:
            return f"IMPROVE: Enhance validation and resubmit (current score: {quality_score:.2f})"
        elif quality_score >= 0.6:
            return f"VALIDATE: Perform additional technical validation (current score: {quality_score:.2f})"
        else:
            return f"REJECT: Insufficient quality for submission (current score: {quality_score:.2f})"