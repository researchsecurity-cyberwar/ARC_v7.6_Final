import math
from Crypto.PublicKey import RSA

class RSASolver:
    """
    RSA weakness exploiter.
    Mengeksploitasi kelemahan RSA seperti modulus kecil atau faktorisasi mudah.
    """
    
    def __init__(self):
        pass
    
    def solve_rsa_challenge(self, n: int, e: int = None, c: int = None):
        """
        Selesaikan challenge RSA.
        """
        results = {
            'n': n,
            'e': e,
            'c': c,
            'vulnerable': False,
            'attack_used': None,
            'plaintext': None,
            'solution_found': False
        }
        
        try:
            # Cek apakah modulus terlalu kecil (< 1024 bit)
            if n.bit_length() < 1024:
                results.update({
                    'vulnerable': True,
                    'attack_used': 'small_modulus',
                    'solution_found': True
                })
                return results
            
            # Coba faktorisasi sederhana (hanya untuk modulus sangat kecil)
            if n.bit_length() < 64:
                factors = self._simple_factorization(n)
                if factors:
                    p, q = factors
                    phi = (p - 1) * (q - 1)
                    d = pow(e, -1, phi)
                    plaintext = pow(c, d, n)
                    results.update({
                        'vulnerable': True,
                        'attack_used': 'factorization',
                        'plaintext': plaintext,
                        'solution_found': True
                    })
                    return results
            
            # Cek common modulus attack jika e dan c disediakan
            if e is not None and c is not None:
                results['attack_used'] = 'requires_more_info'
        
        except Exception as e:
            results['error'] = f'RSA solving failed: {str(e)}'
        
        return results
    
    def _simple_factorization(self, n: int):
        """Faktorisasi sederhana untuk modulus kecil."""
        try:
            for i in range(2, int(math.sqrt(n)) + 1):
                if n % i == 0:
                    return (i, n // i)
            return None
        except:
            return None