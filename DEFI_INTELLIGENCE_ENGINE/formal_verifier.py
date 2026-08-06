import subprocess
import os
import json

class FormalVerifier:
    """
    Formal verification of smart contracts.
    Melakukan verifikasi formal terhadap kontrak pintar menggunakan alat open-source.
    """
    
    def __init__(self, verifier_dir="~/.arc/defi_verification"):
        self.verifier_dir = os.path.expanduser(verifier_dir)
        os.makedirs(self.verifier_dir, exist_ok=True)
        self.supported_tools = ['slither', 'mythx', 'echidna']
    
    def verify_smart_contract(self, contract_path: str, verification_tool: str = 'slither'):
        """
        Verifikasi kontrak pintar menggunakan alat yang ditentukan.
        """
        results = {
            'contract_path': contract_path,
            'verification_tool': verification_tool,
            'verification_successful': False,
            'vulnerabilities_found': [],
            'gas_optimization_issues': [],
            'verification_report': None
        }
        
        try:
            if verification_tool == 'slither':
                report = self._run_slither_analysis(contract_path)
            elif verification_tool == 'mythx':
                report = self._run_mythx_analysis(contract_path)
            elif verification_tool == 'echidna':
                report = self._run_echidna_analysis(contract_path)
            else:
                raise ValueError(f'Unsupported verification tool: {verification_tool}')
            
            results.update({
                'verification_successful': True,
                'vulnerabilities_found': report.get('vulnerabilities', []),
                'gas_optimization_issues': report.get('gas_issues', []),
                'verification_report': report
            })
        
        except Exception as e:
            results['error'] = f'Formal verification failed: {str(e)}'
        
        return results
    
    def _run_slither_analysis(self, contract_path: str) -> dict:
        """Jalankan analisis Slither pada kontrak Solidity."""
        try:
            # Pastikan Slither terinstal
            result = subprocess.run(['slither', '--json', '-', contract_path], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Slither tidak mengembalikan JSON saat sukses, jadi parse output
                vulnerabilities = []
                gas_issues = []
                
                # Cari pola kerentanan umum
                if 'reentrancy' in result.stderr.lower():
                    vulnerabilities.append('Reentrancy vulnerability detected')
                if 'overflow' in result.stderr.lower():
                    vulnerabilities.append('Integer overflow/underflow detected')
                if 'timestamp' in result.stderr.lower():
                    vulnerabilities.append('Dangerous use of block.timestamp detected')
                
                return {
                    'tool': 'slither',
                    'vulnerabilities': vulnerabilities,
                    'gas_issues': gas_issues,
                    'raw_output': result.stderr[:1000]  # Batasi output mentah
                }
            else:
                raise Exception(f'Slither analysis failed: {result.stderr[:200]}')
        
        except FileNotFoundError:
            # Fallback ke analisis statis dasar
            return self._basic_static_analysis(contract_path)
        except subprocess.TimeoutExpired:
            raise Exception('Slither analysis timed out (5 minutes)')
    
    def _run_mythx_analysis(self, contract_path: str) -> dict:
        """Jalankan analisis MythX (memerlukan API key)."""
        # Untuk ARC versi gratis, kembalikan placeholder
        return {
            'tool': 'mythx',
            'vulnerabilities': ['MythX requires paid API key for full analysis'],
            'gas_issues': [],
            'note': 'Upgrade to premium for complete MythX integration'
        }
    
    def _run_echidna_analysis(self, contract_path: str) -> dict:
        """Jalankan analisis Echidna untuk property testing."""
        try:
            # Buat konfigurasi Echidna default
            config_content = """
# Echidna configuration
testMode: assertion
timeout: 100
seqLen: 100
"""
            config_file = os.path.join(self.verifier_dir, "echidna_config.yaml")
            with open(config_file, 'w') as f:
                f.write(config_content)
            
            result = subprocess.run([
                'echidna', contract_path, '--config', config_file
            ], capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                return {
                    'tool': 'echidna',
                    'vulnerabilities': [],
                    'gas_issues': [],
                    'property_testing_passed': True
                }
            else:
                return {
                    'tool': 'echidna',
                    'vulnerabilities': ['Property testing failed - potential vulnerabilities'],
                    'gas_issues': [],
                    'property_testing_passed': False
                }
        
        except FileNotFoundError:
            return {
                'tool': 'echidna',
                'vulnerabilities': ['Echidna not installed - property testing skipped'],
                'gas_issues': [],
                'note': 'Install Echidna for advanced property testing'
            }
        except subprocess.TimeoutExpired:
            raise Exception('Echidna analysis timed out (10 minutes)')
    
    def _basic_static_analysis(self, contract_path: str) -> dict:
        """Lakukan analisis statis dasar jika alat canggih tidak tersedia."""
        try:
            with open(contract_path, 'r') as f:
                contract_code = f.read()
            
            vulnerabilities = []
            gas_issues = []
            
            # Deteksi pola berbahaya
            if '.call(' in contract_code and '!(' in contract_code:
                vulnerabilities.append('Potential reentrancy pattern detected')
            
            if 'block.timestamp' in contract_code or 'now' in contract_code:
                vulnerabilities.append('Use of block.timestamp for critical logic')
            
            if 'tx.origin' in contract_code:
                vulnerabilities.append('Use of tx.origin - vulnerable to phishing attacks')
            
            if '++' in contract_code or '--' in contract_code:
                gas_issues.append('Prefer pre-increment/decrement for gas optimization')
            
            return {
                'tool': 'basic_static',
                'vulnerabilities': vulnerabilities,
                'gas_issues': gas_issues,
                'note': 'Advanced verification tools not available - using basic analysis'
            }
        
        except Exception as e:
            return {
                'tool': 'basic_static',
                'vulnerabilities': [f'Basic analysis failed: {str(e)}'],
                'gas_issues': [],
                'error': True
            }