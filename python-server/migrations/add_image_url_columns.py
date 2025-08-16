from extensions import db
from models.course import Course
from models.subject import Subject
import logging

logger = logging.getLogger(__name__)

def add_image_url_columns():
    """Add image_url columns to Course and Subject models if they don't exist"""
    try:
        # Get database engine
        engine = db.engine
        inspector = db.inspect(engine)
        
        # Check if image_url column exists in courses table
        courses_columns = [col['name'] for col in inspector.get_columns('courses')]
        if 'image_url' not in courses_columns:
            logger.info("Adding image_url column to courses table")
            engine.execute('ALTER TABLE courses ADD COLUMN image_url VARCHAR(512);')
        
        # Check if image_url column exists in subjects table
        subjects_columns = [col['name'] for col in inspector.get_columns('subjects')]
        if 'image_url' not in subjects_columns:
            logger.info("Adding image_url column to subjects table")
            engine.execute('ALTER TABLE subjects ADD COLUMN image_url VARCHAR(512);')
            
        logger.info("Migration completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        return False
