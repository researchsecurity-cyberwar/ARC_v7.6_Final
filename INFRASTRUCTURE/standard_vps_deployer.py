import subprocess
import os
import sys
import time
import json
import tempfile
from typing import Dict, Any, Optional

class StandardVPSDeployer:
    """
    Deploy ke penyedia cloud standar dengan kredensial API.
    Mendukung DigitalOcean, AWS, Azure, GCP, dan penyedia lainnya secara universal.
    """
    
    def __init__(self, arc_dir="~/arc-project"):
        self.arc_dir = os.path.expanduser(arc_dir)
        self.ssh_key_path = os.path.expanduser("~/.ssh/arc_deploy_key")
        self._ensure_ssh_key()
    
    def deploy_to_provider(self, provider: str, config: Dict[str, Any]):
        """
        Deploy ke penyedia VPS spesifik dengan konfigurasi universal.
        
        Args:
            provider (str): 'digitalocean', 'aws', 'azure', 'gcp', 'hcloud', 'linode', 'vultr'
            config (dict): Konfigurasi deployment spesifik penyedia
        
        Returns:
            dict: Hasil deployment dengan IP dan status
        """
        results = {
            'provider': provider,
            'instance_id': None,
            'ip_address': None,
            'deployment_successful': False,
            'errors': []
        }
        
        try:
            # Validasi input
            if not self._validate_config(provider, config):
                results['errors'].append('Invalid configuration for provider')
                return results
            
            # Deploy instance
            instance_info = self._deploy_instance(provider, config)
            if not instance_info.get('success', False):
                results['errors'].append(f'Instance deployment failed: {instance_info.get("error", "Unknown")}')
                return results
            
            # Tunggu instance siap
            ip_address = instance_info['ip_address']
            if not self._wait_for_ssh_ready(ip_address, timeout=300):
                results['errors'].append('SSH connection timeout after 5 minutes')
                return results
            
            # Deploy ARC
            deploy_result = self._deploy_arc_to_vps(ip_address)
            if not deploy_result['success']:
                results['errors'].append(f'ARC deployment failed: {deploy_result.get("error", "Unknown")}')
                return results
            
            results.update({
                'instance_id': instance_info['instance_id'],
                'ip_address': ip_address,
                'deployment_successful': True
            })
        
        except Exception as e:
            results['errors'].append(f'Deployment failed: {str(e)}')
        
        return results
    
    def _validate_config(self, provider: str, config: Dict[str, Any]) -> bool:
        """Validasi konfigurasi berdasarkan penyedia."""
        required_fields = {
            'digitalocean': ['token', 'region', 'size'],
            'aws': ['access_key', 'secret_key', 'region', 'instance_type'],
            'azure': ['subscription_id', 'client_id', 'client_secret', 'tenant_id', 'location'],
            'gcp': ['project_id', 'credentials_file', 'zone', 'machine_type'],
            'hcloud': ['token', 'location', 'server_type'],
            'linode': ['token', 'region', 'type'],
            'vultr': ['api_key', 'region', 'plan']
        }
        
        if provider not in required_fields:
            return False
        
        for field in required_fields[provider]:
            if field not in config:
                return False
        
        return True
    
    def _deploy_instance(self, provider: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy instance di penyedia spesifik."""
        if provider == 'digitalocean':
            return self._deploy_digitalocean(config)
        elif provider == 'aws':
            return self._deploy_aws(config)
        elif provider == 'azure':
            return self._deploy_azure(config)
        elif provider == 'gcp':
            return self._deploy_gcp(config)
        elif provider == 'hcloud':
            return self._deploy_hetzner(config)
        elif provider == 'linode':
            return self._deploy_linode(config)
        elif provider == 'vultr':
            return self._deploy_vultr(config)
        else:
            return {'success': False, 'error': f'Unsupported provider: {provider}'}
    
    def _deploy_digitalocean(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy ke DigitalOcean."""
        try:
            # Install doctl jika belum ada
            if not shutil.which('doctl'):
                subprocess.run(['sudo', 'snap', 'install', 'doctl', '--classic'], check=True, timeout=300)
            
            # Autentikasi
            subprocess.run(['doctl', 'auth', 'init', '-t', config['token']], 
                          input=config['token'], text=True, check=True, timeout=30)
            
            # Buat droplet
            cmd = [
                'doctl', 'compute', 'droplet', 'create', 'arc-agent',
                '--region', config['region'],
                '--size', config['size'],
                '--image', 'ubuntu-22-04-x64',
                '--ssh-keys', self._get_ssh_fingerprint(),
                '--wait',
                '--format', 'ID,PublicIPv4'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode != 0:
                return {'success': False, 'error': result.stderr}
            
            # Parse output untuk dapatkan ID dan IP
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                id_ip = lines[1].split()
                if len(id_ip) >= 2:
                    return {
                        'success': True,
                        'instance_id': id_ip[0],
                        'ip_address': id_ip[1]
                    }
            
            return {'success': False, 'error': 'Failed to parse droplet info'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _deploy_aws(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy ke AWS EC2."""
        try:
            import boto3
            
            ec2 = boto3.resource(
                'ec2',
                aws_access_key_id=config['access_key'],
                aws_secret_access_key=config['secret_key'],
                region_name=config['region']
            )
            
            # Dapatkan key pair name
            key_name = self._import_ssh_key_aws(ec2, config['region'])
            
            instances = ec2.create_instances(
                ImageId='ami-0abcdef1234567890',  # Ubuntu 22.04
                MinCount=1,
                MaxCount=1,
                InstanceType=config['instance_type'],
                KeyName=key_name,
                SecurityGroupIds=self._setup_security_group_aws(ec2, config['region']),
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [{'Key': 'Name', 'Value': 'arc-agent'}]
                    }
                ]
            )
            
            instance = instances[0]
            instance.wait_until_running()
            instance.load()
            
            return {
                'success': True,
                'instance_id': instance.id,
                'ip_address': instance.public_ip_address
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _deploy_azure(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy ke Azure VM."""
        try:
            from azure.identity import ClientSecretCredential
            from azure.mgmt.compute import ComputeManagementClient
            from azure.mgmt.network import NetworkManagementClient
            from azure.mgmt.resource import ResourceManagementClient
            
            # Setup kredensial
            credential = ClientSecretCredential(
                tenant_id=config['tenant_id'],
                client_id=config['client_id'],
                client_secret=config['client_secret']
            )
            
            subscription_id = config['subscription_id']
            location = config['location']
            resource_group = 'arc-deploy-rg'
            
            # Buat resource group
            resource_client = ResourceManagementClient(credential, subscription_id)
            resource_client.resource_groups.create_or_update(
                resource_group,
                {'location': location}
            )
            
            # Setup jaringan
            network_client = NetworkManagementClient(credential, subscription_id)
            vnet_name = 'arc-vnet'
            subnet_name = 'arc-subnet'
            ip_name = 'arc-ip'
            nsg_name = 'arc-nsg'
            
            # Buat virtual network
            async_vnet = network_client.virtual_networks.begin_create_or_update(
                resource_group,
                vnet_name,
                {
                    'location': location,
                    'address_space': {'address_prefixes': ['10.0.0.0/16']}
                }
            )
            vnet_result = async_vnet.result()
            
            # Buat subnet
            async_subnet = network_client.subnets.begin_create_or_update(
                resource_group,
                vnet_name,
                subnet_name,
                {'address_prefix': '10.0.0.0/24'}
            )
            subnet_result = async_subnet.result()
            
            # Buat public IP
            async_ip = network_client.public_ip_addresses.begin_create_or_update(
                resource_group,
                ip_name,
                {
                    'location': location,
                    'public_ip_allocation_method': 'Dynamic'
                }
            )
            ip_result = async_ip.result()
            
            # Buat network security group
            nsg_params = {
                'location': location,
                'security_rules': [{
                    'name': 'SSH',
                    'protocol': 'Tcp',
                    'source_port_range': '*',
                    'destination_port_range': '22',
                    'source_address_prefix': '0.0.0.0/0',
                    'destination_address_prefix': '*',
                    'access': 'Allow',
                    'priority': 100,
                    'direction': 'Inbound'
                }]
            }
            async_nsg = network_client.network_security_groups.begin_create_or_update(
                resource_group,
                nsg_name,
                nsg_params
            )
            nsg_result = async_nsg.result()
            
            # Buat NIC
            nic_params = {
                'location': location,
                'ip_configurations': [{
                    'name': 'ipconfig1',
                    'subnet': {'id': subnet_result.id},
                    'public_ip_address': {'id': ip_result.id}
                }],
                'network_security_group': {'id': nsg_result.id}
            }
            async_nic = network_client.network_interfaces.begin_create_or_update(
                resource_group,
                'arc-nic',
                nic_params
            )
            nic_result = async_nic.result()
            
            # Buat VM
            compute_client = ComputeManagementClient(credential, subscription_id)
            vm_parameters = {
                'location': location,
                'os_profile': {
                    'computer_name': 'arc-agent',
                    'admin_username': 'arcuser',
                    'linux_configuration': {
                        'disable_password_authentication': True,
                        'ssh': {
                            'public_keys': [{
                                'path': '/home/arcuser/.ssh/authorized_keys',
                                'key_data': self._get_public_key()
                            }]
                        }
                    }
                },
                'hardware_profile': {
                    'vm_size': 'Standard_B2s'
                },
                'storage_profile': {
                    'image_reference': {
                        'publisher': 'Canonical',
                        'offer': 'UbuntuServer',
                        'sku': '18.04-LTS',
                        'version': 'latest'
                    }
                },
                'network_profile': {
                    'network_interfaces': [{'id': nic_result.id}]
                }
            }
            
            async_vm = compute_client.virtual_machines.begin_create_or_update(
                resource_group,
                'arc-agent',
                vm_parameters
            )
            vm_result = async_vm.result()
            
            return {
                'success': True,
                'instance_id': vm_result.vm_id,
                'ip_address': ip_result.ip_address
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _deploy_gcp(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy ke Google Cloud Platform."""
        try:
            from google.cloud import compute_v1
            
            # Setup kredensial
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config['credentials_file']
            
            project_id = config['project_id']
            zone = config['zone']
            machine_type = f"zones/{zone}/machineTypes/{config['machine_type']}"
            
            # Buat instance
            instance_client = compute_v1.InstancesClient()
            
            # Konfigurasi disk
            disk = compute_v1.AttachedDisk()
            initialize_params = compute_v1.AttachedDiskInitializeParams()
            initialize_params.source_image = (
                "projects/ubuntu-os-cloud/global/images/family/ubuntu-2204-lts"
            )
            initialize_params.disk_size_gb = 20
            disk.initialize_params = initialize_params
            disk.auto_delete = True
            disk.boot = True
            
            # Konfigurasi jaringan
            network_interface = compute_v1.NetworkInterface()
            network_interface.name = "global/networks/default"
            
            access_config = compute_v1.AccessConfig()
            access_config.name = "External NAT"
            access_config.type_ = "ONE_TO_ONE_NAT"
            access_config.network_tier = "PREMIUM"
            network_interface.access_configs = [access_config]
            
            # Setup SSH key
            metadata = compute_v1.Metadata()
            metadata.items = [{
                'key': 'ssh-keys',
                'value': f"arcuser:{self._get_public_key()}"
            }]
            
            # Buat instance
            instance = compute_v1.Instance()
            instance.name = "arc-agent"
            instance.disks = [disk]
            instance.machine_type = machine_type
            instance.network_interfaces = [network_interface]
            instance.metadata = metadata
            
            operation = instance_client.insert(
                project=project_id, zone=zone, instance_resource=instance
            )
            
            # Tunggu operasi selesai
            while operation.done() is False:
                time.sleep(5)
            
            if operation.error:
                return {'success': False, 'error': str(operation.error)}
            
            # Dapatkan IP publik
            instance_info = instance_client.get(project=project_id, zone=zone, instance="arc-agent")
            ip_address = None
            for interface in instance_info.network_interfaces:
                for config in interface.access_configs:
                    if config.nat_i_p:
                        ip_address = config.nat_i_p
                        break
            
            return {
                'success': True,
                'instance_id': instance_info.id,
                'ip_address': ip_address
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _deploy_hetzner(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy ke Hetzner Cloud."""
        try:
            import hcloud
            
            client = hcloud.Client(token=config['token'])
            
            # Pilih lokasi dan tipe server
            location = client.locations.get_by_name(config['location'])
            server_type = client.server_types.get_by_name(config['server_type'])
            image = client.images.get_by_name("ubuntu-22.04")
            
            # Buat server
            response = client.servers.create(
                name="arc-agent",
                server_type=server_type,
                image=image,
                location=location,
                ssh_keys=[self._get_ssh_fingerprint_hcloud(client)]
            )
            
            server = response.server
            
            # Tunggu server siap
            client.servers.wait_until_running([server])
            
            return {
                'success': True,
                'instance_id': str(server.id),
                'ip_address': server.public_net.ipv4.ip
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _deploy_linode(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy ke Linode."""
        try:
            from linode_api4 import LinodeClient
            
            client = LinodeClient(config['token'])
            
            # Buat instance
            stackscript = client.stackscripts(102637)  # StackScript Ubuntu setup
            
            instance, password = client.linode.instance_create(
                config['type'],
                config['region'],
                image="linode/ubuntu22.04",
                label="arc-agent",
                root_pass=password,
                authorized_keys=[self._get_public_key()]
            )
            
            return {
                'success': True,
                'instance_id': str(instance.id),
                'ip_address': instance.ipv4[0]
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _deploy_vultr(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy ke Vultr."""
        try:
            import vultr
            
            client = vultr.Vultr(config['api_key'])
            
            # Buat instance
            result = client.server.create(
                region=config['region'],
                plan=config['plan'],
                os='387',  # Ubuntu 22.04
                label='arc-agent',
                sshkey_id=self._get_ssh_key_vultr(client)
            )
            
            server_id = result['SUBID']
            
            # Tunggu server siap
            while True:
                server_info = client.server.list(SUBID=server_id)
                if server_info[server_id]['status'] == 'active':
                    break
                time.sleep(10)
            
            server_info = client.server.list(SUBID=server_id)
            
            return {
                'success': True,
                'instance_id': server_id,
                'ip_address': server_info[server_id]['main_ip']
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _ensure_ssh_key(self):
        """Pastikan SSH key tersedia untuk deployment."""
        if not os.path.exists(self.ssh_key_path):
            # Buat SSH key baru
            subprocess.run([
                'ssh-keygen', '-t', 'rsa', '-b', '2048', 
                '-f', self.ssh_key_path, '-N', ''
            ], check=True, timeout=30)
    
    def _get_public_key(self) -> str:
        """Dapatkan public key dalam format teks."""
        public_key_path = f"{self.ssh_key_path}.pub"
        with open(public_key_path, 'r') as f:
            return f.read().strip()
    
    def _get_ssh_fingerprint(self) -> str:
        """Dapatkan fingerprint SSH key untuk DigitalOcean."""
        result = subprocess.run([
            'ssh-keygen', '-E', 'md5', '-lf', f"{self.ssh_key_path}.pub"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return result.stdout.split()[1].replace('MD5:', '')
        return ""
    
    def _get_ssh_fingerprint_hcloud(self, client) -> str:
        """Dapatkan ID SSH key untuk Hetzner."""
        public_key = self._get_public_key()
        ssh_keys = client.ssh_keys.get_all()
        
        for key in ssh_keys:
            if key.public_key.strip() == public_key:
                return key.id
        
        # Buat SSH key baru jika belum ada
        new_key = client.ssh_keys.create(
            name="arc-deploy-key",
            public_key=public_key
        )
        return new_key.id
    
    def _get_ssh_key_vultr(self, client) -> str:
        """Dapatkan ID SSH key untuk Vultr."""
        public_key = self._get_public_key()
        ssh_keys = client.sshkey.list()
        
        for key_id, key_info in ssh_keys.items():
            if key_info['ssh_key'] == public_key:
                return key_id
        
        # Buat SSH key baru jika belum ada
        result = client.sshkey.create(
            name="arc-deploy-key",
            ssh_key=public_key
        )
        return result['SSHKEYID']
    
    def _import_ssh_key_aws(self, ec2, region: str) -> str:
        """Impor SSH key ke AWS."""
        key_name = "arc-deploy-key"
        try:
            # Coba impor key
            ec2.import_key_pair(
                KeyName=key_name,
                PublicKeyMaterial=self._get_public_key().encode()
            )
        except:
            # Key sudah ada, lanjutkan
            pass
        return key_name
    
    def _setup_security_group_aws(self, ec2, region: str) -> list:
        """Setup security group untuk AWS."""
        sg_name = "arc-agent-sg"
        try:
            sg = ec2.create_security_group(
                GroupName=sg_name,
                Description='Security group for ARC agent'
            )
            sg.authorize_ingress(
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    }
                ]
            )
            return [sg.id]
        except:
            # Security group sudah ada
            sgs = list(ec2.security_groups.filter(GroupNames=[sg_name]))
            if sgs:
                return [sgs[0].id]
            else:
                raise Exception("Failed to create security group")
    
    def _wait_for_ssh_ready(self, ip_address: str, timeout: int = 300) -> bool:
        """Tunggu SSH siap menerima koneksi."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                result = subprocess.run([
                    'ssh', '-o', 'ConnectTimeout=10',
                    '-o', 'StrictHostKeyChecking=no',
                    '-i', self.ssh_key_path,
                    f'root@{ip_address}', 'echo', 'ready'
                ], capture_output=True, timeout=15)
                
                if result.returncode == 0:
                    return True
            except:
                pass
            
            time.sleep(10)
        
        return False
    
    def _deploy_arc_to_vps(self, ip_address: str) -> Dict[str, Any]:
        """Deploy ARC ke VPS yang sudah disediakan."""
        try:
            # Salin direktori ARC ke VPS
            scp_cmd = [
                'scp', '-o', 'StrictHostKeyChecking=no',
                '-i', self.ssh_key_path,
                '-r', self.arc_dir,
                f'root@{ip_address}:/root/'
            ]
            subprocess.run(scp_cmd, check=True, timeout=600)
            
            # Jalankan skrip setup di VPS
            setup_script = '''
cd /root/arc-project &&
chmod +x local_deployer.py &&
python3 local_deployer.py --components system,ai_model,tools,environment
'''
            
            ssh_cmd = [
                'ssh', '-o', 'StrictHostKeyChecking=no',
                '-i', self.ssh_key_path,
                f'root@{ip_address}', setup_script
            ]
            subprocess.run(ssh_cmd, check=True, timeout=1200)
            
            return {'success': True}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}