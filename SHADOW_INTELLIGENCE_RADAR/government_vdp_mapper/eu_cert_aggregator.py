import requests
from bs4 import BeautifulSoup
import tempfile
import os
import re

# Import parser dokumen (akan di-handle oleh ARC environment)
try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

class EUCERTAggregator:
    """
    National CERT vulnerability pages.
    Mengumpulkan halaman kerentanan dan dokumen dari CERT nasional Eropa.
    Mendukung ekstraksi konten dari PDF dan DOCX untuk analisis mendalam.
    """
    
    def __init__(self):
        self.eu_certs = {
            'enisa': 'https://www.enisa.europa.eu',
            'cert_eu': 'https://cert.europa.eu',
            'germany': 'https://www.bsi.bund.de/EN/Home/home_node.html',
            'france': 'https://www.cert.ssi.gouv.fr',
            'netherlands': 'https://www.ncsc.nl'
        }
    
    def get_eu_vdp_pages(self):
        """Dapatkan halaman VDP dan dokumen terkait dari CERT Eropa."""
        vdp_pages = []
        
        for country, cert_url in self.eu_certs.items():
            try:
                response = requests.get(cert_url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Temukan link VDP utama
                    vdp_link = self._find_vdp_link(soup, cert_url)
                    
                    # Temukan dokumen PDF/DOCX terkait
                    document_links = self._find_document_links(soup, cert_url)
                    
                    vdp_info = {
                        'country': country,
                        'cert_url': cert_url,
                        'vdp_url': vdp_link,
                        'documents': document_links
                    }
                    
                    # Jika ada dokumen, ekstrak kontennya
                    if document_links and (PDF_AVAILABLE or DOCX_AVAILABLE):
                        vdp_info['document_content'] = self._extract_documents_content(document_links)
                    
                    vdp_pages.append(vdp_info)
                    
            except Exception as e:
                print(f"⚠️ Failed to check {country} CERT: {e}")
                continue
        
        return vdp_pages
    
    def _find_vdp_link(self, soup, base_url):
        """Temukan link VDP dalam halaman CERT."""
        vdp_keywords = ['vulnerability', 'disclosure', 'security', 'report', 'kerentanan']
        
        links = soup.find_all('a', href=True)
        for link in links:
            link_text = link.get_text().lower()
            if any(keyword in link_text for keyword in vdp_keywords):
                href = link['href']
                # Handle relative URLs
                if href.startswith('/'):
                    return f"{base_url.rstrip('/')}{href}"
                elif href.startswith('http'):
                    return href
        
        # Fallback: Gunakan URL utama jika tidak ada link spesifik VDP
        return base_url
    
    def _find_document_links(self, soup, base_url):
        """Temukan tautan ke dokumen PDF, DOCX, atau XLSX."""
        document_links = []
        document_extensions = ['.pdf', '.docx', '.xlsx', '.doc', '.xls']
        
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href'].lower()
            if any(href.endswith(ext) for ext in document_extensions):
                if href.startswith('/'):
                    full_url = f"{base_url.rstrip('/')}{href}"
                elif href.startswith('http'):
                    full_url = href
                else:
                    continue
                
                document_links.append({
                    'url': full日消息,
                    'title': link.get_text(strip=True),
                    'type': self._get_document_type(href)
                })
        
        return document_links[:5]  # Batasi 5 dokumen pertama
    
    def _get_document_type(self, url):
        """Tentukan jenis dokumen berdasarkan ekstensi."""
        if url.endswith('.pdf'):
            return 'pdf'
        elif url.endswith(('.docx', '.doc')):
            return 'docx'
        elif url.endswith(('.xlsx', '.xls')):
            return 'xlsx'
        else:
            return 'unknown'
    
    def _extract_documents_content(self, document_links):
        """Ekstrak konten dari daftar dokumen."""
        contents = []
        
        for doc in document_links:
            try:
                content = self._download_and_extract_document(doc['url'])
                if content:
                    contents.append({
                        'url': doc['url'],
                        'type': doc['type'],
                        'content': content[:5000]  # Batasi 5000 karakter untuk efisiensi
                    })
            except Exception as e:
                print(f"⚠️ Failed to extract {doc['url']}: {e}")
                continue
        
        return contents
    
    def _download_and_extract_document(self, url):
        """Download dan ekstrak konten dari dokumen."""
        if not url:
            return None
        
        # Download ke file sementara
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            try:
                response = requests.get(url, timeout=30)
                if response.status_code != 200:
                    return None
                
                tmp_file.write(response.content)
                tmp_path = tmp_file.name
                
                # Ekstrak berdasarkan jenis dokumen
                if url.lower().endswith('.pdf') and PDF_AVAILABLE:
                    return self._extract_pdf_content(tmp_path)
                elif url.lower().endswith(('.docx', '.doc')) and DOCX_AVAILABLE:
                    return self._extract_docx_content(tmp_path)
                else:
                    return None
                    
            finally:
                # Hapus file sementara
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
    
    def _extract_pdf_content(self, pdf_path):
        """Ekstrak teks dari file PDF menggunakan pdfplumber."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages[:10]:  # Batasi 10 halaman pertama
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text.strip()
        except Exception as e:
            print(f"⚠️ PDF extraction failed: {e}")
            return None
    
    def _extract_docx_content(self, docx_path):
        """Ekstrak teks dari file DOCX."""
        try:
            doc = docx.Document(docx_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text.strip()
        except Exception as e:
            print(f"⚠️ DOCX extraction failed: {e}")
            return None