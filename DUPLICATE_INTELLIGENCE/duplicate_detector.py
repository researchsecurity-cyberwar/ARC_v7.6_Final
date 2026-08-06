import re
from difflib import SequenceMatcher
import json
import os

class DuplicateDetector:
    """
    Deteksi kemiripan temuan.
    Mendeteksi duplikat atau kemiripan antara temuan baru dan laporan existing.
    """
    
    def __init__(self, similarity_threshold=0.85):
        self.similarity_threshold = similarity_threshold
        self.vulnerability_keywords = [
            'xss', 'sqli', 'csrf', 'ssrf', 'rce', 'idor', 'lfi', 'rfi',
            'auth', 'authorization', 'bypass', 'logic', 'business',
            'race', 'timing', 'validation', 'input'
        ]
    
    def detect_duplicates(self, new_finding: dict, existing_reports: list):
        """
        Deteksi duplikat untuk temuan baru.
        """
        results = {
            'new_finding': new_finding,
            'potential_duplicates': [],
            'similarity_score': 0.0,
            'is_duplicate': False,
            'recommendation': None
        }
        
        try:
            max_similarity = 0.0
            most_similar_report = None
            
            for report in existing_reports:
                similarity = self._calculate_similarity(new_finding, report)
                if similarity > max_similarity:
                    max_similarity = similarity
                    most_similar_report = report
            
            results['similarity_score'] = max_similarity
            results['is_duplicate'] = max_similarity >= self.similarity_threshold
            
            if most_similar_report:
                results['potential_duplicates'].append({
                    'report': most_similar_report,
                    'similarity_score': max_similarity
                })
            
            # Berikan rekomendasi
            if results['is_duplicate']:
                results['recommendation'] = f"LIKELY DUPLICATE: {max_similarity:.2%} similarity with existing report"
            elif max_similarity >= 0.6:
                results['recommendation'] = f"SIMILAR FINDING: {max_similarity:.2%} similarity - enhance uniqueness"
            else:
                results['recommendation'] = f"UNIQUE FINDING: Only {max_similarity:.2%} similarity with existing reports"
        
        except Exception as e:
            results['error'] = f'Duplicate detection failed: {str(e)}'
        
        return results
    
    def _calculate_similarity(self, finding1: dict, finding2: dict) -> float:
        """Hitung skor kemiripan antara dua temuan."""
        # Ekstrak teks untuk perbandingan
        text1 = self._extract_comparable_text(finding1)
        text2 = self._extract_comparable_text(finding2)
        
        # Hitung kemiripan sequence
        sequence_similarity = SequenceMatcher(None, text1, text2).ratio()
        
        # Tambahkan bobot untuk kata kunci kerentanan
        keyword_similarity = self._calculate_keyword_similarity(text1, text2)
        
        # Gabungkan skor
        combined_similarity = (sequence_similarity * 0.7) + (keyword_similarity * 0.3)
        
        return combined_similarity
    
    def _extract_comparable_text(self, finding: dict) -> str:
        """Ekstrak teks yang dapat dibandingkan dari temuan."""
        components = []
        
        # Judul/tipe kerentanan
        if 'type' in finding:
            components.append(finding['type'])
        if 'vulnerability_type' in finding:
            components.append(finding['vulnerability_type'])
        
        # Target
        if 'target' in finding:
            components.append(finding['target'])
        if 'target_url' in finding:
            components.append(finding['target_url'])
        
        # Deskripsi
        if 'description' in finding:
            components.append(finding['description'])
        if 'technical_description' in finding:
            components.append(finding['technical_description'])
        
        # Langkah reproduksi
        if 'steps' in finding:
            if isinstance(finding['steps'], list):
                components.extend(finding['steps'])
            else:
                components.append(str(finding['steps']))
        
        return ' '.join(str(comp) for comp in components).lower()
    
    def _calculate_keyword_similarity(self, text1: str, text2: str) -> float:
        """Hitung kemiripan berdasarkan kata kunci kerentanan."""
        words1 = set(re.findall(r'\b\w+\b', text1.lower()))
        words2 = set(re.findall(r'\b\w+\b', text2.lower()))
        
        # Cari kata kunci kerentanan yang sama
        vuln_words1 = words1.intersection(set(self.vulnerability_keywords))
        vuln_words2 = words2.intersection(set(self.vulnerability_keywords))
        
        if not vuln_words1 and not vuln_words2:
            return 0.5  # Default jika tidak ada kata kunci
        
        if not vuln_words1 or not vuln_words2:
            return 0.0  # Tidak mirip jika hanya satu yang memiliki kata kunci
        
        common_vuln_words = vuln_words1.intersection(vuln_words2)
        similarity = len(common_vuln_words) / max(len(vuln_words1), len(vuln_words2))
        
        return similarity