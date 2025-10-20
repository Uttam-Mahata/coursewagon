"""
Database migration to add composite index for enrollment lookups.

Adds a composite index on (user_id, course_id) to optimize batch enrollment checks.
"""
import os
import sys
import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path to import extensions
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def add_enrollment_composite_index():
    """Add composite index for enrollment table"""
    try:
        from extensions import engine
        
        logger.info("Starting enrollment composite index creation...")
        
        with engine.connect() as connection:
            # Start transaction
            trans = connection.begin()
            
            try:
                index_name = "idx_enrollments_user_course"
                table_name = "enrollments"
                
                # Check if index already exists
                check_query = text("""
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
                    # Create composite index on (user_id, course_id)
                    create_index_query = text(f"""
                        CREATE INDEX {index_name} 
                        ON {table_name}(user_id, course_id)
                    """)
                    connection.execute(create_index_query)
                    logger.info(f"✓ Created composite index: {index_name} on {table_name}(user_id, course_id)")
                else:
                    logger.info(f"  Composite index already exists: {index_name}")
                
                # Commit transaction
                trans.commit()
                logger.info("✓ Enrollment composite index creation completed successfully")
                
            except Exception as e:
                trans.rollback()
                logger.error(f"Error during index creation, rolled back: {str(e)}")
                raise
                
    except Exception as e:
        logger.error(f"Failed to add enrollment composite index: {str(e)}")
        # Don't raise - this is not critical for application startup
        return False
    
    return True

if __name__ == "__main__":
    # Run migration
    success = add_enrollment_composite_index()
    sys.exit(0 if success else 1)
