"""
Config Loader - Membaca konfigurasi terpusat dari ~/.arc/config.yaml.

Mendukung 2 sumber konfigurasi:
1. config.yaml - konfigurasi manual yang mudah dibaca/diedit user
   ~/.arc/config.yaml
2. CredentialVault GPG - penyimpanan terenkripsi untuk kredensial sensitif
   ~/.arc/vault/credentials.gpg

Prioritas (higher wins):
1. Environment variables (NVD_API_KEY, dll)
2. config.yaml
3. CredentialVault GPG
"""

import os
import json
from typing import Dict, Any, Optional


class ConfigLoader:
    """Loader terpusat untuk semua konfigurasi ARC."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.expanduser("~/.arc/config.yaml")
        self._config = None

    def load(self) -> Dict[str, Any]:
        """Muat konfigurasi dari config.yaml."""
        if self._config is not None:
            return self._config

        self._config = {}

        if not os.path.exists(self.config_path):
            return self._config

        try:
            # Coba YAML dulu
            try:
                import yaml
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = yaml.safe_load(f) or {}
            except ImportError:
                # Fallback ke JSON jika yaml tidak terinstall
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f) or {}
        except Exception as e:
            print(f"⚠️ Config load warning: {e}")
            self._config = {}

        return self._config

    def get(self, *keys: str, default: Any = None) -> Any:
        """
        Dapatkan nilai dari config.yaml dengan nested key.
        Contoh: get('credentials', 'bug_bounty', 'hackerone_main', 'api_token')
        """
        data = self.load()
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    def get_platform_credentials(self, platform: str) -> Dict[str, Any]:
        """
        Dapatkan kredensial untuk platform tertentu dari config.yaml.
        Mencoba berbagai naming convention (hackerone_main, hackerone_researcher, dll).
        """
        creds = self.get('credentials', 'bug_bounty', default={})
        ctf_creds = self.get('credentials', 'ctf', default={})

        # Cek di bug_bounty section
        if platform in creds and isinstance(creds[platform], dict):
            return creds[platform]

        # Cek di ctf section
        if platform in ctf_creds and isinstance(ctf_creds[platform], dict):
            return ctf_creds[platform]

        # Fallback: cari key yang mengandung platform name
        for key, value in {**creds, **ctf_creds}.items():
            if platform in key and isinstance(value, dict):
                return value

        return {}

    def get_api_key(self, service: str) -> Optional[str]:
        """
        Dapatkan API key dari config.yaml.
        Prioritas:
        1. Environment variable (contoh: NVD_API_KEY)
        2. config.yaml -> credentials.api_keys.<service>

        Args:
            service: Nama service (nvd, shodan, github, dll)

        Returns:
            API key atau None
        """
        # 1. Environment variable (nama service uppercase)
        env_var = f"{service.upper()}_API_KEY"
        env_value = os.environ.get(env_var)
        if env_value:
            return env_value

        # 2. config.yaml -> credentials.api_keys.<service>
        config_value = self.get('credentials', 'api_keys', service)
        if config_value:
            return config_value

        # 3. config.yaml -> api_keys.<service> (alternatif)
        alt_value = self.get('api_keys', service)
        if alt_value:
            return alt_value

        return None

    def get_all_config(self) -> Dict[str, Any]:
        """Dapatkan seluruh konfigurasi."""
        return self.load()


# Singleton global untuk menghindari baca file berkali-kali
_config_loader_instance = None


def get_config_loader() -> ConfigLoader:
    """
    Dapatkan instance ConfigLoader tunggal (singleton).
    Menghindari duplikasi pembacaan file dan memori.
    """
    global _config_loader_instance
    if _config_loader_instance is None:
        _config_loader_instance = ConfigLoader()
    return _config_loader_instance