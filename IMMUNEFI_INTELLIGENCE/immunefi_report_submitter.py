import os
import json
from datetime import datetime

class ImmunefiReportSubmitter:
    """
    Submit ke Immunefi dengan pendekatan template manual.
    Menghasilkan template laporan dan instruksi manual karena Immunefi tidak memiliki API publik.
    
    REALITAS TEKNIS:
    - Immunefi hanya menyediakan form submission web
    - Tidak ada API publik untuk submit laporan
    - ARC hanya bisa membantu generate template dan bukti
    """
    
    def __init__(self, session_cookie: str = None):
        self.session_cookie = session_cookie
        self.immunefi_base_url = "https://immunefi.com"
    
    def submit_report(self, program_name: str, report_data: dict, evidence_files: list = None):
        """
        Generate template laporan Immunefi untuk submit manual.
        """
        try:
            # Bangun template laporan khusus Immunefi
            report_template = self._build_immunefi_report_template(report_data, program_name)
            
            # Simpan sebagai file lokal
            timestamp = int(datetime.now().timestamp())
            template_file = f"~/.arc/reports/immunefi_{program_name}_{timestamp}.md"
            template_file = os.path.expanduser(template_file)
            os.makedirs(os.path.dirname(template_file), exist_ok=True)
            
            with open(template_file, 'w') as f:
                f.write(report_template)
            
            # Instruksi manual untuk pengguna
            instructions = (
                f"✅ Immunefi report template ready!\n\n"
                f"📋 **Manual Submission Steps:**\n"
                f"1. Go to: https://immunefi.com/bounty/{program_name}\n"
                f"2. Click 'Submit a Bug'\n"
                f"3. Fill the form using content from: {template_file}\n"
                f"4. Upload all evidence files (PoC video, HAR, scripts)\n"
                f"5. Ensure economic impact calculation is included\n"
            )
            
            return {
                'success': True,
                'template_file': template_file,
                'message': instructions,
                'report_url': f"https://immunefi.com/bounty/{program_name}"
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Immunefi template generation failed: {str(e)}'
            }
    
    def handle_triage_request(self, request_type: str, request_details: dict):
        """
        TIDAK BISA menangani permintaan triage secara otomatis.
        Hanya memberikan instruksi untuk generate bukti manual.
        """
        finding_id = request_details.get('finding_id', 'unknown')
        platform = 'immunefi'
        
        return {
            'success': False,
            'message': (
                f"⚠️ Immunefi doesn't support auto-response to triage requests.\n\n"
                f"📱 **Use Telegram commands to generate evidence:**\n"
                f"/generate_evidence video {platform} {finding_id}  # PoC video\n"
                f"/generate_evidence har {platform} {finding_id}    # Transaction proof\n"
                f"/generate_patch {platform} {finding_id}           # Contract patch\n\n"
                f"📤 Then upload manually to Immunefi form."
            )
        }
    
    def _build_immunefi_report_template(self, report_data: dict, program_name: str) -> str:
        """Bangun template laporan khusus Immunefi dengan fokus ekonomi."""
        # Gunakan data ekonomi jika tersedia
        economic_analysis = report_data.get('economic_impact', {})
        
        template = f"""# Immunefi Bug Bounty Submission

## Program Information
- **Protocol**: {program_name}
- **Contract Address**: {report_data.get('contract_address', 'N/A')}
- **Vulnerability Type**: {report_data.get('vulnerability_type', 'Other').title()}
- **Severity**: {report_data.get('severity', 'Critical').title()}

## Executive Summary
{report_data.get('executive_summary', 'Brief summary of the vulnerability and its impact')}

## Technical Description

### Vulnerability Details
{report_data.get('technical_description', 'Detailed technical explanation')}

### Attack Scenario
{report_data.get('attack_scenario', 'Step-by-step attack scenario')}

## Economic Impact Analysis

### Profit Simulation Results
- **Attack Cost**: ${economic_analysis.get('attack_cost', 0):,.2f}
- **Potential Profit**: ${economic_analysis.get('potential_profit', 0):,.2f}
- **Net Profit**: ${economic_analysis.get('net_profit', 0):,.2f}
- **Profit Margin**: {economic_analysis.get('profit_margin', 0):.2%}

### Market Impact
- **TVL at Risk**: ${economic_analysis.get('tvl_at_risk', 0):,.2f}
- **Token Price Impact**: {economic_analysis.get('price_impact', 'N/A')}
- **Protocol Revenue Loss**: ${economic_analysis.get('revenue_loss', 0):,.2f}

## Proof of Concept

### Video Demonstration
[Attach PoC video showing the exploit in action]

### Transaction Proof
[Attach HAR file or transaction hash proving the exploit]

### Reproduction Script
[Attach script that reproduces the vulnerability]

## Remediation

### Immediate Mitigation
{report_data.get('immediate_mitigation', 'Steps to immediately stop the attack')}

### Permanent Fix
{report_data.get('permanent_fix', 'Code changes to permanently fix the issue')}

### Contract Upgrade Plan
{report_data.get('upgrade_plan', 'Plan for contract upgrade if applicable')}

## Additional Information
- **Researcher**: Mr Esse14
- **Discovery Date**: {datetime.now().strftime('%Y-%m-%d')}
- **Economic Simulation Date**: {datetime.now().strftime('%Y-%m-%d')}
- **Bounty Expectation**: Based on Immunefi's bounty structure for this severity level

---
*This report was automatically generated by ARC v7.6 Final with economic impact simulation*
"""
        return template