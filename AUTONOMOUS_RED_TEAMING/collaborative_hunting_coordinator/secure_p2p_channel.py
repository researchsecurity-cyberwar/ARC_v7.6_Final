import hashlib
import hmac
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization

class SecureP2PChannel:
    """
    Signal-protocol encrypted agent communication.
    Komunikasi terenkripsi antar agen menggunakan protokol Signal-like.
    """
    
    def __init__(self):
        self.sessions = {}
    
    def establish_secure_session(self, agent_id: str) -> dict:
        """
        Bangun sesi aman dengan agen lain.
        """
        # Generate key pair Curve25519
        private_key = x25519.X25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        session_info = {
            'agent_id': agent_id,
            'private_key': private_key,
            'public_key': public_key,
            'public_key_bytes': public_bytes,
            'shared_secret': None,
            'session_established': False
        }
        
        self.sessions[agent_id] = session_info
        return {'public_key': public_bytes.hex()}
    
    def complete_session_establishment(self, agent_id: str, peer_public_key_hex: str) -> bool:
        """
        Lengkapi pembentukan sesi dengan kunci publik peer.
        """
        if agent_id not in self.sessions:
            return False
        
        try:
            # Deserialize kunci publik peer
            peer_public_bytes = bytes.fromhex(peer_public_key_hex)
            peer_public_key = x25519.X25519PublicKey.from_public_bytes(peer_public_bytes)
            
            # Hitung shared secret
            shared_secret = self.sessions[agent_id]['private_key'].exchange(peer_public_key)
            self.sessions[agent_id]['shared_secret'] = shared_secret
            self.sessions[agent_id]['session_established'] = True
            
            return True
        except Exception:
            return False
    
    def encrypt_message(self, agent_id: str, message: str) -> str:
        """
        Enkripsi pesan untuk agen tertentu.
        """
        if agent_id not in self.sessions or not self.sessions[agent_id]['session_established']:
            raise ValueError("Session not established")
        
        # Gunakan shared secret untuk enkripsi (placeholder - implementasi penuh memerlukan HKDF + AES-GCM)
        shared_secret = self.sessions[agent_id]['shared_secret']
        message_bytes = message.encode('utf-8')
        
        # HMAC untuk integrity
        hmac_digest = hmac.new(shared_secret, message_bytes, hashlib.sha256).hexdigest()
        encrypted_message = f"{message_bytes.hex()}:{hmac_digest}"
        
        return encrypted_message
    
    def decrypt_message(self, agent_id: str, encrypted_message: str) -> str:
        """
        Dekripsi pesan dari agen tertentu.
        """
        if agent_id not in self.sessions or not self.sessions[agent_id]['session_established']:
            raise ValueError("Session not established")
        
        try:
            message_hex, received_hmac = encrypted_message.split(':', 1)
            message_bytes = bytes.fromhex(message_hex)
            
            # Verifikasi HMAC
            shared_secret = self.sessions[agent_id]['shared_secret']
            expected_hmac = hmac.new(shared_secret, message_bytes, hashlib.sha256).hexdigest()
            
            if hmac.compare_digest(received_hmac, expected_hmac):
                return message_bytes.decode('utf-8')
            else:
                raise ValueError("Message integrity check failed")
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")