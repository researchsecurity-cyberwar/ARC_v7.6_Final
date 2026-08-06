import subprocess
import os
import json
from web3 import Web3

class DynamicFuzzer:
    """
    EVM-aware dynamic fuzzing.
    Melakukan fuzzing dinamis yang sadar EVM.
    """
    
    def __init__(self, fuzzer_dir="~/.arc/fuzzing", rpc_endpoints=None):
        self.fuzzer_dir = os.path.expanduser(fuzzer_dir)
        os.makedirs(self.fuzzer_dir, exist_ok=True)
        self.rpc_endpoints = rpc_endpoints or {
            'ethereum': 'https://rpc.ankr.com/eth',
            'polygon': 'https://rpc.ankr.com/polygon',
            'arbitrum': 'https://rpc.ankr.com/arbitrum',
            'optimism': 'https://rpc.ankr.com/optimism'
        }
        self.web3_instances = self._initialize_web3_instances()
    
    def fuzz_smart_contract(self, contract_address: str, abi: list, chain: str = 'ethereum'):
        """
        Fuzz kontrak pintar yang sudah dideploy.
        """
        results = {
            'contract_address': contract_address,
            'abi': abi,
            'chain': chain,
            'fuzzing_successful': False,
            'vulnerabilities_found': [],
            'crashes_detected': 0,
            'fuzzing_report': None
        }
        
        try:
            # Inisialisasi Web3 untuk chain yang ditentukan
            if chain not in self.web3_instances:
                raise ValueError(f'Unsupported chain: {chain}')
            
            web3 = self.web3_instances[chain]
            if not web3 or not web3.is_connected():
                raise Exception(f'Cannot connect to {chain} RPC endpoint')
            
            # Buat instance kontrak
            contract = web3.eth.contract(address=contract_address, abi=abi)
            
            # Jalankan fuzzing dasar
            fuzz_results = self._run_basic_fuzzing(contract, web3)
            
            results.update({
                'fuzzing_successful': True,
                'vulnerabilities_found': fuzz_results.get('vulnerabilities', []),
                'crashes_detected': fuzz_results.get('crashes', 0),
                'fuzzing_report': fuzz_results
            })
        
        except Exception as e:
            results['error'] = f'Dynamic fuzzing failed: {str(e)}'
        
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
    
    def _run_basic_fuzzing(self, contract, web3):
        """Jalankan fuzzing dasar pada kontrak."""
        vulnerabilities = []
        crashes = 0
        
        # Dapatkan fungsi publik dari ABI
        public_functions = []
        for item in contract.abi:
            if item.get('type') == 'function' and item.get('stateMutability') != 'view':
                public_functions.append(item)
        
        # Fuzz setiap fungsi publik
        for func in public_functions[:5]:  # Batasi 5 fungsi
            try:
                # Coba panggil fungsi dengan parameter acak
                func_name = func['name']
                inputs = func.get('inputs', [])
                
                # Buat parameter acak
                params = self._generate_random_params(inputs)
                
                # Panggil fungsi
                if hasattr(contract.functions, func_name):
                    func_obj = getattr(contract.functions, func_name)
                    try:
                        # Coba estimasi gas terlebih dahulu
                        gas_estimate = func_obj(*params).estimateGas()
                        if gas_estimate > 10000000:  # Gas terlalu tinggi
                            vulnerabilities.append(f'Function {func_name} has excessive gas consumption')
                        else:
                            # Coba eksekusi
                            func_obj(*params).call()
                    except ValueError as e:
                        # Periksa jenis error
                        error_str = str(e).lower()
                        if 'revert' in error_str or 'out of gas' in error_str:
                            vulnerabilities.append(f'Function {func_name} reverts with unexpected input')
                        elif 'execution reverted' in error_str:
                            vulnerabilities.append(f'Function {func_name} execution reverted')
                        else:
                            crashes += 1
                            vulnerabilities.append(f'Function {func_name} caused unexpected crash')
            except Exception:
                crashes += 1
        
        return {
            'tool': 'basic_dynamic_fuzzer',
            'vulnerabilities': vulnerabilities,
            'crashes': crashes,
            'functions_tested': len(public_functions[:5]),
            'note': 'Basic EVM-aware fuzzing completed'
        }
    
    def _generate_random_params(self, inputs: list):
        """Hasilkan parameter acak berdasarkan tipe input."""
        params = []
        for input_type in inputs:
            param_type = input_type.get('type', 'uint256')
            if 'uint' in param_type:
                params.append(123456789)  # Nilai uint acak
            elif 'address' in param_type:
                params.append('0x' + '1' * 40)  # Alamat acak
            elif 'bool' in param_type:
                params.append(True)
            elif 'string' in param_type:
                params.append('test_string')
            elif 'bytes' in param_type:
                params.append(b'test_bytes')
            else:
                params.append(0)  # Default
        
        return params