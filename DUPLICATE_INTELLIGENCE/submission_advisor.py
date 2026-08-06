class SubmissionAdvisor:
    """
    Saran kapan dan bagaimana submit.
    Memberikan saran strategis untuk pengiriman laporan.
    """
    
    def __init__(self):
        self.advice_categories = {
            'timing': 'When to submit',
            'formatting': 'How to format the report',
            'evidence': 'What evidence to include',
            'uniqueness': 'How to emphasize uniqueness',
            'follow_up': 'How to follow up appropriately'
        }
    
    def provide_submission_advice(self, duplicate_analysis: dict, timing_analysis: dict):
        """
        Berikan saran pengiriman berdasarkan analisis duplikat dan waktu.
        """
        results = {
            'duplicate_analysis': duplicate_analysis,
            'timing_analysis': timing_analysis,
            'submission_advice': {},
            'overall_recommendation': None,
            'confidence_level': 'high'
        }
        
        try:
            # Saran berdasarkan analisis duplikat
            duplicate_advice = self._generate_duplicate_advice(duplicate_analysis)
            results['submission_advice']['duplicate_handling'] = duplicate_advice
            
            # Saran berdasarkan analisis waktu
            timing_advice = self._generate_timing_advice(timing_analysis)
            results['submission_advice']['timing_strategy'] = timing_advice
            
            # Saran format laporan
            format_advice = self._generate_format_advice(duplicate_analysis)
            results['submission_advice']['report_formatting'] = format_advice
            
            # Rekomendasi keseluruhan
            overall_recommendation = self._generate_overall_recommendation(
                duplicate_analysis, timing_analysis
            )
            results['overall_recommendation'] = overall_recommendation
            
            # Tingkat kepercayaan
            if duplicate_analysis.get('is_duplicate', False):
                results['confidence_level'] = 'low'
            elif timing_analysis.get('safe_to_submit', True):
                results['confidence_level'] = 'high'
            else:
                results['confidence_level'] = 'medium'
        
        except Exception as e:
            results['error'] = f'Submission advice generation failed: {str(e)}'
        
        return results
    
    def _generate_duplicate_advice(self, duplicate_analysis: dict) -> dict:
        """Hasilkan saran penanganan duplikat."""
        if duplicate_analysis.get('is_duplicate', False):
            return {
                'action': 'DO_NOT_SUBMIT',
                'reason': 'High probability of duplicate submission',
                'alternative': 'Enhance uniqueness before submitting'
            }
        elif duplicate_analysis.get('similarity_score', 0) >= 0.6:
            return {
                'action': 'ENHANCE_UNIQUENESS',
                'reason': 'Moderate similarity detected',
                'recommendations': [
                    'Add business impact quantification',
                    'Include additional exploitation paths',
                    'Provide more detailed technical analysis',
                    'Expand scope to affected subdomains'
                ]
            }
        else:
            return {
                'action': 'PROCEED_WITH_SUBMISSION',
                'reason': 'Low similarity with existing reports',
                'confidence': 'High confidence in uniqueness'
            }
    
    def _generate_timing_advice(self, timing_analysis: dict) -> dict:
        """Hasilkan saran strategi waktu."""
        if timing_analysis.get('safe_to_submit', True):
            window = timing_analysis.get('recommended_window', {})
            return {
                'action': 'SUBMIT_DURING_WINDOW',
                'window': window,
                'benefits': [
                    'Higher priority triage',
                    'Faster response time',
                    'Better researcher reputation building'
                ]
            }
        else:
            risk_factors = timing_analysis.get('risk_factors', [])
            return {
                'action': 'DELAY_SUBMISSION',
                'risk_factors': risk_factors,
                'recommendation': 'Wait for lower-risk submission window'
            }
    
    def _generate_format_advice(self, duplicate_analysis: dict) -> dict:
        """Hasilkan saran format laporan."""
        similarity_score = duplicate_analysis.get('similarity_score', 0)
        
        if similarity_score >= 0.8:
            # Format untuk laporan sangat mirip
            return {
                'title_strategy': 'Emphasize unique aspects in title',
                'structure': [
                    'Executive Summary highlighting uniqueness',
                    'Detailed Technical Analysis with novel insights',
                    'Business Impact Quantification',
                    'Enhanced Remediation Recommendations',
                    'Comprehensive Evidence Package'
                ],
                'evidence_requirements': [
                    'Video PoC with URL overlay',
                    'HAR file with request/response details',
                    'Network capture (PCAP)',
                    'Reproduction script',
                    'Economic impact simulation'
                ]
            }
        elif similarity_score >= 0.6:
            # Format untuk laporan cukup mirip
            return {
                'title_strategy': 'Clear vulnerability type and target',
                'structure': [
                    'Technical Description',
                    'Reproduction Steps',
                    'Impact Assessment',
                    'Remediation Advice',
                    'Evidence Package'
                ],
                'evidence_requirements': [
                    'Video PoC',
                    'Screenshots',
                    'HAR file',
                    'Reproduction script'
                ]
            }
        else:
            # Format untuk laporan unik
            return {
                'title_strategy': 'Standard vulnerability description',
                'structure': [
                    'Summary',
                    'Technical Details',
                    'Steps to Reproduce',
                    'Impact',
                    'Remediation'
                ],
                'evidence_requirements': [
                    'Screenshots',
                    'Reproduction steps',
                    'Basic evidence'
                ]
            }
    
    def _generate_overall_recommendation(self, duplicate_analysis: dict, timing_analysis: dict) -> str:
        """Hasilkan rekomendasi keseluruhan."""
        is_duplicate = duplicate_analysis.get('is_duplicate', False)
        safe_to_submit = timing_analysis.get('safe_to_submit', True)
        
        if is_duplicate:
            return "DO NOT SUBMIT - High probability of duplicate. Focus on enhancing uniqueness first."
        elif not safe_to_submit:
            return "DELAY SUBMISSION - Wait for safer timing window to maximize impact and acceptance."
        elif duplicate_analysis.get('similarity_score', 0) >= 0.6:
            return "ENHANCE THEN SUBMIT - Improve uniqueness before submitting during recommended window."
        else:
            return "PROCEED WITH SUBMISSION - Unique finding with optimal timing. Submit during recommended window."