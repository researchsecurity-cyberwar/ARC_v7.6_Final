class ScriptReproducer:
    """
    Generate reproduction scripts.
    Menghasilkan skrip reproduksi sesuai permintaan.
    """
    
    def __init__(self, output_dir="~/.arc/evidence"):
        self.output_dir = os.path.expanduser(output_dir)
        self.repro_builder = ReproducibilityBuilder(output_dir)
    
    def generate_reproduction_script(self, repro_config: dict):
        """
        Hasilkan skrip reproduksi berdasarkan konfigurasi.
        """
        return self.repro_builder.build_reproducibility_package(
            vulnerability_data=repro_config['vulnerability_data'],
            exploit_payload=repro_config['exploit_payload'],
            report_id=repro_config.get('report_id')
        )