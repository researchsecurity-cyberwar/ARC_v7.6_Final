import requests
import json
import os
from bs4 import BeautifulSoup

class CTFChallengeIngestor:
    """
    Ingest challenges from HTB, CTFtime, etc.
    Mengambil challenge hanya dari sumber GRATIS yang tersedia.
    """
    
    def __init__(self, ctf_dir="~/.arc/ctf"):
        self.ctf_dir = os.path.expanduser(ctf_dir)
        os.makedirs(self.ctf_dir, exist_ok=True)
        # Hanya gunakan sumber GRATIS
        self.free_sources = {
            'hackthebox': 'https://www.hackthebox.com/starting-point',
            'tryhackme': 'https://tryhackme.com/path/outline/presecurity',
            'ctftime': 'https://ctftime.org/writeups',
            'github_writeups': 'https://api.github.com/search/repositories'
        }
    
    def ingest_free_challenges(self):
        """
        Ambil challenge dari sumber GRATIS saja.
        """
        results = {
            'htb_challenges': None,
            'thm_rooms': None,
            'ctftime_writeups': None,
            'github_writeups': None,
            'total_challenges': 0,
            'ingestion_successful': False
        }
        
        try:
            # Ambil HTB Starting Point (GRATIS)
            htb_challenges = self._scrape_htb_starting_point()
            results['htb_challenges'] = htb_challenges
            
            # Ambil TryHackMe free rooms
            thm_rooms = self._scrape_tryhackme_free_rooms()
            results['thm_rooms'] = thm_rooms
            
            # Ambil CTFtime write-ups publik
            ctftime_writeups = self._scrape_ctftime_writeups()
            results['ctftime_writeups'] = ctftime_writeups
            
            # Ambil GitHub write-ups
            github_writeups = self._search_github_writeups()
            results['github_writeups'] = github_writeups
            
            total = len(htb_challenges or []) + len(thm_rooms or []) + len(ctftime_writeups or []) + len(github_writeups or [])
            results['total_challenges'] = total
            results['ingestion_successful'] = True
        
        except Exception as e:
            results['error'] = f'CTF challenge ingestion failed: {str(e)}'
        
        return results
    
    def _scrape_htb_starting_point(self):
        """Scrap HTB Starting Point (GRATIS)."""
        try:
            response = requests.get(self.free_sources['hackthebox'], timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                challenges = []
                
                # Cari elemen challenge di Starting Point
                challenge_items = soup.select('.card') or soup.select('.machine-card') or soup.select('article')
                
                for item in challenge_items[:10]:  # Batasi 10 challenge
                    title_elem = item.select_one('h3, h2, .title')
                    if title_elem and 'Starting Point' in title_elem.text:
                        challenges.append({
                            'title': title_elem.text.strip(),
                            'platform': 'hackthebox',
                            'difficulty': 'beginner',
                            'category': self._detect_category_from_title(title_elem.text),
                            'url': self.free_sources['hackthebox']
                        })
                
                # Simpan ke file
                if challenges:
                    timestamp = int(time.time())
                    htb_file = os.path.join(self.ctf_dir, f"htb_starting_{timestamp}.json")
                    with open(htb_file, 'w') as f:
                        json.dump({'challenges': challenges}, f, indent=2)
                    return challenges
            
            return []
        
        except Exception:
            return []
    
    def _scrape_tryhackme_free_rooms(self):
        """Scrap TryHackMe free rooms."""
        try:
            response = requests.get(self.free_sources['tryhackme'], timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                rooms = []
                
                # Cari room gratis
                room_items = soup.select('.room-card') or soup.select('.module-card') or soup.select('article')
                
                for item in room_items[:15]:
                    title_elem = item.select_one('h3, h2, .title')
                    if title_elem:
                        rooms.append({
                            'title': title_elem.text.strip(),
                            'platform': 'tryhackme',
                            'difficulty': 'beginner',
                            'category': self._detect_category_from_title(title_elem.text),
                            'url': self.free_sources['tryhackme']
                        })
                
                if rooms:
                    timestamp = int(time.time())
                    thm_file = os.path.join(self.ctf_dir, f"thm_free_{timestamp}.json")
                    with open(thm_file, 'w') as f:
                        json.dump({'rooms': rooms}, f, indent=2)
                    return rooms
            
            return []
        
        except Exception:
            return []
    
    def _scrape_ctftime_writeups(self):
        """Scrap CTFtime write-ups publik."""
        try:
            response = requests.get(self.free_sources['ctftime'], timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                writeups = []
                
                writeup_items = soup.select('.writeup-list-item') or soup.select('tr') or soup.select('article')
                
                for item in writeup_items[:20]:
                    title_elem = item.select_one('a[href*="/writeup/"]')
                    if title_elem:
                        writeups.append({
                            'title': title_elem.text.strip(),
                            'platform': 'ctftime',
                            'url': f"https://ctftime.org{title_elem['href']}",
                            'source': 'public_writeup'
                        })
                
                if writeups:
                    timestamp = int(time.time())
                    ctftime_file = os.path.join(self.ctf_dir, f"ctftime_writeups_{timestamp}.json")
                    with open(ctftime_file, 'w') as f:
                        json.dump({'writeups': writeups}, f, indent=2)
                    return writeups
            
            return []
        
        except Exception:
            return []
    
    def _search_github_writeups(self):
        """Cari write-up CTF di GitHub."""
        try:
            query = "CTF writeup language:markdown pushed:>2026-07-01"
            params = {'q': query, 'sort': 'updated', 'order': 'desc', 'per_page': 10}
            
            response = requests.get(
                self.free_sources['github_writeups'],
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                repos = []
                
                for item in data.get('items', [])[:10]:
                    repos.append({
                        'title': item.get('name', ''),
                        'description': item.get('description', ''),
                        'url': item.get('html_url', ''),
                        'platform': 'github',
                        'source': 'public_repository'
                    })
                
                if repos:
                    timestamp = int(time.time())
                    github_file = os.path.join(self.ctf_dir, f"github_ctf_{timestamp}.json")
                    with open(github_file, 'w') as f:
                        json.dump({'repositories': repos}, f, indent=2)
                    return repos
            
            return []
        
        except Exception:
            return []
    
    def _detect_category_from_title(self, title: str) -> str:
        """Deteksi kategori dari judul challenge."""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['web', 'website', 'http']):
            return 'web'
        elif any(word in title_lower for word in ['rev', 'reverse', 'binary']):
            return 'reversing'
        elif any(word in title_lower for word in ['crypto', 'cipher', 'rsa']):
            return 'crypto'
        elif any(word in title_lower for word in ['pwn', 'exploit', 'buffer']):
            return 'pwn'
        elif any(word in title_lower for word in ['forensics', 'pcap', 'memory']):
            return 'forensics'
        else:
            return 'misc'