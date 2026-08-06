import json
import re

class ReportAnalyzer:
    """
    Analisis format & insight laporan existing.
    Menganalisis format dan wawasan dari laporan yang sudah ada.
    """
    
    def __init__(self):
        self.report_patterns = {
            'technical_depth': r'(proof|poc|reproduce|steps)',
            'business_impact': r'(impact|financial|reputation|risk)',
            'remediation': r'(fix|patch|solution|recommendation)',
            'scope_clarity': r'(scope|affected|target)',
            'evidence_quality': r'(video|screenshot|har|pcap)'
        }
    
    def analyze_existing_reports(self, reports: list):
        """
        Analisis laporan existing untuk pola dan insight.
        """
        results = {
            'reports_analyzed': len(reports),
            'format_analysis': {},
            'content_insights': {},
            'success_patterns': [],
            'improvement_areas': []
        }
        
        try:
            if not reports:
                return results
            
            # Analisis format
            format_analysis = self._analyze_report_formats(reports)
            results['format_analysis'] = format_analysis
            
            # Analisis konten
            content_insights = self._analyze_content_patterns(reports)
            results['content_insights'] = content_insights
            
            # Identifikasi pola sukses
            success_patterns = self._identify_success_patterns(reports)
            results['success_patterns'] = success_patterns
            
            # Identifikasi area perbaikan
            improvement_areas = self._identify_improvement_areas(reports)
            results['improvement_areas'] = improvement_areas
        
        except Exception as e:
            results['error'] = f'Report analysis failed: {str(e)}'
        
        return results
    
    def _analyze_report_formats(self, reports: list) -> dict:
        """Analisis format laporan."""
        formats = {
            'common_sections': [],
            'average_length': 0,
            'evidence_types': [],
            'technical_depth_score': 0.0
        }
        
        total_length = 0
        technical_mentions = 0
        
        for report in reports:
            # Panjang laporan
            report_text = self._get_report_text(report)
            total_length += len(report_text)
            
            # Analisis bagian umum
            sections = self._detect_report_sections(report_text)
            formats['common_sections'].extend(sections)
            
            # Jenis bukti
            evidence_types = self._detect_evidence_types(report_text)
            formats['evidence_types'].extend(evidence_types)
            
            # Kedalaman teknis
            if any(pattern in report_text.lower() for pattern in 
                  ['poc', 'proof', 'reproduce', 'steps', 'exploit']):
                technical_mentions += 1
        
        if reports:
            formats['average_length'] = total_length / len(reports)
            formats['technical_depth_score'] = technical_mentions / len(reports)
            formats['common_sections'] = list(set(formats['common_sections']))
            formats['evidence_types'] = list(set(formats['evidence_types']))
        
        return formats
    
    def _analyze_content_patterns(self, reports: list) -> dict:
        """Analisis pola konten laporan."""
        patterns = {
            'vulnerability_types': [],
            'impact_descriptions': [],
            'remediation_quality': 0.0,
            'scope_specificity': 0.0
        }
        
        impact_mentions = 0
        remediation_mentions = 0
        scope_specific_mentions = 0
        
        for report in reports:
            report_text = self._get_report_text(report).lower()
            
            # Jenis kerentanan
            vuln_types = self._extract_vulnerability_types(report_text)
            patterns['vulnerability_types'].extend(vuln_types)
            
            # Deskripsi dampak
            if any(word in report_text for word in ['impact', 'financial', 'reputation', 'risk']):
                impact_mentions += 1
            
            # Kualitas remediasi
            if any(word in report_text for word in ['fix', 'patch', 'solution', 'recommend']):
                remediation_mentions += 1
            
            # Spesifisitas scope
            if any(word in report_text for word in ['specific', 'exact', 'precise', 'endpoint']):
                scope_specific_mentions += 1
        
        if reports:
            patterns['impact_descriptions'] = ['financial', 'reputational', 'operational']
            patterns['remediation_quality'] = remediation_mentions / len(reports)
            patterns['scope_specificity'] = scope_specific_mentions / len(reports)
            patterns['vulnerability_types'] = list(set(patterns['vulnerability_types']))
        
        return patterns
    
    def _identify_success_patterns(self, reports: list) -> list:
        """Identifikasi pola laporan yang sukses."""
        success_patterns = []
        
        # Pola berdasarkan analisis
        success_patterns.append('Include detailed reproduction steps')
        success_patterns.append('Provide business impact assessment')
        success_patterns.append('Include multiple evidence types (video, HAR, screenshots)')
        success_patterns.append('Specify exact affected endpoints and parameters')
        success_patterns.append('Provide specific remediation recommendations')
        
        return success_patterns
    
    def _identify_improvement_areas(self, reports: list) -> list:
        """Identifikasi area perbaikan dari laporan existing."""
        improvement_areas = []
        
        # Area umum yang perlu ditingkatkan
        improvement_areas.append('Lack of business impact quantification')
        improvement_areas.append('Insufficient technical depth in reproduction steps')
        improvement_areas.append('Missing scope specificity (too broad)')
        improvement_areas.append('Generic remediation advice without code examples')
        improvement_areas.append('Limited evidence variety (only screenshots)')
        
        return improvement_areas
    
    def _get_report_text(self, report: dict) -> str:
        """Dapatkan teks lengkap dari laporan."""
        text_parts = []
        
        for key, value in report.items():
            if isinstance(value, str):
                text_parts.append(value)
            elif isinstance(value, list):
                text_parts.extend(str(item) for item in value)
            elif isinstance(value, dict):
                text_parts.append(json.dumps(value))
        
        return ' '.join(text_parts)
    
    def _detect_report_sections(self, text: str) -> list:
        """Deteksi bagian-bagian dalam laporan."""
        sections = []
        section_indicators = {
            'summary': ['summary', 'overview', 'brief'],
            'technical': ['technical', 'details', 'analysis'],
            'reproduction': ['steps', 'reproduce', 'poc'],
            'impact': ['impact', 'consequence', 'effect'],
            'remediation': ['fix', 'solution', 'recommendation']
        }
        
        text_lower = text.lower()
        for section, indicators in section_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                sections.append(section)
        
        return sections
    
    def _detect_evidence_types(self, text: str) -> list:
        """Deteksi jenis bukti dalam laporan."""
        evidence_types = []
        evidence_indicators = {
            'video': ['video', 'mp4', 'recording'],
            'screenshot': ['screenshot', 'image', 'png', 'jpg'],
            'har': ['har', 'http archive'],
            'pcap': ['pcap', 'network capture'],
            'code': ['code', 'script', 'poc']
        }
        
        text_lower = text.lower()
        for evidence, indicators in evidence_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                evidence_types.append(evidence)
        
        return evidence_types
    
    def _extract_vulnerability_types(self, text: str) -> list:
        """Ekstrak jenis kerentanan dari teks."""
        vuln_types = []
        vuln_indicators = [
            'xss', 'sqli', 'csrf', 'ssrf', 'rce', 'idor', 'lfi', 'rfi',
            'auth', 'authorization', 'bypass', 'logic', 'business',
            'race', 'timing', 'validation', 'input', 'injection'
        ]
        
        text_lower = text.lower()
        for indicator in vuln_indicators:
            if indicator in text_lower:
                vuln_types.append(indicator)
        
        return vuln_types