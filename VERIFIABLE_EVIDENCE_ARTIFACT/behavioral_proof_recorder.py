import asyncio
import os
from datetime import datetime

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    async_playwright = None
    PLAYWRIGHT_AVAILABLE = False

class BehavioralProofRecorder:
    """
    Playwright → PoC.mp4 with URL overlay.
    Merekam bukti perilaku dalam format video dengan overlay URL.
    """
    
    def __init__(self, output_dir="~/.arc/evidence"):
        self.output_dir = os.path.expanduser(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        if not PLAYWRIGHT_AVAILABLE:
            print("⚠️ Playwright tidak tersedia - BehavioralProofRecorder berjalan dalam mode terbatas")
    
    async def record_behavioral_poc(self, target_url: str, exploit_steps: list, 
                                   vulnerability_type: str, report_id: str = None):
        """
        Rekam PoC perilaku untuk kerentanan tertentu.
        """
        if report_id is None:
            report_id = f"poc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        results = {
            'report_id': report_id,
            'target_url': target_url,
            'vulnerability_type': vulnerability_type,
            'video_path': None,
            'recording_successful': False,
            'duration_seconds': 0,
            'screenshot_path': None
        }
        
        if not PLAYWRIGHT_AVAILABLE:
            results['error'] = 'Playwright tidak tersedia. Install dengan: pip install playwright && playwright install chromium'
            return results
        
        try:
            # Setup output paths
            video_filename = f"{report_id}_{vulnerability_type}.mp4"
            video_path = os.path.join(self.output_dir, video_filename)
            screenshot_filename = f"{report_id}_{vulnerability_type}.png"
            screenshot_path = os.path.join(self.output_dir, screenshot_filename)
            
            async with async_playwright() as p:
                # Launch browser with video recording
                browser = await p.chromium.launch(
                    headless=False,
                    args=['--disable-web-security', '--ignore-certificate-errors']
                )
                
                # Create context with video recording
                context = await browser.new_context(
                    record_video_dir=self.output_dir,
                    record_video_size={'width': 1280, 'height': 720},
                    viewport={'width': 1280, 'height': 720}
                )
                
                page = await context.new_page()
                
                # Record start time
                start_time = datetime.now()
                
                # Execute exploit steps
                for step in exploit_steps:
                    await self._execute_step(page, step, target_url)
                    await page.wait_for_timeout(1000)  # 1 second delay between steps
                
                # Take final screenshot
                await page.screenshot(path=screenshot_path, full_page=True)
                
                # Close context to finalize video
                await context.close()
                await browser.close()
                
                # Calculate duration
                duration = (datetime.now() - start_time).total_seconds()
                
                # Find the actual video file (Playwright generates random filename)
                video_files = [f for f in os.listdir(self.output_dir) if f.endswith('.mp4')]
                if video_files:
                    latest_video = max(video_files, key=lambda x: os.path.getctime(os.path.join(self.output_dir, x)))
                    actual_video_path = os.path.join(self.output_dir, latest_video)
                    # Rename to our desired filename
                    os.rename(actual_video_path, video_path)
                
                results.update({
                    'video_path': video_path,
                    'screenshot_path': screenshot_path,
                    'recording_successful': True,
                    'duration_seconds': round(duration, 2)
                })
        
        except Exception as e:
            results['error'] = f'Behavioral proof recording failed: {str(e)}'
        
        return results
    
    async def _execute_step(self, page, step: dict, base_url: str):
        """Eksekusi satu langkah dalam PoC."""
        action = step.get('action')
        target = step.get('target', '')
        value = step.get('value', '')
        
        if action == 'navigate':
            url = f"{base_url.rstrip('/')}{target}" if target.startswith('/') else target
            await page.goto(url, wait_until='networkidle')
        
        elif action == 'fill':
            await page.fill(target, value)
        
        elif action == 'click':
            await page.click(target)
        
        elif action == 'submit':
            await page.click(target)
            await page.wait_for_load_state('networkidle')
        
        elif action == 'verify':
            # Verify element exists or contains text
            if 'text' in step:
                await page.wait_for_selector(f"text={step['text']}", timeout=5000)
            else:
                await page.wait_for_selector(target, timeout=5000)