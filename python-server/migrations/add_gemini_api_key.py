from extensions import db
import logging

logger = logging.getLogger(__name__)

def add_gemini_api_key_column():
    """Add encrypted_gemini_api_key column to user table for BYOK support"""
    try:
        engine = db.engine
        with engine.connect() as connection:
            try:
                connection.execute(db.text(
                    'ALTER TABLE `user` ADD COLUMN encrypted_gemini_api_key TEXT NULL'
                ))
                connection.commit()
                logger.info("Added encrypted_gemini_api_key column to user table")
            except Exception as e:
                if 'Duplicate column' in str(e) or '1060' in str(e):
                    logger.info("encrypted_gemini_api_key column already exists, skipping")
                else:
                    logger.warning(f"Could not add encrypted_gemini_api_key column: {str(e)}")
        return True
    except Exception as e:
        logger.error(f"Error during add_gemini_api_key migration: {str(e)}")
        return False
