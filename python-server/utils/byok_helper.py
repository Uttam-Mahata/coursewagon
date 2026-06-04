import logging
from typing import Optional

logger = logging.getLogger(__name__)

def get_user_gemini_key(user_id: int, db) -> Optional[str]:
    """Return the decrypted Gemini API key for a user, or None if not set."""
    try:
        from repositories.user_repository import UserRepository
        from utils.encryption import EncryptionService

        user_repo = UserRepository(db)
        user = user_repo.get_user_by_id(user_id)
        if not user or not user.encrypted_gemini_api_key:
            return None
        enc = EncryptionService()
        return enc.decrypt(user.encrypted_gemini_api_key)
    except Exception as e:
        logger.warning(f"Could not retrieve user Gemini key for user {user_id}: {str(e)}")
        return None
