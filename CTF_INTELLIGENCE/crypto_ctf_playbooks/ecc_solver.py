class ECCSolver:
    """
    Elliptic Curve Cryptography solver.
    Menyelesaikan challenge kriptografi kurva eliptik.
    """
    
    def __init__(self):
        pass
    
    def solve_ecc_challenge(self, curve_params: dict, public_key: tuple, ciphertext: str = None):
        """
        Selesaikan challenge ECC.
        """
        results = {
            'curve_params': curve_params,
            'public_key': public_key,
            'ciphertext': ciphertext,
            'vulnerable': False,
            'attack_used': None,
            'plaintext': None,
            'solution_found': False
        }
        
        try:
            # Cek parameter kurva yang lemah
            if self._is_weak_curve(curve_params):
                results.update({
                    'vulnerable': True,
                    'attack_used': 'weak_curve_parameters',
                    'solution_found': True
                })
                return results
            
            # Cek kunci publik yang lemah
            if self._is_weak_public_key(public_key, curve_params):
                results.update({
                    'vulnerable': True,
                    'attack_used': 'weak_public_key',
                    'solution_found': True
                })
                return results
            
            results['attack_used'] = 'requires_advanced_analysis'
        
        except Exception as e:
            results['error'] = f'ECC solving failed: {str(e)}'
        
        return results
    
    def _is_weak_curve(self, params: dict) -> bool:
        """Periksa apakah parameter kurva lemah."""
        # Contoh: kurva dengan order kecil
        if 'order' in params and params['order'] < 2**160:
            return True
        return False
    
    def _is_weak_public_key(self, pubkey: tuple, params: dict) -> bool:
        """Periksa apakah kunci publik lemah."""
        # Contoh: kunci publik adalah titik tak hingga atau titik kecil
        if pubkey == (0, 0):
            return True
        return False