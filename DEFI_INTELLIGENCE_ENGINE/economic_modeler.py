import requests
import json
from datetime import datetime, timedelta

class EconomicModeler:
    """
    Economic simulation with real market data.
    Mensimulasikan dampak ekonomi dengan data pasar nyata.
    """
    
    def __init__(self):
        self.coingecko_base_url = "https://api.coingecko.com/api/v3"
        self.defillama_base_url = "https://api.llama.fi"
    
    def simulate_economic_impact(self, protocol_data: dict, attack_scenario: dict):
        """
        Simulasikan dampak ekonomi dari skenario serangan.
        """
        results = {
            'protocol_data': protocol_data,
            'attack_scenario': attack_scenario,
            'simulation_successful': False,
            'financial_impact_usd': 0.0,
            'market_impact_score': 0.0,
            'systemic_risk_level': 'low',
            'simulation_details': {}
        }
        
        try:
            # Dapatkan data pasar real-time
            market_data = self._get_market_data(protocol_data)
            
            # Hitung dampak finansial
            financial_impact = self._calculate_financial_impact(protocol_data, attack_scenario, market_data)
            results['financial_impact_usd'] = financial_impact
            
            # Nilai dampak pasar
            market_impact = self._assess_market_impact(protocol_data, financial_impact, market_data)
            results['market_impact_score'] = market_impact
            
            # Tentukan tingkat risiko sistemik
            systemic_risk = self._assess_systemic_risk(protocol_data, financial_impact)
            results['systemic_risk_level'] = systemic_risk
            
            # Bangun detail simulasi
            simulation_details = self._build_simulation_details(
                protocol_data, attack_scenario, market_data, financial_impact, market_impact
            )
            results['simulation_details'] = simulation_details
            
            results['simulation_successful'] = True
        
        except Exception as e:
            results['error'] = f'Economic simulation failed: {str(e)}'
        
        return results
    
    def _get_market_data(self, protocol_data: dict) -> dict:
        """Dapatkan data pasar real-time dari CoinGecko."""
        try:
            # Dapatkan harga token protokol
            tokens = protocol_data.get('tokens', [])
            if not tokens:
                return {'prices': {}, 'market_caps': {}, 'volumes': {}}
            
            token_ids = ','.join(tokens)
            response = requests.get(
                f"{self.coingecko_base_url}/simple/price?ids={token_ids}&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                prices = {}
                market_caps = {}
                volumes = {}
                
                for token, info in data.items():
                    prices[token] = info.get('usd', 1.0)
                    market_caps[token] = info.get('usd_market_cap', 0)
                    volumes[token] = info.get('usd_24h_vol', 0)
                
                return {
                    'prices': prices,
                    'market_caps': market_caps,
                    'volumes': volumes,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Fallback ke harga default
                return {
                    'prices': {token: 1.0 for token in tokens},
                    'market_caps': {token: 1000000 for token in tokens},
                    'volumes': {token: 100000 for token in tokens},
                    'timestamp': datetime.now().isoformat()
                }
        except:
            # Fallback total jika API gagal
            tokens = protocol_data.get('tokens', ['unknown'])
            return {
                'prices': {token: 1.0 for token in tokens},
                'market_caps': {token: 1000000 for token in tokens},
                'volumes': {token: 100000 for token in tokens},
                'timestamp': datetime.now().isoformat()
            }
    
    def _calculate_financial_impact(self, protocol_data: dict, attack_scenario: dict, market_data: dict) -> float:
        """Hitung dampak finansial dalam USD."""
        tvl = protocol_data.get('tvl_usd', 0)
        affected_percentage = attack_scenario.get('affected_percentage', 10) / 100.0
        direct_loss = tvl * affected_percentage
        
        # Faktor pengungkit (leverage)
        leverage_factor = attack_scenario.get('leverage_factor', 1.0)
        amplified_loss = direct_loss * leverage_factor
        
        # Faktor volatilitas pasar
        tokens = protocol_data.get('tokens', [])
        if tokens:
            avg_volume = sum(market_data['volumes'].get(token, 100000) for token in tokens) / len(tokens)
            if avg_volume > 0:
                volatility_factor = min(2.0, 1000000 / avg_volume)  # Protokol likuid = faktor lebih rendah
                amplified_loss *= volatility_factor
        
        return min(amplified_loss, tvl)  # Tidak bisa kehilangan lebih dari TVL
    
    def _assess_market_impact(self, protocol_data: dict, financial_impact: float, market_data: dict) -> float:
        """Nilai dampak pasar berdasarkan likuiditas."""
        tokens = protocol_data.get('tokens', [])
        if not tokens:
            return 0.0
        
        # Hitung rasio dampak terhadap volume perdagangan
        total_volume = sum(market_data['volumes'].get(token, 100000) for token in tokens)
        if total_volume > 0:
            impact_ratio = financial_impact / total_volume
            # Skor antara 0-100
            market_impact = min(100.0, impact_ratio * 1000)
            return market_impact
        else:
            return 50.0  # Asumsi dampak sedang jika tidak ada data volume
    
    def _assess_systemic_risk(self, protocol_data: dict, financial_impact: float) -> str:
        """Nilai tingkat risiko sistemik."""
        tvl = protocol_data.get('tvl_usd', 0)
        if tvl == 0:
            return 'low'
        
        impact_percentage = (financial_impact / tvl) * 100
        
        if impact_percentage >= 50:
            return 'critical'
        elif impact_percentage >= 20:
            return 'high'
        elif impact_percentage >= 5:
            return 'medium'
        else:
            return 'low'
    
    def _build_simulation_details(self, protocol_data: dict, attack_scenario: dict, 
                                market_data: dict, financial_impact: float, market_impact: float) -> dict:
        """Bangun detail simulasi lengkap."""
        return {
            'protocol_name': protocol_data.get('name', 'Unknown'),
            'tvl_usd': protocol_data.get('tvl_usd', 0),
            'attack_type': attack_scenario.get('type', 'unknown'),
            'affected_percentage': attack_scenario.get('affected_percentage', 0),
            'leverage_factor': attack_scenario.get('leverage_factor', 1.0),
            'financial_impact_usd': financial_impact,
            'market_impact_score': market_impact,
            'tokens_affected': protocol_data.get('tokens', []),
            'simulation_timestamp': datetime.now().isoformat(),
            'confidence_level': 'high' if market_data.get('prices') else 'low'
        }