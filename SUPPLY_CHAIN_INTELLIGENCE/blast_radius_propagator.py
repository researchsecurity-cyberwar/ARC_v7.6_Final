import requests
import json
from typing import Dict, List

class BlastRadiusPropagator:
    """
    Quantify: 1 package → N organizations impacted.
    Mengkuantifikasi dampak ledakan dari satu paket ke banyak organisasi.
    """
    
    def __init__(self):
        self.dependency_graphs = {
            'npm': 'https://api.deps.dev/v3/systems/npm/packages/',
            'pypi': 'https://api.deps.dev/v3/systems/pypi/packages/',
            'maven': 'https://api.deps.dev/v3/systems/maven/packages/'
        }
        
        self.organization_indicators = [
            'github.com/', 'gitlab.com/', 'bitbucket.org/',
            'company', 'corp', 'enterprise', 'organization'
        ]
    
    def propagate_blast_radius(self, package_name: str, package_version: str, registry_type: str = 'npm'):
        """
        Propagasikan radius dampak dari paket yang rentan.
        """
        results = {
            'package_name': package_name,
            'package_version': package_version,
            'registry_type': registry_type,
            'direct_dependents': 0,
            'transitive_dependents': 0,
            'affected_organizations': [],
            'blast_radius_score': 0.0,
            'impact_assessment': {},
            'mitigation_priority': 'LOW'
        }
        
        try:
            # Dapatkan graf dependensi dari API
            dependency_data = self._fetch_dependency_graph(package_name, package_version, registry_type)
            
            if dependency_data:
                results['direct_dependents'] = dependency_data.get('direct_dependents', 0)
                results['transitive_dependents'] = dependency_data.get('transitive_dependents', 0)
                
                # Estimasi organisasi yang terdampak
                affected_orgs = self._estimate_affected_organizations(
                    dependency_data, results['transitive_dependents']
                )
                results['affected_organizations'] = affected_orgs
                
                # Hitung skor radius dampak
                results['blast_radius_score'] = self._calculate_blast_radius_score(
                    results['direct_dependents'], results['transitive_dependents'], len(affected_orgs)
                )
                
                # Nilai dampak
                results['impact_assessment'] = self._assess_impact(
                    results['blast_radius_score'], len(affected_orgs)
                )
                
                # Tentukan prioritas mitigasi
                results['mitigation_priority'] = self._determine_mitigation_priority(
                    results['blast_radius_score'], results['impact_assessment']['severity']
                )
        
        except Exception as e:
            results['error'] = f'Blast radius propagation failed: {str(e)}'
        
        return results
    
    def _fetch_dependency_graph(self, package_name: str, package_version: str, registry_type: str) -> Dict:
        """Ambil graf dependensi dari API deps.dev."""
        try:
            # Format nama paket untuk Maven
            if registry_type == 'maven':
                # Maven package name format: group:artifact
                if ':' not in package_name:
                    return None
                encoded_name = package_name.replace(':', '/').replace('.', '/')
            else:
                encoded_name = package_name
            
            url = f"{self.dependency_graphs[registry_type]}{encoded_name}/versions/{package_version}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'direct_dependents': data.get('dependentCount', 0),
                    'transitive_dependents': data.get('transitiveDependentCount', 0),
                    'dependent_packages': data.get('dependents', [])
                }
        except Exception:
            pass
        
        return None
    
    def _estimate_affected_organizations(self, dependency_data: Dict, transitive_count: int) -> List[str]:
        """Estimasi organisasi yang terdampak."""
        # Ini akan menganalisis repositori dependen untuk mengidentifikasi organisasi
        # Untuk sekarang, estimasi berdasarkan jumlah dependen
        affected_orgs = []
        
        # Asumsi: 10% dari dependen transitive adalah organisasi
        estimated_orgs = int(transitive_count * 0.1)
        
        if estimated_orgs > 0:
            affected_orgs = [f"Organization_{i+1}" for i in range(min(estimated_orgs, 100))]
        
        return affected_orgs
    
    def _calculate_blast_radius_score(self, direct_deps: int, transitive_deps: int, org_count: int) -> float:
        """Hitung skor radius dampak."""
        # Normalisasi jumlah dependen
        direct_score = min(direct_deps / 1000, 1.0)
        transitive_score = min(transitive_deps / 10000, 1.0)
        org_score = min(org_count / 100, 1.0)
        
        # Bobot: dependen transitif lebih penting
        blast_score = (direct_score * 0.2) + (transitive_score * 0.5) + (org_score * 0.3)
        return min(blast_score, 1.0)
    
    def _assess_impact(self, blast_score: float, org_count: int) -> Dict:
        """Nilai dampak berdasarkan skor radius dampak."""
        if blast_score >= 0.7:
            severity = 'CRITICAL'
            description = 'Widespread impact across hundreds of organizations'
        elif blast_score >= 0.4:
            severity = 'HIGH'
            description = 'Significant impact across multiple organizations'
        elif blast_score >= 0.2:
            severity = 'MEDIUM'
            description = 'Limited impact but potential for escalation'
        else:
            severity = 'LOW'
            description = 'Minimal impact - mostly individual developers'
        
        return {
            'severity': severity,
            'description': description,
            'estimated_financial_impact': self._estimate_financial_impact(severity, org_count)
        }
    
    def _estimate_financial_impact(self, severity: str, org_count: int) -> str:
        """Estimasi dampak finansial."""
        if severity == 'CRITICAL':
            return f"${org_count * 10000:,} - ${org_count * 100000:,}"
        elif severity == 'HIGH':
            return f"${org_count * 1000:,} - ${org_count * 10000:,}"
        elif severity == 'MEDIUM':
            return f"${org_count * 100:,} - ${org_count * 1000:,}"
        else:
            return "$0 - $1,000"
    
    def _determine_mitigation_priority(self, blast_score: float, severity: str) -> str:
        """Tentukan prioritas mitigasi."""
        if blast_score >= 0.7 or severity == 'CRITICAL':
            return 'IMMEDIATE'
        elif blast_score >= 0.4 or severity == 'HIGH':
            return 'HIGH'
        elif blast_score >= 0.2:
            return 'MEDIUM'
        else:
            return 'LOW'