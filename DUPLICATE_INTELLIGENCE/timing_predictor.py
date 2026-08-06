import json
from datetime import datetime, timedelta

class TimingPredictor:
    """
    Prediksi window aman untuk submit.
    Memprediksi waktu terbaik untuk mengirimkan laporan guna menghindari duplikat.
    """
    
    def __init__(self):
        self.submission_windows = {
            'monday': {'start': 9, 'end': 17},
            'tuesday': {'start': 9, 'end': 17},
            'wednesday': {'start': 9, 'end': 17},
            'thursday': {'start': 9, 'end': 17},
            'friday': {'start': 9, 'end': 15},
            'weekend': {'submit': False}
        }
    
    def predict_safe_submission_window(self, target_program: str, vulnerability_data: dict):
        """
        Prediksi window aman untuk pengiriman laporan.
        """
        results = {
            'target_program': target_program,
            'vulnerability_data': vulnerability_data,
            'safe_to_submit': False,
            'recommended_window': None,
            'risk_factors': [],
            'confidence_score': 0.0
        }
        
        try:
            # Analisis faktor risiko
            risk_factors = self._analyze_risk_factors(target_program, vulnerability_data)
            results['risk_factors'] = risk_factors
            
            # Tentukan apakah aman untuk mengirim
            safe_to_submit = len(risk_factors) == 0
            results['safe_to_submit'] = safe_to_submit
            
            if safe_to_submit:
                # Rekomendasikan window waktu
                current_time = datetime.now()
                recommended_window = self._get_recommended_window(current_time)
                results['recommended_window'] = recommended_window
                
                # Skor kepercayaan tinggi jika tidak ada faktor risiko
                results['confidence_score'] = 0.95
            else:
                # Skor kepercayaan rendah jika ada faktor risiko
                results['confidence_score'] = max(0.1, 1.0 - (len(risk_factors) * 0.2))
        
        except Exception as e:
            results['error'] = f'Timing prediction failed: {str(e)}'
        
        return results
    
    def _analyze_risk_factors(self, program: str, vuln_data: dict) -> list:
        """Analisis faktor risiko untuk duplikat."""
        risk_factors = []
        
        # Faktor 1: Program dengan banyak peneliti aktif
        high_activity_programs = ['hackerone', 'bugcrowd', 'intigriti']
        if any(high_activity in program.lower() for high_activity in high_activity_programs):
            risk_factors.append('High researcher activity increases duplicate risk')
        
        # Faktor 2: Jenis kerentanan umum
        common_vulns = ['xss', 'csrf', 'info disclosure']
        vuln_type = vuln_data.get('type', '').lower()
        if any(common in vuln_type for common in common_vulns):
            risk_factors.append('Common vulnerability type has higher duplicate probability')
        
        # Faktor 3: Target populer
        popular_targets = ['facebook', 'google', 'microsoft', 'amazon']
        target = vuln_data.get('target', '').lower()
        if any(popular in target for popular in popular_targets):
            risk_factors.append('Popular target attracts many researchers')
        
        # Faktor 4: Waktu peluncuran fitur baru
        # (Asumsikan risiko tinggi jika dalam 7 hari terakhir)
        discovery_date = vuln_data.get('discovery_date')
        if discovery_date:
            try:
                disc_dt = datetime.fromisoformat(discovery_date.replace('Z', '+00:00'))
                if datetime.now() - disc_dt < timedelta(days=7):
                    risk_factors.append('Recent discovery during high-activity period')
            except:
                pass
        
        return risk_factors
    
    def _get_recommended_window(self, current_time: datetime) -> dict:
        """Dapatkan window waktu yang direkomendasikan."""
        day_name = current_time.strftime('%A').lower()
        
        if day_name in ['saturday', 'sunday']:
            # Rekomendasikan Senin pagi
            next_monday = current_time + timedelta(days=(7 - current_time.weekday()))
            return {
                'day': 'Monday',
                'start_time': '09:00',
                'end_time': '11:00',
                'reason': 'Early week submission avoids weekend backlog'
            }
        elif day_name == 'friday':
            # Rekomendasikan Jumat pagi
            return {
                'day': 'Friday',
                'start_time': '09:00',
                'end_time': '11:00',
                'reason': 'Early Friday avoids weekend delay'
            }
        else:
            # Rekomendasikan pagi hari
            return {
                'day': day_name.capitalize(),
                'start_time': '09:00',
                'end_time': '11:00',
                'reason': 'Morning submission gets priority triage'
            }