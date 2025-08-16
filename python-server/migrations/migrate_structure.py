import logging
from extensions import db
from models.chapter import Chapter
from models.content import Content
from models.topic import Topic
from sqlalchemy import text

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def migrate_database_structure():
    """
    Migrate database from Course > Subject > Module > Chapter > Topic > Subtopic > Content
    to Course > Subject > Chapter > Topic > Content
    """
    try:
        logger.info("Starting database structure migration...")
        
        # 1. Create temporary tables to store relationships
        logger.info("Creating temporary mapping tables...")
        create_temp_tables()
        
        # 2. Store current relationships
        logger.info("Storing current relationships...")
        store_relationships()
        
        # 3. Update chapters to reference subjects instead of modules
        logger.info("Updating chapters to reference subjects...")
        update_chapters()
        
        # 4. Update content to reference topics instead of subtopics
        logger.info("Updating content to reference topics...")
        update_content()
        
        # 5. Clean up unused tables
        logger.info("Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}", exc_info=True)
        raise

def create_temp_tables():
    """Create temporary tables to store mappings"""
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS temp_module_subject_map (
            module_id INTEGER PRIMARY KEY,
            subject_id INTEGER
        )
    """))
    
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS temp_subtopic_topic_map (
            subtopic_id INTEGER PRIMARY KEY,
            topic_id INTEGER
        )
    """))
    
    db.session.commit()

def store_relationships():
    """Store current relationship mappings in temp tables"""
    # Store module to subject mapping
    db.session.execute(text("""
        INSERT INTO temp_module_subject_map (module_id, subject_id)
        SELECT id, subject_id FROM modules
    """))
    
    # Store subtopic to topic mapping
    db.session.execute(text("""
        INSERT INTO temp_subtopic_topic_map (subtopic_id, topic_id)
        SELECT id, topic_id FROM subtopics
    """))
    
    db.session.commit()

def update_chapters():
    """Update chapters to reference subjects directly"""
    # Add subject_id column if it doesn't exist
    db.session.execute(text("""
        ALTER TABLE chapters ADD COLUMN IF NOT EXISTS subject_id INTEGER
    """))
    
    # Update chapters with subject_id from the module they currently reference
    db.session.execute(text("""
        UPDATE chapters
        SET subject_id = (
            SELECT subject_id 
            FROM modules 
            WHERE modules.id = chapters.module_id
        )
    """))
    
    db.session.commit()

def update_content():
    """Update content to reference topics directly"""
    # Add topic_id column if it doesn't exist
    db.session.execute(text("""
        ALTER TABLE content ADD COLUMN IF NOT EXISTS topic_id INTEGER
    """))
    
    # Update content with topic_id from the subtopic they currently reference
    db.session.execute(text("""
        UPDATE content
        SET topic_id = (
            SELECT topic_id 
            FROM subtopics 
            WHERE subtopics.id = content.subtopic_id
        )
    """))
    
    db.session.commit()

if __name__ == "__main__":
    from app import app
    with app.app_context():
        migrate_database_structure()
