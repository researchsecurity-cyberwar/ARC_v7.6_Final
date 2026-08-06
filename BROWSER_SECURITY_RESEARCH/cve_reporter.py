import json
import os
from datetime import datetime

class CVEReporter:
    """
    Generate Chromium-compliant CVE reports.
    Menghasilkan laporan CVE yang sesuai standar Chromium.
    """
    
    def __init__(self, report_dir="~/.arc/cve_reports"):
        self.report_dir = os.path.expanduser(report_dir)
        os.makedirs(self.report_dir, exist_ok=True)
    
    def generate_chromium_cve_report(self, vulnerability_data: dict):
        """
        Hasilkan laporan CVE yang sesuai standar Chromium.
        """
        results = {
            'vulnerability_data': vulnerability_data,
            'report_generated': False,
            'report_file': None,
            'cve_id': None
        }
        
        try:
            # Bangun struktur laporan CVE
            cve_report = self._build_cve_report_structure(vulnerability_data)
            
            # Simpan laporan ke file
            report_filename = f"cve_report_{int(time.time())}.json"
            report_file = os.path.join(self.report_dir, report_filename)
            
            with open(report_file, 'w') as f:
                json.dump(cve_report, f, indent=2)
            
            results.update({
                'report_generated': True,
                'report_file': report_file,
                'cve_id': cve_report.get('cve', {}).get('id', 'CVE-PENDING')
            })
        
        except Exception as e:
            results['error'] = f'CVE report generation failed: {str(e)}'
        
        return results
    
    def _build_cve_report_structure(self, vuln_data: dict) -> dict:
        """Bangun struktur laporan CVE."""
        current_time = datetime.now().isoformat()
        
        return {
            "cve": {
                "id": "CVE-PENDING",
                "assigner": "enthusiastsecurity@gmail.com",
                "description": {
                    "lang": "en",
                    "value": vuln_data.get('description', 'Security vulnerability in Chromium')
                },
                "references": [
                    {
                        "url": vuln_data.get('poc_url', ''),
                        "name": "Proof of Concept"
                    }
                ],
                "affected": [
                    {
                        "vendor": "Google",
                        "product": "Chromium",
                        "versions": [
                            {
                                "version": vuln_data.get('affected_version', 'all'),
                                "status": "affected"
                            }
                        ]
                    }
                ],
                "problemtype": {
                    "problemtype_data": [
                        {
                            "description": [
                                {
                                    "lang": "en",
                                    "value": vuln_data.get('vulnerability_type', 'Unknown vulnerability')
                                }
                            ]
                        }
                    ]
                },
                "impact": {
                    "cvss": {
                        "vectorString": vuln_data.get('cvss_vector', 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H'),
                        "baseScore": vuln_data.get('cvss_score', 9.8),
                        "baseSeverity": vuln_data.get('severity', 'CRITICAL').upper()
                    }
                },
                "publishedDate": current_time,
                "lastModified": current_time
            },
            "metadata": {
                "reporter": vuln_data.get('reporter', 'ARC AI Agent'),
                "discovery_date": vuln_data.get('discovery_date', current_time),
                "disclosure_status": "coordinated",
                "chromium_bug_id": vuln_data.get('chromium_bug_id', 'PENDING')
            }
        }