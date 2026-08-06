import networkx as nx
from typing import Dict, List

class AttackGraphConstructor:
    """
    Dynamic graph: nodes=vulns, edges=exploitation paths.
    Membangun graf serangan dinamis dari temuan kerentanan.
    """
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.vulnerability_types = {
            'entry_point': ['xss', 'sqli', 'ssrf', 'idor', 'csrf'],
            'escalation': ['lfi', 'rce', 'jwt_flaw', 'command_injection'],
            'persistence': ['backdoor', 'webshell', 'scheduled_task'],
            'lateral_movement': ['credential_theft', 'session_hijack', 'token_impersonation'],
            'impact': ['data_exfiltration', 'account_takeover', 'system_compromise']
        }
    
    def construct_attack_graph(self, vulnerabilities: List[Dict], target_context: Dict) -> Dict:
        """
        Bangun graf serangan dari daftar kerentanan.
        """
        results = {
            'target_context': target_context,
            'vulnerabilities_analyzed': len(vulnerabilities),
            'attack_paths': [],
            'graph_metrics': {},
            'critical_paths': []
        }
        
        try:
            # Reset graf
            self.graph.clear()
            
            # Tambahkan node untuk setiap kerentanan
            for i, vuln in enumerate(vulnerabilities):
                node_id = f"vuln_{i}"
                vuln_type = vuln.get('type', 'unknown').lower()
                node_data = {
                    'vulnerability': vuln,
                    'type': vuln_type,
                    'category': self._categorize_vulnerability(vuln_type),
                    'severity': vuln.get('severity', 'medium'),
                    'exploitability': vuln.get('exploitability', 0.5)
                }
                self.graph.add_node(node_id, **node_data)
            
            # Bangun edge berdasarkan ketergantungan eksploitasi
            self._build_exploitation_edges()
            
            # Temukan jalur serangan
            attack_paths = self._find_attack_paths()
            results['attack_paths'] = attack_paths
            
            # Identifikasi jalur kritis
            critical_paths = self._identify_critical_paths(attack_paths)
            results['critical_paths'] = critical_paths
            
            # Hitung metrik graf
            results['graph_metrics'] = self._calculate_graph_metrics()
        
        except Exception as e:
            results['error'] = f'Attack graph construction failed: {str(e)}'
        
        return results
    
    def _categorize_vulnerability(self, vuln_type: str) -> str:
        """Kategorikan kerentanan berdasarkan tipe."""
        for category, types in self.vulnerability_types.items():
            if vuln_type in types:
                return category
        return 'unknown'
    
    def _build_exploitation_edges(self):
        """Bangun edge eksploitasi antar node."""
        nodes = list(self.graph.nodes(data=True))
        
        for i, (node1, data1) in enumerate(nodes):
            for j, (node2, data2) in enumerate(nodes):
                if i != j:
                    # Cek apakah node1 bisa mengarah ke node2
                    if self._can_exploit_to(node1, data1, node2, data2):
                        self.graph.add_edge(
                            node1, node2,
                            weight=self._calculate_edge_weight(data1, data2),
                            exploitation_type='chain'
                        )
    
    def _can_exploit_to(self, source_node: str, source_data: Dict, target_node: str, target_data: Dict) -> bool:
        """Cek apakah sumber bisa dieksploitasi ke target."""
        source_category = source_data.get('category', 'unknown')
        target_category = target_data.get('category', 'unknown')
        
        # Aturan chaining dasar
        chaining_rules = {
            'entry_point': ['escalation', 'impact'],
            'escalation': ['persistence', 'lateral_movement', 'impact'],
            'persistence': ['lateral_movement', 'impact'],
            'lateral_movement': ['impact'],
            'impact': []
        }
        
        return target_category in chaining_rules.get(source_category, [])
    
    def _calculate_edge_weight(self, source_data: Dict, target_data: Dict) -> float:
        """Hitung bobot edge berdasarkan kemungkinan eksploitasi."""
        source_exploit = source_data.get('exploitability', 0.5)
        target_severity = 1.0 if target_data.get('severity') == 'critical' else 0.7
        
        return source_exploit * target_severity
    
    def _find_attack_paths(self) -> List[Dict]:
        """Temukan semua jalur serangan dalam graf."""
        paths = []
        
        # Temukan node entry point dan impact
        entry_nodes = [n for n, d in self.graph.nodes(data=True) if d.get('category') == 'entry_point']
        impact_nodes = [n for n, d in self.graph.nodes(data=True) if d.get('category') == 'impact']
        
        for entry in entry_nodes:
            for impact in impact_nodes:
                try:
                    # Temukan jalur terpendek
                    path = nx.shortest_path(self.graph, source=entry, target=impact)
                    path_data = self._extract_path_data(path)
                    paths.append(path_data)
                except nx.NetworkXNoPath:
                    continue
        
        # Urutkan berdasarkan skor dampak
        paths.sort(key=lambda x: x['impact_score'], reverse=True)
        return paths[:10]  # Batasi 10 jalur teratas
    
    def _extract_path_data(self, path: List[str]) -> Dict:
        """Ekstrak data dari jalur serangan."""
        nodes_data = [self.graph.nodes[node] for node in path]
        
        total_score = sum(node.get('exploitability', 0.5) for node in nodes_data)
        impact_score = sum(1.0 for node in nodes_data if node.get('category') == 'impact')
        
        return {
            'path': path,
            'nodes': nodes_data,
            'length': len(path),
            'total_score': total_score,
            'impact_score': impact_score,
            'description': self._generate_path_description(nodes_data)
        }
    
    def _generate_path_description(self, nodes_data: List[Dict]) -> str:
        """Hasilkan deskripsi jalur serangan."""
        steps = []
        for node in nodes_data:
            vuln_type = node.get('vulnerability', {}).get('type', 'unknown')
            steps.append(vuln_type)
        
        return " → ".join(steps)
    
    def _identify_critical_paths(self, attack_paths: List[Dict]) -> List[Dict]:
        """Identifikasi jalur kritis berdasarkan skor dampak."""
        critical_paths = []
        for path in attack_paths:
            if path['impact_score'] >= 1.0 and path['total_score'] >= 2.0:
                critical_paths.append(path)
        return critical_paths
    
    def _calculate_graph_metrics(self) -> Dict:
        """Hitung metrik graf serangan."""
        if self.graph.number_of_nodes() == 0:
            return {'density': 0, 'diameter': 0, 'connectivity': 0}
        
        try:
            density = nx.density(self.graph)
            diameter = nx.diameter(self.graph) if nx.is_strongly_connected(self.graph) else float('inf')
            connectivity = nx.node_connectivity(self.graph) if self.graph.number_of_nodes() > 1 else 0
            
            return {
                'density': density,
                'diameter': diameter if diameter != float('inf') else -1,
                'connectivity': connectivity,
                'number_of_nodes': self.graph.number_of_nodes(),
                'number_of_edges': self.graph.number_of_edges()
            }
        except Exception:
            return {'density': 0, 'diameter': -1, 'connectivity': 0}