import boto3
import json
from typing import Dict, List

try:
    from azure.identity import DefaultAzureCredential
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    DefaultAzureCredential = None

try:
    from google.auth import default as gcp_default
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False
    gcp_default = None

class CrossAccountPivoter:
    """
    Cross-account/cloud pivoting via assumed roles.
    Melakukan pergerakan lateral antar akun/cloud melalui peran yang diasumsikan.
    """
    
    def __init__(self):
        self.pivot_techniques = {
            'aws_cross_account': self._pivot_aws_cross_account,
            'azure_cross_tenant': self._pivot_azure_cross_tenant,
            'gcp_cross_project': self._pivot_gcp_cross_project,
            'cloud_hopping': self._pivot_cloud_hopping
        }
    
    def pivot_between_environments(self, source_credentials: Dict, target_environment: str):
        """
        Lakukan pergerakan lateral ke lingkungan target.
        """
        results = {
            'source_environment': source_credentials.get('platform'),
            'target_environment': target_environment,
            'pivoting_successful': False,
            'accessed_resources': [],
            'technique_used': None,
            'risk_level': 'NONE',
            'recommendations': []
        }
        
        try:
            # Tentukan teknik pivoting berdasarkan sumber dan target
            technique_key = self._determine_pivot_technique(
                source_credentials.get('platform'), target_environment
            )
            
            if technique_key in self.pivot_techniques:
                pivot_result = self.pivot_techniques[technique_key](source_credentials, target_environment)
                results.update(pivot_result)
                results['technique_used'] = technique_key
                results['risk_level'] = 'CRITICAL' if pivot_result.get('pivoting_successful') else 'NONE'
                results['recommendations'] = self._generate_pivot_recommendations(technique_key)
            else:
                results['error'] = f'No pivoting technique available for {source_credentials.get("platform")} → {target_environment}'
        
        except Exception as e:
            results['error'] = f'Cross-environment pivoting failed: {str(e)}'
        
        return results
    
    def _determine_pivot_technique(self, source_platform: str, target_environment: str) -> str:
        """Tentukan teknik pivoting berdasarkan platform sumber dan target."""
        if source_platform == 'aws' and 'aws' in target_environment.lower():
            return 'aws_cross_account'
        elif source_platform == 'azure' and 'azure' in target_environment.lower():
            return 'azure_cross_tenant'
        elif source_platform == 'gcp' and 'gcp' in target_environment.lower():
            return 'gcp_cross_project'
        else:
            return 'cloud_hopping'
    
    def _pivot_aws_cross_account(self, aws_creds: Dict, target_account: str) -> Dict:
        """Lakukan pivoting cross-account AWS."""
        try:
            # Gunakan kredensial AWS untuk mengasumsikan peran di akun target
            sts_client = boto3.client(
                'sts',
                aws_access_key_id=aws_creds.get('access_key'),
                aws_secret_access_key=aws_creds.get('secret_key'),
                aws_session_token=aws_creds.get('session_token')
            )
            
            # Asumsikan peran di akun target
            assumed_role = sts_client.assume_role(
                RoleArn=f'arn:aws:iam::{target_account}:role/CrossAccountAccessRole',
                RoleSessionName='ARC-Pivot-Session'
            )
            
            # Gunakan kredensial yang diasumsikan untuk akses sumber daya
            target_client = boto3.client(
                's3',
                aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
                aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
                aws_session_token=assumed_role['Credentials']['SessionToken']
            )
            
            # Daftar bucket di akun target
            buckets = target_client.list_buckets()
            bucket_names = [bucket['Name'] for bucket in buckets['Buckets']]
            
            return {
                'pivoting_successful': True,
                'accessed_resources': bucket_names,
                'assumed_role_arn': f'arn:aws:iam::{target_account}:role/CrossAccountAccessRole'
            }
        
        except Exception as e:
            return {
                'pivoting_successful': False,
                'error': str(e)
            }
    
    def _pivot_azure_cross_tenant(self, azure_creds: Dict, target_tenant: str) -> Dict:
        """Lakukan pivoting cross-tenant Azure."""
        # Placeholder - implementasi nyata memerlukan Azure SDK
        return {
            'pivoting_successful': False,
            'error': 'Azure cross-tenant pivoting requires interactive authentication'
        }
    
    def _pivot_gcp_cross_project(self, gcp_creds: Dict, target_project: str) -> Dict:
        """Lakukan pivoting cross-project GCP."""
        # Placeholder - implementasi nyata memerlukan GCP SDK
        return {
            'pivoting_successful': False,
            'error': 'GCP cross-project pivoting requires service account impersonation'
        }
    
    def _pivot_cloud_hopping(self, source_creds: Dict, target_cloud: str) -> Dict:
        """Lakukan hopping antar cloud (misal: AWS → Azure)."""
        # Ini mensimulasikan skenario di mana kredensial cloud satu digunakan
        # untuk mengakses sumber daya di cloud lain melalui integrasi
        
        # Contoh: Kredensial AWS digunakan untuk mengakses secret di Parameter Store
        # yang berisi kredensial Azure
        
        if source_creds.get('platform') == 'aws':
            # Simulasikan akses ke AWS Systems Manager Parameter Store
            # yang berisi kredensial Azure
            simulated_azure_creds = {
                'client_id': 'simulated-azure-client-id',
                'client_secret': 'simulated-azure-client-secret',
                'tenant_id': 'simulated-azure-tenant-id'
            }
            
            return {
                'pivoting_successful': True,
                'accessed_resources': ['Azure Key Vault secrets', 'Azure Storage accounts'],
                'hopping_path': 'AWS Parameter Store → Azure Credentials'
            }
        
        return {
            'pivoting_successful': False,
            'error': 'Cloud hopping simulation only supports AWS as source'
        }
    
    def _generate_pivot_recommendations(self, technique: str) -> List[str]:
        """Buat rekomendasi pencegahan pivoting."""
        recommendations = []
        
        if technique == 'aws_cross_account':
            recommendations.extend([
                'Restrict cross-account role trust policies to specific principals',
                'Implement external ID requirements for cross-account roles',
                'Monitor AssumeRole events in CloudTrail'
            ])
        elif technique == 'cloud_hopping':
            recommendations.extend([
                'Never store credentials for one cloud in another cloud\'s secret manager',
                'Implement strict access controls on secret management services',
                'Use dedicated service accounts with minimal permissions'
            ])
        else:
            recommendations.append('Implement comprehensive cross-environment monitoring')
        
        return recommendations