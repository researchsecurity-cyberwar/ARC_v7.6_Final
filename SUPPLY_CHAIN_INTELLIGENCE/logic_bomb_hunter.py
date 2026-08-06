import os
import re
import datetime
from typing import List, Dict

class LogicBombHunter:
    """
    Find time/geo-triggered payloads in open-source packages.
    Mencari payload yang dipicu waktu/lokasi dalam paket open-source.
    """
    
    def __init__(self):
        self.time_trigger_patterns = {
            'date_check': r'(?:new\s+Date|Date\.now|datetime\.now).*?(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
            'timestamp_check': r'(?:time\.time|Date\.parse).*?(\d{10,})',
            'cron_like': r'(?:\d+\s+){4,}\d+',
            'weekday_check': r'(?:getDay|weekday).*?==\s*(\d)',
            'month_check': r'(?:getMonth|month).*?==\s*(\d)'
        }
        
        self.geo_trigger_patterns = {
            'ip_geolocation': r'(?:ipinfo|ipapi|geoip).*?country.*?["\'](US|CN|RU|IR)["\']',
            'timezone_check': r'(?:Intl\.DateTimeFormat|timezone).*?["\'](Asia/Tokyo|Europe/Moscow)["\']',
            'language_check': r'(?:navigator\.language|locale).*?["\'](zh|ru|fa)["\']'
        }
        
        self.malicious_action_patterns = {
            'data_destruction': r'(?:rm\s+-rf|shred|del|unlink|remove).*?[/\\]',
            'network_exfiltration': r'(?:fetch|axios\.post|requests\.post).*?http[s]?://[^\s"\']+',
            'system_command': r'(?:exec|spawn|system|os\.system).*?\(',
            'crypto_locking': r'(?:encrypt|AES\.encrypt|crypto\.publicEncrypt)',
            'backdoor_creation': r'(?:createServer|listen|bind).*?\d{4,5}'
        }
    
    def hunt_logic_bombs(self, package_path: str):
        """
        Buru logic bomb dalam paket open-source.
        """
        results = {
            'package_path': package_path,
            'logic_bombs_found': [],
            'suspicious_files': [],
            'risk_level': 'NONE',
            'recommendations': []
        }
        
        try:
            # Cari file sumber dalam paket
            source_files = self._find_source_files(package_path)
            
            # Analisis setiap file
            for file_path in source_files[:50]:  # Batasi 50 file pertama
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    try:
                        content = f.read()
                        file_analysis = self._analyze_file_for_logic_bomb(content, file_path)
                        
                        if file_analysis['triggers'] or file_analysis['malicious_actions']:
                            results['suspicious_files'].append(file_analysis)
                            
                            # Cek kombinasi trigger + aksi jahat
                            if file_analysis['triggers'] and file_analysis['malicious_actions']:
                                results['logic_bombs_found'].append({
                                    'file': file_path,
                                    'triggers': file_analysis['triggers'],
                                    'malicious_actions': file_analysis['malicious_actions'],
                                    'severity': 'CRITICAL'
                                })
                    except Exception:
                        continue  # Lewati file yang tidak bisa dibaca
            
            # Tentukan tingkat risiko
            results['risk_level'] = self._calculate_logic_bomb_risk(results['logic_bombs_found'])
            
            # Buat rekomendasi
            results['recommendations'] = self._generate_logic_bomb_recommendations(results['logic_bombs_found'])
        
        except Exception as e:
            results['error'] = f'Logic bomb hunting failed: {str(e)}'
        
        return results
    
    def _find_source_files(self, package_path: str) -> List[str]:
        """Cari file sumber dalam paket."""
        source_files = []
        extensions = ['.js', '.py', '.java', '.ts', '.jsx', '.tsx', '.php', '.rb', '.go']
        
        for root, dirs, files in os.walk(package_path):
            # Abaikan node_modules dan direktori build
            dirs[:] = [d for d in dirs if d not in ['node_modules', 'dist', 'build', '__pycache__']]
            
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    source_files.append(os.path.join(root, file))
        
        return source_files
    
    def _analyze_file_for_logic_bomb(self, content: str, file_path: str) -> Dict:
        """Analisis file untuk logic bomb."""
        triggers = []
        malicious_actions = []
        
        # Deteksi trigger waktu
        for trigger_type, pattern in self.time_trigger_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                trigger_value = match.group(1) if match.groups() else 'unknown'
                triggers.append({
                    'type': trigger_type,
                    'value': trigger_value,
                    'line_number': content.count('\n', 0, match.start()) + 1
                })
        
        # Deteksi trigger geografis
        for trigger_type, pattern in self.geo_trigger_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                trigger_value = match.group(1) if match.groups() else 'unknown'
                triggers.append({
                    'type': trigger_type,
                    'value': trigger_value,
                    'line_number': content.count('\n', 0, match.start()) + 1
                })
        
        # Deteksi aksi jahat
        for action_type, pattern in self.malicious_action_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                malicious_actions.append({
                    'type': action_type,
                    'code_snippet': match.group()[:100],
                    'line_number': content.count('\n', 0, match.start()) + 1
                })
        
        return {
            'file': file_path,
            'triggers': triggers,
            'malicious_actions': malicious_actions
        }
    
    def _calculate_logic_bomb_risk(self, logic_bombs: List) -> str:
        """Hitung tingkat risiko logic bomb."""
        if logic_bombs:
            return 'CRITICAL'
        else:
            return 'NONE'
    
    def _generate_logic_bomb_recommendations(self, logic_bombs: List) -> List[str]:
        """Buat rekomendasi deteksi logic bomb."""
        recommendations = []
        
        if logic_bombs:
            recommendations.extend([
                'Immediately quarantine and analyze the suspicious package',
                'Do not execute or deploy the package in any environment',
                'Report findings to package registry and security community',
                'Implement static analysis with logic bomb detection in CI/CD'
            ])
        else:
            recommendations.append('No logic bombs detected in analyzed files')
        
        recommendations.extend([
            'Review all third-party dependencies before integration',
            'Monitor package behavior in isolated sandbox environments',
            'Implement runtime application self-protection (RASP) controls'
        ])
        
        return recommendations
    
    def check_current_triggers(self, logic_bomb_triggers: List) -> List[Dict]:
        """
        Periksa apakah trigger logic bomb aktif saat ini.
        """
        active_triggers = []
        current_date = datetime.datetime.now()
        current_timestamp = int(current_date.timestamp())
        
        for trigger in logic_bomb_triggers:
            if trigger['type'] == 'date_check':
                # Parse tanggal dari trigger
                try:
                    trigger_date = datetime.datetime.strptime(trigger['value'].replace('/', '-'), '%Y-%m-%d')
                    if trigger_date.date() == current_date.date():
                        active_triggers.append(trigger)
                except:
                    pass
            
            elif trigger['type'] == 'timestamp_check':
                try:
                    trigger_ts = int(trigger['value'])
                    if abs(trigger_ts - current_timestamp) < 86400:  # Dalam 24 jam
                        active_triggers.append(trigger)
                except:
                    pass
        
        return active_triggers