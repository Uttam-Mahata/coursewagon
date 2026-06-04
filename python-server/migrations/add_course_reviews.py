"""
Migration script to add course reviews and ratings functionality
This includes:
- Adding average_rating and review_count to courses table
- Creating course_reviews table with relationships and constraints
"""
from sqlalchemy import text
from extensions import SessionLocal
import logging

logger = logging.getLogger(__name__)

def add_course_rating_fields():
    """Add average_rating and review_count columns to courses table"""
    session = SessionLocal()
    try:
        # Check if average_rating column exists
        result = session.execute(text("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'courses'
            AND COLUMN_NAME = 'average_rating'
        """))

        row = result.fetchone()
        count = row[0] if row else 0

        if count == 0:
            logger.info("Adding rating fields to courses table...")

            session.execute(text("""
                ALTER TABLE courses
                ADD average_rating FLOAT DEFAULT 0.0 NOT NULL
            """))

            session.execute(text("""
                ALTER TABLE courses
                ADD review_count INT DEFAULT 0 NOT NULL
            """))

            session.commit()
            logger.info("Successfully added rating fields to courses table")
        else:
            logger.info("Course rating fields already exist")

    except Exception as e:
        session.rollback()
        logger.error(f"Error adding course rating fields: {str(e)}")
        raise
    finally:
        session.close()

def create_course_reviews_table():
    """Create course_reviews table"""
    session = SessionLocal()
    try:
        # Check if table exists
        result = session.execute(text("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_NAME = 'course_reviews'
        """))

        row = result.fetchone()
        count = row[0] if row else 0

        if count == 0:
            logger.info("Creating course_reviews table...")

            session.execute(text("""
                IF OBJECT_ID('course_reviews', 'U') IS NULL
                CREATE TABLE course_reviews (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    user_id INT NOT NULL,
                    course_id INT NOT NULL,
                    enrollment_id INT NOT NULL,
                    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
                    review_text NVARCHAR(MAX) NULL,
                    is_visible BIT DEFAULT 1 NOT NULL,
                    helpful_count INT DEFAULT 0 NOT NULL,
                    created_at DATETIME NOT NULL DEFAULT GETDATE(),
                    updated_at DATETIME NOT NULL DEFAULT GETDATE(),
                    FOREIGN KEY (user_id) REFERENCES [user](id) ON DELETE CASCADE,
                    FOREIGN KEY (course_id) REFERENCES courses(id),
                    FOREIGN KEY (enrollment_id) REFERENCES enrollments(id),
                    CONSTRAINT unique_user_course_review UNIQUE (user_id, course_id)
                )
            """))

            # Create indexes separately (MSSQL does not support inline INDEX in CREATE TABLE)
            session.execute(text("""
                IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'idx_course_visible' AND object_id = OBJECT_ID('course_reviews'))
                    CREATE INDEX idx_course_visible ON course_reviews(course_id, is_visible)
            """))

            session.execute(text("""
                IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'idx_user_course' AND object_id = OBJECT_ID('course_reviews'))
                    CREATE INDEX idx_user_course ON course_reviews(user_id, course_id)
            """))

            session.execute(text("""
                IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'idx_rating' AND object_id = OBJECT_ID('course_reviews'))
                    CREATE INDEX idx_rating ON course_reviews(course_id, rating)
            """))

            session.commit()
            logger.info("Successfully created course_reviews table")
        else:
            logger.info("Course reviews table already exists")

    except Exception as e:
        session.rollback()
        logger.error(f"Error creating course_reviews table: {str(e)}")
        raise
    finally:
        session.close()

def run_migration():
    """Run all review migrations in order"""
    logger.info("Starting course reviews migration...")

    add_course_rating_fields()
    create_course_reviews_table()

    logger.info("All course reviews migrations completed successfully!")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_migration()
