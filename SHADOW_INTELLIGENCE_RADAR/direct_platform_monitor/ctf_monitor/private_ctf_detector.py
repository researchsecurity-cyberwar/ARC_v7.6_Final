import requests
from bs4 import BeautifulSoup
import re

class PrivateCTFDetector:
    """
    Deteksi CTF private via login.
    Mendeteksi event CTF private yang hanya terlihat setelah login.
    """
    
    def __init__(self, platform_sessions):
        """
        platform_sessions: dict dengan sesi untuk berbagai platform
        Contoh: {'htb': 'session123', 'thm': 'session456'}
        """
        self.platform_sessions = platform_sessions
        self.htb_scraper = HackTheBoxScraper(platform_sessions.get('htb', ''))
        self.thm_scraper = TryHackMeScraper(platform_sessions.get('thm', ''))
    
    def detect_private_events(self):
        """Deteksi event CTF private di semua platform."""
        private_events = []
        
        # Cek HTB untuk event private
        try:
            htb_events = self._check_htb_private_events()
            private_events.extend(htb_events)
        except Exception as e:
            print(f"⚠️ HTB private event detection failed: {e}")
        
        # Cek THM untuk event private  
        try:
            thm_events = self._check_thm_private_events()
            private_events.extend(thm_events)
        except Exception as e:
            print(f"⚠️ THM private event detection failed: {e}")
        
        return private_events
    
    def _check_htb_private_events(self):
        """Cek event private di HackTheBox."""
        events = []
        try:
            # Akses halaman event HTB
            events_url = "https://www.hackthebox.com/events"
            response = self.htb_scraper.session.get(events_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                event_cards = soup.find_all(class_=re.compile(r'.*event-card.*'))
                
                for card in event_cards:
                    # Cek apakah event memiliki indikator private
                    if card.find(text=re.compile(r'Private|Invite-only|VIP', re.IGNORECASE)):
                        title_elem = card.find('h3') or card.find('h2')
                        if title_elem:
                            events.append({
                                'platform': 'hackthebox',
                                'name': title_elem.get_text(strip=True),
                                'type': 'private',
                                'prize_pool': self._extract_prize_pool(card)
                            })
        except Exception as e:
            print(f"⚠️ HTB private event check failed: {e}")
        
        return events
    
    def _check_thm_private_events(self):
        """Cek event private di TryHackMe."""
        events = []
        try:
            # Akses halaman kompetisi THM
            comp_url = "https://tryhackme.com/competitions"
            response = self.thm_scraper.session.get(comp_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                comp_cards = soup.find_all(class_=re.compile(r'.*competition.*'))
                
                for card in comp_cards:
                    if card.find(text=re.compile(r'Private|Exclusive', re.IGNORECASE)):
                        title_elem = card.find('h3') or card.find('h2')
                        if title_elem:
                            events.append({
                                'platform': 'tryhackme',
                                'name': title_elem.get_text(strip=True),
                                'type': 'private',
                                'team_size': self._extract_team_size(card)
                            })
        except Exception as e:
            print(f"⚠️ THM private event check failed: {e}")
        
        return events
    
    def _extract_prize_pool(self, card):
        """Ekstrak informasi prize pool dari kartu event."""
        prize_text = card.get_text()
        prize_match = re.search(r'\$(\d+(?:,\d+)*)', prize_text)
        if prize_match:
            return int(prize_match.group(1).replace(',', ''))
        return 0
    
    def _extract_team_size(self, card):
        """Ekstrak informasi ukuran tim dari kartu kompetisi."""
        team_text = card.get_text()
        team_match = re.search(r'(\d+)\s*members?', team_text, re.IGNORECASE)
        if team_match:
            return int(team_match.group(1))
        return 0