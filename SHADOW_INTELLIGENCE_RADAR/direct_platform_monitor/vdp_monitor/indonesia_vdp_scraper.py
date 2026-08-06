import requests
from bs4 import BeautifulSoup
import re
import tempfile
import os

class IndonesiaVDPScraper:
    """
    Ambil informasi VDP Indonesia berdasarkan fakta lapangan yang diverifikasi.
    Menggunakan email resmi yang terbukti ada di sumber publik BSSN dan OJK.
    Mendukung parsing dokumen PDF/DOCX dari situs .go.id.
    """
    
    # Data statis berdasarkan sumber resmi yang diverifikasi
    STATIC_VDP_INFO = [
        {
            'agency': 'Badan Siber dan Sandi Negara (BSSN)',
            'contact_email': 'govcsirt@bssn.go.id',
            'alternative_email': 'bantuan70@bssn.go.id',
            'vdp_url': 'https://www.bssn.go.id',
            'scope': [
                'Sistem pemerintah Indonesia',
                'Critical infrastructure nasional', 
                'Layanan digital pemerintah'
            ],
            'requirements': [
                'Pelaporan insiden keamanan siber',
                'Compliance dengan UU ITE No. 11/2008',
                'Good faith security research'
            ],
            'reporting_method': 'Email langsung ke govcsirt@bssn.go.id',
            'source': 'static_verified'
        },
        {
            'agency': 'Otoritas Jasa Keuangan (OJK)',
            'contact_email': 'csirt@ojk.go.id',
            'vdp_url': 'https://www.ojk.go.id',
            'scope': [
                'Lembaga keuangan terdaftar OJK',
                'Fintech dan penyelenggara IKNB',
                'Sistem pembayaran digital'
            ],
            'requirements': [
                'Valid proof of concept',
                'Responsible disclosure timeline',
                'Compliance dengan POJK No. 13/2023'
            ],
            'reporting_method': 'Email ke csirt@ojk.go.id',
            'source': 'static_verified'
        }
    ]
    
    def __init__(self, session_cookies=None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; ARC-Scanner/1.0)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })
        if session_cookies:
            for name, value in session_cookies.items():
                self.session.cookies.set(name, value)
    
    def get_indonesia_vdp_info(self):
        """
        Dapatkan info VDP Indonesia lengkap - gabungkan data statis dengan scraping dinamis.
        """
        vdp_programs = []
        
        # Tambahkan data statis yang sudah diverifikasi
        vdp_programs.extend(self.STATIC_VDP_INFO)
        
        # Coba scrape informasi dinamis dari situs .go.id
        try:
            dynamic_programs = self._scrape_dynamic_vdp_info()
            vdp_programs.extend(dynamic_programs)
        except Exception as e:
            print(f"⚠️ Dynamic VDP scraping failed, using static data only: {e}")
        
        return vdp_programs
    
    def _scrape_dynamic_vdp_info(self):
        """
        Scrape informasi VDP dinamis dari situs .go.id.
        """
        dynamic_programs = []
        vdp_urls = [
            "https://www.bssn.go.id/",
            "https://www.ojk.go.id/id/",
            "https://www.komdigi.go.id/"
        ]
        
        for url in vdp_urls:
            try:
                program_info = self._scrape_single_vdp_page(url)
                if program_info:
                    dynamic_programs.append(program_info)
            except Exception as e:
                print(f"⚠️ Failed to scrape {url}: {e}")
                continue
        
        return dynamic_programs
    
    def _scrape_single_vdp_page(self, url):
        """
        Scrape satu halaman VDP dan ekstrak informasinya.
        """
        response = self.session.get(url, timeout=10)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        agency_name = self._extract_agency_name_from_url(url)
        
        # Deteksi dan proses dokumen (PDF/DOCX)
        document_links = self._find_document_links(soup, url)
        extracted_content = ""
        
        for doc_link in document_links[:2]:  # Maksimal 2 dokumen
            try:
                doc_content = self._download_and_extract_document(doc_link)
                if doc_content:
                    extracted_content += f"\n\n[DOKUMEN: {doc_link}]\n{doc_content}"
            except Exception as e:
                print(f"⚠️ Document extraction failed for {doc_link}: {e}")
                continue
        
        return {
            'agency': agency_name,
            'contact_email': self._extract_contact_email(soup, extracted_content),
            'vdp_url': url,
            'scope': self._extract_scope_info(soup, extracted_content),
            'requirements': self._extract_requirements(soup, extracted_content),
            'reporting_method': self._extract_reporting_method(soup, extracted_content),
            'source': 'dynamic_scraped'
        }
    
    def _extract_agency_name_from_url(self, url):
        """Ekstrak nama agensi dari URL."""
        domain_map = {
            'bssn.go.id': 'Badan Siber dan Sandi Negara (BSSN)',
            'ojk.go.id': 'Otoritas Jasa Keuangan (OJK)',
            'kominfo.go.id': 'Kementerian Komunikasi dan Informatika'
        }
        for domain, name in domain_map.items():
            if domain in url:
                return name
        return url.split('/')[2]
    
    def _find_document_links(self, soup, base_url):
        """Temukan link ke dokumen PDF/DOCX di halaman."""
        document_links = []
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            if any(href.lower().endswith(ext) for ext in ['.pdf', '.docx', '.doc']):
                # Handle relative URLs
                if href.startswith('/'):
                    full_url = f"{base_url.rstrip('/')}{href}"
                elif href.startswith('http'):
                    full_url = href
                else:
                    from urllib.parse import urljoin
                    full_url = urljoin(base_url, href)
                
                document_links.append(full_url)
        
        return document_links[:3]  # Maksimal 3 dokumen
    
    def _download_and_extract_document(self, document_url):
        """
        Download dan ekstrak konten dari dokumen (PDF/DOCX).
        """
        # Download ke file sementara
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            response = self.session.get(document_url, timeout=15)
            tmp_file.write(response.content)
            tmp_path = tmp_file.name
        
        try:
            if document_url.lower().endswith('.pdf'):
                return self._extract_pdf_content(tmp_path)
            elif document_url.lower().endswith(('.docx', '.doc')):
                return self._extract_docx_content(tmp_path)
            else:
                return None
        finally:
            # Hapus file sementara
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def _extract_pdf_content(self, pdf_path):
        """Ekstrak teks dari file PDF."""
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages[:5]:  # Maksimal 5 halaman pertama
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip() if text else None
        except Exception as e:
            print(f"⚠️ PDF extraction failed: {e}")
            return None
    
    def _extract_docx_content(self, docx_path):
        """Ekstrak teks dari file DOCX."""
        try:
            from docx import Document
            doc = Document(docx_path)
            text = "\n".join([para.text for para in doc.paragraphs[:50]])  # Maksimal 50 paragraf
            return text.strip() if text else None
        except Exception as e:
            print(f"⚠️ DOCX extraction failed: {e}")
            return None
    
    def _extract_contact_email(self, soup, extracted_content=""):
        """Ekstrak email kontak dari HTML dan konten dokumen."""
        # Cari di HTML
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        html_emails = re.findall(email_pattern, soup.get_text())
        
        # Cari di konten dokumen
        doc_emails = re.findall(email_pattern, extracted_content) if extracted_content else []
        
        all_emails = html_emails + doc_emails
        
        # Prioritaskan email yang mengandung kata kunci VDP/security
        for email in all_emails:
            if any(keyword in email.lower() for keyword in ['security', 'vdp', 'csirt', 'kerentanan']):
                return email
        
        # Kembalikan email pertama jika tidak ada yang spesifik
        return all_emails[0] if all_emails else ''
    
    def _extract_scope_info(self, soup, extracted_content=""):
        """Ekstrak informasi scope dari HTML dan dokumen."""
        scope_keywords = ['lingkup', 'scope', 'cakupan', 'domain', 'sistem', 'layanan']
        scope_info = []
        
        # Cari di HTML
        for keyword in scope_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            for elem in elements[:2]:
                parent = elem.parent
                if parent:
                    text = parent.get_text(strip=True)
                    if len(text) > 20 and text not in scope_info:
                        scope_info.append(text)
        
        # Cari di konten dokumen
        if extracted_content:
            lines = extracted_content.split('\n')
            for line in lines[:10]:  # 10 baris pertama
                if any(keyword in line.lower() for keyword in scope_keywords) and len(line) > 30:
                    if line.strip() not in scope_info:
                        scope_info.append(line.strip())
        
        return scope_info[:3]  # Maksimal 3 poin scope
    
    def _extract_requirements(self, soup, extracted_content=""):
        """Ekstrak persyaratan pelaporan."""
        req_keywords = ['persyaratan', 'requirement', 'syarat', 'ketentuan', 'aturan']
        requirements = []
        
        # Cari di HTML
        for keyword in req_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            for elem in elements[:2]:
                parent = elem.parent
                if parent:
                    text = parent.get_text(strip=True)
                    if len(text) > 30 and text not in requirements:
                        requirements.append(text)
        
        # Cari di konten dokumen
        if extracted_content:
            lines = extracted_content.split('\n')
            for line in lines[:15]:
                if any(keyword in line.lower() for keyword in req_keywords) and len(line) > 40:
                    if line.strip() not in requirements:
                        requirements.append(line.strip())
        
        return requirements[:5]  # Maksimal 5 persyaratan
    
    def _extract_reporting_method(self, soup, extracted_content=""):
        """Ekstrak metode pelaporan."""
        method_indicators = ['lapor', 'report', 'email', 'formulir', 'portal', 'kontak']
        methods = []
        
        # Cari di HTML
        for indicator in method_indicators:
            elements = soup.find_all(text=re.compile(indicator, re.IGNORECASE))
            for elem in elements[:1]:
                parent = elem.parent
                if parent:
                    text = parent.get_text(strip=True)
                    if len(text) > 20 and text not in methods:
                        methods.append(text)
        
        # Gunakan metode default jika tidak ditemukan
        if not methods:
            return "Email ke alamat kontak resmi"
        
        return methods[0]