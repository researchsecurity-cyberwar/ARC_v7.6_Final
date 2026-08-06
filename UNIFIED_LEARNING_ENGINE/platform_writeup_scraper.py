"""
Platform Writeup Scraper - Mengumpulkan write-up dari semua platform bug bounty.
Menghubungkan hasil scraping ke Learning Bridge untuk pembelajaran berkelanjutan.
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import time

from .hackerone_writeup_scraper import HackerOneWriteupScraper
from .bugcrowd_writeup_scraper import BugCrowdWriteupScraper
from .intigriti_writeup_scraper import IntigritiWriteupScraper
from .yeswehack_writeup_scraper import YesWeHackWriteupScraper
from .immunefi_writeup_scraper import ImmunefiWriteupScraper


class PlatformWriteupScraper:
    """
    Scrap write-up dari semua platform.
    Mengumpulkan write-up publik dari berbagai platform bug bounty.
    Setiap write-up yang ter-scrap otomatis dikirim ke self-learning engine
    untuk memperkaya pengetahuan AI agent.
    """

    def __init__(self, writeups_dir="~/.arc/writeups", learning_bridge=None):
        self.writeups_dir = os.path.expanduser(writeups_dir)
        os.makedirs(self.writeups_dir, exist_ok=True)
        self.learning_bridge = learning_bridge
        self.last_writeups = {}

        # Inisialisasi scraper per platform
        self.platforms = {}
        try:
            self.platforms['hackerone'] = HackerOneWriteupScraper()
        except Exception:
            pass
        try:
            self.platforms['bugcrowd'] = BugCrowdWriteupScraper()
        except Exception:
            pass
        try:
            self.platforms['intigriti'] = IntigritiWriteupScraper()
        except Exception:
            pass
        try:
            self.platforms['yeswehack'] = YesWeHackWriteupScraper()
        except Exception:
            pass
        try:
            self.platforms['immunefi'] = ImmunefiWriteupScraper()
        except Exception:
            pass

    def set_learning_bridge(self, bridge):
        """Hubungkan dengan Learning Bridge untuk self-learning."""
        self.learning_bridge = bridge

    def scrape_all_platforms(self):
        """
        Scrap write-up dari semua platform yang tersedia.
        Hasilnya otomatis dikirim ke self-learning engine.
        """
        results = {
            'hackerone_writeups': None,
            'bugcrowd_writeups': None,
            'intigriti_writeups': None,
            'yeswehack_writeups': None,
            'immunefi_writeups': None,
            'total_writeups': 0,
            'scraping_successful': False,
            'learning_insights_fed': 0
        }

        try:
            total = 0
            fed = 0

            # Scrap HackerOne
            h1_writeups = self._scrape_platform('hackerone', 'scrape_public_reports')
            results['hackerone_writeups'] = h1_writeups
            total += len(h1_writeups or [])
            fed += self._feed_writeups_to_learning(h1_writeups, 'hackerone')

            # Scrap BugCrowd
            bc_writeups = self._scrape_platform('bugcrowd', 'scrape_disclosure_reports')
            results['bugcrowd_writeups'] = bc_writeups
            total += len(bc_writeups or [])
            fed += self._feed_writeups_to_learning(bc_writeups, 'bugcrowd')

            # Scrap Intigriti
            intigriti_writeups = self._scrape_platform('intigriti', 'scrape_public_writeups')
            results['intigriti_writeups'] = intigriti_writeups
            total += len(intigriti_writeups or [])
            fed += self._feed_writeups_to_learning(intigriti_writeups, 'intigriti')

            # Scrap YesWeHack
            ywh_writeups = self._scrape_platform('yeswehack', 'scrape_public_reports')
            results['yeswehack_writeups'] = ywh_writeups
            total += len(ywh_writeups or [])
            fed += self._feed_writeups_to_learning(ywh_writeups, 'yeswehack')

            # Scrap Immunefi
            immunefi_writeups = self._scrape_platform('immunefi', 'scrape_blog_writeups')
            results['immunefi_writeups'] = immunefi_writeups
            total += len(immunefi_writeups or [])
            fed += self._feed_writeups_to_learning(immunefi_writeups, 'immunefi')

            results['total_writeups'] = total
            results['learning_insights_fed'] = fed
            results['scraping_successful'] = True

        except Exception as e:
            results['error'] = f'Platform scraping failed: {str(e)}'

        return results

    def _scrape_platform(self, platform, method_name):
        """Scrap satu platform dengan aman."""
        scraper = self.platforms.get(platform)
        if not scraper:
            return []

        try:
            method = getattr(scraper, method_name, None)
            if method:
                result = method()
                # Simpan untuk deduplikasi learning
                self.last_writeups[platform] = result
                return result
        except Exception:
            pass

        return []

    def _feed_writeups_to_learning(self, writeups, platform) -> int:
        """
        Kirim write-up ke learning bridge untuk pembelajaran.
        Write-up berisi teknik nyata yang telah terbukti berhasil
        - sumber pengetahuan paling berharga untuk AI agent.
        """
        if not writeups or not self.learning_bridge:
            return 0

        # Cegah duplikasi: gunakan ID/URL unik per writeup
        seen_ids = set()
        fed_count = 0

        for writeup in writeups:
            writeup_id = str(writeup.get('id') or writeup.get('url') or writeup.get('title') or '')
            if not writeup_id or writeup_id in seen_ids:
                continue

            # Deduplikasi global via learning bridge
            try:
                if self.learning_bridge.report_writeup_insight(writeup, platform):
                    fed_count += 1
                    seen_ids.add(writeup_id)
            except Exception:
                continue

        return fed_count