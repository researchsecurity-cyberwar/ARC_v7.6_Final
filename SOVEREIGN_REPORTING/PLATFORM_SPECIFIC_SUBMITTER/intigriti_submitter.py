import requests
import json
import os
import time

class IntigritiSubmitter:
    """
    Submit to Intigriti (with Personal Access Token).
    Mengirim laporan ke Intigriti dengan Personal Access Token yang valid.
    
    REALITAS TEKNIS:
    - Intigriti menyediakan Personal Access Token API (bukan session cookie)
    - API mendukung submit laporan dan upload bukti
    - Dukungan penuh untuk auto-response ke permintaan triage
    - Integrasi dengan ConversationEngine untuk pemrosesan perintah alami
    """
    
    def __init__(self, personal_access_token: str):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; ARC-Scanner/1.0)',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-API-KEY': personal_access_token  # Intigriti menggunakan X-API-KEY
        })
        self.intigriti_base_url = "https://api.intigriti.com"
    
    def submit_report(self, company_handle: str, report_data: dict, evidence_files: list = None):
        """
        Kirim laporan ke program Intigriti tertentu.
        """
        try:
            # Validasi program tersedia
            program_info = self._get_program_info(company_handle)
            if not program_info.get('exists', False):
                return {'success': False, 'error': f'Program {company_handle} not found'}
            
            # Bangun payload laporan
            report_payload = self._build_intigriti_payload(report_data, company_handle)
            
            # Kirim laporan
            submit_url = f"{self.intigriti_base_url}/external/researcher/v1/reports"
            response = self.session.post(submit_url, json=report_payload, timeout=30)
            
            if response.status_code == 201:
                report_json = response.json()
                report_id = report_json.get('id')
                
                # Upload file bukti jika tersedia
                if evidence_files:
                    upload_result = self._upload_intigriti_evidence_files(report_id, evidence_files)
                
                return {
                    'success': True,
                    'report_id': report_id,
                    'report_url': f"https://www.intigriti.com/dashboard/reports/{report_id}",
                    'message': 'Report submitted successfully to Intigriti'
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
                'error': f'Intigriti submission failed: {str(e)}'
            }
    
    def handle_triage_request(self, request_type: str, request_details: dict):
        """
        Tangani permintaan dari tim triage secara otomatis.
        HANYA UNTUK INTIGRITI (karena API publik tersedia).
        """
        try:
            report_id = request_details.get('report_id')
            if not report_id:
                return {'success': False, 'error': 'Report ID required for triage request'}
            
            if request_type == "additional_screenshot":
                if 'evidence_generator' in request_details:
                    evidence_generator = request_details['evidence_generator']
                    new_screenshot = evidence_generator.create_custom_screenshot(
                        target=request_details.get('target'),
                        payload=request_details.get('payload'),
                        browser_state=request_details.get('browser_state', 'default')
                    )
                    
                    upload_result = self._upload_intigriti_evidence_files(report_id, [new_screenshot])
                    return {
                        'success': True,
                        'action': 'screenshot_generated_and_uploaded',
                        'file_path': new_screenshot,
                        'report_id': report_id
                    }
                else:
                    return {'success': False, 'error': 'Evidence generator not provided'}
            
            elif request_type == "network_capture":
                if 'evidence_generator' in request_details:
                    evidence_generator = request_details['evidence_generator']
                    network_evidence = evidence_generator.create_network_capture(
                        endpoints=request_details.get('endpoints', []),
                        duration=request_details.get('duration', 30),
                        capture_type=request_details.get('capture_type', 'har')
                    )
                    
                    upload_result = self._upload_intigriti_evidence_files(report_id, [network_evidence])
                    return {
                        'success': True,
                        'action': 'network_capture_generated_and_uploaded',
                        'file_path': network_evidence,
                        'report_id': report_id
                    }
                else:
                    return {'success': False, 'error': 'Evidence generator not provided'}
            
            elif request_type == "remediation_patch":
                if 'patch_generator' in request_details:
                    patch_generator = request_details['patch_generator']
                    patch = patch_generator.create_security_patch(
                        vulnerability_type=request_details.get('vulnerability_type'),
                        affected_code=request_details.get('affected_code', ''),
                        framework=request_details.get('framework', 'unknown'),
                        language=request_details.get('language', 'javascript')
                    )
                    
                    patch_file = f"/tmp/intigriti_patch_{report_id}_{int(time.time())}.txt"
                    with open(patch_file, 'w') as f:
                        f.write(patch)
                    
                    upload_result = self._upload_intigriti_evidence_files(report_id, [patch_file])
                    return {
                        'success': True,
                        'action': 'remediation_patch_generated_and_uploaded',
                        'file_path': patch_file,
                        'report_id': report_id
                    }
                else:
                    return {'success': False, 'error': 'Patch generator not provided'}
            
            elif request_type == "clarification_response":
                clarification_text = request_details.get('clarification_text', '')
                if clarification_text:
                    discussion_result = self._add_intigriti_discussion_comment(report_id, clarification_text)
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
    
    def _add_intigriti_discussion_comment(self, report_id: str, comment_text: str):
        """Tambahkan komentar ke diskusi laporan Intigriti."""
        try:
            comment_url = f"{self.intigriti_base_url}/external/researcher/v1/reports/{report_id}/comments"
            comment_payload = {
                "content": comment_text,
                "visibility": "PUBLIC"  # atau "PRIVATE"
            }
            
            response = self.session.post(comment_url, json=comment_payload, timeout=30)
            if response.status_code == 201:
                comment_json = response.json()
                return {'success': True, 'comment_id': comment_json.get('id')}
            else:
                return {'success': False, 'error': f'Comment submission failed: {response.status_code}'}
        except Exception as e:
            return {'success': False, 'error': f'Comment submission error: {str(e)}'}
    
    def _get_program_info(self, company_handle: str) -> dict:
        """Dapatkan informasi program Intigriti."""
        try:
            # Endpoint untuk mendapatkan info program
            program_url = f"{self.intigriti_base_url}/external/researcher/v1/companies/{company_handle}"
            response = self.session.get(program_url, timeout=10)
            return {'exists': response.status_code == 200}
        except:
            return {'exists': False}
    
    def _build_intigriti_payload(self, report_data: dict, company_handle: str) -> dict:
        """Bangun payload laporan Intigriti sesuai dokumentasi API resmi."""
        # Mapping severity Intigriti
        severity_mapping = {
            'critical': 'CRITICAL',
            'high': 'HIGH', 
            'medium': 'MEDIUM',
            'low': 'LOW',
            'info': 'INFORMATIONAL'
        }
        
        return {
            "title": report_data.get('title', f"{report_data.get('vulnerability_type', 'Vulnerability')}"),
            "vulnerabilityType": report_data.get('vulnerability_type', 'other'),
            "description": report_data.get('technical_description', 'No description provided'),
            "reproductionSteps": report_data.get('reproduction_steps', 'Steps not specified'),
            "impact": report_data.get('business_impact', 'Significant impact'),
            "companyHandle": company_handle,
            "affectedUrl": report_data.get('target_url', ''),
            "severity": severity_mapping.get(report_data.get('severity', 'medium').lower(), 'MEDIUM')
        }
    
    def set_evidence_generator(self, evidence_generator):
        """Set evidence generator untuk integrasi."""
        self.evidence_generator = evidence_generator
    
    def set_patch_generator(self, patch_generator):
        """Set patch generator untuk integrasi."""
        self.patch_generator = patch_generator
    
    def _upload_intigriti_evidence_files(self, report_id: str, file_paths: list):
        """Upload file bukti ke laporan Intigriti."""
        uploaded_files = []
        for file_path in file_paths[:10]:  # Batasi 10 file
            try:
                if os.path.exists(file_path):
                    # Intigriti mengharapkan multipart/form-data untuk upload
                    with open(file_path, 'rb') as f:
                        files = {'file': f}
                        upload_url = f"{self.intigriti_base_url}/external/researcher/v1/reports/{report_id}/attachments"
                        response = self.session.post(upload_url, files=files, timeout=60)
                        if response.status_code == 201:
                            uploaded_files.append(file_path)
            except Exception:
                continue
        return {'uploaded_files': uploaded_files, 'count': len(uploaded_files)}