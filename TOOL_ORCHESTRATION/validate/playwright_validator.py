import asyncio
from playwright.async_api import async_playwright
import os
import time

class PlaywrightValidator:
    """
    Behavioral proof execution (headless browser).
    Menjalankan validasi bukti perilaku dengan browser headless.
    """
    
    def __init__(self, output_dir="~/.arc/validate"):
        self.output_dir = os.path.expanduser(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def execute_behavioral_validation(self, target_url: str, validation_steps: list):
        """
        Jalankan validasi perilaku dengan Playwright.
        """
        results = {
            'target_url': target_url,
            'validation_steps': validation_steps,
            'screenshot_path': None,
            'validation_successful': False,
            'execution_time': 0.0
        }
        
        try:
            start_time = time.time()
            
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = await context.new_page()
                
                # Eksekusi langkah validasi
                validation_success = await self._execute_validation_steps(page, target_url, validation_steps)
                
                # Ambil tangkapan layar
                timestamp = int(time.time())
                screenshot_path = os.path.join(self.output_dir, f"validation_{timestamp}.png")
                await page.screenshot(path=screenshot_path, full_page=True)
                
                await context.close()
                await browser.close()
            
            execution_time = time.time() - start_time
            
            results.update({
                'screenshot_path': screenshot_path,
                'validation_successful': validation_success,
                'execution_time': round(execution_time, 2)
            })
        
        except Exception as e:
            results['error'] = f'Playwright validation failed: {str(e)}'
        
        return results
    
    async def _execute_validation_steps(self, page, base_url: str, steps: list) -> bool:
        """Eksekusi langkah-langkah validasi."""
        try:
            for step in steps:
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
                
                elif action == 'verify_element':
                    await page.wait_for_selector(target, timeout=5000)
                
                elif action == 'verify_text':
                    await page.wait_for_function(f"() => document.body.innerText.includes('{value}')", timeout=5000)
            
            return True
        
        except Exception:
            return False