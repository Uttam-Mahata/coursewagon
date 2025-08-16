from extensions import db
import logging

logger = logging.getLogger(__name__)

def remove_api_key_columns():
    """Remove API key columns from User model since we're using environment variables"""
    try:
        # Get database engine
        engine = db.engine
        
        # Use a more direct approach to check and remove columns
        with engine.connect() as connection:
            # Check if api_key column exists and remove it
            try:
                logger.info("Attempting to remove api_key column from users table")
                result = connection.execute(db.text('ALTER TABLE users DROP COLUMN api_key'))
                logger.info("Successfully removed api_key column")
            except Exception as e:
                logger.info(f"api_key column may not exist or already removed: {str(e)}")
                
            # Check if encrypted_api_key column exists and remove it  
            try:
                logger.info("Attempting to remove encrypted_api_key column from users table")
                result = connection.execute(db.text('ALTER TABLE users DROP COLUMN encrypted_api_key'))
                logger.info("Successfully removed encrypted_api_key column")
            except Exception as e:
                logger.info(f"encrypted_api_key column may not exist or already removed: {str(e)}")
                
            connection.commit()
            
        logger.info("API key columns removal migration completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error during API key columns removal migration: {str(e)}")
        return False
