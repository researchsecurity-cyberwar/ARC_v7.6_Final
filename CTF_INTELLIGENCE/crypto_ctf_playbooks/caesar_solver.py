class CaesarSolver:
    """
    Caesar cipher solver.
    Menyelesaikan cipher Caesar secara otomatis.
    """
    
    def __init__(self):
        self.common_words = ['the', 'and', 'flag', 'ctf', 'is', 'for', 'you', 'can', 'this', 'that']
    
    def solve_caesar_cipher(self, ciphertext: str):
        """
        Selesaikan cipher Caesar.
        """
        results = {
            'ciphertext': ciphertext,
            'plaintext': None,
            'shift_used': None,
            'solution_found': False
        }
        
        try:
            best_shift = 0
            best_score = 0
            best_plaintext = ""
            
            for shift in range(26):
                plaintext = self._caesar_decrypt(ciphertext, shift)
                score = self._calculate_score(plaintext)
                
                if score > best_score:
                    best_score = score
                    best_shift = shift
                    best_plaintext = plaintext
            
            if best_score > 0:
                results.update({
                    'plaintext': best_plaintext,
                    'shift_used': best_shift,
                    'solution_found': True
                })
        
        except Exception as e:
            results['error'] = f'Caesar solving failed: {str(e)}'
        
        return results
    
    def _caesar_decrypt(self, text: str, shift: int) -> str:
        """Dekripsi Caesar dengan shift tertentu."""
        result = ""
        for char in text:
            if char.isalpha():
                ascii_offset = 65 if char.isupper() else 97
                result += chr((ord(char) - ascii_offset - shift) % 26 + ascii_offset)
            else:
                result += char
        return result
    
    def _calculate_score(self, text: str) -> int:
        """Hitung skor berdasarkan kata umum."""
        score = 0
        text_lower = text.lower()
        for word in self.common_words:
            if word in text_lower:
                score += 1
        return score