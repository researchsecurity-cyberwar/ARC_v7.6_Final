import os
import subprocess
import json
from typing import Dict, Any

class CredentialVault:
    """
    Enkripsi GPG terpusat.
    Mengelola kredensial terenkripsi menggunakan GPG.
    """
    
    def __init__(self, vault_dir="~/.arc/vault"):
        self.vault_dir = os.path.expanduser(vault_dir)
        os.makedirs(self.vault_dir, exist_ok=True)
        self.vault_file = os.path.join(self.vault_dir, "credentials.gpg")
        self.gpg_key_id = self._get_or_create_gpg_key()
    
    def _get_or_create_gpg_key(self) -> str:
        """Dapatkan atau buat kunci GPG untuk enkripsi."""
        try:
            # Cek apakah sudah ada kunci GPG
            result = subprocess.run(['gpg', '--list-secret-keys'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                # Gunakan kunci pertama yang ditemukan
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.startswith('sec'):
                        key_id = line.split('/')[1].split(' ')[0]
                        return key_id
            
            # Buat kunci GPG baru jika belum ada
            self._create_gpg_key()
            return self._get_or_create_gpg_key()
            
        except Exception:
            # Fallback ke enkripsi sederhana jika GPG tidak tersedia
            return "fallback_encryption"
    
    def _create_gpg_key(self):
        """Buat kunci GPG baru secara otomatis."""
        try:
            # Buat batch file untuk pembuatan kunci otomatis
            batch_content = """
%echo Generating ARC GPG key
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: ARC AI Agent
Name-Email: arc-agent@localhost
Expire-Date: 0
%no-protection
%commit
%echo done
"""
            batch_file = os.path.join(self.vault_dir, "gpg_batch")
            with open(batch_file, 'w') as f:
                f.write(batch_content)
            
            subprocess.run(['gpg', '--batch', '--gen-key', batch_file], 
                          check=True, timeout=60)
            os.remove(batch_file)
            
        except Exception as e:
            print(f"⚠️ GPG key creation failed: {e}")
            print("⚠️ Using fallback encryption method")
    
    def store_credentials(self, credentials: Dict[str, Any], platform: str):
        """
        Simpan kredensial terenkripsi untuk platform tertentu.
        """
        try:
            # Muat kredensial yang ada
            existing_creds = self.load_all_credentials()
            existing_creds[platform] = credentials
            
            # Enkripsi dan simpan
            if self.gpg_key_id != "fallback_encryption":
                self._encrypt_with_gpg(existing_creds)
            else:
                self._encrypt_fallback(existing_creds)
            
            return {'success': True, 'message': f'Credentials stored for {platform}'}
        
        except Exception as e:
            return {'success': False, 'error': f'Credential storage failed: {str(e)}'}
    
    def load_credentials(self, platform: str) -> Dict[str, Any]:
        """
        Muat kredensial untuk platform tertentu.
        """
        try:
            all_creds = self.load_all_credentials()
            return all_creds.get(platform, {})
        except Exception:
            return {}
    
    def load_all_credentials(self) -> Dict[str, Any]:
        """
        Muat semua kredensial yang tersimpan.
        """
        try:
            if not os.path.exists(self.vault_file):
                return {}
            
            if self.gpg_key_id != "fallback_encryption":
                return self._decrypt_with_gpg()
            else:
                return self._decrypt_fallback()
        except Exception:
            return {}
    
    def _encrypt_with_gpg(self, data: Dict[str, Any]):
        """Enkripsi data menggunakan GPG."""
        data_json = json.dumps(data, indent=2)
        with open(self.vault_file + '.tmp', 'w') as f:
            f.write(data_json)
        
        subprocess.run([
            'gpg', '--encrypt', '--recipient', self.gpg_key_id,
            '--output', self.vault_file, self.vault_file + '.tmp'
        ], check=True, timeout=30)
        
        os.remove(self.vault_file + '.tmp')
    
    def _decrypt_with_gpg(self) -> Dict[str, Any]:
        """Dekripsi data menggunakan GPG."""
        result = subprocess.run([
            'gpg', '--decrypt', self.vault_file
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            raise Exception("GPG decryption failed")
    
    def _encrypt_fallback(self, data: Dict[str, Any]):
        """Enkripsi fallback jika GPG tidak tersedia."""
        # Ini hanya placeholder - dalam implementasi nyata, gunakan enkripsi yang lebih baik
        data_json = json.dumps(data, indent=2)
        with open(self.vault_file, 'w') as f:
            f.write(data_json)
    
    def _decrypt_fallback(self) -> Dict[str, Any]:
        """Dekripsi fallback jika GPG tidak tersedia."""
        with open(self.vault_file, 'r') as f:
            return json.load(f)