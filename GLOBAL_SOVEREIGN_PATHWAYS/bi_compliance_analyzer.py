class BIComplianceAnalyzer:
    """
    Bank Indonesia regulation mapper.
    Memetakan regulasi Bank Indonesia untuk program keamanan.
    """
    
    def __init__(self):
        self.bi_regulations = {
            'pbi_23_2_2021': {
                'title': 'PBI No. 23/2/2021 tentang Standar Keamanan Sistem Informasi',
                'key_requirements': [
                    'Implementasi manajemen risiko keamanan siber',
                    'Pelaporan insiden keamanan siber ke BI',
                    'Audit keamanan siber minimal 1x per tahun',
                    'Pemantauan keamanan siber secara real-time'
                ],
                'incident_reporting': {
                    'timeline': '2x24 jam untuk insiden kritis',
                    'format': 'Formulir Pelaporan Insiden Keamanan Siber BI',
                    'contact': 'direktur.pengawasan@bi.go.id'
                },
                'penalties': 'Denda hingga Rp5 miliar atau pencabutan izin operasional'
            },
            'pbi_22_23_2020': {
                'title': 'PBI No. 22/23/PBI/2020 tentang Penyelenggaraan Sistem Pembayaran',
                'key_requirements': [
                    'Keamanan transaksi pembayaran real-time',
                    'Proteksi data nasabah dalam sistem pembayaran',
                    'Ketersediaan sistem pembayaran 24/7',
                    'Manajemen risiko operasional sistem pembayaran'
                ],
                'incident_reporting': {
                    'timeline': '1x24 jam untuk gangguan sistem pembayaran',
                    'format': 'Laporan Gangguan Sistem Pembayaran',
                    'contact': 'sistem.pembayaran@bi.go.id'
                },
                'penalties': 'Denda hingga Rp2 miliar per insiden'
            }
        }
    
    def analyze_bi_compliance(self, target_institution: str, vulnerability_data: dict):
        """
        Analisis kepatuhan regulasi BI untuk institusi target.
        """
        results = {
            'target_institution': target_institution,
            'vulnerability_data': vulnerability_data,
            'applicable_regulations': [],
            'compliance_gaps': [],
            'reporting_requirements': {},
            'risk_assessment': {}
        }
        
        try:
            # Tentukan regulasi BI yang berlaku
            applicable_regs = self._determine_applicable_regulations(target_institution, vulnerability_data)
            results['applicable_regulations'] = applicable_regs
            
            # Identifikasi kesenjangan kepatuhan
            compliance_gaps = self._identify_compliance_gaps(vulnerability_data, applicable_regs)
            results['compliance_gaps'] = compliance_gaps
            
            # Bangun persyaratan pelaporan
            reporting_reqs = self._build_reporting_requirements(applicable_regs)
            results['reporting_requirements'] = reporting_reqs
            
            # Nilai risiko regulasi
            risk_assessment = self._assess_regulatory_risk(vulnerability_data, applicable_regs)
            results['risk_assessment'] = risk_assessment
        
        except Exception as e:
            results['error'] = f'BI compliance analysis failed: {str(e)}'
        
        return results
    
    def _determine_applicable_regulations(self, institution: str, vuln_data: dict) -> list:
        """Tentukan regulasi BI yang berlaku."""
        applicable = []
        institution_lower = institution.lower()
        vuln_type = vuln_data.get('type', '').lower()
        
        # Cek PBI 23/2/2021 (Standar Keamanan Sistem Informasi)
        if any(keyword in institution_lower for keyword in ['bank', 'financial', 'payment', 'fintech']):
            applicable.append('pbi_23_2_2021')
        
        # Cek PBI 22/23/2020 (Sistem Pembayaran)
        payment_related_vulns = ['payment', 'transaction', 'qr', 'transfer', 'realtime']
        if any(keyword in vuln_type for keyword in payment_related_vulns):
            applicable.append('pbi_22_23_2020')
        
        return applicable
    
    def _identify_compliance_gaps(self, vuln_data: dict, regulations: list) -> list:
        """Identifikasi kesenjangan kepatuhan."""
        gaps = []
        
        for reg_key in regulations:
            reg_info = self.bi_regulations[reg_key]
            
            # Cek apakah kerentanan melanggar persyaratan utama
            for requirement in reg_info['key_requirements']:
                if self._vulnerability_violates_requirement(vuln_data, requirement):
                    gaps.append({
                        'regulation': reg_key,
                        'requirement_violated': requirement,
                        'severity': 'HIGH' if 'critical' in vuln_data.get('severity', '').lower() else 'MEDIUM'
                    })
        
        return gaps
    
    def _vulnerability_violates_requirement(self, vuln_data: dict, requirement: str) -> bool:
        """Periksa apakah kerentanan melanggar persyaratan."""
        vuln_type = vuln_data.get('type', '').lower()
        severity = vuln_data.get('severity', '').lower()
        
        # Mapping sederhana antara tipe kerentanan dan pelanggaran
        violation_mapping = {
            'data_breach': ['manajemen risiko', 'proteksi data'],
            'system_compromise': ['keamanan siber', 'ketersediaan sistem'],
            'payment_abuse': ['keamanan transaksi', 'sistem pembayaran'],
            'rce': ['keamanan siber', 'manajemen risiko']
        }
        
        for vuln_category, keywords in violation_mapping.items():
            if vuln_category in vuln_type or any(keyword in requirement.lower() for keyword in keywords):
                return True
        
        return False
    
    def _build_reporting_requirements(self, regulations: list) -> dict:
        """Bangun persyaratan pelaporan."""
        if not regulations:
            return {'message': 'No BI regulations applicable'}
        
        # Gabungkan persyaratan dari semua regulasi yang berlaku
        combined_requirements = {
            'timeline': 'ASAP',
            'format': 'Combined BI Reporting Format',
            'contacts': [],
            'documentation_needed': []
        }
        
        for reg_key in regulations:
            reg_info = self.bi_regulations[reg_key]
            incident_info = reg_info['incident_reporting']
            
            combined_requirements['contacts'].append(incident_info['contact'])
            combined_requirements['documentation_needed'].extend([
                incident_info['format'],
                'Analisis dampak bisnis',
                'Rencana mitigasi'
            ])
        
        # Tentukan timeline paling ketat
        timelines = [reg_info['incident_reporting']['timeline'] 
                    for reg_key, reg_info in self.bi_regulations.items() 
                    if reg_key in regulations]
        combined_requirements['timeline'] = min(timelines, key=lambda x: ('2x24' in x, '1x24' in x))
        
        return combined_requirements
    
    def _assess_regulatory_risk(self, vuln_data: dict, regulations: list) -> dict:
        """Nilai risiko regulasi."""
        if not regulations:
            return {'risk_level': 'LOW', 'potential_penalties': 'None', 'recommendation': 'Standard disclosure'}
        
        severity = vuln_data.get('severity', 'medium').lower()
        impact = vuln_data.get('business_impact', '')
        
        if 'critical' in severity or 'financial loss' in impact.lower():
            risk_level = 'CRITICAL'
            potential_penalties = 'Denda hingga Rp5 miliar + pencabutan izin'
        elif 'high' in severity:
            risk_level = 'HIGH'
            potential_penalties = 'Denda hingga Rp2 miliar'
        else:
            risk_level = 'MEDIUM'
            potential_penalties = 'Peringatan tertulis + audit wajib'
        
        return {
            'risk_level': risk_level,
            'potential_penalties': potential_penalties,
            'recommendation': self._get_risk_recommendation(risk_level, regulations)
        }
    
    def _get_risk_recommendation(self, risk_level: str, regulations: list) -> str:
        """Dapatkan rekomendasi berdasarkan tingkat risiko."""
        if risk_level == 'CRITICAL':
            return 'Segera laporkan ke BI dalam 24 jam dan koordinasi dengan tim hukum'
        elif risk_level == 'HIGH':
            return 'Laporkan dalam 48 jam dan siapkan dokumentasi lengkap'
        else:
            return 'Laporkan sesuai timeline standar dan dokumentasi dasar'