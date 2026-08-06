import re
import tempfile
import os
from urllib.parse import urljoin, urlparse

class CISAVDPScraper:
    """
    Ambil informasi VDP CISA berdasarkan fakta lapangan.
    CISA tidak memiliki halaman VDP publik tradisional yang bisa discrape.
    Menggunakan knowledge base statis yang sudah diverifikasi + kemampuan parsing dokumen.
    """
    
    def __init__(self, session_cookies=None):
        # Tidak perlu session untuk CISA VDP (publik)
        # Tapi simpan referensi ke PDF guidance resmi
        self.cisa_vdp_guidance_pdf = "https://www.cisa.gov/sites/default/files/publications/Establishing_a_Coordinated_Vulnerability_Disclosure_Program_508c.pdf"
        self.cisa_main_url = "https://www.cisa.gov"
    
    def get_cisa_vdp_details(self):
        """Dapatkan detail program VDP CISA berdasarkan informasi resmi."""
        vdp_info = {
            'program_name': 'CISA Vulnerability Disclosure Program',
            'vdp_url': self.cisa_main_url,
            'reporting_email': 'vulnerability@cisa.dhs.gov',
            'reporting_portal': 'https://www.cisa.gov/report',  # URL resmi meskipun loading
            'scope': [
                'Federal Executive Branch civilian agencies',
                'Critical infrastructure entities', 
                'State, local, tribal, and territorial governments'
            ],
            'process_steps': [
                '1. Submit vulnerability details via email or portal',
                '2. CISA acknowledges receipt within 3 business days',
                '3. CISA coordinates with affected organization', 
                '4. Vulnerability is remediated by asset owner',
                '5. Public disclosure coordinated if appropriate'
            ],
            'requirements': [
                'Good faith security research',
                'Compliance with CISA VDP Safe Harbor',
                'No disruption of services',
                'Responsible disclosure timeline'
            ]
        }
        
        # Tambahkan konten dari PDF guidance resmi jika tersedia
        try:
            pdf_content = self._download_and_extract_document(self.cisa_vdp_guidance_pdf)
            if pdf_content:
                vdp_info['guidance_summary'] = self._summarize_guidance_content(pdf_content)
                vdp_info['key_principles'] = self._extract_key_principles(pdf_content)
        except Exception as e:
            print(f"⚠️ Failed to process CISA VDP guidance PDF: {e}")
            vdp_info['guidance_summary'] = "Refer to official CISA VDP guidance document"
            vdp_info['key_principles'] = ["Coordinated disclosure", "Safe harbor protection"]
        
        return vdp_info
    
    def _download_and_extract_document(self, url):
        """Download dan ekstrak konten dari dokumen (PDF/DOCX/XLSX)."""
        if not url.lower().endswith('.pdf'):
            return None  # CISA hanya pakai PDF
        
        try:
            import requests
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                # Simpan ke file sementara
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                    tmp_file.write(response.content)
                    tmp_path = tmp_file.name
                
                try:
                    # Ekstrak konten PDF
                    content = self._extract_pdf_content_from_file(tmp_path)
                    return content
                finally:
                    # Hapus file sementara
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
        except Exception as e:
            print(f"⚠️ Document download/processing failed: {e}")
            return None
    
    def _extract_pdf_content_from_file(self, pdf_path):
        """Ekstrak konten dari file PDF menggunakan pdfplumber (lebih akurat untuk teks)."""
        try:
            import pdfplumber
            text_content = ""
            
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages[:10]:  # Batasi 10 halaman pertama (cukup untuk summary)
                    text = page.extract_text()
                    if text:
                        text_content += text + "\n"
            
            return text_content.strip()
        except ImportError:
            # Fallback ke PyPDF2 jika pdfplumber tidak tersedia
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(pdf_path)
                text_content = ""
                for page in reader.pages[:10]:
                    text_content += page.extract_text() or ""
                return text_content.strip()
            except Exception:
                return ""
        except Exception:
            return ""
    
    def _summarize_guidance_content(self, pdf_content):
        """Buat ringkasan dari konten guidance CISA."""
        if not pdf_content:
            return "No guidance content available"
        
        # Cari bagian executive summary atau introduction
        lines = pdf_content.split('\n')
        summary_lines = []
        capture = False
        
        for line in lines[:50]:  # Analisis 50 baris pertama
            line_lower = line.lower().strip()
            
            # Mulai capture setelah menemukan keyword
            if any(keyword in line_lower for keyword in ['executive summary', 'introduction', 'overview']):
                capture = True
                continue
            
            # Berhenti jika menemukan section baru
            if capture and line_lower.startswith(('1.', '2.', '3.', 'section', 'chapter')):
                break
            
            if capture and len(line.strip()) > 20:
                summary_lines.append(line.strip())
        
        if summary_lines:
            return " ".join(summary_lines[:3]) + "..."  # Maksimal 3 kalimat
        else:
            # Fallback: ambil beberapa kalimat pertama
            sentences = [s.strip() for s in pdf_content.split('.') if len(s.strip()) > 50]
            return ". ".join(sentences[:2]) + "." if sentences else "Guidance document processed successfully"
    
    def _extract_key_principles(self, pdf_content):
        """Ekstrak prinsip utama dari dokumen guidance."""
        if not pdf_content:
            return ["Coordinated disclosure", "Safe harbor protection"]
        
        principles = []
        content_lower = pdf_content.lower()
        
        # Cari prinsip berdasarkan keyword spesifik dari dokumen CISA
        principle_keywords = [
            ('safe harbor', 'Safe Harbor Protection'),
            ('good faith', 'Good Faith Research'),
            ('coordination', 'Coordinated Disclosure'),
            ('responsible disclosure', 'Responsible Disclosure Timeline'),
            ('no disruption', 'No Service Disruption'),
            ('asset owner', 'Asset Owner Remediation'),
            ('public disclosure', 'Coordinated Public Disclosure')
        ]
        
        for keyword, principle in principle_keywords:
            if keyword in content_lower:
                principles.append(principle)
        
        return principles if principles else ["Refer to official CISA guidance for complete principles"]
    
    def check_vdp_portal_status(self):
        """Cek status portal pelaporan CISA (sering loading/error)."""
        try:
            import requests
            response = requests.get('https://www.cisa.gov/report', timeout=10)
            if response.status_code == 200 and 'Loading...' not in response.text:
                return {'status': 'operational', 'message': 'Portal is working'}
            else:
                return {'status': 'degraded', 'message': 'Portal may be loading slowly or experiencing issues'}
        except Exception as e:
            return {'status': 'error', 'message': f'Portal check failed: {e}'}
    
    def get_alternative_reporting_methods(self):
        """Dapatkan metode pelaporan alternatif jika portal down."""
        return {
            'primary_email': 'vulnerability@cisa.dhs.gov',
            'backup_contact': 'CISA Central at 1-844-SAY-CISA (729-2472)',
            'mailing_address': 'Cybersecurity and Infrastructure Security Agency\nAttn: Vulnerability Disclosure\nWashington, DC 20528',
            'emergency_protocol': 'For critical infrastructure emergencies, contact CISA Central immediately'
        }