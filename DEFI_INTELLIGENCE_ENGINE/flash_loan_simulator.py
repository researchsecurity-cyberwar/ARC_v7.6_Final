import requests
import json
from web3 import Web3

class FlashLoanSimulator:
    """
    Real-time flash loan attack simulation.
    Mensimulasikan serangan flash loan secara real-time.
    """
    
    def __init__(self, rpc_endpoints=None):
        self.rpc_endpoints = rpc_endpoints or {
            'ethereum': 'https://rpc.ankr.com/eth',
            'polygon': 'https://rpc.ankr.com/polygon',
            'arbitrum': 'https://rpc.ankr.com/arbitrum',
            'optimism': 'https://rpc.ankr.com/optimism'
        }
        self.flash_loan_protocols = {
            'aave': '0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9',
            'balancer': '0xBA12222222228d8Ba445958a75a0704d566BF2C8',
            'uniswap': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'
        }
        self.web3_instances = self._initialize_web3_instances()
    
    def simulate_flash_loan_attack(self, target_protocol: dict, attack_parameters: dict):
        """
        Simulasikan serangan flash loan terhadap protokol target.
        """
        results = {
            'target_protocol': target_protocol,
            'attack_parameters': attack_parameters,
            'simulation_successful': False,
            'attack_feasible': False,
            'estimated_profit_usd': 0.0,
            'gas_cost_usd': 0.0,
            'net_profit_usd': 0.0,
            'simulation_details': {}
        }
        
        try:
            chain = target_protocol.get('chain', 'ethereum')
            
            # Dapatkan harga token saat ini
            token_prices = self._get_token_prices(target_protocol)
            
            # Estimasi profit kotor
            gross_profit = self._estimate_gross_profit(target_protocol, attack_parameters, token_prices)
            results['estimated_profit_usd'] = gross_profit
            
            # Estimasi biaya gas
            gas_cost = self._estimate_gas_cost(chain, attack_parameters)
            results['gas_cost_usd'] = gas_cost
            
            # Hitung profit bersih
            net_profit = gross_profit - gas_cost
            results['net_profit_usd'] = net_profit
            
            # Tentukan kelayakan
            attack_feasible = net_profit > 0
            results['attack_feasible'] = attack_feasible
            
            # Bangun detail simulasi
            simulation_details = self._build_simulation_details(
                target_protocol, attack_parameters, token_prices, gross_profit, gas_cost, net_profit
            )
            results['simulation_details'] = simulation_details
            
            results['simulation_successful'] = True
        
        except Exception as e:
            results['error'] = f'Flash loan simulation failed: {str(e)}'
        
        return results
    
    def _initialize_web3_instances(self):
        """Inisialisasi instance Web3 untuk berbagai chain."""
        instances = {}
        for chain, rpc_url in self.rpc_endpoints.items():
            try:
                instances[chain] = Web3(Web3.HTTPProvider(rpc_url))
            except:
                pass
        return instances
    
    def _get_token_prices(self, protocol_data: dict) -> dict:
        """Dapatkan harga token dari CoinGecko."""
        try:
            tokens = protocol_data.get('tokens', [])
            if not tokens:
                return {token: 1.0 for token in tokens}
            
            token_ids = ','.join(tokens)
            response = requests.get(
                f"https://api.coingecko.com/api/v3/simple/price?ids={token_ids}&vs_currencies=usd",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {token: 1.0 for token in tokens}
        except:
            return {token: 1.0 for token in tokens}
    
    def _estimate_gross_profit(self, protocol_data: dict, attack_params: dict, prices: dict) -> float:
        """Estimasi profit kotor dari serangan flash loan."""
        tvl = protocol_data.get('tvl_usd', 0)
        attack_size_percentage = attack_params.get('loan_size_percentage', 10) / 100.0
        loan_amount = tvl * attack_size_percentage
        
        # Faktor pengungkit berdasarkan jenis serangan
        attack_type = attack_params.get('attack_type', 'arbitrage')
        leverage_factors = {
            'arbitrage': 1.1,
            'oracle_manipulation': 2.5,
            'sandwich': 1.8,
            'liquidation': 3.0
        }
        leverage = leverage_factors.get(attack_type, 1.5)
        
        gross_profit = loan_amount * (leverage - 1.0)
        return min(gross_profit, tvl * 0.5)  # Batasi maksimum 50% dari TVL
    
    def _estimate_gas_cost(self, chain: str, attack_params: dict) -> float:
        """Estimasi biaya gas untuk serangan flash loan."""
        # Estimasi berdasarkan kompleksitas serangan
        attack_complexity = attack_params.get('complexity', 'medium')
        complexity_factors = {'low': 0.5, 'medium': 1.0, 'high': 2.0}
        complexity_multiplier = complexity_factors.get(attack_complexity, 1.0)
        
        # Harga gas berdasarkan chain
        chain_gas_prices = {
            'ethereum': 50.0,      # USD
            'polygon': 0.1,        # USD
            'arbitrum': 1.5,       # USD
            'optimism': 2.0        # USD
        }
        base_gas_cost = chain_gas_prices.get(chain, 10.0)
        
        return base_gas_cost * complexity_multiplier
    
    def _build_simulation_details(self, protocol_data: dict, attack_params: dict,
                                prices: dict, gross_profit: float, gas_cost: float, net_profit: float) -> dict:
        """Bangun detail simulasi lengkap."""
        return {
            'protocol_name': protocol_data.get('name', 'Unknown'),
            'chain': protocol_data.get('chain', 'ethereum'),
            'attack_type': attack_params.get('attack_type', 'unknown'),
            'loan_size_percentage': attack_params.get('loan_size_percentage', 0),
            'complexity': attack_params.get('complexity', 'medium'),
            'gross_profit_usd': gross_profit,
            'gas_cost_usd': gas_cost,
            'net_profit_usd': net_profit,
            'feasibility': 'feasible' if net_profit > 0 else 'not_feasible',
            'risk_level': self._assess_attack_risk(net_profit, gross_profit),
            'simulation_timestamp': datetime.now().isoformat()
        }
    
    def _assess_attack_risk(self, net_profit: float, gross_profit: float) -> str:
        """Nilai tingkat risiko serangan."""
        if gross_profit == 0:
            return 'none'
        
        success_rate = net_profit / gross_profit if gross_profit > 0 else 0
        
        if success_rate >= 0.8:
            return 'low'
        elif success_rate >= 0.5:
            return 'medium'
        elif success_rate >= 0.2:
            return 'high'
        else:
            return 'critical'