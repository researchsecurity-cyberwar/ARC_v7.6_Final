class GameTheoryAnalyzer:
    """
    Game theory analysis of incentive mechanisms.
    Menganalisis mekanisme insentif menggunakan teori permainan.
    """
    
    def __init__(self):
        self.attack_strategies = ['honest', 'griefing', 'sandwich', 'front_run', 'back_run']
        self.defender_strategies = ['monitor', 'circuit_breaker', 'delay', 'penalty']
    
    def analyze_incentive_mechanisms(self, protocol_data: dict):
        """
        Analisis mekanisme insentif protokol DeFi.
        """
        results = {
            'protocol_data': protocol_data,
            'nash_equilibrium_found': False,
            'dominant_strategies': {},
            'attack_profitability': {},
            'defense_effectiveness': {},
            'analysis_complete': False
        }
        
        try:
            # Identifikasi strategi dominan penyerang
            dominant_attacks = self._find_dominant_attack_strategies(protocol_data)
            results['dominant_strategies']['attacker'] = dominant_attacks
            
            # Identifikasi strategi dominan pembela
            dominant_defenses = self._find_dominant_defense_strategies(protocol_data)
            results['dominant_strategies']['defender'] = dominant_defenses
            
            # Analisis profitabilitas serangan
            attack_profits = self._analyze_attack_profitability(protocol_data)
            results['attack_profitability'] = attack_profits
            
            # Analisis efektivitas pertahanan
            defense_effectiveness = self._analyze_defense_effectiveness(protocol_data)
            results['defense_effectiveness'] = defense_effectiveness
            
            # Periksa keseimbangan Nash
            nash_found = self._check_nash_equilibrium(dominant_attacks, dominant_defenses)
            results['nash_equilibrium_found'] = nash_found
            
            results['analysis_complete'] = True
        
        except Exception as e:
            results['error'] = f'Game theory analysis failed: {str(e)}'
        
        return results
    
    def _find_dominant_attack_strategies(self, protocol_data: dict) -> dict:
        """Temukan strategi serangan dominan berdasarkan data protokol."""
        strategies = {}
        
        # Analisis berdasarkan jenis protokol
        protocol_type = protocol_data.get('category', '').lower()
        
        if 'dex' in protocol_type or 'amm' in protocol_type:
            strategies['sandwich'] = 0.8
            strategies['front_run'] = 0.7
            strategies['back_run'] = 0.6
        elif 'lending' in protocol_type:
            strategies['griefing'] = 0.9
            strategies['liquidation_front_run'] = 0.8
        elif 'staking' in protocol_type:
            strategies['griefing'] = 0.7
            strategies['withdrawal_delay_exploit'] = 0.6
        
        # Strategi jujur selalu tersedia tapi tidak menguntungkan
        strategies['honest'] = 0.1
        
        return strategies
    
    def _find_dominant_defense_strategies(self, protocol_data: dict) -> dict:
        """Temukan strategi pertahanan dominan."""
        strategies = {}
        
        # Pertahanan berdasarkan kapasitas protokol
        tvl = protocol_data.get('tvl_usd', 0)
        
        if tvl > 100000000:  # $100M+
            strategies['circuit_breaker'] = 0.9
            strategies['monitor'] = 0.8
            strategies['penalty'] = 0.7
        elif tvl > 10000000:  # $10M+
            strategies['monitor'] = 0.8
            strategies['delay'] = 0.7
            strategies['penalty'] = 0.6
        else:
            strategies['monitor'] = 0.7
            strategies['delay'] = 0.5
        
        return strategies
    
    def _analyze_attack_profitability(self, protocol_data: dict) -> dict:
        """Analisis profitabilitas berbagai strategi serangan."""
        profitability = {}
        
        tvl = protocol_data.get('tvl_usd', 0)
        protocol_type = protocol_data.get('category', '').lower()
        
        if 'dex' in protocol_type:
            profitability['sandwich'] = min(tvl * 0.05, 1000000)  # Maks $1M per serangan
            profitability['front_run'] = min(tvl * 0.03, 500000)
            profitability['back_run'] = min(tvl * 0.02, 300000)
        elif 'lending' in protocol_type:
            profitability['griefing'] = min(tvl * 0.1, 2000000)
            profitability['liquidation_front_run'] = min(tvl * 0.08, 1500000)
        else:
            profitability['griefing'] = min(tvl * 0.05, 500000)
        
        profitability['honest'] = 0.0  # Tidak ada keuntungan dari strategi jujur
        
        return profitability
    
    def _analyze_defense_effectiveness(self, protocol_data: dict) -> dict:
        """Analisis efektivitas berbagai strategi pertahanan."""
        effectiveness = {}
        
        tvl = protocol_data.get('tvl_usd', 0)
        
        if tvl > 100000000:
            effectiveness['circuit_breaker'] = 0.95
            effectiveness['monitor'] = 0.85
            effectiveness['penalty'] = 0.80
            effectiveness['delay'] = 0.75
        elif tvl > 10000000:
            effectiveness['monitor'] = 0.80
            effectiveness['delay'] = 0.70
            effectiveness['penalty'] = 0.65
            effectiveness['circuit_breaker'] = 0.60
        else:
            effectiveness['monitor'] = 0.70
            effectiveness['delay'] = 0.50
            effectiveness['penalty'] = 0.40
            effectiveness['circuit_breaker'] = 0.30
        
        return effectiveness
    
    def _check_nash_equilibrium(self, attack_strategies: dict, defense_strategies: dict) -> bool:
        """Periksa apakah ada keseimbangan Nash."""
        # Keseimbangan Nash ditemukan jika tidak ada pemain yang bisa meningkatkan payoff
        # dengan mengubah strategi secara unilateral
        
        if not attack_strategies or not defense_strategies:
            return False
        
        # Temukan strategi terbaik untuk masing-masing pihak
        best_attack = max(attack_strategies.values())
        best_defense = max(defense_strategies.values())
        
        # Jika kedua pihak memiliki strategi dominan yang stabil, maka ada keseimbangan Nash
        return best_attack > 0.5 and best_defense > 0.5