class BIRegulatoryMapper:
    """
    POJK/BI regulation mapping.
    Memetakan temuan kerentanan ke regulasi Bank Indonesia/OJK.
    """
    
    REGULATORY_MAPPING = {
        'data_breach': {
            'regulations': ['POJK No. 13/2023', 'UU PDP No. 27/2022'],
            'requirements': [
                'Pelaporan insiden dalam 72 jam',
                'Notifikasi kepada pemilik data',
                'Audit forensik wajib'
            ],
            'penalties': 'Denda hingga 2% dari pendapatan tahunan'
        },
        'transaction_abuse': {
            'regulations': ['POJK No. 12/2018', 'POJK No. 13/2023'],
            'requirements': [
                'Validasi ganda untuk transaksi besar',
                'Monitoring transaksi mencurigakan',
                'Batas transaksi harian'
            ],
            'penalties': 'Suspensi layanan pembayaran'
        },
        'authentication_bypass': {
            'regulations': ['POJK No. 13/2023', 'Peraturan BI No. 22/2020'],
            'requirements': [
                'Autentikasi dua faktor wajib',
                'Proteksi terhadap session hijacking',
                'Validasi OTP sekali pakai'
            ],
            'penalties': 'Denda hingga Rp 5 miliar'
        }
    }
    
    def map_vulnerability_to_regulation(self, vulnerability_type):
        """
        Petakan tipe kerentanan ke regulasi yang relevan.
        """
        vuln_key = vulnerability_type.lower().replace(' ', '_')
        
        for key, mapping in self.REGULATORY_MAPPING.items():
            if key in vuln_key or vuln_key in key:
                return mapping
        
        # Default mapping
        return {
            'regulations': ['POJK No. 13/2023'],
            'requirements': ['Standar keamanan informasi umum'],
            'penalties': 'Sesuai ketentuan OJK'
        }
    
    def generate_regulatory_pressure_text(self, vulnerability_data):
        """
        Hasilkan teks tekanan regulasi untuk laporan bug bounty.
        """
        regulation_info = self.map_vulnerability_to_regulation(vulnerability_data['type'])
        
        pressure_text = f"""
### Tekanan Regulasi OJK/BI

Kerentanan ini melanggar ketentuan berikut:

**Regulasi:** {', '.join(regulation_info['regulations'])}

**Kewajiban:**  
{chr(10).join([f"- {req}" for req in regulation_info['requirements']])}

**Konsekuensi:** {regulation_info['penalties']}

Mengingat tenggat waktu pelaporan insiden 72 jam menurut POJK No. 13/2023, kami sangat menyarankan penanganan segera.
"""
        return pressure_text