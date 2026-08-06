class CTFChallengeClassifier:
    """
    Classify challenge type (web, rev, crypto, etc.).
    Mengklasifikasikan tipe challenge berdasarkan deskripsi dan konteks.
    """
    
    def __init__(self):
        self.category_keywords = {
            'web': ['web', 'http', 'website', 'html', 'javascript', 'xss', 'sqli', 'csrf', 'ssrf'],
            'reversing': ['rev', 'reverse', 'binary', 'disassemble', 'decompile', 'ghidra', 'ida'],
            'crypto': ['crypto', 'cipher', 'rsa', 'aes', 'encryption', 'decryption', 'hash'],
            'pwn': ['pwn', 'exploit', 'buffer', 'overflow', 'rop', 'shellcode', 'format string'],
            'forensics': ['forensics', 'pcap', 'memory', 'disk', 'steganography', 'network'],
            'osint': ['osint', 'open source', 'intelligence', 'google', 'social media'],
            'misc': ['misc', 'miscellaneous', 'trivia', 'guessing']
        }
    
    def classify_challenge(self, challenge_data: dict) -> dict:
        """
        Klasifikasikan challenge berdasarkan data yang tersedia.
        """
        results = {
            'challenge_data': challenge_data,
            'predicted_category': 'misc',
            'confidence_score': 0.0,
            'matching_keywords': [],
            'alternative_categories': []
        }
        
        try:
            # Gabungkan semua teks yang tersedia
            text_sources = [
                challenge_data.get('title', ''),
                challenge_data.get('description', ''),
                challenge_data.get('category', ''),
                challenge_data.get('tags', '')
            ]
            full_text = ' '.join(str(source) for source in text_sources).lower()
            
            # Hitung skor untuk setiap kategori
            category_scores = {}
            for category, keywords in self.category_keywords.items():
                score = sum(1 for keyword in keywords if keyword in full_text)
                category_scores[category] = score
            
            # Tentukan kategori dengan skor tertinggi
            best_category = max(category_scores, key=category_scores.get)
            best_score = category_scores[best_category]
            
            if best_score > 0:
                results['predicted_category'] = best_category
                results['confidence_score'] = min(best_score / 3.0, 1.0)  # Normalisasi
                
                # Cari keyword yang cocok
                matching_keywords = [kw for kw in self.category_keywords[best_category] if kw in full_text]
                results['matching_keywords'] = matching_keywords
                
                # Kategori alternatif
                sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
                alternative_cats = [cat for cat, score in sorted_categories[1:3] if score > 0]
                results['alternative_categories'] = alternative_cats
            else:
                results['confidence_score'] = 0.1  # Sangat rendah
        
        except Exception as e:
            results['error'] = f'Challenge classification failed: {str(e)}'
        
        return results