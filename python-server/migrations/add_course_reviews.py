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
            SELECT COUNT(*) as count
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'courses'
            AND COLUMN_NAME = 'average_rating'
        """))

        if result.fetchone().count == 0:
            logger.info("Adding rating fields to courses table...")

            session.execute(text("""
                ALTER TABLE courses
                ADD COLUMN average_rating FLOAT DEFAULT 0.0 NOT NULL,
                ADD COLUMN review_count INT DEFAULT 0 NOT NULL
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
            SELECT COUNT(*) as count
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'course_reviews'
        """))

        if result.fetchone().count == 0:
            logger.info("Creating course_reviews table...")

            session.execute(text("""
                CREATE TABLE course_reviews (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    course_id INT NOT NULL,
                    enrollment_id INT NOT NULL,
                    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
                    review_text TEXT NULL,
                    is_visible BOOLEAN DEFAULT TRUE NOT NULL,
                    helpful_count INT DEFAULT 0 NOT NULL,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
                    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
                    FOREIGN KEY (enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_user_course_review (user_id, course_id),
                    INDEX idx_course_visible (course_id, is_visible),
                    INDEX idx_user_course (user_id, course_id),
                    INDEX idx_rating (course_id, rating)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
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
