"""
Migration script to add welcome_email_sent field to user table
Run this script after updating the User model
"""
from sqlalchemy import text
from extensions import SessionLocal
import logging

logger = logging.getLogger(__name__)

def add_welcome_email_sent_column():
    """Add welcome_email_sent column to user table if it doesn't exist"""
    session = SessionLocal()
    try:
        # Check if column already exists
        result = session.execute(text("""
            SELECT COUNT(*) as count 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'user' 
            AND COLUMN_NAME = 'welcome_email_sent'
        """))
        
        column_exists = result.fetchone().count > 0
        
        if not column_exists:
            logger.info("Adding welcome_email_sent column to user table...")
            
            # Add the column with default value False
            session.execute(text("""
                ALTER TABLE user 
                ADD COLUMN welcome_email_sent BOOLEAN DEFAULT FALSE
            """))
            
            # Update existing users to have welcome_email_sent = TRUE
            # (assuming they already received welcome emails or don't need them)
            session.execute(text("""
                UPDATE user 
                SET welcome_email_sent = TRUE 
                WHERE welcome_email_sent IS NULL
            """))
            
            session.commit()
            logger.info("Successfully added welcome_email_sent column to user table")
            
        else:
            logger.info("welcome_email_sent column already exists in user table")
            
    except Exception as e:
        session.rollback()
        logger.error(f"Error adding welcome_email_sent column: {str(e)}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    # Run migration
    add_welcome_email_sent_column()
