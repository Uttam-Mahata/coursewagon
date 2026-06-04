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
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'user'
            AND COLUMN_NAME = 'email_verified'
        """))

        row = result.fetchone()
        count = row[0] if row else 0
        column_exists = count > 0

        if not column_exists:
            logger.info("Adding email_verified column to user table...")

            # Add the email_verified column with default value 0 (False)
            session.execute(text("""
                ALTER TABLE [user]
                ADD email_verified BIT DEFAULT 0 NOT NULL
            """))

            # Mark existing users as verified (they're already active)
            session.execute(text("""
                UPDATE [user]
                SET email_verified = 1
            """))

            session.commit()
            logger.info("Successfully added email_verified column to user table")
        else:
            logger.info("email_verified column already exists in user table")

        # Check if email_verification_sent_at column already exists
        result = session.execute(text("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'user'
            AND COLUMN_NAME = 'email_verification_sent_at'
        """))

        row = result.fetchone()
        count = row[0] if row else 0
        column_exists = count > 0

        if not column_exists:
            logger.info("Adding email_verification_sent_at column to user table...")

            # Add the email_verification_sent_at column
            session.execute(text("""
                ALTER TABLE [user]
                ADD email_verification_sent_at DATETIME NULL
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
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_NAME = 'email_verification'
        """))

        row = result.fetchone()
        count = row[0] if row else 0
        table_exists = count > 0

        if not table_exists:
            logger.info("Creating email_verification table...")

            # Create the table
            session.execute(text("""
                IF OBJECT_ID('email_verification', 'U') IS NULL
                CREATE TABLE email_verification (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    user_id INT NOT NULL,
                    token NVARCHAR(255) NOT NULL UNIQUE,
                    created_at DATETIME DEFAULT GETDATE(),
                    expires_at DATETIME NOT NULL,
                    used BIT DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES [user](id) ON DELETE CASCADE
                )
            """))

            # Create indexes separately (MSSQL does not support inline INDEX in CREATE TABLE)
            session.execute(text("""
                IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'idx_ev_token' AND object_id = OBJECT_ID('email_verification'))
                    CREATE INDEX idx_ev_token ON email_verification(token)
            """))

            session.execute(text("""
                IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'idx_ev_user_id' AND object_id = OBJECT_ID('email_verification'))
                    CREATE INDEX idx_ev_user_id ON email_verification(user_id)
            """))

            session.execute(text("""
                IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'idx_ev_expires_at' AND object_id = OBJECT_ID('email_verification'))
                    CREATE INDEX idx_ev_expires_at ON email_verification(expires_at)
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
