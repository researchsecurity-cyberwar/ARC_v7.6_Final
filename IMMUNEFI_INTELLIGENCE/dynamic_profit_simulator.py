import requests
import json
from web3 import Web3
import time

class DynamicProfitSimulator:
    """
    Real-time economic exploit simulation across protocols.
    Mensimulasikan profit eksploitasi ekonomi secara real-time di berbagai protokol.
    Menggunakan strategi multi-layer fallback untuk keandalan maksimal.
    """
    
    def __init__(self, rpc_endpoints=None):
        # Layer 1: Public RPC endpoints gratis (prioritas utama)
        self.public_rpcs = {
            'ethereum': [
                'https://rpc.ankr.com/eth',
                'https://cloudflare-eth.com',
                'https://eth-mainnet.public.blastapi.io',
                'https://mainnet.eth.cloud.ava.do'
            ],
            'polygon': [
                'https://rpc.ankr.com/polygon',
                'https://polygon-rpc.com',
                'https://poly-rpc.gateway.pokt.network',
                'https://polygon-mainnet.public.blastapi.io'
            ],
            'arbitrum': [
                'https://rpc.ankr.com/arbitrum',
                'https://arbitrum.publicnode.com',
                'https://arb1.arbitrum.io/rpc'
            ],
            'optimism': [
                'https://rpc.ankr.com/optimism',
                'https://optimism.publicnode.com',
                'https://mainnet.optimism.io'
            ]
        }
        
        # Layer 2: Simulasi offline jika semua RPC gagal
        self.offline_gas_prices = {
            'ethereum': 25.0,      # USD
            'polygon': 0.01,       # USD  
            'arbitrum': 1.2,       # USD
            'optimism': 1.8        # USD
        }
        
        # Inisialisasi Web3 instances dengan fallback
        self.web3_instances = self._initialize_web3_with_fallback()
    
    def _initialize_web3_with_fallback(self):
        """Inisialisasi Web3 dengan strategi fallback multi-layer."""
        instances = {}
        
        for chain, rpc_list in self.public_rpcs.items():
            for rpc_url in rpc_list:
                try:
                    web3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={'timeout': 10}))
                    if web3.is_connected():
                        instances[chain] = web3
                        print(f"✅ {chain} connected via: {rpc_url}")
                        break
                except Exception as e:
                    continue
            
            # Jika semua RPC gagal, gunakan mode offline
            if chain not in instances:
                instances[chain] = None
                print(f"⚠️ {chain} using offline mode (no RPC available)")
        
        return instances
    
    def simulate_exploit_profit(self, exploit_scenario: dict):
        """
        Simulasikan profit dari skenario eksploitasi dengan fallback cerdas.
        """
        results = {
            'exploit_scenario': exploit_scenario,
            'simulation_successful': False,
            'profit_usd': 0.0,
            'gas_cost_usd': 0.0,
            'net_profit_usd': 0.0,
            'feasibility': 'not_feasible',
            'simulation_mode': 'online'  # atau 'offline'
        }
        
        try:
            # Dapatkan harga token saat ini
            token_prices = self._get_current_token_prices(exploit_scenario)
            
            # Hitung potensi profit
            gross_profit = self._calculate_gross_profit(exploit_scenario, token_prices)
            results['profit_usd'] = gross_profit
            
            # Hitung biaya gas dengan strategi fallback
            gas_cost = self._calculate_gas_cost_with_fallback(exploit_scenario)
            results['gas_cost_usd'] = gas_cost
            
            # Hitung profit bersih
            net_profit = gross_profit - gas_cost
            results['net_profit_usd'] = net_profit
            
            # Tentukan kelayakan
            if net_profit > 0:
                results['feasibility'] = 'feasible'
                results['simulation_successful'] = True
            else:
                results['feasibility'] = 'not_feasible'
                results['simulation_successful'] = True
        
        except Exception as e:
            # Fallback ke mode offline jika semua gagal
            results.update(self._simulate_offline_fallback(exploit_scenario))
        
        return results
    
    def _get_current_token_prices(self, scenario: dict):
        """Dapatkan harga token dari CoinGecko dengan caching."""
        try:
            tokens = scenario.get('affected_tokens', [])
            if not tokens:
                return {}
            
            # Gunakan caching untuk menghindari rate limit
            cache_key = ','.join(sorted(tokens))
            if hasattr(self, '_price_cache') and time.time() - getattr(self, '_price_cache_time', 0) < 60:
                if getattr(self, '_price_cache_key', '') == cache_key:
                    return self._price_cache
            
            # Ambil harga dari CoinGecko
            token_ids = ','.join(tokens)
            response = requests.get(
                f"https://api.coingecko.com/api/v3/simple/price?ids={token_ids}&vs_currencies=usd",
                timeout=10
            )
            
            if response.status_code == 200:
                prices = response.json()
                # Simpan ke cache
                self._price_cache = prices
                self._price_cache_time = time.time()
                self._price_cache_key = cache_key
                return prices
            else:
                # Fallback ke harga default jika CoinGecko gagal
                return {token: 1.0 for token in tokens}
                
        except:
            return {token: 1.0 for token in tokens}
    
    def _calculate_gross_profit(self, scenario: dict, prices: dict):
        """Hitung profit kotor dari skenario eksploitasi."""
        affected_tokens = scenario.get('affected_tokens', [])
        stolen_amounts = scenario.get('stolen_amounts', {})
        
        total_profit = 0.0
        for token in affected_tokens:
            amount = stolen_amounts.get(token, 0)
            price = prices.get(token, {}).get('usd', 1.0)
            total_profit += amount * price
        
        return total_profit
    
    def _calculate_gas_cost_with_fallback(self, scenario: dict):
        """Hitung biaya gas dengan strategi fallback multi-layer."""
        chain = scenario.get('chain', 'ethereum')
        estimated_gas = scenario.get('estimated_gas', 1000000)
        
        # Layer 1: Coba RPC publik
        if chain in self.web3_instances and self.web3_instances[chain]:
            try:
                web3 = self.web3_instances[chain]
                gas_price_wei = web3.eth.gas_price
                eth_price = self._get_eth_price()
                gas_cost_eth = (gas_price_wei * estimated_gas) / 1e18
                return gas_cost_eth * eth_price
            except:
                pass
        
        # Layer 2: Fallback ke estimasi offline
        return self.offline_gas_prices.get(chain, 10.0)
    
    def _get_eth_price(self):
        """Dapatkan harga ETH dari CoinGecko dengan fallback."""
        try:
            response = requests.get(
                "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd",
                timeout=10
            )
            if response.status_code == 200:
                return response.json()['ethereum']['usd']
            else:
                return 2000.0  # Harga default
        except:
            return 2000.0
    
    def _simulate_offline_fallback(self, scenario: dict):
        """Simulasi offline jika semua RPC gagal."""
        chain = scenario.get('chain', 'ethereum')
        gross_profit = self._calculate_gross_profit(scenario, {token: {'usd': 1.0} for token in scenario.get('affected_tokens', [])})
        gas_cost = self.offline_gas_prices.get(chain, 10.0)
        net_profit = gross_profit - gas_cost
        
        return {
            'simulation_successful': True,
            'profit_usd': gross_profit,
            'gas_cost_usd': gas_cost,
            'net_profit_usd': net_profit,
            'feasibility': 'feasible' if net_profit > 0 else 'not_feasible',
            'simulation_mode': 'offline',
            'warning': 'Using offline simulation due to RPC unavailability'
        }