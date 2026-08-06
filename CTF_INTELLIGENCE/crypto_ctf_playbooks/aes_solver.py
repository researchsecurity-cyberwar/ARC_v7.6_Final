import re
from Crypto.Cipher import AES

class AESSolver:
    """
    AES mode detector & solver.
    Mendeteksi mode AES dan mencoba menyelesaikan challenge.
    """
    
    def __init__(self):
        self.mode_indicators = {
            'ecb': 'repeating_blocks',
            'cbc': 'iv_required',
            'ctr': 'nonce_required',
            'gcm': 'auth_tag_required'
        }
    
    def solve_aes_challenge(self, ciphertext: str, key: str = None, iv: str = None):
        """
        Selesaikan challenge AES.
        """
        results = {
            'ciphertext': ciphertext[:50] + '...' if len(ciphertext) > 50 else ciphertext,
            'key_provided': key is not None,
            'iv_provided': iv is not None,
            'mode_detected': None,
            'plaintext': None,
            'solution_found': False
        }
        
        try:
            # Deteksi mode berdasarkan panjang dan struktur
            mode = self._detect_aes_mode(ciphertext)
            results['mode_detected'] = mode
            
            # Jika kunci disediakan, coba dekripsi
            if key:
                plaintext = self._attempt_decryption(ciphertext, key, iv, mode)
                if plaintext:
                    results.update({
                        'plaintext': plaintext,
                        'solution_found': True
                    })
        
        except Exception as e:
            results['error'] = f'AES solving failed: {str(e)}'
        
        return results
    
    def _detect_aes_mode(self, ciphertext: str) -> str:
        """Deteksi mode AES berdasarkan ciphertext."""
        # Konversi hex ke bytes jika perlu
        try:
            if re.match(r'^[0-9A-Fa-f]+$', ciphertext):
                ciphertext_bytes = bytes.fromhex(ciphertext)
            else:
                ciphertext_bytes = ciphertext.encode()
            
            # ECB memiliki blok berulang
            block_size = 16
            blocks = [ciphertext_bytes[i:i+block_size] for i in range(0, len(ciphertext_bytes), block_size)]
            unique_blocks = set(blocks)
            
            if len(blocks) != len(unique_blocks):
                return 'ecb'
            else:
                return 'cbc'  # Default assumption
        except:
            return 'unknown'
    
    def _attempt_decryption(self, ciphertext: str, key: str, iv: str, mode: str):
        """Coba dekripsi dengan parameter yang diberikan."""
        try:
            # Konversi input ke bytes
            if re.match(r'^[0-9A-Fa-f]+$', ciphertext):
                ct_bytes = bytes.fromhex(ciphertext)
            else:
                ct_bytes = ciphertext.encode()
            
            if re.match(r'^[0-9A-Fa-f]+$', key):
                key_bytes = bytes.fromhex(key)
            else:
                key_bytes = key.encode()
            
            if iv and re.match(r'^[0-9A-Fa-f]+$', iv):
                iv_bytes = bytes.fromhex(iv)
            elif iv:
                iv_bytes = iv.encode()
            else:
                iv_bytes = b'\x00' * 16  # IV default
            
            # Dekripsi berdasarkan mode
            if mode == 'ecb':
                cipher = AES.new(key_bytes, AES.MODE_ECB)
                return cipher.decrypt(ct_bytes).decode('utf-8', errors='ignore')
            elif mode == 'cbc':
                cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
                return cipher.decrypt(ct_bytes).decode('utf-8', errors='ignore')
            else:
                return None
        except:
            return None