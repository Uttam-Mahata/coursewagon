"""
Migration script to add is_admin column to user table
"""
from sqlalchemy import text
from extensions import SessionLocal
import logging

logger = logging.getLogger(__name__)

def add_is_admin_column():
    """Add is_admin column to user table if it doesn't exist"""
    session = SessionLocal()
    try:
        # Check if is_admin column already exists
        result = session.execute(text("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'user'
            AND COLUMN_NAME = 'is_admin'
        """))

        row = result.fetchone()
        count = row[0] if row else 0
        column_exists = count > 0

        if not column_exists:
            logger.info("Adding is_admin column to user table...")

            session.execute(text("""
                ALTER TABLE [user]
                ADD is_admin BIT DEFAULT 0 NOT NULL
            """))

            session.commit()
            logger.info("Successfully added is_admin column to user table")
        else:
            logger.info("is_admin column already exists in user table")

    except Exception as e:
        session.rollback()
        logger.error(f"Error adding is_admin column: {str(e)}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    add_is_admin_column()
