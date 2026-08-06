class EWalletAbuse:
    """
    OVO/DANA/LinkAja chain reaction.
    Mendeteksi abuse pattern pada e-wallet Indonesia.
    """
    
    E_WALLET_DOMAINS = {
        'ovo': ['ovo.id', 'ovo.co.id'],
        'dana': ['dana.id', 'dana.app'],
        'linkaja': ['linkaja.id', 'linkaja.co.id']
    }
    
    def __init__(self):
        self.abuse_chains = {
            'promo_stacking': [
                'multiple_coupon_application',
                'loyalty_point_manipulation',
                'cashback_abuse'
            ],
            'account_takeover': [
                'otp_reuse',
                'session_fixation',
                'phone_number_hijack'
            ],
            'transfer_abuse': [
                'recipient_validation_bypass',
                'amount_manipulation',
                'fee_evasion'
            ]
        }
    
    def detect_ewallet_abuse(self, target_domain, ewallet_type):
        """
        Deteksi pola abuse spesifik e-wallet.
        """
        if ewallet_type not in self.E_WALLET_DOMAINS:
            return []
        
        vulnerabilities = []
        
        # Deteksi promo stacking
        if self._check_promo_stacking_vulnerability(target_domain):
            vulnerabilities.append({
                'type': 'Promo Stacking',
                'ewallet': ewallet_type,
                'impact': 'Financial loss through multiple coupon usage',
                'severity': 'HIGH'
            })
        
        # Deteksi OTP reuse
        if self._check_otp_reuse_vulnerability(target_domain):
            vulnerabilities.append({
                'type': 'OTP Reuse Chain',
                'ewallet': ewallet_type,
                'impact': 'Account takeover via OTP replay',
                'severity': 'CRITICAL'
            })
        
        return vulnerabilities
    
    def _check_promo_stacking_vulnerability(self, domain):
        """Cek kerentanan promo stacking."""
        # Akan diimplementasi dengan analisis API nanti
        return False
    
    def _check_otp_reuse_vulnerability(self, domain):
        """Cek kerentanan reuse OTP."""
        # Akan diimplementasi dengan analisis alur OTP nanti  
        return False
    
    def map_ewallet_to_regulations(self, ewallet_type):
        """
        Petakan e-wallet ke regulasi OJK/BI yang relevan.
        """
        regulations = {
            'ovo': ['POJK No. 12/2018', 'POJK No. 13/2023'],
            'dana': ['POJK No. 12/2018', 'POJK No. 13/2023'],
            'linkaja': ['POJK No. 12/2018', 'POJK No. 13/2023']
        }
        return regulations.get(ewallet_type, ['POJK No. 12/2018'])