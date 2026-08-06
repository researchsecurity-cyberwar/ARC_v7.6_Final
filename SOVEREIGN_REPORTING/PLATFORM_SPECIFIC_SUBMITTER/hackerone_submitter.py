import requests
import json
import os
import time

class HackerOneSubmitter:
    """
    Submit to HackerOne (with login).
    Mengirim laporan ke HackerOne dengan sesi login yang valid.
    Mendukung respon otomatis ke permintaan tim triage via API.
    
    REALITAS TEKNIS:
    - HackerOne menyediakan API publik lengkap untuk submit & upload bukti
    - Dukungan penuh untuk auto-response ke permintaan triage
    - Integrasi dengan ConversationEngine untuk pemrosesan perintah alami
    """
    
    def __init__(self, session_token: str):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; ARC-Scanner/1.0)',
            'Accept': 'application/json',
            'X-Csrf-Token': self._get_csrf_token(),
            'Authorization': f'Bearer {session_token}'
        })
        self.h1_base_url = "https://hackerone.com"
    
    def submit_report(self, program_handle: str, report_data: dict, evidence_files: list = None):
        """
        Kirim laporan ke program HackerOne tertentu.
        """
        try:
            # Dapatkan informasi program
            program_info = self._get_program_info(program_handle)
            if not program_info.get('exists', False):
                return {'success': False, 'error': f'Program {program_handle} not found'}
            
            # Bangun payload laporan
            report_payload = self._build_h1_report_payload(report_data, program_handle)
            
            # Kirim laporan
            create_url = f"{self.h1_base_url}/api/v1/hackers/reports"
            response = self.session.post(create_url, json=report_payload, timeout=30)
            
            if response.status_code == 201:
                report_json = response.json()
                report_id = report_json['data']['id']
                
                # Upload file bukti jika tersedia
                if evidence_files:
                    upload_result = self._upload_h1_evidence_files(report_id, evidence_files)
                
                return {
                    'success': True,
                    'report_id': report_id,
                    'report_url': f"{self.h1_base_url}/reports/{report_id}",
                    'message': 'Report submitted successfully to HackerOne'
                }
            else:
                return {
                    'success': False,
                    'error': f'Submission failed: {response.status_code} - {response.text[:200]}',
                    'status_code': response.status_code
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'HackerOne submission failed: {str(e)}'
            }
    
    def handle_triage_request(self, request_type: str, request_details: dict):
        """
        Tangani permintaan dari tim triage secara otomatis.
        HANYA UNTUK HACKERONE (karena API publik tersedia).
        """
        try:
            report_id = request_details.get('report_id')
            if not report_id:
                return {'success': False, 'error': 'Report ID required for triage request'}
            
            if request_type == "additional_screenshot":
                # Generate screenshot spesifik yang diminta
                if 'evidence_generator' in request_details:
                    evidence_generator = request_details['evidence_generator']
                    new_screenshot = evidence_generator.create_targeted_screenshot(
                        target=request_details.get('target'),
                        payload=request_details.get('payload'),
                        browser_state=request_details.get('browser_state', 'default')
                    )
                    
                    # Upload screenshot ke laporan
                    upload_result = self._upload_h1_evidence_files(report_id, [new_screenshot])
                    
                    return {
                        'success': True,
                        'action': 'screenshot_generated_and_uploaded',
                        'file_path': new_screenshot,
                        'report_id': report_id
                    }
                else:
                    return {'success': False, 'error': 'Evidence generator not provided'}
            
            elif request_type == "network_capture":
                # Generate PCAP/HAR tambahan
                if 'evidence_generator' in request_details:
                    evidence_generator = request_details['evidence_generator']
                    network_evidence = evidence_generator.create_network_capture(
                        endpoints=request_details.get('endpoints', []),
                        duration=request_details.get('duration', 30),
                        capture_type=request_details.get('capture_type', 'har')
                    )
                    
                    # Upload file jaringan ke laporan
                    upload_result = self._upload_h1_evidence_files(report_id, [network_evidence])
                    
                    return {
                        'success': True,
                        'action': 'network_capture_generated_and_uploaded',
                        'file_path': network_evidence,
                        'report_id': report_id
                    }
                else:
                    return {'success': False, 'error': 'Evidence generator not provided'}
            
            elif request_type == "remediation_patch":
                # Generate kode perbaikan spesifik
                if 'patch_generator' in request_details:
                    patch_generator = request_details['patch_generator']
                    patch = patch_generator.create_security_patch(
                        vulnerability_type=request_details.get('vulnerability_type'),
                        affected_code=request_details.get('affected_code', ''),
                        framework=request_details.get('framework', 'unknown'),
                        language=request_details.get('language', 'javascript')
                    )
                    
                    # Simpan patch sebagai file sementara
                    patch_file = f"/tmp/h1_patch_{report_id}_{int(time.time())}.txt"
                    with open(patch_file, 'w') as f:
                        f.write(patch)
                    
                    # Upload patch ke laporan
                    upload_result = self._upload_h1_evidence_files(report_id, [patch_file])
                    
                    return {
                        'success': True,
                        'action': 'remediation_patch_generated_and_uploaded',
                        'file_path': patch_file,
                        'report_id': report_id
                    }
                else:
                    return {'success': False, 'error': 'Patch generator not provided'}
            
            elif request_type == "clarification_response":
                # Kirim respons klarifikasi ke diskusi laporan
                clarification_text = request_details.get('clarification_text', '')
                if clarification_text:
                    discussion_result = self._add_h1_discussion_comment(report_id, clarification_text)
                    return {
                        'success': True,
                        'action': 'clarification_response_submitted',
                        'report_id': report_id,
                        'comment_id': discussion_result.get('comment_id')
                    }
                else:
                    return {'success': False, 'error': 'Clarification text required'}
            
            else:
                return {'success': False, 'error': f'Unsupported triage request type: {request_type}'}
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Triage request handling failed: {str(e)}'
            }
    
    def _add_h1_discussion_comment(self, report_id: str, comment_text: str):
        """Tambahkan komentar ke diskusi laporan HackerOne."""
        try:
            comment_url = f"{self.h1_base_url}/api/v1/hackers/reports/{report_id}/comments"
            comment_payload = {
                "comment": {
                    "content": comment_text,
                    "visibility": "public"  # atau "private" untuk internal notes
                }
            }
            
            response = self.session.post(comment_url, json=comment_payload, timeout=30)
            if response.status_code == 201:
                comment_json = response.json()
                return {'success': True, 'comment_id': comment_json['data']['id']}
            else:
                return {'success': False, 'error': f'Comment submission failed: {response.status_code}'}
        except Exception as e:
            return {'success': False, 'error': f'Comment submission error: {str(e)}'}
    
    def set_evidence_generator(self, evidence_generator):
        """Set evidence generator untuk integrasi."""
        self.evidence_generator = evidence_generator
    
    def set_patch_generator(self, patch_generator):
        """Set patch generator untuk integrasi."""
        self.patch_generator = patch_generator
    
    def _get_csrf_token(self):
        """Dapatkan CSRF token dari halaman utama HackerOne."""
        try:
            response = self.session.get(f"{self.h1_base_url}/")
            if response.status_code == 200:
                import re
                csrf_match = re.search(r'meta content="([^"]+)" name="csrf-token"', response.text)
                if csrf_match:
                    return csrf_match.group(1)
        except:
            pass
        return ''
    
    def _get_program_info(self, program_handle: str) -> dict:
        """Dapatkan informasi program HackerOne."""
        try:
            program_url = f"{self.h1_base_url}/api/v1/hackers/programs/{program_handle}"
            response = self.session.get(program_url, timeout=10)
            return {'exists': response.status_code == 200}
        except:
            return {'exists': False}
    
    def _build_h1_report_payload(self, report_data: dict, program_handle: str) -> dict:
        """Bangun payload laporan HackerOne."""
        return {
            "report": {
                "title": report_data.get('title', f"{report_data.get('vulnerability_type', 'Vulnerability')} in {program_handle}"),
                "vulnerability_information": report_data.get('technical_description', 'No description provided'),
                "steps_to_reproduce": report_data.get('reproduction_steps', 'Steps not specified'),
                "impact": report_data.get('business_impact', 'Significant impact'),
                "structured_scope": {
                    "url": report_data.get('target_url', ''),
                    "asset_identifier": report_data.get('asset_identifier', ''),
                    "asset_type": report_data.get('asset_type', 'url')
                },
                "program_handle": program_handle
            }
        }
    
    def _upload_h1_evidence_files(self, report_id: str, file_paths: list):
        """Upload file bukti ke laporan HackerOne."""
        uploaded_files = []
        for file_path in file_paths[:10]:  # Batasi 10 file
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        files = {'file': f}
                        upload_url = f"{self.h1_base_url}/api/v1/hackers/reports/{report_id}/attachments"
                        response = self.session.post(upload_url, files=files, timeout=60)
                        if response.status_code == 201:
                            uploaded_files.append(file_path)
            except Exception:
                continue
        return {'uploaded_files': uploaded_files, 'count': len(uploaded_files)}