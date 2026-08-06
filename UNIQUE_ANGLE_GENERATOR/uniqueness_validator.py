import json
import os
from difflib import SequenceMatcher

class UniquenessValidator:
    """
    Validate uniqueness before submit.
    Memvalidasi keunikan temuan sebelum pengiriman.
    """
    
    def __init__(self, reports_dir="~/.arc/reports"):
        self.reports_dir = os.path.expanduser(reports_dir)
        os.makedirs(self.reports_dir, exist_ok=True)
        self.uniqueness_threshold = 0.75  # 75% similarity dianggap duplikat
    
    def validate_uniqueness(self, new_finding: dict):
        """
        Validasi keunikan temuan baru.
        """
        results = {
            'new_finding': new_finding,
            'is_unique': False,
            'similarity_score': 0.0,
            'most_similar_report': None,
            'uniqueness_confidence': 'low',
            'validation_successful': False
        }
        
        try:
            # Muat laporan existing
            existing_reports = self._load_existing_reports()
            
            if not existing_reports:
                # Jika tidak ada laporan existing, anggap unik
                results.update({
                    'is_unique': True,
                    'similarity_score': 0.0,
                    'uniqueness_confidence': 'high'
                })
            else:
                # Bandingkan dengan laporan existing
                max_similarity = 0.0
                most_similar = None
                
                for report in existing_reports:
                    similarity = self._calculate_similarity(new_finding, report)
                    if similarity > max_similarity:
                        max_similarity = similarity
                        most_similar = report
                
                results['similarity_score'] = max_similarity
                results['most_similar_report'] = most_similar
                results['is_unique'] = max_similarity < self.uniqueness_threshold
                
                # Tentukan tingkat kepercayaan
                if max_similarity < 0.5:
                    confidence = 'high'
                elif max_similarity < 0.75:
                    confidence = 'medium'
                else:
                    confidence = 'low'
                
                results['uniqueness_confidence'] = confidence
            
            results['validation_successful'] = True
        
        except Exception as e:
            results['error'] = f'Uniqueness validation failed: {str(e)}'
        
        return results
    
    def _load_existing_reports(self) -> list:
        """Muat laporan existing dari direktori."""
        reports = []
        
        # Cari semua file laporan JSON
        report_files = [f for f in os.listdir(self.reports_dir) if f.endswith('.json')]
        
        for report_file in report_files:
            try:
                with open(os.path.join(self.reports_dir, report_file), 'r') as f:
                    data = json.load(f)
                    # Ekstrak laporan individual
                    if 'reports' in data:
                        reports.extend(data['reports'])
                    elif isinstance(data, list):
                        reports.extend(data)
                    else:
                        reports.append(data)
            except:
                continue
        
        return reports
    
    def _calculate_similarity(self, finding1: dict, finding2: dict) -> float:
        """Hitung skor kemiripan antara dua temuan."""
        # Ekstrak komponen penting untuk perbandingan
        text1 = self._extract_comparable_text(finding1)
        text2 = self._extract_comparable_text(finding2)
        
        # Hitung kemiripan sequence dasar
        sequence_similarity = SequenceMatcher(None, text1, text2).ratio()
        
        # Bobot tambahan untuk elemen kritis
        critical_similarity = self._calculate_critical_similarity(finding1, finding2)
        
        # Gabungkan skor dengan bobot
        combined_similarity = (sequence_similarity * 0.6) + (critical_similarity * 0.4)
        
        return min(1.0, combined_similarity)
    
    def _extract_comparable_text(self, finding: dict) -> str:
        """Ekstrak teks yang dapat dibandingkan dari temuan."""
        components = []
        
        # Komponen wajib
        for key in ['type', 'target', 'vulnerability_type', 'target_url']:
            if key in finding and finding[key]:
                components.append(str(finding[key]))
        
        # Komponen opsional
        for key in ['description', 'technical_description', 'steps', 'reproduction_steps']:
            if key in finding and finding[key]:
                if isinstance(finding[key], list):
                    components.extend([str(item) for item in finding[key]])
                else:
                    components.append(str(finding[key]))
        
        return ' '.join(components).lower()
    
    def _calculate_critical_similarity(self, finding1: dict, finding2: dict) -> float:
        """Hitung kemiripan berdasarkan elemen kritis."""
        score = 0.0
        total_weight = 0.0
        
        # Kesamaan tipe kerentanan (bobot tinggi)
        vuln1 = finding1.get('type', '').lower()
        vuln2 = finding2.get('type', '').lower()
        if vuln1 == vuln2 and vuln1:
            score += 0.4
        total_weight += 0.4
        
        # Kesamaan target (bobot tinggi)
        target1 = finding1.get('target_url', '').lower()
        target2 = finding2.get('target_url', '').lower()
        if target1 and target2:
            # Ekstrak domain untuk perbandingan
            from urllib.parse import urlparse
            domain1 = urlparse(target1).netloc
            domain2 = urlparse(target2).netloc
            if domain1 == domain2:
                score += 0.4
        total_weight += 0.4
        
        # Kesamaan parameter (bobot sedang)
        param1 = finding1.get('parameter', '').lower()
        param2 = finding2.get('parameter', '').lower()
        if param1 == param2 and param1:
            score += 0.2
        total_weight += 0.2
        
        return score / total_weight if total_weight > 0 else 0.0