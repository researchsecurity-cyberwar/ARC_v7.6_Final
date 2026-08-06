import os
import re
from datetime import datetime

class TwitterSecurityParser:
    """
    Parse security researcher tweets for early signals.
    Mengurai tweet peneliti keamanan untuk sinyal dini.
    """
    
    def __init__(self, data_dir="~/.arc/intel"):
        self.data_dir = os.path.expanduser(data_dir)
        self.security_researchers = [
            'taviso', 'mwrinfosecurity', 'foxglove_sec', 'nahamsec',
            'intigriti', 'hacker0x01', 'thehackerschoice', 'liveoverflow'
        ]
    
    def parse_security_tweets(self):
        """
        Parse tweet keamanan untuk sinyal dini.
        """
        results = {
            'early_signals': [],
            'cve_mentions': [],
            'exploit_disclosures': [],
            'parsing_successful': False
        }
        
        try:
            # Temukan file data Twitter terbaru
            twitter_files = [f for f in os.listdir(self.data_dir) if f.startswith('twitter_raw_')]
            if not twitter_files:
                return results
            
            latest_file = max(twitter_files, key=lambda x: int(x.split('_')[-1].replace('.html', '')))
            with open(os.path.join(self.data_dir, latest_file), 'r') as f:
                html_content = f.read()
            
            # Ekstrak sinyal dini dari konten HTML
            signals = self._extract_early_signals(html_content)
            cve_mentions = self._extract_cve_mentions(html_content)
            exploit_disclosures = self._extract_exploit_disclosures(html_content)
            
            results.update({
                'early_signals': signals,
                'cve_mentions': cve_mentions,
                'exploit_disclosures': exploit_disclosures,
                'parsing_successful': True
            })
        
        except Exception as e:
            results['error'] = f'Twitter security parsing failed: {str(e)}'
        
        return results
    
    def _extract_early_signals(self, html_content):
        """Ekstrak sinyal dini dari konten HTML."""
        signals = []
        
        # Pola untuk sinyal dini
        early_signal_patterns = [
            r'working on.*vulnerability',
            r'found a.*bug in',
            r'researching.*security issue',
            r'disclosing.*soon',
            r'zero day.*in'
        ]
        
        for pattern in early_signal_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            signals.extend(matches)
        
        return signals[:10]  # Batasi 10 sinyal
    
    def _extract_cve_mentions(self, html_content):
        """Ekstrak sebutan CVE dari konten HTML."""
        cve_pattern = r'CVE-\d{4}-\d{4,}'
        cve_matches = re.findall(cve_pattern, html_content)
        return list(set(cve_matches))[:10]  # Unik dan batasi 10
    
    def _extract_exploit_disclosures(self, html_content):
        """Ekstrak pengungkapan exploit dari konten HTML."""
        exploit_patterns = [
            r'exploit.*available',
            r'poc.*published',
            r'proof of concept.*here',
            r'github.*exploit',
            r'demo.*vulnerability'
        ]
        
        disclosures = []
        for pattern in exploit_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            disclosures.extend(matches)
        
        return disclosures[:10]  # Batasi 10 pengungkapan