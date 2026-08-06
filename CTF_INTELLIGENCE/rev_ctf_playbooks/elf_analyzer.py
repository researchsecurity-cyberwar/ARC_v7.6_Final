import subprocess
import os

class ELFAnalyzer:
    """
    ELF binary analysis.
    Menganalisis binary ELF untuk challenge reverse engineering.
    """
    
    def __init__(self):
        self.tools = ['file', 'strings', 'objdump', 'readelf', 'ltrace']
    
    def analyze_elf_binary(self, binary_path: str):
        """
        Analisis binary ELF.
        """
        results = {
            'binary_path': binary_path,
            'file_type': None,
            'strings_found': [],
            'functions_found': [],
            'imports_found': [],
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
            results['strings_found'] = strings_result.stdout.split('\n')[:50]  # Batasi 50 string
            
            # Analisis fungsi
            objdump_result = subprocess.run(['objdump', '-t', binary_path], capture_output=True, text=True)
            functions = []
            for line in objdump_result.stdout.split('\n'):
                if ' F .text' in line:
                    parts = line.split()
                    if len(parts) > 5:
                        functions.append(parts[-1])
            results['functions_found'] = functions[:20]
            
            # Analisis import
            readelf_result = subprocess.run(['readelf', '-d', binary_path], capture_output=True, text=True)
            imports = []
            for line in readelf_result.stdout.split('\n'):
                if '(NEEDED)' in line:
                    imports.append(line.split('[')[1].split(']')[0])
            results['imports_found'] = imports
            
            results['analysis_complete'] = True
        
        except Exception as e:
            results['error'] = f'ELF analysis failed: {str(e)}'
        
        return results