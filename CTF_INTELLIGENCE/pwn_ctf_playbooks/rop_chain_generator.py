import subprocess
import re

class ROPChainGenerator:
    """
    ROP chain generator.
    Menghasilkan ROP chain untuk challenge binary exploitation.
    """
    
    def __init__(self):
        self.gadgets = {}
    
    def generate_rop_chain(self, binary_path: str, target_function: str = None):
        """
        Hasilkan ROP chain.
        """
        results = {
            'binary_path': binary_path,
            'target_function': target_function,
            'gadgets_found': [],
            'rop_chain': None,
            'chain_generated': False
        }
        
        try:
            # Cari gadgets menggunakan ROPgadget
            gadgets = self._find_rop_gadgets(binary_path)
            results['gadgets_found'] = gadgets
            
            if gadgets:
                # Bangun ROP chain
                rop_chain = self._build_rop_chain(gadgets, target_function)
                results['rop_chain'] = rop_chain
                results['chain_generated'] = True
        
        except Exception as e:
            results['error'] = f'ROP chain generation failed: {str(e)}'
        
        return results
    
    def _find_rop_gadgets(self, binary_path: str) -> list:
        """Cari ROP gadgets dalam binary."""
        try:
            result = subprocess.run(['ROPgadget', '--binary', binary_path, '--only', 'pop|ret'], 
                                  capture_output=True, text=True, timeout=30)
            gadgets = []
            for line in result.stdout.split('\n'):
                if '0x' in line and ':' in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        address = parts[0].strip()
                        instruction = ':'.join(parts[1:]).strip()
                        gadgets.append({'address': address, 'instruction': instruction})
            return gadgets[:20]
        except:
            return []
    
    def _build_rop_chain(self, gadgets: list, target_function: str) -> str:
        """Bangun ROP chain dari gadgets yang ditemukan."""
        # Cari gadget pop rdi; ret untuk x64
        pop_rdi = None
        ret_gadget = None
        
        for gadget in gadgets:
            if 'pop rdi' in gadget['instruction']:
                pop_rdi = gadget
            elif 'ret' in gadget['instruction']:
                ret_gadget = gadget
        
        if pop_rdi and ret_gadget:
            chain = f"{pop_rdi['address']} -> [target_address] -> {ret_gadget['address']}"
            return chain
        
        return "Basic ROP chain using available gadgets"