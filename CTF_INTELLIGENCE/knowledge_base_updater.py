import json
import os

class KnowledgeBaseUpdater:
    """
    Update playbooks based on learning.
    Memperbarui playbook berdasarkan pembelajaran dari kegagalan.
    """
    
    def __init__(self, knowledge_dir="~/.arc/knowledge"):
        self.knowledge_dir = os.path.expanduser(knowledge_dir)
        os.makedirs(self.knowledge_dir, exist_ok=True)
        self.knowledge_base_file = os.path.join(self.knowledge_dir, "ctf_knowledge.json")
        self.knowledge_base = self._load_knowledge_base()
    
    def update_knowledge_base(self, learning_data: dict):
        """
        Perbarui basis pengetahuan dengan pembelajaran baru.
        """
        results = {
            'learning_data': learning_data,
            'update_successful': False,
            'new_techniques_added': 0,
            'playbooks_updated': []
        }
        
        try:
            # Ekstrak teknik baru dari data pembelajaran
            new_techniques = self._extract_new_techniques(learning_data)
            
            # Tambahkan ke basis pengetahuan
            for technique in new_techniques:
                category = technique['category']
                if category not in self.knowledge_base:
                    self.knowledge_base[category] = []
                self.knowledge_base[category].append(technique)
            
            # Simpan basis pengetahuan yang diperbarui
            self._save_knowledge_base()
            
            results.update({
                'update_successful': True,
                'new_techniques_added': len(new_techniques),
                'playbooks_updated': list(set(t['category'] for t in new_techniques))
            })
        
        except Exception as e:
            results['error'] = f'Knowledge base update failed: {str(e)}'
        
        return results
    
    def _load_knowledge_base(self):
        """Muat basis pengetahuan dari file."""
        if os.path.exists(self.knowledge_base_file):
            try:
                with open(self.knowledge_base_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_knowledge_base(self):
        """Simpan basis pengetahuan ke file."""
        with open(self.knowledge_base_file, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
    
    def _extract_new_techniques(self, learning_data: dict) -> list:
        """Ekstrak teknik baru dari data pembelajaran."""
        techniques = []
        opportunities = learning_data.get('learning_opportunities', [])
        
        for opportunity in opportunities:
            technique = {
                'technique_name': opportunity.get('technique_learned', 'Unknown technique'),
                'category': learning_data.get('challenge_data', {}).get('category', 'misc'),
                'root_cause_solved': opportunity.get('root_cause_addressed', 'unknown'),
                'source_writeup': opportunity.get('writeup_url', ''),
                'confidence_boost': opportunity.get('confidence_improvement', 0.1),
                'added_timestamp': time.time()
            }
            techniques.append(technique)
        
        return techniques
    
    def get_knowledge_for_category(self, category: str) -> list:
        """Dapatkan pengetahuan untuk kategori tertentu."""
        return self.knowledge_base.get(category, [])