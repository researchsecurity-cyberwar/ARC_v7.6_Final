import requests
import base64
import json

class K8sAttackSurface:
    """
    Kubernetes misconfig → cluster takeover (RBAC, pods).
    Mengeksploitasi salah konfigurasi Kubernetes untuk takeover cluster.
    """
    
    def __init__(self):
        self.k8s_attack_vectors = {
            'anonymous_access': {
                'path': '/api/v1/namespaces/default/pods',
                'method': 'GET',
                'description': 'Anonymous access to Kubernetes API server'
            },
            'pod_exec_privilege_escalation': {
                'technique': 'Exec into pod with high privileges',
                'prerequisites': ['pods/exec permission', 'privileged pod']
            },
            'service_account_token_theft': {
                'path': '/var/run/secrets/kubernetes.io/serviceaccount/token',
                'description': 'Steal service account token from pod filesystem'
            },
            'kubelet_read_only_port': {
                'port': 10255,
                'path': '/pods',
                'description': 'Read-only Kubelet port exposes pod information'
            }
        }
        
        self.rbac_privesc_chains = {
            'edit_to_admin': {
                'required_role': 'edit',
                'escalated_role': 'admin',
                'exploit_path': 'Create pod with hostPath volume mounting /etc/kubernetes'
            },
            'view_to_edit': {
                'required_role': 'view',
                'escalated_role': 'edit',
                'exploit_path': 'Access configmaps/secrets to find credentials'
            }
        }
    
    def analyze_k8s_attack_surface(self, cluster_endpoint: str, auth_token: str = None):
        """
        Analisis permukaan serangan Kubernetes untuk potensi takeover.
        """
        results = {
            'cluster_endpoint': cluster_endpoint,
            'attack_vectors': [],
            'rbac_vulnerabilities': [],
            'compromise_potential': 'NONE',
            'risk_level': 'NONE',
            'recommendations': []
        }
        
        try:
            # Uji vektor serangan anonim
            anonymous_vectors = self._test_anonymous_access(cluster_endpoint)
            results['attack_vectors'].extend(anonymous_vectors)
            
            # Uji dengan token autentikasi jika tersedia
            if auth_token:
                authenticated_vectors = self._test_authenticated_access(cluster_endpoint, auth_token)
                results['attack_vectors'].extend(authenticated_vectors)
                
                # Analisis eskalasi RBAC
                rbac_vulns = self._analyze_rbac_escalation(auth_token)
                results['rbac_vulnerabilities'] = rbac_vulns
            
            # Tentukan potensi kompromi
            results['compromise_potential'] = self._assess_compromise_potential(results['attack_vectors'], results['rbac_vulnerabilities'])
            results['risk_level'] = 'CRITICAL' if results['compromise_potential'] == 'FULL_CLUSTER_TAKEOVER' else 'HIGH'
            
            # Buat rekomendasi
            results['recommendations'] = self._generate_k8s_recommendations(results['attack_vectors'], results['rbac_vulnerabilities'])
        
        except Exception as e:
            results['error'] = f'Kubernetes attack surface analysis failed: {str(e)}'
        
        return results
    
    def _test_anonymous_access(self, cluster_endpoint: str) -> List[Dict]:
        """Uji akses anonim ke API server Kubernetes."""
        attack_vectors = []
        
        try:
            # Uji akses anonim ke endpoint umum
            for vector_name, vector_info in self.k8s_attack_vectors.items():
                if 'path' in vector_info:
                    url = f"{cluster_endpoint.rstrip('/')}{vector_info['path']}"
                    response = requests.get(url, timeout=5, verify=False)
                    
                    if response.status_code == 200:
                        attack_vectors.append({
                            'vector_name': vector_name,
                            'description': vector_info['description'],
                            'severity': 'CRITICAL',
                            'evidence': f'Anonymous access granted to {vector_info["path"]}'
                        })
            
            # Uji port Kubelet read-only
            kubelet_url = f"http://{cluster_endpoint.replace('https://', '').replace('http://', '').split(':')[0]}:10255/pods"
            try:
                response = requests.get(kubelet_url, timeout=3)
                if response.status_code == 200:
                    attack_vectors.append({
                        'vector_name': 'kubelet_read_only_port',
                        'description': self.k8s_attack_vectors['kubelet_read_only_port']['description'],
                        'severity': 'HIGH',
                        'evidence': 'Kubelet read-only port accessible'
                    })
            except:
                pass
        
        except Exception:
            pass
        
        return attack_vectors
    
    def _test_authenticated_access(self, cluster_endpoint: str, auth_token: str) -> List[Dict]:
        """Uji akses dengan token autentikasi."""
        attack_vectors = []
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        try:
            # Uji kemampuan exec ke pod
            pods_url = f"{cluster_endpoint}/api/v1/namespaces/default/pods"
            response = requests.get(pods_url, headers=headers, timeout=10, verify=False)
            
            if response.status_code == 200:
                pods_data = response.json()
                for pod in pods_data.get('items', []):
                    pod_name = pod['metadata']['name']
                    # Coba akses exec ke pod
                    exec_url = f"{cluster_endpoint}/api/v1/namespaces/default/pods/{pod_name}/exec"
                    exec_response = requests.get(exec_url, headers=headers, timeout=5, verify=False)
                    
                    if exec_response.status_code in [200, 400]:  # 400 berarti exec didukung tapi parameter kurang
                        attack_vectors.append({
                            'vector_name': 'pod_exec_privilege_escalation',
                            'description': 'Pod exec capability detected',
                            'severity': 'HIGH',
                            'target_pod': pod_name
                        })
                        break  # Cukup satu pod
        
        except Exception:
            pass
        
        return attack_vectors
    
    def _analyze_rbac_escalation(self, auth_token: str) -> List[Dict]:
        """Analisis potensi eskalasi RBAC."""
        rbac_vulns = []
        
        # Ini akan terintegrasi dengan kubectl atau API Kubernetes langsung
        # Untuk sekarang, simulasi berdasarkan token yang diberikan
        token_payload = self._decode_service_account_token(auth_token)
        
        if token_payload:
            namespace = token_payload.get('namespace', 'default')
            service_account = token_payload.get('kubernetes.io/serviceaccount/service-account.name', 'default')
            
            # Simulasi: jika service account adalah 'edit', maka bisa eskalasi ke 'admin'
            if service_account == 'edit':
                rbac_vulns.append({
                    'chain_name': 'edit_to_admin',
                    'required_role': 'edit',
                    'escalated_role': 'admin',
                    'exploit_path': self.rbac_privesc_chains['edit_to_admin']['exploit_path'],
                    'severity': 'CRITICAL'
                })
            elif service_account == 'view':
                rbac_vulns.append({
                    'chain_name': 'view_to_edit',
                    'required_role': 'view',
                    'escalated_role': 'edit',
                    'exploit_path': self.rbac_privesc_chains['view_to_edit']['exploit_path'],
                    'severity': 'HIGH'
                })
        
        return rbac_vulns
    
    def _decode_service_account_token(self, token: str) -> Dict:
        """Dekode JWT service account token Kubernetes."""
        try:
            parts = token.split('.')
            if len(parts) == 3:
                # Decode header dan payload
                payload = base64.b64decode(parts[1] + '==').decode('utf-8')
                return json.loads(payload)
        except Exception:
            pass
        return None
    
    def _assess_compromise_potential(self, attack_vectors: List, rbac_vulns: List) -> str:
        """Nilai potensi kompromi cluster."""
        if any(vec['severity'] == 'CRITICAL' for vec in attack_vectors):
            return 'FULL_CLUSTER_TAKEOVER'
        elif rbac_vulns or any(vec['severity'] == 'HIGH' for vec in attack_vectors):
            return 'PARTIAL_CLUSTER_COMPROMISE'
        else:
            return 'NO_COMPROMISE_POSSIBLE'
    
    def _generate_k8s_recommendations(self, attack_vectors: List, rbac_vulns: List) -> List[str]:
        """Buat rekomendasi keamanan Kubernetes."""
        recommendations = []
        
        if attack_vectors:
            recommendations.extend([
                'Disable anonymous access to Kubernetes API server',
                'Close Kubelet read-only port (10255)',
                'Implement network policies to restrict pod communication',
                'Use PodSecurityPolicy or Pod Security Standards'
            ])
        
        if rbac_vulns:
            recommendations.extend([
                'Implement least privilege RBAC policies',
                'Avoid using built-in roles (edit, admin) for service accounts',
                'Regularly audit RBAC bindings and role assignments'
            ])
        
        if not recommendations:
            recommendations.append('Kubernetes cluster appears secure against common attack vectors')
        
        recommendations.extend([
            'Enable Kubernetes audit logging',
            'Use admission controllers (OPA Gatekeeper, Kyverno)',
            'Implement runtime security monitoring (Falco, Sysdig)'
        ])
        
        return recommendations