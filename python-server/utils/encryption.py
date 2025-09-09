from cryptography.fernet import Fernet
import os
import base64
import logging
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dotenv import load_dotenv


logger = logging.getLogger(__name__)

load_dotenv()

class EncryptionService:
    """Service for handling encryption and decryption of sensitive data"""
    
    def __init__(self):
        # Get the encryption key from environment variable
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        if not encryption_key:
            logger.critical("ENCRYPTION_KEY not found in environment variables!")
            raise ValueError("Encryption key not configured")
            
        # Get salt from environment - handle both string and bytes
        salt_value = os.environ.get('ENCRYPTION_SALT', 'coursewagon_salt')
        if isinstance(salt_value, str):
            self.salt = salt_value.encode()
        else:
            self.salt = salt_value
        
        # Derive a proper key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(encryption_key.encode()))
        self.cipher = Fernet(key)
    
    def encrypt(self, text):
        """Encrypt plaintext data"""
        if not text:
            return None
        try:
            return self.cipher.encrypt(text.encode()).decode()
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            raise
    
    def decrypt(self, encrypted_text):
        """Decrypt encrypted data"""
        if not encrypted_text:
            return None
        try:
            return self.cipher.decrypt(encrypted_text.encode()).decode()
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            raise
