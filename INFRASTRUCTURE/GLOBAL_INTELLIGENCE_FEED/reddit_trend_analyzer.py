import json
import os
from collections import Counter

class RedditTrendAnalyzer:
    """
    Analyze /r/bugbounty for logic flaw trends.
    Menganalisis tren kerentanan logika di /r/bugbounty.
    """
    
    def __init__(self, data_dir="~/.arc/intel"):
        self.data_dir = os.path.expanduser(data_dir)
    
    def analyze_bugbounty_trends(self):
        """
        Analisis tren bug bounty dari data Reddit.
        """
        results = {
            'logic_flaw_trends': [],
            'popular_targets': [],
            'bounty_amounts': [],
            'analysis_successful': False
        }
        
        try:
            # Temukan file data Reddit terbaru
            reddit_files = [f for f in os.listdir(self.data_dir) if f.startswith('reddit_bb_')]
            if not reddit_files:
                return results
            
            latest_file = max(reddit_files, key=lambda x: int(x.split('_')[-1].replace('.json', '')))
            with open(os.path.join(self.data_dir, latest_file), 'r') as f:
                reddit_data = json.load(f)
            
            posts = reddit_data.get('posts', [])
            if not posts:
                return results
            
            # Ekstrak tren kerentanan logika
            logic_keywords = ['logic', 'business', 'workflow', 'authorization', 'race', 'validation']
            logic_posts = []
            
            for post in posts:
                title = post.get('title', '').lower()
                text = post.get('selftext', '').lower()
                
                if any(keyword in title or keyword in text for keyword in logic_keywords):
                    logic_posts.append(post)
            
            # Analisis target populer
            targets = []
            for post in posts:
                title = post.get('title', '')
                # Ekstrak nama perusahaan dari judul
                if ']' in title and '[' in title:
                    target = title.split(']')[0].replace('[', '').strip()
                    if target and len(target) > 2:
                        targets.append(target)
            
            # Analisis jumlah bounty
            bounty_amounts = []
            for post in posts:
                text = post.get('selftext', '')
                # Cari pola jumlah bounty
                import re
                amounts = re.findall(r'\$(\d+(?:,\d+)*)', text)
                for amount in amounts:
                    try:
                        clean_amount = int(amount.replace(',', ''))
                        if clean_amount > 0:
                            bounty_amounts.append(clean_amount)
                    except:
                        continue
            
            results.update({
                'logic_flaw_trends': self._categorize_logic_flaws(logic_posts),
                'popular_targets': Counter(targets).most_common(10),
                'bounty_amounts': sorted(bounty_amounts)[-10:],  # 10 bounty terbesar
                'analysis_successful': True
            })
        
        except Exception as e:
            results['error'] = f'Reddit trend analysis failed: {str(e)}'
        
        return results
    
    def _categorize_logic_flaws(self, posts):
        """Kategorikan jenis kerentanan logika."""
        categories = {
            'authorization_bypass': ['auth', 'permission', 'access control'],
            'business_logic_abuse': ['business', 'workflow', 'process'],
            'race_condition': ['race', 'concurrent', 'timing'],
            'validation_bypass': ['validation', 'input', 'check']
        }
        
        categorized = {}
        for category, keywords in categories.items():
            count = sum(
                1 for post in posts 
                if any(keyword in post.get('title', '').lower() or 
                      keyword in post.get('selftext', '').lower() 
                      for keyword in keywords)
            )
            if count > 0:
                categorized[category] = count
        
        return categorized