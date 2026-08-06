import os
import re

class POCGenerator:
    """
    Auto-generate reliable PoC from crashes.
    Menghasilkan PoC yang andal dari crash secara otomatis.
    """
    
    def __init__(self, poc_dir="~/.arc/pocs"):
        self.poc_dir = os.path.expanduser(poc_dir)
        os.makedirs(self.poc_dir, exist_ok=True)
    
    def generate_poc_from_crash(self, crash_analysis: dict, original_testcase: str = None):
        """
        Hasilkan PoC dari analisis crash.
        """
        results = {
            'crash_analysis': crash_analysis,
            'poc_generated': False,
            'poc_file': None,
            'poc_content': None,
            'reliability_score': 0.0
        }
        
        try:
            if not crash_analysis.get('security_relevant', False):
                results['error'] = 'Crash is not security relevant'
                return results
            
            crash_type = crash_analysis.get('crash_type', 'unknown')
            severity = crash_analysis.get('severity', 'low')
            
            # Hasilkan konten PoC berdasarkan tipe crash
            if original_testcase:
                # Gunakan testcase asli sebagai dasar
                poc_content = self._refine_original_testcase(original_testcase, crash_type)
            else:
                # Hasilkan PoC dari nol
                poc_content = self._generate_poc_from_scratch(crash_type, severity)
            
            if poc_content:
                # Simpan PoC ke file
                poc_filename = f"poc_{crash_type}_{int(time.time())}.html"
                poc_file = os.path.join(self.poc_dir, poc_filename)
                
                with open(poc_file, 'w') as f:
                    f.write(poc_content)
                
                results.update({
                    'poc_generated': True,
                    'poc_file': poc_file,
                    'poc_content': poc_content,
                    'reliability_score': self._calculate_reliability_score(crash_type, severity)
                })
        
        except Exception as e:
            results['error'] = f'PoC generation failed: {str(e)}'
        
        return results
    
    def _refine_original_testcase(self, testcase: str, crash_type: str) -> str:
        """Perbaiki testcase asli untuk meningkatkan keandalan."""
        # Ini akan mengimplementasikan teknik minimisasi dan stabilisasi
        # Untuk sekarang, kembalikan testcase asli dengan komentar
        return f"<!-- Refined PoC for {crash_type} -->\n{testcase}"
    
    def _generate_poc_from_scratch(self, crash_type: str, severity: str) -> str:
        """Hasilkan PoC dari nol berdasarkan tipe crash."""
        templates = {
            'heap_buffer_overflow': '''
<!DOCTYPE html>
<html>
<head><title>Heap Buffer Overflow PoC</title></head>
<body>
<script>
// Heap buffer overflow trigger
function triggerHeapOverflow() {
    let arr = new Array(0x1000);
    arr.fill(0x41414141);
    // Vulnerable operation here
    return arr;
}
triggerHeapOverflow();
</script>
</body>
</html>
''',
            'use_after_free': '''
<!DOCTYPE html>
<html>
<head><title>Use-After-Free PoC</title></head>
<body>
<script>
// Use-after-free trigger
function triggerUAF() {
    let obj = { data: new ArrayBuffer(0x100) };
    let view = new Uint32Array(obj.data);
    // Free the object
    obj = null;
    // Use after free
    view[0] = 0x41414141;
}
triggerUAF();
</script>
</body>
</html>
''',
            'segmentation_fault': '''
<!DOCTYPE html>
<html>
<head><title>Segmentation Fault PoC</title></head>
<body>
<script>
// Segmentation fault trigger
function triggerSegFault() {
    // Invalid memory access
    let arr = [1, 2, 3];
    arr[-1] = 0x41414141; // Out of bounds write
}
triggerSegFault();
</script>
</body>
</html>
'''
        }
        
        return templates.get(crash_type, f"<!-- Generic PoC for {crash_type} -->\n<p>PoC content</p>")
    
    def _calculate_reliability_score(self, crash_type: str, severity: str) -> float:
        """Hitung skor keandalan PoC."""
        base_score = 0.5
        
        if crash_type in ['heap_buffer_overflow', 'use_after_free']:
            base_score += 0.3
        elif crash_type == 'segmentation_fault':
            base_score += 0.1
        
        if severity == 'high':
            base_score += 0.2
        elif severity == 'medium':
            base_score += 0.1
        
        return min(1.0, base_score)