import os
import json
import re
import requests
from typing import Dict, List

class DependencyGraphAnalyzer:
    """
    Map npm/PyPI/Maven dependencies from code/repos.
    Memetakan dependensi perangkat lunak dari kode dan repositori.
    """
    
    def __init__(self):
        self.dependency_files = {
            'npm': ['package.json', 'package-lock.json', 'yarn.lock'],
            'pypi': ['requirements.txt', 'Pipfile', 'pyproject.toml', 'setup.py'],
            'maven': ['pom.xml', 'mvn-dependency-tree.txt']
        }
        
        self.registry_apis = {
            'npm': 'https://registry.npmjs.org/',
            'pypi': 'https://pypi.org/pypi/',
            'maven': 'https://search.maven.org/solrsearch/select'
        }
    
    def analyze_dependency_graph(self, repo_path: str, repo_url: str = None):
        """
        Analisis graf dependensi dari repositori lokal atau remote.
        """
        results = {
            'repo_path': repo_path,
            'repo_url': repo_url,
            'dependencies_found': {},
            'vulnerable_dependencies': [],
            'dependency_tree': {},
            'risk_score': 0.0,
            'recommendations': []
        }
        
        try:
            # Deteksi jenis proyek berdasarkan file yang ada
            project_type = self._detect_project_type(repo_path)
            
            if project_type:
                # Ekstrak dependensi berdasarkan tipe proyek
                dependencies = self._extract_dependencies(repo_path, project_type)
                results['dependencies_found'] = dependencies
                
                # Bangun pohon dependensi
                dependency_tree = self._build_dependency_tree(dependencies, project_type)
                results['dependency_tree'] = dependency_tree
                
                # Analisis kerentanan
                vulnerable_deps = self._analyze_vulnerable_dependencies(dependencies, project_type)
                results['vulnerable_dependencies'] = vulnerable_deps
                
                # Hitung skor risiko
                results['risk_score'] = self._calculate_supply_chain_risk(vulnerable_deps, len(dependencies))
                
                # Buat rekomendasi
                results['recommendations'] = self._generate_dependency_recommendations(vulnerable_deps)
            else:
                results['error'] = 'No supported dependency files found in repository'
        
        except Exception as e:
            results['error'] = f'Dependency graph analysis failed: {str(e)}'
        
        return results
    
    def _detect_project_type(self, repo_path: str) -> str:
        """Deteksi tipe proyek berdasarkan file dependensi yang ada."""
        for project_type, files in self.dependency_files.items():
            for file in files:
                if os.path.exists(os.path.join(repo_path, file)):
                    return project_type
        return None
    
    def _extract_dependencies(self, repo_path: str, project_type: str) -> Dict[str, List[Dict]]:
        """Ekstrak dependensi dari file proyek."""
        dependencies = {'direct': [], 'indirect': []}
        
        if project_type == 'npm':
            package_json_path = os.path.join(repo_path, 'package.json')
            if os.path.exists(package_json_path):
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                
                # Dependensi langsung
                for dep_type in ['dependencies', 'devDependencies']:
                    if dep_type in package_data:
                        for name, version in package_data[dep_type].items():
                            dependencies['direct'].append({
                                'name': name,
                                'version': version,
                                'type': dep_type
                            })
        
        elif project_type == 'pypi':
            requirements_path = os.path.join(repo_path, 'requirements.txt')
            if os.path.exists(requirements_path):
                with open(requirements_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Parse requirement (sederhana)
                            match = re.match(r'([a-zA-Z0-9_-]+)(.*)', line)
                            if match:
                                name = match.group(1)
                                version_spec = match.group(2).strip() if match.group(2) else '*'
                                dependencies['direct'].append({
                                    'name': name,
                                    'version': version_spec,
                                    'type': 'production'
                                })
        
        elif project_type == 'maven':
            pom_path = os.path.join(repo_path, 'pom.xml')
            if os.path.exists(pom_path):
                with open(pom_path, 'r') as f:
                    content = f.read()
                
                # Ekstrak dependensi Maven (sederhana)
                dep_matches = re.findall(r'<dependency>\s*<groupId>([^<]+)</groupId>\s*<artifactId>([^<]+)</artifactId>\s*<version>([^<]+)</version>', content)
                for group_id, artifact_id, version in dep_matches:
                    full_name = f"{group_id}:{artifact_id}"
                    dependencies['direct'].append({
                        'name': full_name,
                        'version': version,
                        'type': 'compile'
                    })
        
        return dependencies
    
    def _build_dependency_tree(self, dependencies: Dict, project_type: str) -> Dict:
        """Bangun pohon dependensi (placeholder untuk integrasi registry)."""
        # Ini akan terintegrasi dengan API registry untuk mendapatkan dependensi transitif
        tree = {'root': {'name': 'project', 'children': []}}
        
        for dep in dependencies['direct']:
            tree['root']['children'].append({
                'name': dep['name'],
                'version': dep['version'],
                'children': []  # Akan diisi dengan dependensi transitif
            })
        
        return tree
    
    def _analyze_vulnerable_dependencies(self, dependencies: Dict, project_type: str) -> List[Dict]:
        """Analisis dependensi untuk kerentanan keamanan."""
        vulnerable_deps = []
        
        # Cek setiap dependensi langsung
        for dep in dependencies['direct']:
            # Query registry untuk informasi keamanan
            security_info = self._query_registry_security(dep['name'], dep['version'], project_type)
            
            if security_info.get('vulnerable', False):
                vulnerable_deps.append({
                    'name': dep['name'],
                    'version': dep['version'],
                    'vulnerabilities': security_info.get('vulnerabilities', []),
                    'severity': security_info.get('max_severity', 'MEDIUM'),
                    'cvss_score': security_info.get('cvss_score', 0.0)
                })
        
        return vulnerable_deps
    
    def _query_registry_security(self, package_name: str, version: str, registry_type: str) -> Dict:
        """Query registry untuk informasi keamanan paket."""
        try:
            if registry_type == 'npm':
                # Gunakan npm audit API (placeholder)
                return self._check_npm_security(package_name, version)
            elif registry_type == 'pypi':
                # Gunakan PyPI security API atau sumber eksternal
                return self._check_pypi_security(package_name, version)
            elif registry_type == 'maven':
                # Gunakan Maven Central security data
                return self._check_maven_security(package_name, version)
        except Exception:
            pass
        
        return {'vulnerable': False}
    
    def _check_npm_security(self, package_name: str, version: str) -> Dict:
        """Cek keamanan paket npm."""
        # Placeholder - dalam implementasi nyata akan menggunakan npm audit atau Snyk API
        known_vulnerable = {
            'event-stream': ['3.3.6'],
            'flatmap-stream': ['0.1.0', '0.1.1']
        }
        
        if package_name in known_vulnerable and version in known_vulnerable[package_name]:
            return {
                'vulnerable': True,
                'vulnerabilities': [{'id': 'MAL-001', 'description': 'Malicious package'}],
                'max_severity': 'CRITICAL',
                'cvss_score': 9.8
            }
        
        return {'vulnerable': False}
    
    def _check_pypi_security(self, package_name: str, version: str) -> Dict:
        """Cek keamanan paket PyPI."""
        # Placeholder
        return {'vulnerable': False}
    
    def _check_maven_security(self, package_name: str, version: str) -> Dict:
        """Cek keamanan artefak Maven."""
        # Placeholder
        return {'vulnerable': False}
    
    def _calculate_supply_chain_risk(self, vulnerable_deps: List, total_deps: int) -> float:
        """Hitung skor risiko rantai pasok."""
        if not vulnerable_deps:
            return 0.1
        
        critical_count = sum(1 for dep in vulnerable_deps if dep['severity'] == 'CRITICAL')
        high_count = sum(1 for dep in vulnerable_deps if dep['severity'] == 'HIGH')
        
        base_risk = 0.3
        base_risk += critical_count * 0.4
        base_risk += high_count * 0.2
        base_risk += (len(vulnerable_deps) / total_deps) * 0.3  # Proporsi dependensi rentan
        
        return min(base_risk, 0.95)
    
    def _generate_dependency_recommendations(self, vulnerable_deps: List) -> List[str]:
        """Buat rekomendasi manajemen dependensi."""
        recommendations = []
        
        if vulnerable_deps:
            recommendations.extend([
                'Update vulnerable dependencies to secure versions immediately',
                'Implement automated dependency scanning in CI/CD pipeline',
                'Use lock files to pin dependency versions',
                'Monitor for new vulnerabilities in existing dependencies'
            ])
            
            critical_deps = [dep for dep in vulnerable_deps if dep['severity'] == 'CRITICAL']
            if critical_deps:
                recommendations.append('Consider removing or replacing critically vulnerable dependencies')
        else:
            recommendations.append('No vulnerable dependencies detected - continue monitoring')
        
        recommendations.append('Use software composition analysis (SCA) tools for comprehensive coverage')
        
        return recommendations