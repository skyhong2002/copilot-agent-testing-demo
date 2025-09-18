import base64
import logging
from typing import Any, Optional
from .config import APIConfig
from .exceptions import EncryptionError

logger = logging.getLogger(__name__)

class EncryptionService:
    """Handles data encryption and decryption operations."""

    def __init__(self, api_config: APIConfig):
        self.encryption_key = api_config.encryption_key

    def encrypt_data(self, data: Any) -> str:
        """Encrypt data using base64 encoding (demo implementation)."""
        try:
            data_bytes = str(data).encode('utf-8')
            encrypted = base64.b64encode(data_bytes).decode('utf-8')
            logger.debug("Data encrypted successfully")
            return encrypted
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise EncryptionError(f"Encryption failed: {str(e)}")

    def decrypt_data(self, encrypted_data: str) -> Optional[str]:
        """Decrypt data using base64 decoding (demo implementation)."""
        try:
            decrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted = decrypted_bytes.decode('utf-8')
            logger.debug("Data decrypted successfully")
            return decrypted
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise EncryptionError(f"Decryption failed: {str(e)}")