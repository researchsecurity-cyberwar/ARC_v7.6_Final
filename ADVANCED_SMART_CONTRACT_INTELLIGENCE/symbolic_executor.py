class SymbolicExecutor:
    """
    Symbolic execution for complex paths.
    Melakukan eksekusi simbolik untuk jalur kompleks dalam kontrak pintar.
    """
    
    def __init__(self, executor_dir="~/.arc/symbolic_execution"):
        self.executor_dir = os.path.expanduser(executor_dir)
        os.makedirs(self.executor_dir, exist_ok=True)
    
    def execute_symbolically(self, contract_path: str, target_function: str = None):
        """
        Eksekusi kontrak secara simbolik.
        """
        results = {
            'contract_path': contract_path,
            'target_function': target_function,
            'execution_successful': False,
            'paths_explored': 0,
            'vulnerabilities_found': [],
            'execution_report': None
        }
        
        try:
            # Gunakan Mythril untuk eksekusi simbolik jika tersedia
            if self._check_mythril_available():
                report = self._run_mythril_symbolic_execution(contract_path, target_function)
            else:
                # Fallback ke analisis jalur dasar
                report = self._run_basic_path_analysis(contract_path, target_function)
            
            results.update({
                'execution_successful': True,
                'paths_explored': report.get('paths', 0),
                'vulnerabilities_found': report.get('vulnerabilities', []),
                'execution_report': report
            })
        
        except Exception as e:
            results['error'] = f'Symbolic execution failed: {str(e)}'
        
        return results
    
    def _check_mythril_available(self):
        """Periksa apakah Mythril tersedia."""
        try:
            subprocess.run(['myth', '--version'], capture_output=True, timeout=10)
            return True
        except:
            return False
    
    def _run_mythril_symbolic_execution(self, contract_path: str, target_function: str = None):
        """Jalankan eksekusi simbolik Mythril."""
        try:
            cmd = ['myth', 'analyze', contract_path, '--execution-timeout', '300']
            if target_function:
                cmd.extend(['--solver-timeout', '100'])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                vulnerabilities = []
                paths = 0
                
                # Parse output untuk menemukan jalur dan kerentanan
                if 'integer overflow' in result.stdout.lower():
                    vulnerabilities.append('Integer overflow vulnerability detected')
                if 'reentrancy' in result.stdout.lower():
                    vulnerabilities.append('Reentrancy vulnerability detected')
                if 'Assertion violation' in result.stdout:
                    vulnerabilities.append('Assertion violation detected')
                
                # Hitung jumlah jalur yang dieksplorasi
                paths = result.stdout.count('Path:') + result.stdout.count('State:')
                
                return {
                    'tool': 'mythril',
                    'vulnerabilities': vulnerabilities,
                    'paths': paths,
                    'raw_output': result.stdout[:1000]
                }
            else:
                raise Exception(f'Mythril symbolic execution failed: {result.stderr[:200]}')
        
        except subprocess.TimeoutExpired:
            raise Exception('Mythril symbolic execution timed out (10 minutes)')
    
    def _run_basic_path_analysis(self, contract_path: str, target_function: str = None):
        """Jalankan analisis jalur dasar jika Mythril tidak tersedia."""
        try:
            with open(contract_path, 'r') as f:
                contract_code = f.read()
            
            vulnerabilities = []
            paths = 0
            
            # Analisis jalur dasar berdasarkan struktur kontrol
            if 'if' in contract_code:
                paths += contract_code.count('if')
            if 'require' in contract_code:
                paths += contract_code.count('require')
            if 'assert' in contract_code:
                paths += contract_code.count('assert')
            
            # Deteksi potensi kerentanan berdasarkan pola
            if 'call(' in contract_code and 'require(' not in contract_code:
                vulnerabilities.append('Missing return value check after external call')
            
            if 'balance' in contract_code and 'transfer' in contract_code:
                vulnerabilities.append('Potential reentrancy vulnerability')
            
            return {
                'tool': 'basic_path_analysis',
                'vulnerabilities': vulnerabilities,
                'paths': paths,
                'note': 'Mythril not available - using basic path analysis'
            }
        
        except Exception as e:
            return {
                'tool': 'basic_path_analysis',
                'vulnerabilities': [f'Basic path analysis failed: {str(e)}'],
                'paths': 0,
                'error': True
            }