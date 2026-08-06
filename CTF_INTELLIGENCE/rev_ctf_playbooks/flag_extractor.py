import re

class FlagExtractor:
    """
    Automated flag pattern extraction.
    Mengekstraksi pola flag secara otomatis dari output.
    """
    
    def __init__(self):
        self.flag_patterns = [
            r'CTF\{[^}]+\}',
            r'flag\{[^}]+\}',
            r'FLAG\{[^}]+\}',
            r'picoCTF\{[^}]+\}',
            r'DESC\{[^}]+\}',
            r'HTB\{[^}]+\}',
            r'TRYHACKME\{[^}]+\}'
        ]
    
    def extract_flags(self, input_text: str):
        """
        Ekstrak flag dari teks input.
        """
        results = {
            'input_text': input_text[:200] + '...' if len(input_text) > 200 else input_text,
            'flags_found': [],
            'extraction_successful': False
        }
        
        try:
            flags = []
            for pattern in self.flag_patterns:
                matches = re.findall(pattern, input_text, re.IGNORECASE)
                flags.extend(matches)
            
            results['flags_found'] = list(set(flags))  # Hapus duplikat
            results['extraction_successful'] = len(flags) > 0
        
        except Exception as e:
            results['error'] = f'Flag extraction failed: {str(e)}'
        
        return results