import requests
from bs4 import BeautifulSoup
import re
import tempfile
import os

class ASEANVDPScraper:
    """
    Scrap VDP ASEAN (MY/TH/VN/SG).
    Mengakses program VDP negara ASEAN melalui sesi yang valid.
    Menggunakan URL yang telah diverifikasi aktif per Juli 2026.
    """
    
    def __init__(self, session_cookies=None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; ARC-Scanner/1.0)'
        })
        if session_cookies:
            for name, value in session_cookies.items():
                self.session.cookies.set(name, value)
        
        # URL yang telah diverifikasi AKTIF (Juli 2026)
        self.asean_vdp_urls = {
            'malaysia': 'https://www.cybersecurity.my/',
            'thailand': 'https://www.mcert.or.th/',
            'vietnam': 'https://ais.gov.vn/',
            'singapore': 'https://www.csa.gov.sg/'
        }
    
    def scrape_all_asean_vdp(self):
        """Scrap semua program VDP ASEAN."""
        asean_programs = {}
        
        for country, url in self.asean_vdp_urls.items():
            try:
                program_info = self._scrape_single_asean_vdp(url, country)
                if program_info:
                    asean_programs[country] = program_info
            except Exception as e:
                print(f"⚠️ Failed to scrape {country} VDP ({url}): {e}")
                continue
        
        return asean_programs
    
    def _scrape_single_asean_vdp(self, url, country):
        """Scrap satu program VDP ASEAN."""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Cek apakah ada link ke dokumen PDF/DOCX
                document_links = self._find_document_links(soup, url)
                document_content = ""
                
                if document_links:
                    for doc_url in document_links[:2]:  # Maksimal 2 dokumen
                        content = self._download_and_extract_document(doc_url)
                        if content:
                            document_content += f"\n\n=== DOCUMENT CONTENT ===\n{content}"
                
                return {
                    'country': country.upper(),
                    'vdp_url': url,
                    'contact_info': self._extract_contact_info(soup, country),
                    'reporting_process': self._extract_reporting_process(soup, document_content),
                    'local_requirements': self._extract_local_requirements(soup, country, document_content),
                    'document_sources': document_links[:2]
                }
        except Exception as e:
            print(f"⚠️ Single ASEAN VDP scrape failed for {country}: {e}")
        
        return None
    
    def _find_document_links(self, soup, base_url):
        """Temukan link ke dokumen PDF/DOCX di halaman."""
        document_links = []
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            if href.lower().endswith(('.pdf', '.docx', '.doc')):
                # Handle relative URLs
                if href.startswith('/'):
                    full_url = f"{base_url.rstrip('/')}{href}"
                elif href.startswith('http'):
                    full_url = href
                else:
                    continue
                
                document_links.append(full_url)
        
        return document_links
    
    def _download_and_extract_document(self, doc_url):
        """Download dan ekstrak konten dari dokumen dengan cleanup otomatis."""
        try:
            # Download ke file sementara
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                response = self.session.get(doc_url, timeout=30)
                tmp_file.write(response.content)
                tmp_path = tmp_file.name
            
            # Ekstrak berdasarkan format
            if doc_url.lower().endswith('.pdf'):
                content = self._extract_pdf_content(tmp_path)
            elif doc_url.lower().endswith(('.docx', '.doc')):
                content = self._extract_docx_content(tmp_path)
            else:
                content = ""
            
            # Hapus file sementara
            os.unlink(tmp_path)
            return content
            
        except Exception as e:
            print(f"⚠️ Document extraction failed for {doc_url}: {e}")
            # Pastikan file sementara dihapus meski error
            try:
                os.unlink(tmp_path)
            except:
                pass
            return ""
    
    def _extract_pdf_content(self, pdf_path):
        """Ekstrak konten PDF menggunakan pdfplumber (lebih akurat untuk teks)."""
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages[:10]:  # Maksimal 10 halaman
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except ImportError:
            # Fallback ke PyPDF2 jika pdfplumber tidak tersedia
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(pdf_path)
                text = ""
                for page in reader.pages[:10]:
                    text += page.extract_text() or ""
                return text.strip()
            except:
                return ""
        except Exception:
            return ""
    
    def _extract_docx_content(self, docx_path):
        """Ekstrak konten DOCX."""
        try:
            from docx import Document
            doc = Document(docx_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text.strip()
        except Exception:
            return ""
    
    def _extract_contact_info(self, soup, country):
        """Ekstrak informasi kontak berdasarkan negara."""
        page_text = soup.get_text()
        
        # Pola email berdasarkan data aktual Juli 2026
        email_patterns = {
            'malaysia': r'\b[A-Za-z0-9._%+-]+@cybersecurity\.my\b',
            'thailand': r'\b[A-Za-z0-9._%+-]+@(mcert\.or\.th|etda\.or\.th)\b',
            'vietnam': r'\b[A-Za-z0-9._%+-]+@ais\.gov\.vn\b',
            'singapore': r'\b(vulnerability|singcert)@csa\.gov\.sg\b'
        }
        
        pattern = email_patterns.get(country, r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        emails = re.findall(pattern, page_text)
        return emails[0] if emails else f'No contact found for {country}'
    
    def _extract_reporting_process(self, soup, document_content=""):
        """Ekstrak proses pelaporan dari HTML + konten dokumen."""
        process_steps = []
        
        # Dari halaman HTML
        step_indicators = soup.find_all(
            ['li', 'p', 'div'], 
            string=re.compile(r'Step|Proses|ขั้นตอน|Quy trình|Cách báo cáo|Report|Laporkan', re.IGNORECASE)
        )
        
        for step in step_indicators[:5]:
            step_text = step.get_text(strip=True)
            if len(step_text) > 20 and not any(skip in step_text for skip in ['Copyright', '©', 'All rights']):
                process_steps.append(step_text)
        
        # Dari konten dokumen (jika ada)
        if document_content:
            doc_steps = re.findall(r'(?:Step|Langkah|ขั้นที่|Bước)\s*\d+[:.\-]\s*.*', document_content, re.IGNORECASE)
            for step in doc_steps[:3]:
                if len(step) > 20:
                    process_steps.append(step.strip())
        
        return process_steps if process_steps else ['Visit official VDP portal for reporting instructions']
    
    def _extract_local_requirements(self, soup, country, document_content=""):
        """Ekstrak persyaratan lokal dari HTML + dokumen."""
        requirements = []
        combined_text = soup.get_text() + document_content
        
        # Persyaratan berdasarkan regulasi aktual per Juli 2026
        local_requirements = {
            'malaysia': [
                'Akta Perlindungan Data Peribadi 2010 (PDPA)',
                'MS ISO/IEC 29147:2018 vulnerability disclosure'
            ],
            'thailand': [
                'พระราชบัญญัติคุ้มครองข้อมูลส่วนบุคคล พ.ศ. 2562 (PDPA Thailand)',
                'ThaiCERT coordination required'
            ],
            'vietnam': [
                'Luật An toàn thông tin mạng số 86/2015/QH13',
                'Nghị định 53/2022/NĐ-CP quy định chi tiết'
            ],
            'singapore': [
                'Singapore Cybersecurity Act 2018',
                'Personal Data Protection Act 2012 (PDPA)',
                'SingCERT coordination mandatory'
            ]
        }
        
        country_reqs = local_requirements.get(country, [])
        for req in country_reqs:
            if req.split()[0].lower() in combined_text.lower():  # Cek keyword pertama
                requirements.append(req)
        
        return requirements if requirements else ['Follow international vulnerability disclosure standards (ISO/IEC 29147)']