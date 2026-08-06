import json
import os
from datetime import datetime

class HARExporter:
    """
    HTTP Archive format export for Burp replay.
    Mengekspor capture jaringan dalam format HAR untuk replay Burp.
    """
    
    def __init__(self, output_dir="~/.arc/evidence"):
        self.output_dir = os.path.expanduser(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def export_har_from_requests(self, requests_data: list, target_url: str, 
                                vulnerability_type: str, report_id: str = None):
        """
        Ekspor data permintaan ke format HAR.
        """
        if report_id is None:
            report_id = f"har_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        har_data = self._build_har_structure(requests_data, target_url, vulnerability_type)
        har_filename = f"{report_id}_{vulnerability_type}.har"
        har_path = os.path.join(self.output_dir, har_filename)
        
        try:
            with open(har_path, 'w') as f:
                json.dump(har_data, f, indent=2)
            
            return {
                'report_id': report_id,
                'har_path': har_path,
                'export_successful': True,
                'entry_count': len(requests_data),
                'target_url': target_url
            }
        
        except Exception as e:
            return {
                'report_id': report_id,
                'error': f'HAR export failed: {str(e)}',
                'export_successful': False
            }
    
    def _build_har_structure(self, requests_data: list, target_url: str, vuln_type: str) -> dict:
        """Bangun struktur data HAR."""
        entries = []
        
        for req in requests_data:
            entry = {
                "startedDateTime": req.get('timestamp', datetime.now().isoformat()),
                "time": req.get('duration_ms', 0),
                "request": {
                    "method": req.get('method', 'GET'),
                    "url": req.get('url', ''),
                    "httpVersion": req.get('http_version', 'HTTP/1.1'),
                    "cookies": req.get('cookies', []),
                    "headers": req.get('headers', []),
                    "queryString": req.get('query_params', []),
                    "postData": req.get('post_data', {}),
                    "headersSize": req.get('headers_size', -1),
                    "bodySize": req.get('body_size', -1)
                },
                "response": {
                    "status": req.get('status_code', 200),
                    "statusText": req.get('status_text', 'OK'),
                    "httpVersion": req.get('response_http_version', 'HTTP/1.1'),
                    "cookies": req.get('response_cookies', []),
                    "headers": req.get('response_headers', []),
                    "content": {
                        "size": req.get('response_size', 0),
                        "mimeType": req.get('content_type', 'text/html'),
                        "text": req.get('response_body', '')[:10000]  # Limit 10KB
                    },
                    "redirectURL": req.get('redirect_url', ''),
                    "headersSize": req.get('response_headers_size', -1),
                    "bodySize": req.get('response_body_size', -1)
                },
                "cache": {},
                "timings": req.get('timings', {"blocked": 0, "dns": 0, "connect": 0, "send": 0, "wait": 0, "receive": 0}),
                "serverIPAddress": req.get('server_ip', ''),
                "connection": req.get('connection_id', ''),
                "_securityState": req.get('security_state', 'secure')
            }
            entries.append(entry)
        
        return {
            "log": {
                "version": "1.2",
                "creator": {"name": "ARC v7.6 Final", "version": "1.0"},
                "browser": {"name": "Chromium", "version": "122"},
                "pages": [{
                    "startedDateTime": datetime.now().isoformat(),
                    "id": f"page_{target_url.replace('://', '_').replace('/', '_')}",
                    "title": f"{vuln_type.upper()} Proof - {target_url}",
                    "pageTimings": {"onContentLoad": 0, "onLoad": 0}
                }],
                "entries": entries
            }
        }