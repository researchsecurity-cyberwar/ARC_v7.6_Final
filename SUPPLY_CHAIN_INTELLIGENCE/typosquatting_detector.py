import re
import requests
from difflib import SequenceMatcher

class TyposquattingDetector:
    """
    Detect malicious lookalike packages (e.g., react-componets).
    Mendeteksi paket jahat yang menyerupai nama paket populer.
    """
    
    def __init__(self):
        self.popular_packages = {
            'npm': [
                'react', 'vue', 'angular', 'lodash', 'express', 
                'jquery', 'bootstrap', 'moment', 'axios', 'webpack'
            ],
            'pypi': [
                'requests', 'numpy', 'pandas', 'django', 'flask',
                'scipy', 'matplotlib', 'pillow', 'sqlalchemy', 'boto3'
            ],
            'maven': [
                'org.springframework:spring-core',
                'com.google.guava:guava',
                'org.apache.commons:commons-lang3',
                'com.fasterxml.jackson.core:jackson-databind',
                'org.slf4j:slf4j-api'
            ]
        }
        
        self.typosquatting_patterns = {
            'character_substitution': {
                'patterns': ['0', '1', 'l', 'I', 'O', '0'],
                'description': 'Character substitution (e.g., l instead of I)'
            },
            'missing_character': {
                'description': 'Missing character (e.g., react-componets)'
            },
            'extra_character': {
                'description': 'Extra character (e.g., reactt-components)'
            },
            'hyphen_underscore_swap': {
                'description': 'Hyphen/underscore swap (e.g., react_components)'
            },
            'prefix_suffix_addition': {
                'description': 'Added prefix/suffix (e.g., python-requests-official)'
            }
        }
    
    def detect_typosquatting(self, package_name: str, registry_type: str = 'npm'):
        """
        Deteksi potensi typosquatting pada nama paket.
        """
        results = {
            'package_name': package_name,
            'registry_type': registry_type,
            'typosquatting_detected': False,
            'similarity_matches': [],
            'suspicious_patterns': [],
            'risk_level': 'LOW',
            'recommendations': []
        }
        
        try:
            # Bandingkan dengan paket populer
            popular_list = self.popular_packages.get(registry_type, [])
            
            for popular_pkg in popular_list:
                similarity = self._calculate_similarity(package_name, popular_pkg)
                
                if similarity >= 0.8:  # Threshold 80% similarity
                    # Deteksi pola typosquatting spesifik
                    patterns = self._detect_typosquatting_patterns(package_name, popular_pkg)
                    
                    results['similarity_matches'].append({
                        'popular_package': popular_pkg,
                        'similarity_score': similarity,
                        'patterns': patterns,
                        'risk_level': 'HIGH' if similarity >= 0.9 else 'MEDIUM'
                    })
            
            # Tentukan apakah typosquatting terdeteksi
            if results['similarity_matches']:
                results['typosquatting_detected'] = True
                results['risk_level'] = max(
                    match['risk_level'] for match in results['similarity_matches']
                )
            
            # Deteksi pola mencurigakan umum
            suspicious_patterns = self._detect_general_suspicious_patterns(package_name)
            results['suspicious_patterns'] = suspicious_patterns
            
            # Buat rekomendasi
            results['recommendations'] = self._generate_typosquatting_recommendations(
                results['typosquatting_detected'], results['suspicious_patterns']
            )
        
        except Exception as e:
            results['error'] = f'Typosquatting detection failed: {str(e)}'
        
        return results
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Hitung tingkat kemiripan antara dua string."""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def _detect_typosquatting_patterns(self, suspicious_pkg: str, popular_pkg: str) -> List[str]:
        """Deteksi pola typosquatting spesifik antara dua paket."""
        patterns = []
        s1, s2 = suspicious_pkg.lower(), popular_pkg.lower()
        
        # Cek substitusi karakter
        if self._has_character_substitution(s1, s2):
            patterns.append('character_substitution')
        
        # Cek karakter yang hilang
        if len(s1) < len(s2) and self._is_missing_character(s1, s2):
            patterns.append('missing_character')
        
        # Cek karakter tambahan
        if len(s1) > len(s2) and self._is_extra_character(s1, s2):
            patterns.append('extra_character')
        
        # Cek pertukaran hyphen/underscore
        if ('-' in s1 and '_' in s2) or ('_' in s1 and '-' in s2):
            patterns.append('hyphen_underscore_swap')
        
        # Cek penambahan prefix/suffix
        if s1.startswith(s2) or s1.endswith(s2) or s2.startswith(s1) or s2.endswith(s1):
            if abs(len(s1) - len(s2)) <= 5:  # Perbedaan panjang wajar
                patterns.append('prefix_suffix_addition')
        
        return patterns
    
    def _has_character_substitution(self, s1: str, s2: str) -> bool:
        """Cek apakah ada substitusi karakter yang mencurigakan."""
        similar_chars = [('0', 'o'), ('1', 'l'), ('1', 'i'), ('l', 'i'), ('o', '0')]
        
        if len(s1) == len(s2):
            diff_count = sum(1 for a, b in zip(s1, s2) if a != b)
            if diff_count == 1:
                for a, b in zip(s1, s2):
                    if a != b:
                        if (a, b) in similar_chars or (b, a) in similar_chars:
                            return True
        return False
    
    def _is_missing_character(self, s1: str, s2: str) -> bool:
        """Cek apakah s1 kehilangan satu karakter dari s2."""
        if len(s2) - len(s1) == 1:
            i = j = 0
            diff = 0
            while i < len(s1) and j < len(s2):
                if s1[i] == s2[j]:
                    i += 1
                else:
                    diff += 1
                    if diff > 1:
                        return False
                j += 1
            return True
        return False
    
    def _is_extra_character(self, s1: str, s2: str) -> bool:
        """Cek apakah s1 memiliki karakter tambahan dibanding s2."""
        return self._is_missing_character(s2, s1)
    
    def _detect_general_suspicious_patterns(self, package_name: str) -> List[str]:
        """Deteksi pola mencurigakan umum dalam nama paket."""
        suspicious = []
        name_lower = package_name.lower()
        
        # Cek kata kunci mencurigakan
        suspicious_keywords = ['official', 'secure', 'verified', 'trusted', 'pro', 'premium']
        if any(keyword in name_lower for keyword in suspicious_keywords):
            suspicious.append('suspicious_keywords')
        
        # Cek angka acak di akhir
        if re.search(r'\d{3,}$', package_name):
            suspicious.append('random_numbers_suffix')
        
        # Cek banyak simbol tidak biasa
        symbol_count = sum(1 for c in package_name if c in '-_.')
        if symbol_count > 3:
            suspicious.append('excessive_symbols')
        
        return suspicious
    
    def _generate_typosquatting_recommendations(self, detected: bool, suspicious_patterns: List) -> List[str]:
        """Buat rekomendasi pencegahan typosquatting."""
        recommendations = []
        
        if detected:
            recommendations.extend([
                'Verify package authenticity before installation',
                'Check package download counts and publication date',
                'Review package source code and maintainers',
                'Use official package names from documentation'
            ])
        
        if 'suspicious_keywords' in suspicious_patterns:
            recommendations.append('Be cautious of packages using "official" or "verified" in name')
        
        if 'random_numbers_suffix' in suspicious_patterns:
            recommendations.append('Avoid packages with random numbers in the name')
        
        if not recommendations:
            recommendations.append('Package name appears legitimate')
        
        return recommendations