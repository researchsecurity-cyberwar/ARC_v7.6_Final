import json
from collections import defaultdict, deque

class TechniqueKnowledgeGraph:
    """
    Build cross-platform technique graph.
    Membangun graf pengetahuan teknik lintas platform.
    """
    
    def __init__(self, graph_dir="~/.arc/knowledge_graph"):
        self.graph_dir = os.path.expanduser(graph_dir)
        os.makedirs(self.graph_dir, exist_ok=True)
        self.graph_file = os.path.join(self.graph_dir, "technique_graph.json")
        self.graph = self._load_graph()
    
    def build_technique_graph(self, unified_patterns: list, source_data: dict):
        """
        Bangun atau perbarui graf teknik berdasarkan pola terpadu.
        """
        results = {
            'unified_patterns': unified_patterns,
            'source_data': source_data,
            'graph_updated': False,
            'new_techniques_added': 0,
            'relationships_created': 0
        }
        
        try:
            new_techniques = 0
            relationships = 0
            
            # Tambahkan teknik baru ke graf
            for pattern in unified_patterns:
                if pattern not in self.graph['nodes']:
                    self.graph['nodes'][pattern] = {
                        'id': pattern,
                        'type': 'technique',
                        'occurrences': 1,
                        'platforms': [source_data.get('platform', 'unknown')],
                        'related_techniques': [],
                        'success_rate': source_data.get('success_rate', 0.5)
                    }
                    new_techniques += 1
                else:
                    # Perbarui node yang ada
                    self.graph['nodes'][pattern]['occurrences'] += 1
                    platform = source_data.get('platform', 'unknown')
                    if platform not in self.graph['nodes'][pattern]['platforms']:
                        self.graph['nodes'][pattern]['platforms'].append(platform)
                    
                    # Perbarui tingkat keberhasilan
                    current_rate = self.graph['nodes'][pattern]['success_rate']
                    new_rate = source_data.get('success_rate', 0.5)
                    self.graph['nodes'][pattern]['success_rate'] = (current_rate + new_rate) / 2
            
            # Buat hubungan antar teknik
            for i, pattern1 in enumerate(unified_patterns):
                for j, pattern2 in enumerate(unified_patterns):
                    if i != j:
                        if pattern2 not in self.graph['nodes'][pattern1]['related_techniques']:
                            self.graph['nodes'][pattern1]['related_techniques'].append(pattern2)
                            relationships += 1
            
            # Simpan graf yang diperbarui
            self._save_graph()
            
            results.update({
                'graph_updated': True,
                'new_techniques_added': new_techniques,
                'relationships_created': relationships
            })
        
        except Exception as e:
            results['error'] = f'Technique graph building failed: {str(e)}'
        
        return results
    
    def find_optimal_technique_path(self, target_category: str, constraints: dict = None):
        """
        Temukan jalur teknik optimal untuk kategori target.
        """
        results = {
            'target_category': target_category,
            'constraints': constraints,
            'optimal_path': [],
            'confidence_score': 0.0,
            'path_found': False
        }
        
        try:
            if target_category not in self.graph['nodes']:
                results['error'] = f'Target category {target_category} not found in knowledge graph'
                return results
            
            # Gunakan BFS untuk menemukan jalur optimal
            optimal_path = self._find_bfs_path(target_category, constraints)
            
            if optimal_path:
                results.update({
                    'optimal_path': optimal_path,
                    'confidence_score': self._calculate_path_confidence(optimal_path),
                    'path_found': True
                })
            else:
                results['error'] = 'No optimal path found with given constraints'
        
        except Exception as e:
            results['error'] = f'Optimal path finding failed: {str(e)}'
        
        return results
    
    def _load_graph(self):
        """Muat graf dari file atau buat baru."""
        if os.path.exists(self.graph_file):
            try:
                with open(self.graph_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'nodes': {},
            'metadata': {
                'created_at': time.time(),
                'last_updated': time.time(),
                'total_techniques': 0,
                'total_relationships': 0
            }
        }
    
    def _save_graph(self):
        """Simpan graf ke file."""
        self.graph['metadata']['last_updated'] = time.time()
        self.graph['metadata']['total_techniques'] = len(self.graph['nodes'])
        total_relationships = sum(len(node['related_techniques']) for node in self.graph['nodes'].values())
        self.graph['metadata']['total_relationships'] = total_relationships
        
        with open(self.graph_file, 'w') as f:
            json.dump(self.graph, f, indent=2)
    
    def _find_bfs_path(self, target: str, constraints: dict = None) -> list:
        """Temukan jalur menggunakan BFS dengan batasan."""
        if not constraints:
            constraints = {}
        
        max_depth = constraints.get('max_depth', 3)
        min_success_rate = constraints.get('min_success_rate', 0.3)
        required_platforms = constraints.get('platforms', [])
        
        # Mulai BFS dari teknik dengan tingkat keberhasilan tertinggi
        start_nodes = sorted(
            [(node_id, node_data['success_rate']) for node_id, node_data in self.graph['nodes'].items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        for start_node, _ in start_nodes[:5]:  # Coba 5 node teratas
            queue = deque([(start_node, [start_node], 0)])
            visited = set([start_node])
            
            while queue:
                current, path, depth = queue.popleft()
                
                if depth >= max_depth:
                    continue
                
                if current == target:
                    return path
                
                # Periksa tetangga
                neighbors = self.graph['nodes'][current]['related_techniques']
                for neighbor in neighbors:
                    if neighbor not in visited:
                        neighbor_data = self.graph['nodes'][neighbor]
                        
                        # Periksa batasan
                        if neighbor_data['success_rate'] < min_success_rate:
                            continue
                        
                        if required_platforms and not any(p in neighbor_data['platforms'] for p in required_platforms):
                            continue
                        
                        visited.add(neighbor)
                        queue.append((neighbor, path + [neighbor], depth + 1))
        
        return []
    
    def _calculate_path_confidence(self, path: list) -> float:
        """Hitung kepercayaan jalur berdasarkan node individu."""
        if not path:
            return 0.0
        
        # Rata-rata tingkat keberhasilan dikalikan dengan panjang jalur
        avg_success = sum(self.graph['nodes'][node]['success_rate'] for node in path) / len(path)
        length_factor = min(1.0, len(path) / 5.0)  # Jalur lebih pendek = lebih percaya diri
        
        return avg_success * length_factor