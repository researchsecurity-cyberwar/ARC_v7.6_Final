import subprocess
import json
import os
import re
import shlex
from typing import Dict, List

class CLIToolAdapter:
    """
    Adapt CLI tools automatically.
    Mengadaptasi alat CLI secara otomatis tanpa konfigurasi manual.
    """
    
    def __init__(self, tools_dir="~/.arc/tools"):
        self.tools_dir = os.path.expanduser(tools_dir)
        os.makedirs(self.tools_dir, exist_ok=True)
        self.tool_signatures = {
            'subdomain_enum': ['amass', 'subfinder', 'assetfinder'],
            'port_scan': ['naabu', 'masscan', 'nmap'],
            'web_scan': ['nuclei', 'dalfox', 'ffuf'],
            'api_test': ['postman', 'insomnia', 'curl']
        }
    
    def adapt_cli_tool(self, tool_name: str, command_template: str = None):
        """
        Adaptasi alat CLI untuk penggunaan dalam ARC.
        """
        results = {
            'tool_name': tool_name,
            'command_template': command_template,
            'detected_capabilities': [],
            'execution_method': None,
            'success': False
        }
        
        try:
            # Deteksi kemampuan alat berdasarkan nama
            capabilities = self._detect_tool_capabilities(tool_name)
            results['detected_capabilities'] = capabilities
            
            # Bangun metode eksekusi
            if command_template:
                execution_method = self._build_execution_method(command_template)
            else:
                execution_method = self._build_default_execution(tool_name)
            
            results['execution_method'] = execution_method
            results['success'] = True
        
        except Exception as e:
            results['error'] = f'CLI tool adaptation failed: {str(e)}'
        
        return results
    
    def _detect_tool_capabilities(self, tool_name: str) -> List[str]:
        """Deteksi kemampuan alat berdasarkan nama."""
        capabilities = []
        tool_lower = tool_name.lower()
        
        for category, tools in self.tool_signatures.items():
            if any(tool in tool_lower for tool in tools):
                capabilities.append(category)
        
        return capabilities or ['generic']
    
    def _build_execution_method(self, command_template: str) -> Dict:
        """Bangun metode eksekusi dari template perintah."""
        # Ekstrak placeholder dari template
        placeholders = re.findall(r'\{(\w+)\}', command_template)
        
        return {
            'type': 'template_based',
            'template': command_template,
            'placeholders': placeholders,
            'executor': self._execute_with_template
        }
    
    def _build_default_execution(self, tool_name: str) -> Dict:
        """Bangun metode eksekusi default."""
        return {
            'type': 'direct_execution',
            'tool_name': tool_name,
            'executor': self._execute_directly
        }
    
    def _execute_with_template(self, template: str, parameters: Dict) -> Dict:
        """Eksekusi dengan template perintah."""
        try:
            # Isi placeholder dengan parameter
            command = template.format(**parameters)
            # gunakan shlex.split agar aman terhadap nilai/path yang mengandung spasi
            cmd_list = shlex.split(command)
            
            # Eksekusi perintah
            result = subprocess.run(
                cmd_list,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=self.tools_dir
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_directly(self, tool_name: str, args: List[str]) -> Dict:
        """Eksekusi langsung alat CLI."""
        try:
            cmd_list = [tool_name] + args
            result = subprocess.run(
                cmd_list,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=self.tools_dir
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}