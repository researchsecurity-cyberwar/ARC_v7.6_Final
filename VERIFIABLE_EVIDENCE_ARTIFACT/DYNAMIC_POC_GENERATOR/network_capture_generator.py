class NetworkCaptureGenerator:
    """
    Generate HAR/PCAP on request.
    Menghasilkan capture jaringan sesuai permintaan.
    """
    
    def __init__(self, output_dir="~/.arc/evidence"):
        self.output_dir = os.path.expanduser(output_dir)
        self.har_exporter = HARExporter(output_dir)
        self.pcap_logger = PCAPLogger(output_dir)
        self.redaction_engine = RedactionEngine()
    
    def generate_network_capture(self, capture_config: dict):
        """
        Hasilkan capture jaringan berdasarkan konfigurasi.
        """
        results = {
            'har_result': None,
            'pcap_result': None,
            'redaction_result': None
        }
        
        # Generate HAR if requested
        if capture_config.get('generate_har', False):
            har_result = self.har_exporter.export_har_from_requests(
                requests_data=capture_config['requests'],
                target_url=capture_config['target_url'],
                vulnerability_type=capture_config['vulnerability_type'],
                report_id=capture_config.get('report_id')
            )
            results['har_result'] = har_result
        
        # Generate PCAP if requested
        if capture_config.get('generate_pcap', False):
            pcap_result = self.pcap_logger.start_pcap_capture(
                target_host=capture_config.get('target_host'),
                duration=capture_config.get('duration', 60),
                report_id=capture_config.get('report_id'),
                interface=capture_config.get('interface', 'any')
            )
            results['pcap_result'] = pcap_result
        
        # Apply redaction if requested
        if capture_config.get('apply_redaction', False) and results['har_result']:
            har_path = results['har_result'].get('har_path')
            if har_path:
                redaction_result = self.redaction_engine.redact_har_file(har_path)
                results['redaction_result'] = redaction_result
        
        return results