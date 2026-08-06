import requests
from bs4 import BeautifulSoup
import re
import tempfile
import os

class ENISAVDPScraper:
    """
    Scrap ENISA VDP guidance (bukan program VDP langsung).
    ENISA berperan sebagai koordinator, bukan penerima laporan langsung.
    Berdasarkan fakta lapangan: ENISA tidak menerima laporan kerentanan langsung dari peneliti eksternal.
    """
    
    def __init__(self, session_cookies=None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; ARC-Scanner/1.0)'
        })
        if session_cookies:
            for name, value in session_cookies.items():
                self.session.cookies.set(name, value)
        # Halaman resmi tentang Coordinated Vulnerability Disclosure
        self.enisa_cvd_url = "https://www.enisa.europa.eu/topics/vulnerability-disclosure"
        # Halaman publikasi utama
        self.enisa_publications_url = "https://www.enisa.europa.eu/publications"
    
    def get_enisa_vdp_guidance(self):
        """Dapatkan panduan VDP dari ENISA berdasarkan informasi aktual."""
        try:
            response = self.session.get(self.enisa_cvd_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                return {
                    'program_name': 'ENISA Coordinated Vulnerability Disclosure',
                    'guidance_url': self.enisa_cvd_url,
                    'role': 'EU Coordination & Best Practices',
                    'target_audience': 'National CSIRTs and EU Authorities',
                    'key_documents': self._extract_key_documents(soup),
                    'coordination_process': self._extract_coordination_info(soup),
                    'reporting_guidance': 'Direct reports should be sent to relevant national CERT or affected organization, NOT to ENISA directly',
                    'legal_framework': 'NIS2 Directive, Cybersecurity Act (2019), Cyber Resilience Act (2024)'
                }
            else:
                return self._get_fallback_guidance()
        except Exception as e:
            print(f"⚠️ ENISA CVD scraping failed: {e}")
            return self._get_fallback_guidance()
    
    def _get_fallback_guidance(self):
        """Panduan fallback berdasarkan knowledge base ENISA yang valid."""
        return {
            'program_name': 'ENISA Coordinated Vulnerability Disclosure',
            'guidance_url': 'https://www.enisa.europa.eu/topics/vulnerability-disclosure',
            'role': 'EU Cybersecurity Agency - Coordinator',
            'target_audience': 'National CSIRTs and EU Member States',
            'key_documents': [
                'Good practices guide for Coordinated Vulnerability Disclosure',
                'Vulnerability Disclosure Handbook for National Authorities',
                'ENISA NIS360 Assessment Framework'
            ],
            'coordination_process': 'ENISA coordinates the EU CSIRT Network but does not accept direct vulnerability reports from external researchers. Reports should be submitted to the relevant national CERT or the affected organization directly.',
            'reporting_guidance': 'External researchers should contact the national CERT of the affected country or the organization directly. ENISA provides coordination support between national CERTs.',
            'legal_framework': 'NIS2 Directive mandates CSIRT involvement in national CVD processes. ENISA maintains European Vulnerability Database for voluntary disclosure.'
        }
    
    def _extract_key_documents(self, soup):
        """Ekstrak dokumen kunci dari halaman CVD ENISA."""
        documents = []
        
        # Cari link ke publikasi PDF
        pdf_links = soup.find_all('a', href=re.compile(r'\.pdf$', re.IGNORECASE))
        for link in pdf_links[:3]:
            doc_text = link.get_text(strip=True)
            if doc_text and len(doc_text) > 15:
                documents.append(doc_text)
        
        # Jika tidak ada PDF, cari referensi dokumen dalam teks
        if not documents:
            page_text = soup.get_text()
            doc_patterns = [
                r'Good practices guide.*?CVD',
                r'Vulnerability Disclosure.*?Handbook',
                r'NIS360.*?Framework',
                r'European.*?Vulnerability.*?Database'
            ]
            
            for pattern in doc_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                for match in matches[:2]:
                    documents.append(match.strip())
        
        # Jamin minimal ada 1 dokumen
        if not documents:
            documents = [
                'Good practices guide for Coordinated Vulnerability Disclosure',
                'Vulnerability Disclosure Handbook for National Authorities'
            ]
        
        return documents[:3]  # Maksimal 3 dokumen
    
    def _extract_coordination_info(self, soup):
        """Ekstrak informasi proses koordinasi yang akurat."""
        coordination_info = []
        
        # Cari paragraf yang mengandung informasi koordinasi
        coord_paragraphs = soup.find_all('p')
        for p in coord_paragraphs:
            text = p.get_text()
            if any(keyword in text.lower() for keyword in ['coordinat', 'csirt', 'network', 'multi-party']):
                if len(text) > 80:  # Filter teks pendek
                    coordination_info.append(text.strip())
                    break  # Ambil paragraf pertama yang relevan
        
        # Jika tidak ditemukan, gunakan informasi dari knowledge base
        if not coordination_info:
            coordination_info = [
                "ENISA coordinates the EU CSIRT Network but does not accept direct vulnerability reports from external researchers. "
                "The agency supports CSIRTs designated as coordinators to cooperate within the network when vulnerabilities have "
                "potentially significant impact on entities in more than one Member State."
            ]
        
        return coordination_info[0]
    
    def _download_and_extract_document(self, url):
        """Download dan ekstrak konten dari dokumen PDF ENISA."""
        if not url.lower().endswith('.pdf'):
            return None
        
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                    tmp_file.write(response.content)
                    tmp_path = tmp_file.name
                
                try:
                    # Gunakan pdfplumber untuk ekstraksi teks yang lebih akurat
                    import pdfplumber
                    with pdfplumber.open(tmp_path) as pdf:
                        text = ""
                        for page in pdf.pages[:5]:  # Maksimal 5 halaman pertama
                            text += (page.extract_text() or "") + "\n"
                    return text.strip()
                finally:
                    # Hapus file sementara
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
        except Exception as e:
            print(f"⚠️ Failed to extract PDF content from {url}: {e}")
        
        return None
    
    def analyze_enisa_publications(self):
        """Analisis publikasi terbaru ENISA untuk panduan VDP."""
        try:
            response = self.session.get(self.enisa_publications_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                publications = []
                
                # Cari publikasi terkait VDP/CVD
                pub_items = soup.find_all(class_=re.compile(r'.*publication.*|.*document.*'))
                for item in pub_items[:5]:
                    title_elem = item.find(['h3', 'h4'])
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        if any(keyword in title.lower() for keyword in ['vulnerability', 'cvd', 'disclosure', 'nist', 'security']):
                            link_elem = item.find('a', href=True)
                            pub_url = link_elem['href'] if link_elem else ''
                            
                            # Jika link relatif, buat absolut
                            if pub_url and pub_url.startswith('/'):
                                pub_url = f"https://www.enisa.europa.eu{pub_url}"
                            
                            publications.append({
                                'title': title,
                                'url': pub_url,
                                'is_pdf': pub_url.lower().endswith('.pdf') if pub_url else False
                            })
                
                return publications
        except Exception as e:
            print(f"⚠️ ENISA publications analysis failed: {e}")
        
        return []