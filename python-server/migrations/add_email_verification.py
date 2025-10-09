"""
Migration script to add email verification functionality
1. Add email_verified and email_verification_sent_at columns to user table
2. Create email_verification table

Run this script after updating the User model and creating EmailVerification model
"""
from sqlalchemy import text
from extensions import SessionLocal
import logging

logger = logging.getLogger(__name__)

def add_email_verification_to_user_table():
    """Add email verification columns to user table"""
    session = SessionLocal()
    try:
        # Check if email_verified column already exists
        result = session.execute(text("""
            SELECT COUNT(*) as count
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'user'
            AND COLUMN_NAME = 'email_verified'
        """))

        column_exists = result.fetchone().count > 0

        if not column_exists:
            logger.info("Adding email_verified column to user table...")

            # Add the email_verified column with default value False
            session.execute(text("""
                ALTER TABLE user
                ADD COLUMN email_verified BOOLEAN DEFAULT FALSE NOT NULL
            """))

            # Mark existing users as verified (they're already active)
            session.execute(text("""
                UPDATE user
                SET email_verified = TRUE
            """))

            session.commit()
            logger.info("Successfully added email_verified column to user table")
        else:
            logger.info("email_verified column already exists in user table")

        # Check if email_verification_sent_at column already exists
        result = session.execute(text("""
            SELECT COUNT(*) as count
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'user'
            AND COLUMN_NAME = 'email_verification_sent_at'
        """))

        column_exists = result.fetchone().count > 0

        if not column_exists:
            logger.info("Adding email_verification_sent_at column to user table...")

            # Add the email_verification_sent_at column
            session.execute(text("""
                ALTER TABLE user
                ADD COLUMN email_verification_sent_at DATETIME NULL
            """))

            session.commit()
            logger.info("Successfully added email_verification_sent_at column to user table")
        else:
            logger.info("email_verification_sent_at column already exists in user table")

    except Exception as e:
        session.rollback()
        logger.error(f"Error adding email verification columns: {str(e)}")
        raise
    finally:
        session.close()

def create_email_verification_table():
    """Create email_verification table"""
    session = SessionLocal()
    try:
        # Check if table already exists
        result = session.execute(text("""
            SELECT COUNT(*) as count
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'email_verification'
        """))

        table_exists = result.fetchone().count > 0

        if not table_exists:
            logger.info("Creating email_verification table...")

            # Create the table
            session.execute(text("""
                CREATE TABLE email_verification (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    token VARCHAR(255) NOT NULL UNIQUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME NOT NULL,
                    used BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
                    INDEX idx_token (token),
                    INDEX idx_user_id (user_id),
                    INDEX idx_expires_at (expires_at)
                )
            """))

            session.commit()
            logger.info("Successfully created email_verification table")
        else:
            logger.info("email_verification table already exists")

    except Exception as e:
        session.rollback()
        logger.error(f"Error creating email_verification table: {str(e)}")
        raise
    finally:
        session.close()

def run_migration():
    """Run all email verification migrations"""
    logger.info("Starting email verification migration...")

    # Add columns to user table
    add_email_verification_to_user_table()

    # Create email_verification table
    create_email_verification_table()

    logger.info("Email verification migration completed successfully!")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Run migration
    run_migration()
