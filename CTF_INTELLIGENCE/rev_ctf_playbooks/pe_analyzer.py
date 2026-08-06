import subprocess
import os

class PEAnalyzer:
    """
    Windows PE analysis.
    Menganalisis binary PE Windows untuk challenge reverse engineering.
    """
    
    def __init__(self):
        self.tools = ['file', 'strings', 'objdump', 'pefile']
    
    def analyze_pe_binary(self, binary_path: str):
        """
        Analisis binary PE.
        """
        results = {
            'binary_path': binary_path,
            'file_type': None,
            'strings_found': [],
            'imports_found': [],
            'sections_found': [],
            'analysis_complete': False
        }
        
        try:
            if not os.path.exists(binary_path):
                results['error'] = 'Binary file not found'
                return results
            
            # Analisis tipe file
            file_result = subprocess.run(['file', binary_path], capture_output=True, text=True)
            results['file_type'] = file_result.stdout.strip()
            
            # Ekstrak strings
            strings_result = subprocess.run(['strings', binary_path], capture_output=True, text=True)
            results['strings_found'] = strings_result.stdout.split('\n')[:50]
            
            # Analisis import (gunakan objdump untuk PE)
            try:
                objdump_result = subprocess.run(['objdump', '-p', binary_path], capture_output=True, text=True)
                imports = []
                for line in objdump_result.stdout.split('\n'):
                    if 'DLL Name:' in line:
                        imports.append(line.split(': ')[1])
                results['imports_found'] = imports
            except:
                results['imports_found'] = ['objdump analysis failed']
            
            # Analisis section
            sections = []
            if 'objdump_result' in locals():
                for line in objdump_result.stdout.split('\n'):
                    if '.text' in line or '.data' in line or '.rsrc' in line:
                        sections.append(line.strip())
            results['sections_found'] = sections[:10]
            
            results['analysis_complete'] = True
        
        except Exception as e:
            results['error'] = f'PE analysis failed: {str(e)}'
        
        return results