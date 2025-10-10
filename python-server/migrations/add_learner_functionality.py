"""
Migration script to add course learner functionality
This includes:
- Adding role, bio, and profile_image_url to user table
- Adding publishing fields to courses table
- Creating enrollments table
- Creating learning_progress table
"""
from sqlalchemy import text
from extensions import SessionLocal
import logging

logger = logging.getLogger(__name__)

def add_user_role_fields():
    """Add role, bio, and profile_image_url columns to user table"""
    session = SessionLocal()
    try:
        # Check if role column exists
        result = session.execute(text("""
            SELECT COUNT(*) as count
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'user'
            AND COLUMN_NAME = 'role'
        """))

        if result.fetchone().count == 0:
            logger.info("Adding role, bio, and profile_image_url columns to user table...")

            # Add role column
            session.execute(text("""
                ALTER TABLE user
                ADD COLUMN role VARCHAR(50) DEFAULT 'both' NOT NULL
            """))

            # Add bio column
            session.execute(text("""
                ALTER TABLE user
                ADD COLUMN bio TEXT NULL
            """))

            # Add profile_image_url column
            session.execute(text("""
                ALTER TABLE user
                ADD COLUMN profile_image_url VARCHAR(512) NULL
            """))

            session.commit()
            logger.info("Successfully added role fields to user table")
        else:
            logger.info("User role fields already exist")

    except Exception as e:
        session.rollback()
        logger.error(f"Error adding user role fields: {str(e)}")
        raise
    finally:
        session.close()

def add_course_publishing_fields():
    """Add publishing-related fields to courses table"""
    session = SessionLocal()
    try:
        # Check if is_published column exists
        result = session.execute(text("""
            SELECT COUNT(*) as count
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'courses'
            AND COLUMN_NAME = 'is_published'
        """))

        if result.fetchone().count == 0:
            logger.info("Adding publishing fields to courses table...")

            session.execute(text("""
                ALTER TABLE courses
                ADD COLUMN is_published BOOLEAN DEFAULT FALSE NOT NULL,
                ADD COLUMN published_at DATETIME NULL,
                ADD COLUMN category VARCHAR(100) NULL,
                ADD COLUMN difficulty_level VARCHAR(50) NULL,
                ADD COLUMN estimated_duration_hours INT NULL,
                ADD COLUMN enrollment_count INT DEFAULT 0 NOT NULL
            """))

            session.commit()
            logger.info("Successfully added publishing fields to courses table")
        else:
            logger.info("Course publishing fields already exist")

    except Exception as e:
        session.rollback()
        logger.error(f"Error adding course publishing fields: {str(e)}")
        raise
    finally:
        session.close()

def create_enrollments_table():
    """Create enrollments table"""
    session = SessionLocal()
    try:
        # Check if table exists
        result = session.execute(text("""
            SELECT COUNT(*) as count
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'enrollments'
        """))

        if result.fetchone().count == 0:
            logger.info("Creating enrollments table...")

            session.execute(text("""
                CREATE TABLE enrollments (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    course_id INT NOT NULL,
                    enrolled_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'active' NOT NULL,
                    progress_percentage FLOAT DEFAULT 0.0 NOT NULL,
                    last_accessed_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    completed_at DATETIME NULL,
                    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
                    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_enrollment (user_id, course_id)
                )
            """))

            session.commit()
            logger.info("Successfully created enrollments table")
        else:
            logger.info("Enrollments table already exists")

    except Exception as e:
        session.rollback()
        logger.error(f"Error creating enrollments table: {str(e)}")
        raise
    finally:
        session.close()

def create_learning_progress_table():
    """Create learning_progress table"""
    session = SessionLocal()
    try:
        # Check if table exists
        result = session.execute(text("""
            SELECT COUNT(*) as count
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'learning_progress'
        """))

        if result.fetchone().count == 0:
            logger.info("Creating learning_progress table...")

            session.execute(text("""
                CREATE TABLE learning_progress (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    enrollment_id INT NOT NULL,
                    topic_id INT NOT NULL,
                    content_id INT NULL,
                    completed BOOLEAN DEFAULT FALSE NOT NULL,
                    time_spent_seconds INT DEFAULT 0 NOT NULL,
                    last_position TEXT NULL,
                    started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME NULL,
                    last_accessed_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE,
                    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
                    FOREIGN KEY (content_id) REFERENCES content(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_progress (enrollment_id, topic_id)
                )
            """))

            session.commit()
            logger.info("Successfully created learning_progress table")
        else:
            logger.info("Learning progress table already exists")

    except Exception as e:
        session.rollback()
        logger.error(f"Error creating learning_progress table: {str(e)}")
        raise
    finally:
        session.close()

def run_all_migrations():
    """Run all migrations in order"""
    logger.info("Starting learner functionality migration...")

    add_user_role_fields()
    add_course_publishing_fields()
    create_enrollments_table()
    create_learning_progress_table()

    logger.info("All learner functionality migrations completed successfully!")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_all_migrations()
