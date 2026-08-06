import asyncio
from playwright.async_api import async_playwright
import os
import json

class UIToolAutomator:
    """
    Automate UI-based tools via Playwright.
    Mengotomatisasi alat berbasis UI melalui Playwright.
    """
    
    def __init__(self, tools_dir="~/.arc/tools"):
        self.tools_dir = os.path.expanduser(tools_dir)
        os.makedirs(self.tools_dir, exist_ok=True)
    
    async def automate_ui_tool(self, tool_config: dict):
        """
        Otomatisasi alat berbasis UI.
        """
        results = {
            'tool_config': tool_config,
            'automation_successful': False,
            'screenshot_path': None,
            'output_data': None,
            'execution_time': 0.0
        }
        
        try:
            start_time = asyncio.get_event_loop().time()
            
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = await context.new_page()
                
                # Jalankan skenario otomatisasi
                output_data = await self._execute_ui_scenario(page, tool_config)
                
                # Ambil tangkapan layar
                screenshot_path = os.path.join(self.tools_dir, f"ui_automation_{int(asyncio.get_event_loop().time())}.png")
                await page.screenshot(path=screenshot_path, full_page=True)
                
                await context.close()
                await browser.close()
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            results.update({
                'automation_successful': output_data is not None,
                'screenshot_path': screenshot_path,
                'output_data': output_data,
                'execution_time': round(execution_time, 2)
            })
        
        except Exception as e:
            results['error'] = f'UI tool automation failed: {str(e)}'
        
        return results
    
    async def _execute_ui_scenario(self, page, config: dict):
        """Eksekusi skenario otomatisasi UI."""
        try:
            # Navigasi ke URL target
            await page.goto(config['url'], wait_until='networkidle')
            
            # Eksekusi langkah-langkah
            for step in config.get('steps', []):
                action = step.get('action')
                selector = step.get('selector')
                value = step.get('value', '')
                
                if action == 'fill':
                    await page.fill(selector, value)
                elif action == 'click':
                    await page.click(selector)
                elif action == 'select':
                    await page.select_option(selector, value)
                elif action == 'wait_for':
                    await page.wait_for_selector(selector, timeout=10000)
            
            # Ekstrak data hasil
            if 'extract' in config:
                extracted_data = {}
                for field, selector in config['extract'].items():
                    element = await page.query_selector(selector)
                    if element:
                        extracted_data[field] = await element.inner_text()
                return extracted_data
            
            return {'status': 'completed'}
        
        except Exception:
            return None