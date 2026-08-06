import json
import os
from datetime import datetime

class ReputationCapitalBuilder:
    """
    Track acceptance rate, triage speed, scope compliance.
    Membangun modal reputasi melalui pelacakan metrik kinerja.
    """
    
    def __init__(self, reputation_dir="~/.arc/reputation"):
        self.reputation_dir = os.path.expanduser(reputation_dir)
        os.makedirs(self.reputation_dir, exist_ok=True)
        self.reputation_file = os.path.join(self.reputation_dir, "reputation_metrics.json")
        self.metrics_history = self._load_metrics_history()
    
    def track_reputation_metrics(self, program_name: str, submission_data: dict):
        """
        Lacak metrik reputasi untuk program tertentu.
        """
        results = {
            'program_name': program_name,
            'submission_data': submission_data,
            'metrics_updated': False,
            'current_metrics': {},
            'reputation_score': 0.0,
            'recommendations': []
        }
        
        try:
            # Update metrik untuk program
            program_metrics = self._update_program_metrics(program_name, submission_data)
            
            # Simpan riwayat yang diperbarui
            self.metrics_history[program_name] = program_metrics
            self._save_metrics_history()
            
            # Hitung skor reputasi
            reputation_score = self._calculate_reputation_score(program_metrics)
            
            results.update({
                'metrics_updated': True,
                'current_metrics': program_metrics,
                'reputation_score': reputation_score,
                'recommendations': self._generate_reputation_recommendations(program_metrics, reputation_score)
            })
        
        except Exception as e:
            results['error'] = f'Reputation tracking failed: {str(e)}'
        
        return results
    
    def _load_metrics_history(self) -> dict:
        """Muat riwayat metrik dari file."""
        if os.path.exists(self.reputation_file):
            try:
                with open(self.reputation_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_metrics_history(self):
        """Simpan riwayat metrik ke file."""
        with open(self.reputation_file, 'w') as f:
            json.dump(self.metrics_history, f, indent=2)
    
    def _update_program_metrics(self, program_name: str, submission_data: dict) -> dict:
        """Update metrik untuk program tertentu."""
        # Dapatkan metrik saat ini atau inisialisasi baru
        current_metrics = self.metrics_history.get(program_name, {
            'submissions': [],
            'acceptance_rate': 0.0,
            'average_triage_time': 0,
            'scope_compliance_rate': 0.0,
            'total_submissions': 0,
            'accepted_submissions': 0,
            'scope_compliant_submissions': 0
        })
        
        # Tambahkan submission baru
        submission_record = {
            'submission_id': submission_data.get('id', f"sub_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            'timestamp': datetime.now().isoformat(),
            'status': submission_data.get('status', 'submitted'),
            'triage_time_hours': submission_data.get('triage_time_hours', 0),
            'scope_compliant': submission_data.get('scope_compliant', True),
            'severity': submission_data.get('severity', 'medium'),
            'bounty_amount': submission_data.get('bounty_amount', 0)
        }
        
        current_metrics['submissions'].append(submission_record)
        current_metrics['total_submissions'] += 1
        
        # Update acceptance rate
        if submission_data.get('status') == 'accepted':
            current_metrics['accepted_submissions'] += 1
        
        current_metrics['acceptance_rate'] = (
            current_metrics['accepted_submissions'] / current_metrics['total_submissions']
        )
        
        # Update scope compliance rate
        if submission_data.get('scope_compliant', True):
            current_metrics['scope_compliant_submissions'] += 1
        
        current_metrics['scope_compliance_rate'] = (
            current_metrics['scope_compliant_submissions'] / current_metrics['total_submissions']
        )
        
        # Update average triage time
        triage_times = [s['triage_time_hours'] for s in current_metrics['submissions'] if s['triage_time_hours'] > 0]
        if triage_times:
            current_metrics['average_triage_time'] = sum(triage_times) / len(triage_times)
        
        return current_metrics
    
    def _calculate_reputation_score(self, metrics: dict) -> float:
        """Hitung skor reputasi berdasarkan metrik."""
        # Bobot untuk setiap metrik
        weights = {
            'acceptance_rate': 0.4,
            'triage_speed': 0.3,
            'scope_compliance': 0.3
        }
        
        # Skor acceptance rate (semakin tinggi semakin baik)
        acceptance_score = min(metrics['acceptance_rate'], 1.0)
        
        # Skor kecepatan triage (semakin cepat semakin baik)
        # Asumsikan triage ideal < 72 jam, skor turun setelah itu
        avg_triage = metrics['average_triage_time']
        if avg_triage <= 72:
            triage_score = 1.0
        elif avg_triage <= 168:  # 1 minggu
            triage_score = 0.7
        else:
            triage_score = 0.4
        
        # Skor kepatuhan scope
        scope_score = min(metrics['scope_compliance_rate'], 1.0)
        
        # Hitung skor akhir
        reputation_score = (
            acceptance_score * weights['acceptance_rate'] +
            triage_score * weights['triage_speed'] +
            scope_score * weights['scope_compliance']
        )
        
        return min(1.0, reputation_score)
    
    def _generate_reputation_recommendations(self, metrics: dict, reputation_score: float) -> list:
        """Hasilkan rekomendasi berdasarkan metrik reputasi."""
        recommendations = []
        
        if metrics['acceptance_rate'] < 0.7:
            recommendations.append('Improve technical validation before submission')
        
        if metrics['average_triage_time'] > 168:  # Lebih dari 1 minggu
            recommendations.append('Engage with program managers for faster triage')
        
        if metrics['scope_compliance_rate'] < 0.9:
            recommendations.append('Review program scope more carefully before testing')
        
        if reputation_score >= 0.8:
            recommendations.append('Leverage high reputation for premium programs')
        elif reputation_score >= 0.6:
            recommendations.append('Focus on consistent quality to build reputation')
        else:
            recommendations.append('Prioritize scope compliance and validation quality')
        
        return recommendations
    
    def get_reputation_dashboard(self) -> dict:
        """Dapatkan dashboard reputasi untuk semua program."""
        dashboard = {
            'total_programs': len(self.metrics_history),
            'overall_reputation_score': 0.0,
            'top_performing_programs': [],
            'improvement_areas': [],
            'last_updated': datetime.now().isoformat()
        }
        
        if not self.metrics_history:
            return dashboard
        
        # Hitung skor reputasi keseluruhan
        program_scores = []
        for program_name, metrics in self.metrics_history.items():
            score = self._calculate_reputation_score(metrics)
            program_scores.append((program_name, score, metrics))
        
        # Urutkan berdasarkan skor
        program_scores.sort(key=lambda x: x[1], reverse=True)
        
        dashboard['overall_reputation_score'] = sum(score for _, score, _ in program_scores) / len(program_scores)
        dashboard['top_performing_programs'] = [
            {'program': name, 'score': score, 'metrics': metrics}
            for name, score, metrics in program_scores[:5]
        ]
        
        # Identifikasi area perbaikan
        low_acceptance = [name for name, score, metrics in program_scores if metrics['acceptance_rate'] < 0.6]
        if low_acceptance:
            dashboard['improvement_areas'].append(f'Low acceptance rate in: {", ".join(low_acceptance[:3])}')
        
        slow_triage = [name for name, score, metrics in program_scores if metrics['average_triage_time'] > 168]
        if slow_triage:
            dashboard['improvement_areas'].append(f'Slow triage in: {", ".join(slow_triage[:3])}')
        
        return dashboard