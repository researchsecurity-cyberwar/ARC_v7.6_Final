import random
import time
import requests

class SelfHealingAdaptor:
    """
    If blocked → switch IP/tool/strategy automatically.
    Mengadaptasi secara otomatis saat operasi diblokir atau gagal.
    """
    
    def __init__(self):
        self.adaptation_strategies = {
            'ip_rotation': self._rotate_ip,
            'tool_switching': self._switch_tool,
            'strategy_mutation': self._mutate_strategy,
            'timing_adjustment': self._adjust_timing
        }
        
        self.block_indicators = {
            'rate_limit': [429],
            'waf_block': [403, 406],
            'captcha': ['captcha', 'verify you are human'],
            'timeout': ['timeout', 'connection refused']
        }
    
    def adapt_to_failure(self, operation_context: dict, failure_details: dict):
        """
        Lakukan adaptasi otomatis berdasarkan kegagalan yang terdeteksi.
        """
        results = {
            'original_operation': operation_context,
            'failure_details': failure_details,
            'adaptation_applied': None,
            'new_context': {},
            'success_probability': 0.0
        }
        
        try:
            # Deteksi jenis kegagalan
            failure_type = self._detect_failure_type(failure_details)
            
            # Pilih strategi adaptasi berdasarkan jenis kegagalan
            if failure_type == 'rate_limit':
                strategy = 'timing_adjustment'
            elif failure_type == 'waf_block':
                strategy = 'tool_switching'
            elif failure_type == 'captcha':
                strategy = 'ip_rotation'
            elif failure_type == 'timeout':
                strategy = 'ip_rotation'
            else:
                strategy = random.choice(list(self.adaptation_strategies.keys()))
            
            # Terapkan strategi adaptasi
            adaptation_result = self.adaptation_strategies[strategy](operation_context)
            results['adaptation_applied'] = strategy
            results['new_context'] = adaptation_result
            
            # Hitung probabilitas keberhasilan setelah adaptasi
            results['success_probability'] = self._calculate_success_probability(strategy, failure_type)
        
        except Exception as e:
            results['error'] = f'Self-healing adaptation failed: {str(e)}'
        
        return results
    
    def _detect_failure_type(self, failure_details: dict) -> str:
        """Deteksi jenis kegagalan berdasarkan detail error."""
        status_code = failure_details.get('status_code', 0)
        error_message = str(failure_details.get('error', '')).lower()
        
        if status_code in self.block_indicators['rate_limit']:
            return 'rate_limit'
        elif status_code in self.block_indicators['waf_block']:
            return 'waf_block'
        elif any(indicator in error_message for indicator in self.block_indicators['captcha']):
            return 'captcha'
        elif any(indicator in error_message for indicator in self.block_indicators['timeout']):
            return 'timeout'
        else:
            return 'unknown'
    
    def _rotate_ip(self, context: dict) -> dict:
        """Rotasi IP menggunakan Tor atau proxy."""
        new_context = context.copy()
        
        # Aktifkan Tor jika belum aktif
        if not new_context.get('use_tor', False):
            new_context['use_tor'] = True
            new_context['tor_rotated'] = True
        
        # Tambahkan delay untuk rotasi
        new_context['delay_after_rotation'] = random.uniform(5, 15)
        
        return new_context
    
    def _switch_tool(self, context: dict) -> dict:
        """Ganti tool eksploitasi ke alternatif."""
        new_context = context.copy()
        
        # Peta tool alternatif
        tool_alternatives = {
            'nuclei': 'dalfox',
            'dalfox': 'nuclei',
            'sqlmap': 'manual_sqli',
            'httpx': 'amass',
            'gau': 'wayback'
        }
        
        current_tool = context.get('current_tool', '')
        if current_tool in tool_alternatives:
            new_context['current_tool'] = tool_alternatives[current_tool]
            new_context['tool_switched'] = True
        
        return new_context
    
    def _mutate_strategy(self, context: dict) -> dict:
        """Mutasi strategi eksploitasi."""
        new_context = context.copy()
        
        # Mutasi payload atau pendekatan
        mutation_types = ['encoding', 'case_variation', 'whitespace_obfuscation']
        new_context['mutation_type'] = random.choice(mutation_types)
        new_context['strategy_mutated'] = True
        
        return new_context
    
    def _adjust_timing(self, context: dict) -> dict:
        """Sesuaikan timing operasi."""
        new_context = context.copy()
        
        # Tingkatkan delay secara eksponensial
        current_delay = context.get('rate_limit_delay', (1, 3))
        new_min = min(current_delay[0] * 2, 30)  # Maks 30 detik
        new_max = min(current_delay[1] * 2, 60)  # Maks 60 detik
        new_context['rate_limit_delay'] = (new_min, new_max)
        new_context['timing_adjusted'] = True
        
        return new_context
    
    def _calculate_success_probability(self, strategy: str, failure_type: str) -> float:
        """Hitung probabilitas keberhasilan setelah adaptasi."""
        base_probabilities = {
            'ip_rotation': {'captcha': 0.8, 'timeout': 0.7, 'default': 0.6},
            'tool_switching': {'waf_block': 0.7, 'default': 0.5},
            'strategy_mutation': {'waf_block': 0.6, 'default': 0.4},
            'timing_adjustment': {'rate_limit': 0.9, 'default': 0.3}
        }
        
        strategy_probs = base_probabilities.get(strategy, {})
        return strategy_probs.get(failure_type, strategy_probs.get('default', 0.5))