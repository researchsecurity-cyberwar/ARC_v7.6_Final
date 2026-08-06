import os
import re
import subprocess

class CrashAnalyzer:
    """
    Auto-analyze crash dumps for security relevance.
    Menganalisis dump crash secara otomatis untuk relevansi keamanan.
    """
    
    def __init__(self, analysis_dir="~/.arc/crash_analysis"):
        self.analysis_dir = os.path.expanduser(analysis_dir)
        os.makedirs(self.analysis_dir, exist_ok=True)
        self.security_indicators = [
            'SEGV', 'SIGSEGV', 'segmentation fault',
            'heap-buffer-overflow', 'stack-buffer-overflow',
            'use-after-free', 'double-free',
            'READ of size', 'WRITE of size',
            'ASAN:', 'UBSAN:'
        ]
    
    def analyze_crash_dump(self, crash_file: str, target_binary: str = None):
        """
        Analisis dump crash untuk relevansi keamanan.
        """
        results = {
            'crash_file': crash_file,
            'target_binary': target_binary,
            'security_relevant': False,
            'crash_type': None,
            'severity': 'low',
            'analysis_successful': False
        }
        
        try:
            if not os.path.exists(crash_file):
                results['error'] = 'Crash file not found'
                return results
            
            # Baca isi file crash
            with open(crash_file, 'r') as f:
                crash_content = f.read()
            
            # Deteksi indikator keamanan
            security_indicators_found = []
            for indicator in self.security_indicators:
                if indicator.lower() in crash_content.lower():
                    security_indicators_found.append(indicator)
            
            if security_indicators_found:
                results['security_relevant'] = True
                
                # Tentukan tipe crash
                crash_type = self._determine_crash_type(crash_content)
                results['crash_type'] = crash_type
                
                # Tentukan tingkat keparahan
                severity = self._assess_severity(crash_type, crash_content)
                results['severity'] = severity
            
            results['analysis_successful'] = True
        
        except Exception as e:
            results['error'] = f'Crash analysis failed: {str(e)}'
        
        return results
    
    def _determine_crash_type(self, crash_content: str) -> str:
        """Tentukan tipe crash berdasarkan isi dump."""
        content_lower = crash_content.lower()
        
        if 'heap-buffer-overflow' in content_lower:
            return 'heap_buffer_overflow'
        elif 'stack-buffer-overflow' in content_lower:
            return 'stack_buffer_overflow'
        elif 'use-after-free' in content_lower:
            return 'use_after_free'
        elif 'double-free' in content_lower:
            return 'double_free'
        elif 'segmentation fault' in content_lower or 'segv' in content_lower:
            return 'segmentation_fault'
        else:
            return 'unknown_crash'
    
    def _assess_severity(self, crash_type: str, crash_content: str) -> str:
        """Nilai tingkat keparahan crash."""
        if crash_type in ['heap_buffer_overflow', 'use_after_free']:
            return 'high'
        elif crash_type in ['stack_buffer_overflow', 'double_free']:
            return 'medium'
        elif crash_type == 'segmentation_fault':
            # Periksa apakah ada kontrol alur
            if 'rip' in crash_content.lower() or 'eip' in crash_content.lower():
                return 'high'
            else:
                return 'low'
        else:
            return 'low'