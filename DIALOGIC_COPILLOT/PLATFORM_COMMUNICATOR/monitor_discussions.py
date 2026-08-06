import requests
import time
from urllib.parse import urljoin

class MonitorDiscussions:
    """
    Monitor new messages from platforms.
    Memantau pesan baru dari platform bug bounty dan CTF.
    """
    
    def __init__(self):
        self.platform_endpoints = {
            'hackerone': '/notifications',
            'bugcrowd': '/dashboard',
            'intigriti': '/dashboard/submissions',
            'hackthebox': '/dashboard/teams',
            'tryhackme': '/dashboard'
        }
        
        self.message_indicators = {
            'hackerone': ['new-message', 'comment-created'],
            'bugcrowd': ['notification', 'message'],
            'intigriti': ['submission-update', 'triage-update'],
            'hackthebox': ['team-invite', 'challenge-solved'],
            'tryhackme': ['room-completed', 'achievement-unlocked']
        }
    
    def monitor_platform_messages(self, platform: str, session_cookie: str, check_interval: int = 300):
        """
        Pantau pesan baru dari platform tertentu.
        """
        if platform not in self.platform_endpoints:
            return {'error': f'Unsupported platform: {platform}'}
        
        results = {
            'platform': platform,
            'monitoring_active': True,
            'check_interval': check_interval,
            'new_messages': [],
            'last_check': None
        }
        
        try:
            # Setup session dengan cookie
            session = requests.Session()
            session.cookies.set('session_token', session_cookie)
            
            # Endpoint dasar platform
            base_urls = {
                'hackerone': 'https://hackerone.com',
                'bugcrowd': 'https://bugcrowd.com',
                'intigriti': 'https://www.intigriti.com',
                'hackthebox': 'https://www.hackthebox.com',
                'tryhackme': 'https://tryhackme.com'
            }
            
            base_url = base_urls.get(platform, '')
            endpoint = self.platform_endpoints[platform]
            full_url = urljoin(base_url, endpoint)
            
            # Loop pemantauan
            while results['monitoring_active']:
                try:
                    response = session.get(full_url, timeout=10)
                    
                    if response.status_code == 200:
                        new_messages = self._extract_new_messages(response.text, platform)
                        if new_messages:
                            results['new_messages'].extend(new_messages)
                            # Kirim notifikasi ke channel yang sesuai
                            self._trigger_notifications(new_messages, platform)
                    
                    results['last_check'] = time.time()
                    time.sleep(check_interval)
                    
                except Exception as e:
                    print(f"⚠️ Monitoring error for {platform}: {e}")
                    time.sleep(check_interval)
        
        except Exception as e:
            results['error'] = f'Monitoring setup failed: {str(e)}'
            results['monitoring_active'] = False
        
        return results
    
    def _extract_new_messages(self, page_content: str, platform: str) -> list:
        """Ekstrak pesan baru dari konten halaman."""
        messages = []
        indicators = self.message_indicators.get(platform, [])
        
        for indicator in indicators:
            if indicator in page_content.lower():
                # Ekstrak detail pesan (placeholder - implementasi penuh perlu parsing HTML)
                messages.append({
                    'platform': platform,
                    'type': indicator,
                    'timestamp': time.time(),
                    'preview': f'New {indicator} detected on {platform}'
                })
                break  # Cukup satu indikator
        
        return messages
    
    def _trigger_notifications(self, messages: list, platform: str):
        """Picu notifikasi untuk pesan baru."""
        # Ini akan terintegrasi dengan notifier spesifik
        for message in messages:
            print(f"🔔 NEW MESSAGE: {message['preview']}")