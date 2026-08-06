import json
from typing import Dict, List

class IdentityAttackMapper:
    """
    IAM privilege escalation path enumeration (AWS/Azure/GCP).
    Memetakan jalur eskalasi hak IAM di lingkungan multi-cloud.
    """
    
    def __init__(self):
        self.iam_privesc_chains = {
            'aws': {
                's3_getobject_to_s3_putobject': {
                    'required_permissions': ['s3:GetObject'],
                    'escalated_permissions': ['s3:PutObject', 's3:DeleteObject'],
                    'exploit_complexity': 'LOW'
                },
                'iam_createpolicyversion': {
                    'required_permissions': ['iam:CreatePolicyVersion'],
                    'escalated_permissions': ['*:*'],
                    'exploit_complexity': 'MEDIUM'
                },
                'lambda_updatefunctioncode': {
                    'required_permissions': ['lambda:UpdateFunctionCode'],
                    'escalated_permissions': ['lambda:InvokeFunction', 'iam:PassRole'],
                    'exploit_complexity': 'HIGH'
                }
            },
            'azure': {
                'storage_blob_contributor_to_owner': {
                    'required_permissions': ['Storage Blob Data Contributor'],
                    'escalated_permissions': ['Owner'],
                    'exploit_complexity': 'MEDIUM'
                },
                'reader_to_contributor_via_template': {
                    'required_permissions': ['Reader'],
                    'escalated_permissions': ['Contributor'],
                    'exploit_complexity': 'HIGH'
                }
            },
            'gcp': {
                'storage_object_admin_to_owner': {
                    'required_permissions': ['roles/storage.objectAdmin'],
                    'escalated_permissions': ['roles/owner'],
                    'exploit_complexity': 'MEDIUM'
                },
                'service_account_token_creator': {
                    'required_permissions': ['iam.serviceAccountTokenCreator'],
                    'escalated_permissions': ['all service account permissions'],
                    'exploit_complexity': 'HIGH'
                }
            }
        }
    
    def map_iam_attack_paths(self, cloud_platform: str, current_permissions: List[str]):
        """
        Petakan jalur serangan IAM berdasarkan izin saat ini.
        """
        results = {
            'cloud_platform': cloud_platform,
            'current_permissions': current_permissions,
            'attack_paths': [],
            'risk_level': 'NONE',
            'recommendations': []
        }
        
        try:
            if cloud_platform not in self.iam_privesc_chains:
                results['error'] = f'Unsupported cloud platform: {cloud_platform}'
                return results
            
            # Temukan jalur eskalasi yang mungkin
            attack_paths = []
            platform_chains = self.iam_privesc_chains[cloud_platform]
            
            for chain_name, chain_info in platform_chains.items():
                required_perms = set(chain_info['required_permissions'])
                current_perms_set = set(current_permissions)
                
                # Cek apakah semua izin yang dibutuhkan tersedia
                if required_perms.issubset(current_perms_set):
                    attack_paths.append({
                        'chain_name': chain_name,
                        'required_permissions': list(required_perms),
                        'escalated_permissions': chain_info['escalated_permissions'],
                        'exploit_complexity': chain_info['exploit_complexity'],
                        'blast_radius': self._calculate_blast_radius(cloud_platform, chain_info['escalated_permissions']),
                        'exploitation_steps': self._generate_exploitation_steps(cloud_platform, chain_name)
                    })
            
            results['attack_paths'] = attack_paths
            results['risk_level'] = self._calculate_iam_risk(attack_paths)
            results['recommendations'] = self._generate_iam_recommendations(attack_paths, cloud_platform)
        
        except Exception as e:
            results['error'] = f'IAM attack mapping failed: {str(e)}'
        
        return results
    
    def _calculate_blast_radius(self, cloud_platform: str, escalated_permissions: List[str]) -> str:
        """Hitung radius dampak dari eskalasi hak."""
        critical_perms = {
            'aws': ['*:*', 'iam:', 's3:', 'ec2:RunInstances'],
            'azure': ['Owner', 'Contributor', '*:*'],
            'gcp': ['roles/owner', '*:*', 'iam.serviceAccounts.*']
        }
        
        platform_critical = critical_perms.get(cloud_platform, [])
        has_critical = any(
            any(critical in perm for critical in platform_critical)
            for perm in escalated_permissions
        )
        
        return 'CRITICAL' if has_critical else 'HIGH'
    
    def _generate_exploitation_steps(self, cloud_platform: str, chain_name: str) -> List[str]:
        """Hasilkan langkah eksploitasi untuk jalur tertentu."""
        steps = []
        
        if cloud_platform == 'aws':
            if 's3' in chain_name:
                steps = [
                    '1. Download sensitive files from S3 bucket',
                    '2. Upload malicious files or backdoors',
                    '3. Delete audit logs or critical data'
                ]
            elif 'iam' in chain_name:
                steps = [
                    '1. Create new policy version with full admin rights',
                    '2. Attach policy to current user/role',
                    '3. Assume full administrative privileges'
                ]
            elif 'lambda' in chain_name:
                steps = [
                    '1. Update Lambda function code with reverse shell',
                    '2. Invoke function to establish persistence',
                    '3. Use attached role for further escalation'
                ]
        
        elif cloud_platform == 'azure':
            if 'storage' in chain_name:
                steps = [
                    '1. Access blob storage with contributor rights',
                    '2. Upload malicious scripts or credentials',
                    '3. Leverage storage access for VM compromise'
                ]
            elif 'template' in chain_name:
                steps = [
                    '1. Deploy ARM template with elevated permissions',
                    '2. Create new resource with contributor access',
                    '3. Escalate to full subscription access'
                ]
        
        elif cloud_platform == 'gcp':
            if 'storage' in chain_name:
                steps = [
                    '1. Modify object ACLs to grant public access',
                    '2. Upload malicious content to storage buckets',
                    '3. Leverage storage access for project compromise'
                ]
            elif 'service_account' in chain_name:
                steps = [
                    '1. Generate access token for target service account',
                    '2. Impersonate service account with higher privileges',
                    '3. Access resources owned by the service account'
                ]
        
        return steps
    
    def _calculate_iam_risk(self, attack_paths: List) -> str:
        """Hitung tingkat risiko IAM."""
        if not attack_paths:
            return 'NONE'
        
        critical_paths = sum(1 for path in attack_paths if path['blast_radius'] == 'CRITICAL')
        if critical_paths > 0:
            return 'CRITICAL'
        elif len(attack_paths) > 2:
            return 'HIGH'
        else:
            return 'MEDIUM'
    
    def _generate_iam_recommendations(self, attack_paths: List, cloud_platform: str) -> List[str]:
        """Buat rekomendasi mitigasi IAM."""
        recommendations = []
        
        if attack_paths:
            recommendations.extend([
                'Implement principle of least privilege for all identities',
                'Regularly audit and remove unnecessary permissions',
                'Use permission boundaries to limit maximum permissions',
                'Enable CloudTrail/Azure Activity Log/GCP Audit Logs'
            ])
            
            if any('s3' in path['chain_name'] for path in attack_paths):
                recommendations.append('Restrict S3 bucket policies and ACLs')
            
            if any('iam' in path['chain_name'] for path in attack_paths):
                recommendations.append('Disable iam:CreatePolicyVersion unless absolutely necessary')
        else:
            recommendations.append('Current IAM configuration appears secure against known escalation paths')
        
        # Rekomendasi spesifik cloud
        if cloud_platform == 'aws':
            recommendations.append('Use AWS IAM Access Analyzer for external access monitoring')
        elif cloud_platform == 'azure':
            recommendations.append('Implement Azure Policy for resource compliance')
        elif cloud_platform == 'gcp':
            recommendations.append('Use GCP Recommender for IAM optimization')
        
        return recommendations