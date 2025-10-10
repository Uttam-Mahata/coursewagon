"""
Database migration to add indexes for performance optimization.

Adds indexes to frequently queried columns to improve query performance.
"""
import os
import sys
import logging
from sqlalchemy import create_engine, text, Index, MetaData, Table
from sqlalchemy.exc import SQLAlchemyError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path to import extensions
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def add_database_indexes():
    """Add performance indexes to database tables"""
    try:
        from extensions import engine
        
        logger.info("Starting database index creation...")
        
        with engine.connect() as connection:
            # Start transaction
            trans = connection.begin()
            
            try:
                # Indexes for course table
                indexes_to_create = [
                    # Course table indexes
                    ("idx_course_user_id", "course", "user_id"),
                    ("idx_course_is_published", "course", "is_published"),
                    ("idx_course_category", "course", "category"),
                    ("idx_course_published_at", "course", "published_at"),
                    
                    # Subject table indexes
                    ("idx_subject_course_id", "subject", "course_id"),
                    
                    # Chapter table indexes (if exists)
                    ("idx_chapter_subject_id", "chapter", "subject_id"),
                    
                    # Topic table indexes
                    ("idx_topic_subject_id", "topic", "subject_id"),
                    ("idx_topic_chapter_id", "topic", "chapter_id"),
                    
                    # Content table indexes
                    ("idx_content_topic_id", "content", "topic_id"),
                    
                    # User table indexes
                    ("idx_user_email", "user", "email"),
                    ("idx_user_firebase_uid", "user", "firebase_uid"),
                    
                    # Enrollment table indexes
                    ("idx_enrollment_user_id", "enrollment", "user_id"),
                    ("idx_enrollment_course_id", "enrollment", "course_id"),
                    ("idx_enrollment_status", "enrollment", "status"),
                    
                    # Learning progress indexes
                    ("idx_learning_progress_user_id", "learning_progress", "user_id"),
                    ("idx_learning_progress_content_id", "learning_progress", "content_id"),
                ]
                
                for index_name, table_name, column_name in indexes_to_create:
                    try:
                        # Check if index already exists
                        check_query = text(f"""
                            SELECT COUNT(*) as count 
                            FROM information_schema.statistics 
                            WHERE table_schema = DATABASE() 
                            AND table_name = :table_name 
                            AND index_name = :index_name
                        """)
                        
                        result = connection.execute(
                            check_query,
                            {"table_name": table_name, "index_name": index_name}
                        ).fetchone()
                        
                        if result[0] == 0:
                            # Create index
                            create_index_query = text(f"""
                                CREATE INDEX {index_name} 
                                ON {table_name}({column_name})
                            """)
                            connection.execute(create_index_query)
                            logger.info(f"✓ Created index: {index_name} on {table_name}({column_name})")
                        else:
                            logger.info(f"  Index already exists: {index_name}")
                            
                    except SQLAlchemyError as e:
                        # Log error but continue with other indexes
                        logger.warning(f"  Could not create index {index_name}: {str(e)}")
                        continue
                
                # Commit transaction
                trans.commit()
                logger.info("✓ Database index creation completed successfully")
                
            except Exception as e:
                trans.rollback()
                logger.error(f"Error during index creation, rolled back: {str(e)}")
                raise
                
    except Exception as e:
        logger.error(f"Failed to add database indexes: {str(e)}")
        # Don't raise - this is not critical for application startup
        return False
    
    return True

if __name__ == "__main__":
    # Run migration
    success = add_database_indexes()
    sys.exit(0 if success else 1)
