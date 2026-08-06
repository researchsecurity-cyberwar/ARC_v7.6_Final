import base64
import binascii
import re

class CipherDetector:
    """
    Auto-detect cipher type.
    Mendeteksi jenis cipher secara otomatis.
    """
    
    def __init__(self):
        self.cipher_signatures = {
            'base64': r'^[A-Za-z0-9+/]*={0,2}$',
            'hex': r'^[0-9A-Fa-f]+$',
            'binary': r'^[01\s]+$',
            'morse': r'^[\.\-\s]+$',
            'caesar': r'^[A-Za-z\s]+$',
            'rot13': r'^[A-Za-z\s]+$'
        }
    
    def detect_cipher(self, ciphertext: str):
        """
        Deteksi jenis cipher.
        """
        results = {
            'ciphertext': ciphertext[:100] + '...' if len(ciphertext) > 100 else ciphertext,
            'detected_cipher': None,
            'confidence_score': 0.0,
            'possible_ciphers': []
        }
        
        try:
            clean_text = ciphertext.strip()
            possible_ciphers = []
            
            # Uji Base64
            if re.match(self.cipher_signatures['base64'], clean_text) and len(clean_text) % 4 == 0:
                try:
                    base64.b64decode(clean_text)
                    possible_ciphers.append('base64')
                except:
                    pass
            
            # Uji Hex
            if re.match(self.cipher_signatures['hex'], clean_text) and len(clean_text) % 2 == 0:
                possible_ciphers.append('hex')
            
            # Uji Binary
            if re.match(self.cipher_signatures['binary'], clean_text.replace(' ', '')):
                possible_ciphers.append('binary')
            
            # Uji Morse
            if re.match(self.cipher_signatures['morse'], clean_text):
                possible_ciphers.append('morse')
            
            # Uji Caesar/Rot13 (hanya huruf dan spasi)
            if re.match(self.cipher_signatures['caesar'], clean_text):
                possible_ciphers.extend(['caesar', 'rot13'])
            
            results['possible_ciphers'] = possible_ciphers
            
            if possible_ciphers:
                results['detected_cipher'] = possible_ciphers[0]
                results['confidence_score'] = min(len(possible_ciphers) * 0.3, 1.0)
            else:
                results['detected_cipher'] = 'unknown'
                results['confidence_score'] = 0.1
        
        except Exception as e:
            results['error'] = f'Cipher detection failed: {str(e)}'
        
        return results