import asyncio
from playwright.async_api import async_playwright
import os

class VideoPoCGenerator:
    """
    Generate video PoC on request.
    Menghasilkan video PoC sesuai permintaan.
    """
    
    def __init__(self, output_dir="~/.arc/evidence"):
        self.output_dir = os.path.expanduser(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def generate_video_poc(self, poc_config: dict):
        """
        Hasilkan video PoC berdasarkan konfigurasi.
        """
        recorder = BehavioralProofRecorder(self.output_dir)
        return await recorder.record_behavioral_poc(
            target_url=poc_config['target_url'],
            exploit_steps=poc_config['steps'],
            vulnerability_type=poc_config['vulnerability_type'],
            report_id=poc_config.get('report_id')
        )