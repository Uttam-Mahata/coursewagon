"""
Migration script to add video_url column to content table
"""
from sqlalchemy import text
from extensions import SessionLocal
import logging

logger = logging.getLogger(__name__)

def add_video_url_to_content():
    """Add video_url column to content table if it doesn't exist"""
    session = SessionLocal()
    try:
        # Check if video_url column already exists
        result = session.execute(text("""
            SELECT COUNT(*) as count
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'content'
            AND COLUMN_NAME = 'video_url'
        """))

        column_exists = result.fetchone().count > 0

        if not column_exists:
            logger.info("Adding video_url column to content table...")

            # Add the video_url column
            session.execute(text("""
                ALTER TABLE content
                ADD COLUMN video_url TEXT NULL
            """))

            session.commit()
            logger.info("Successfully added video_url column to content table")
        else:
            logger.info("video_url column already exists in content table")

        return True

    except Exception as e:
        session.rollback()
        logger.error(f"Error during migration: {str(e)}")
        return False
    finally:
        session.close()
