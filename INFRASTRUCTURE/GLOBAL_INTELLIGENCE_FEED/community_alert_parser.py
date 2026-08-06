import requests
import json
import os
import time

class CommunityAlertParser:
    """
    Parse Reddit/Twitter/Nitter for emerging threats.
    Menggunakan sumber yang benar-benar tersedia di 2026.
    """
    
    def __init__(self, data_dir="~/.arc/intel", tor_proxies=None):
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        self.tor_proxies = tor_proxies or {'http': 'socks5h://127.0.0.1:9050',
                                          'https': 'socks5h://127.0.0.1:9050'}
    
    def parse_community_alerts(self):
        """Parse alert komunitas dari sumber yang tersedia."""
        results = {
            'reddit_alerts': 0,
            'twitter_alerts': 0,
            'total_alerts': 0,
            'parsing_successful': False
        }
        
        try:
            reddit_count = self._parse_reddit_alerts()
            results['reddit_alerts'] = reddit_count
            
            twitter_count = self._parse_twitter_alerts()
            results['twitter_alerts'] = twitter_count
            
            results['total_alerts'] = reddit_count + twitter_count
            results['parsing_successful'] = True
        
        except Exception as e:
            results['error'] = f'Community alert parsing failed: {str(e)}'
        
        return results
    
    def _parse_reddit_alerts(self):
        """Parse /r/bugbounty menggunakan Reddit JSON API langsung."""
        try:
            # Gunakan Reddit JSON API (masih publik di 2026)
            reddit_url = "https://www.reddit.com/r/bugbounty/new.json"
            params = {'limit': 20}
            
            response = requests.get(
                reddit_url,
                params=params,
                proxies=self.tor_proxies,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('data', {}).get('children', [])
                
                reddit_posts = []
                for post in posts:
                    post_data = post.get('data', {})
                    reddit_posts.append({
                        'title': post_data.get('title', ''),
                        'selftext': post_data.get('selftext', ''),
                        'created_utc': post_data.get('created_utc', 0),
                        'url': f"https://reddit.com{post_data.get('permalink', '')}"
                    })
                
                timestamp = int(time.time())
                reddit_file = os.path.join(self.data_dir, f"reddit_bb_{timestamp}.json")
                with open(reddit_file, 'w') as f:
                    json.dump({'posts': reddit_posts}, f, indent=2)
                
                return len(reddit_posts)
            else:
                return 0
        
        except Exception:
            return 0
    
    def _parse_twitter_alerts(self):
        """Parse tweet keamanan menggunakan Nitter (fallback)."""
        try:
            nitter_instances = [
                'https://nitter.net',
                'https://nitter.poast.org',
                'https://nitter.moomoo.me'
            ]
            
            for instance in nitter_instances:
                try:
                    search_url = f"{instance}/search"
                    params = {'q': 'CVE OR exploit OR vulnerability', 'f': 'tweets'}
                    
                    response = requests.get(
                        search_url,
                        params=params,
                        proxies=self.tor_proxies,
                        timeout=20
                    )
                    
                    if response.status_code == 200:
                        timestamp = int(time.time())
                        twitter_file = os.path.join(self.data_dir, f"twitter_raw_{timestamp}.html")
                        with open(twitter_file, 'w') as f:
                            f.write(response.text)
                        return 1  # Cukup satu instance berhasil
                
                except:
                    continue
            
            return 0
        
        except Exception:
            return 0