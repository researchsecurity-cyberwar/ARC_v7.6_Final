import subprocess
import os
import json

class StaticAnalyzer:
    """
    Enhanced static analysis with dataflow.
    Melakukan analisis statis yang ditingkatkan dengan analisis alur data.
    """
    
    def __init__(self, analysis_dir="~/.arc/smart_contract_analysis"):
        self.analysis_dir = os.path.expanduser(analysis_dir)
        os.makedirs(self.analysis_dir, exist_ok=True)
        self.supported_tools = ['slither', 'mythril', 'oyente']
    
    def analyze_smart_contract(self, contract_path: str, analysis_tool: str = 'slither'):
        """
        Analisis kontrak pintar menggunakan alat yang ditentukan.
        """
        results = {
            'contract_path': contract_path,
            'analysis_tool': analysis_tool,
            'analysis_successful': False,
            'vulnerabilities_found': [],
            'dataflow_issues': [],
            'gas_optimization_issues': [],
            'analysis_report': None
        }
        
        try:
            if analysis_tool == 'slither':
                report = self._run_slither_analysis(contract_path)
            elif analysis_tool == 'mythril':
                report = self._run_mythril_analysis(contract_path)
            elif analysis_tool == 'oyente':
                report = self._run_oyente_analysis(contract_path)
            else:
                raise ValueError(f'Unsupported analysis tool: {analysis_tool}')
            
            results.update({
                'analysis_successful': True,
                'vulnerabilities_found': report.get('vulnerabilities', []),
                'dataflow_issues': report.get('dataflow_issues', []),
                'gas_optimization_issues': report.get('gas_issues', []),
                'analysis_report': report
            })
        
        except Exception as e:
            results['error'] = f'Static analysis failed: {str(e)}'
        
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
                dataflow_issues = []
                gas_issues = []
                
                # Cari pola kerentanan umum
                if 'reentrancy' in result.stderr.lower():
                    vulnerabilities.append('Reentrancy vulnerability detected')
                if 'overflow' in result.stderr.lower():
                    vulnerabilities.append('Integer overflow/underflow detected')
                if 'timestamp' in result.stderr.lower():
                    vulnerabilities.append('Dangerous use of block.timestamp detected')
                if 'tx.origin' in result.stderr.lower():
                    vulnerabilities.append('Use of tx.origin - vulnerable to phishing attacks')
                
                # Cari isu alur data
                if 'uninitialized' in result.stderr.lower():
                    dataflow_issues.append('Uninitialized storage variable detected')
                if 'shadowing' in result.stderr.lower():
                    dataflow_issues.append('Variable shadowing detected')
                
                # Cari isu optimasi gas
                if '++' in result.stderr.lower() or '--' in result.stderr.lower():
                    gas_issues.append('Prefer pre-increment/decrement for gas optimization')
                
                return {
                    'tool': 'slither',
                    'vulnerabilities': vulnerabilities,
                    'dataflow_issues': dataflow_issues,
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
    
    def _run_mythril_analysis(self, contract_path: str) -> dict:
        """Jalankan analisis Mythril pada kontrak Solidity."""
        try:
            result = subprocess.run(['myth', 'analyze', contract_path], 
                                  capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                vulnerabilities = []
                dataflow_issues = []
                
                # Parse output Mythril
                if 'integer overflow' in result.stdout.lower():
                    vulnerabilities.append('Integer overflow vulnerability detected')
                if 'reentrancy' in result.stdout.lower():
                    vulnerabilities.append('Reentrancy vulnerability detected')
                if 'unchecked call return value' in result.stdout.lower():
                    vulnerabilities.append('Unchecked call return value detected')
                
                return {
                    'tool': 'mythril',
                    'vulnerabilities': vulnerabilities,
                    'dataflow_issues': dataflow_issues,
                    'gas_issues': [],
                    'raw_output': result.stdout[:1000]
                }
            else:
                raise Exception(f'Mythril analysis failed: {result.stderr[:200]}')
        
        except FileNotFoundError:
            return {
                'tool': 'mythril',
                'vulnerabilities': ['Mythril not installed - install with pip install mythril'],
                'dataflow_issues': [],
                'gas_issues': [],
                'note': 'Install Mythril for advanced symbolic analysis'
            }
        except subprocess.TimeoutExpired:
            raise Exception('Mythril analysis timed out (10 minutes)')
    
    def _run_oyente_analysis(self, contract_path: str) -> dict:
        """Jalankan analisis Oyente pada kontrak Solidity."""
        try:
            result = subprocess.run(['oyente', '-s', contract_path], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                vulnerabilities = []
                
                if 'Reentrancy' in result.stdout:
                    vulnerabilities.append('Reentrancy vulnerability detected')
                if 'Integer Overflow' in result.stdout:
                    vulnerabilities.append('Integer overflow detected')
                if 'Timestamp Dependency' in result.stdout:
                    vulnerabilities.append('Timestamp dependency detected')
                
                return {
                    'tool': 'oyente',
                    'vulnerabilities': vulnerabilities,
                    'dataflow_issues': [],
                    'gas_issues': [],
                    'raw_output': result.stdout[:1000]
                }
            else:
                raise Exception(f'Oyente analysis failed: {result.stderr[:200]}')
        
        except FileNotFoundError:
            return {
                'tool': 'oyente',
                'vulnerabilities': ['Oyente not installed - requires Python 2.7 environment'],
                'dataflow_issues': [],
                'gas_issues': [],
                'note': 'Oyente requires legacy Python 2.7 - consider using Slither instead'
            }
        except subprocess.TimeoutExpired:
            raise Exception('Oyente analysis timed out (5 minutes)')
    
    def _basic_static_analysis(self, contract_path: str) -> dict:
        """Lakukan analisis statis dasar jika alat canggih tidak tersedia."""
        try:
            with open(contract_path, 'r') as f:
                contract_code = f.read()
            
            vulnerabilities = []
            dataflow_issues = []
            gas_issues = []
            
            # Deteksi pola berbahaya
            if '.call(' in contract_code and '!(' in contract_code:
                vulnerabilities.append('Potential reentrancy pattern detected')
            
            if 'block.timestamp' in contract_code or 'now' in contract_code:
                vulnerabilities.append('Use of block.timestamp for critical logic')
            
            if 'tx.origin' in contract_code:
                vulnerabilities.append('Use of tx.origin - vulnerable to phishing attacks')
            
            if 'address(' in contract_code and ').call(' in contract_code:
                vulnerabilities.append('Low-level call without return value check')
            
            # Deteksi isu alur data
            if 'storage' in contract_code and '=' in contract_code:
                lines = contract_code.split('\n')
                for i, line in enumerate(lines):
                    if 'storage' in line and '=' in line:
                        # Cek apakah variabel diinisialisasi sebelum digunakan
                        var_name = line.split('=')[0].strip().split()[-1]
                        used_before_init = False
                        for j in range(i):
                            if var_name in lines[j] and 'function' not in lines[j]:
                                used_before_init = True
                                break
                        if used_before_init:
                            dataflow_issues.append(f'Variable {var_name} used before initialization')
            
            # Deteksi isu gas
            if '++' in contract_code or '--' in contract_code:
                gas_issues.append('Prefer pre-increment/decrement for gas optimization')
            
            if 'for (uint i = 0; i < array.length; i++)' in contract_code:
                gas_issues.append('Cache array length in for loop to save gas')
            
            return {
                'tool': 'basic_static',
                'vulnerabilities': vulnerabilities,
                'dataflow_issues': dataflow_issues,
                'gas_issues': gas_issues,
                'note': 'Advanced analysis tools not available - using basic analysis'
            }
        
        except Exception as e:
            return {
                'tool': 'basic_static',
                'vulnerabilities': [f'Basic analysis failed: {str(e)}'],
                'dataflow_issues': [],
                'gas_issues': [],
                'error': True
            }