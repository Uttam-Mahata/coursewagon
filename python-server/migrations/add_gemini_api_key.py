from extensions import db
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

def add_gemini_api_key_column():
    """Add encrypted_gemini_api_key column to user table for BYOK support"""
    try:
        engine = db.engine
        with engine.connect() as connection:
            try:
                connection.execute(text(
                    'ALTER TABLE [user] ADD encrypted_gemini_api_key NVARCHAR(MAX) NULL'
                ))
                connection.commit()
                logger.info("Added encrypted_gemini_api_key column to user table")
            except Exception as e:
                # MSSQL error 2705: column already exists in the table
                if '2705' in str(e) or 'already exists' in str(e).lower():
                    logger.info("encrypted_gemini_api_key column already exists, skipping")
                else:
                    logger.warning(f"Could not add encrypted_gemini_api_key column: {str(e)}")
        return True
    except Exception as e:
        logger.error(f"Error during add_gemini_api_key migration: {str(e)}")
        return False
