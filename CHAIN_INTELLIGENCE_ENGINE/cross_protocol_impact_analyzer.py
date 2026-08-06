class CrossProtocolImpactAnalyzer:
    """
    Analyze cross-protocol dependencies.
    Menganalisis ketergantungan dan dampak lintas protokol.
    """
    
    def __init__(self):
        self.protocol_dependencies = {
            'http': ['dns', 'tls', 'tcp'],
            'dns': ['udp', 'tcp'],
            'tls': ['tcp', 'x509'],
            'smtp': ['tcp', 'dns'],
            'ssh': ['tcp', 'rsa'],
            'ftp': ['tcp', 'ssl'],
            'websocket': ['http', 'tcp', 'tls'],
            'grpc': ['http2', 'tls', 'protobuf']
        }
        
        self.protocol_vulnerabilities = {
            'dns': ['cache_poisoning', 'amplification_attack', 'zone_transfer'],
            'tls': ['heartbleed', 'poodle', 'beast', 'weak_ciphers'],
            'http': ['header_injection', 'response_splitting', 'host_header_attack'],
            'smtp': ['open_relay', 'email_injection', 'spoofing'],
            'ssh': ['weak_keys', 'brute_force', 'protocol_downgrade']
        }
    
    def analyze_cross_protocol_impact(self, primary_vulnerability: Dict, target_protocols: List[str]) -> Dict:
        """
        Analisis dampak lintas protokol dari kerentanan utama.
        """
        results = {
            'primary_vulnerability': primary_vulnerability,
            'target_protocols': target_protocols,
            'cross_protocol_chains': [],
            'dependency_map': {},
            'risk_amplification': 0.0,
            'mitigation_strategies': []
        }
        
        try:
            # Bangun peta ketergantungan
            dependency_map = self._build_dependency_map(target_protocols)
            results['dependency_map'] = dependency_map
            
            # Temukan rantai lintas protokol
            cross_chains = self._find_cross_protocol_chains(primary_vulnerability, dependency_map)
            results['cross_protocol_chains'] = cross_chains
            
            # Hitung amplifikasi risiko
            results['risk_amplification'] = self._calculate_risk_amplification(cross_chains)
            
            # Buat strategi mitigasi
            results['mitigation_strategies'] = self._generate_mitigation_strategies(cross_chains)
        
        except Exception as e:
            results['error'] = f'Cross-protocol analysis failed: {str(e)}'
        
        return results
    
    def _build_dependency_map(self, protocols: List[str]) -> Dict:
        """Bangun peta ketergantungan protokol."""
        dependency_map = {}
        
        for protocol in protocols:
            dependencies = self.protocol_dependencies.get(protocol, [])
            dependency_map[protocol] = dependencies
            
            # Rekursif tambahkan dependensi dependensi
            for dep in dependencies:
                sub_deps = self.protocol_dependencies.get(dep, [])
                dependency_map[dep] = sub_deps
        
        return dependency_map
    
    def _find_cross_protocol_chains(self, primary_vuln: Dict, dependency_map: Dict) -> List[Dict]:
        """Temukan rantai lintas protokol."""
        chains = []
        primary_protocol = primary_vuln.get('protocol', 'http')
        
        # Cari kerentanan di protokol dependen
        for protocol, dependencies in dependency_map.items():
            if protocol == primary_protocol:
                for dep_protocol in dependencies:
                    dep_vulns = self.protocol_vulnerabilities.get(dep_protocol, [])
                    if dep_vulns:
                        chains.append({
                            'source_protocol': primary_protocol,
                            'target_protocol': dep_protocol,
                            'vulnerabilities': dep_vulns,
                            'impact_description': f'{primary_protocol.upper()} vulnerability can lead to {dep_protocol.upper()} exploitation',
                            'severity': 'HIGH' if dep_protocol in ['tls', 'dns'] else 'MEDIUM'
                        })
        
        return chains
    
    def _calculate_risk_amplification(self, cross_chains: List[Dict]) -> float:
        """Hitung amplifikasi risiko dari rantai lintas protokol."""
        if not cross_chains:
            return 1.0
        
        high_severity_count = sum(1 for chain in cross_chains if chain['severity'] == 'HIGH')
        total_chains = len(cross_chains)
        
        # Amplifikasi berdasarkan jumlah dan tingkat keparahan rantai
        amplification_factor = 1.0 + (high_severity_count * 0.5) + (total_chains * 0.2)
        return min(amplification_factor, 3.0)  # Maks 3x amplifikasi
    
    def _generate_mitigation_strategies(self, cross_chains: List[Dict]) -> List[str]:
        """Hasilkan strategi mitigasi untuk rantai lintas protokol."""
        strategies = set()
        
        for chain in cross_chains:
            target_protocol = chain['target_protocol']
            
            if target_protocol == 'tls':
                strategies.add('Implement strong TLS configuration with modern cipher suites')
            elif target_protocol == 'dns':
                strategies.add('Deploy DNSSEC and secure DNS resolver configuration')
            elif target_protocol == 'http':
                strategies.add('Implement proper HTTP security headers and input validation')
            elif target_protocol == 'smtp':
                strategies.add('Configure SMTP authentication and prevent open relay')
            elif target_protocol == 'ssh':
                strategies.add('Use strong SSH key management and disable weak algorithms')
        
        if not strategies:
            strategies.add('Implement defense in depth across all protocol layers')
        
        strategies.add('Monitor and log traffic at all protocol layers')
        strategies.add('Regularly update and patch all protocol implementations')
        
        return list(strategies)