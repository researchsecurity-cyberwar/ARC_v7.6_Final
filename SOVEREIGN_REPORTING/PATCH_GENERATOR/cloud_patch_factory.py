class CloudPatchFactory:
    """
    S3, IAM policy fixes.
    Menghasilkan patch konfigurasi cloud untuk kerentanan.
    """
    
    def __init__(self):
        self.cloud_patch_templates = {
            's3_bucket_policy': {
                'public_read_fix': '''{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::ACCOUNT_ID:role/ApplicationRole"
            },
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": "arn:aws:s3:::BUCKET_NAME/*"
        }
    ]
}''',
                'block_public_access': '''# Enable S3 Block Public Access
aws s3api put-public-access-block \\
    --bucket BUCKET_NAME \\
    --public-access-block-configuration \\
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
'''
            },
            'iam_policy': {
                'least_privilege': '''{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": "arn:aws:s3:::SPECIFIC_BUCKET/*"
        }
    ]
}''',
                'permission_boundary': '''# Apply permission boundary to IAM role
aws iam put-role-permissions-boundary \\
    --role-name ROLE_NAME \\
    --permissions-boundary arn:aws:iam::aws:policy/PERMISSIONS_BOUNDARY_POLICY
'''
            }
        }
    
    def generate_cloud_patch(self, vulnerability_type: str, cloud_provider: str = 'aws') -> str:
        """Hasilkan patch cloud untuk tipe kerentanan tertentu."""
        if vulnerability_type not in self.cloud_patch_templates:
            return f"# No patch template available for {vulnerability_type}\n# Please implement custom fix"
        
        templates = self.cloud_patch_templates[vulnerability_type]
        return next(iter(templates.values()))
    
    def generate_cloud_fix_recommendation(self, vuln_data: dict) -> dict:
        """Hasilkan rekomendasi perbaikan cloud lengkap."""
        vuln_type = vuln_data.get('type', 'unknown')
        cloud_provider = vuln_data.get('cloud_provider', 'aws')
        resource_name = vuln_data.get('resource_name', 'RESOURCE_NAME')
        
        patch_code = self.generate_cloud_patch(vuln_type, cloud_provider)
        # Replace placeholder with actual resource name
        patch_code = patch_code.replace('BUCKET_NAME', resource_name).replace('ACCOUNT_ID', vuln_data.get('account_id', 'ACCOUNT_ID'))
        
        return {
            'vulnerability_type': vuln_type,
            'cloud_provider': cloud_provider,
            'resource_name': resource_name,
            'patch_code': patch_code,
            'deployment_method': self._get_deployment_method(cloud_provider),
            'verification_steps': self._get_verification_steps(vuln_type, cloud_provider)
        }
    
    def _get_deployment_method(self, cloud_provider: str) -> str:
        """Dapatkan metode deployment."""
        methods = {
            'aws': 'Use AWS CLI, CloudFormation, or Terraform to apply the policy',
            'azure': 'Use Azure CLI, ARM templates, or Bicep to apply the configuration',
            'gcp': 'Use gcloud CLI, Deployment Manager, or Terraform to apply the policy'
        }
        return methods.get(cloud_provider, 'Apply using your infrastructure as code tool')
    
    def _get_verification_steps(self, vuln_type: str, cloud_provider: str) -> list:
        """Dapatkan langkah verifikasi."""
        steps = {
            's3_bucket_policy': [
                'Verify bucket is no longer publicly accessible',
                'Test authorized access still works',
                'Confirm Block Public Access is enabled'
            ],
            'iam_policy': [
                'Verify role can only access intended resources',
                'Test that excessive permissions are removed',
                'Confirm permission boundaries are applied'
            ]
        }
        return steps.get(vuln_type, ['Apply patch', 'Test functionality', 'Verify security'])