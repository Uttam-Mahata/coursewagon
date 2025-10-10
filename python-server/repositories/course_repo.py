# repositories/course_repo.py
from models.course import Course
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class CourseRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_course(self, course):
        try:
            self.db.add(course)
            self.db.commit()
            return course
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error adding course: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding course: {e}")
            raise

    def get_all_courses(self):
        try:
            return self.db.query(Course).all()
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error getting all courses: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error getting all courses: {e}")
            raise
    
    def get_user_courses(self, user_id):
        try:
            return self.db.query(Course).filter(Course.user_id == user_id).all()
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error getting user courses: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error getting user courses: {e}")
            raise

    def get_course_by_id(self, course_id):
        try:
            return self.db.query(Course).filter(Course.id == course_id).first()
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error getting course by ID: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error getting course by ID: {e}")
            raise
        
    def set_has_subjects(self, course_id, has_subjects):
        try:
            course = self.get_course_by_id(course_id)
            if course:
                course.has_subjects = has_subjects
                self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error setting has_subjects: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error setting has_subjects: {e}")
            raise
            
    # New CRUD operations
    def update_course(self, course_id, name, description=None):
        try:
            course = self.get_course_by_id(course_id)
            if course:
                course.name = name
                if description:
                    course.description = description
                self.db.commit()
                return course
            return None
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error updating course: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating course: {e}")
            raise
        
    def delete_course(self, course_id):
        try:
            course = self.get_course_by_id(course_id)
            if course:
                self.db.delete(course)
                self.db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error deleting course: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting course: {e}")
            raise
        
    def create_course(self, name, description, user_id):
        try:
            course = Course(name=name, description=description, user_id=user_id)
            self.db.add(course)
            self.db.commit()
            return course
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error creating course: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating course: {e}")
            raise
        
    # Image-related operations
    def update_course_image(self, course_id, image_url):
        """Update the image URL for a course"""
        try:
            course = self.get_course_by_id(course_id)
            if course:
                course.image_url = image_url
                self.db.commit()
                return course
            return None
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error updating course image: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating course image: {e}")
            raise
        
    def get_course_image_url(self, course_id):
        """Get the image URL for a course"""
        try:
            course = self.get_course_by_id(course_id)
            if course:
                return course.image_url
            return None
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error getting course image URL: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error getting course image URL: {e}")
            raise

    # Publishing and discovery methods
    def publish_course(self, course_id, category=None, difficulty_level=None, estimated_duration_hours=None):
        """Publish a course for learners"""
        try:
            from datetime import datetime
            course = self.get_course_by_id(course_id)
            if course:
                course.is_published = True
                course.published_at = datetime.utcnow()
                if category:
                    course.category = category
                if difficulty_level:
                    course.difficulty_level = difficulty_level
                if estimated_duration_hours:
                    course.estimated_duration_hours = estimated_duration_hours
                self.db.commit()
                return course
            return None
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error publishing course: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error publishing course: {e}")
            raise

    def unpublish_course(self, course_id):
        """Unpublish a course"""
        try:
            course = self.get_course_by_id(course_id)
            if course:
                course.is_published = False
                self.db.commit()
                return course
            return None
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error unpublishing course: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error unpublishing course: {e}")
            raise

    def get_published_courses(self, limit=None, offset=None):
        """Get all published courses"""
        try:
            query = self.db.query(Course).filter(Course.is_published == True).order_by(Course.published_at.desc())

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            return query.all()
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error getting published courses: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error getting published courses: {e}")
            raise

    def get_courses_by_category(self, category, limit=None):
        """Get published courses by category"""
        try:
            query = self.db.query(Course).filter(
                Course.is_published == True,
                Course.category == category
            ).order_by(Course.published_at.desc())

            if limit:
                query = query.limit(limit)

            return query.all()
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error getting courses by category: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error getting courses by category: {e}")
            raise

    def search_courses(self, search_term, limit=None):
        """Search published courses by name or description"""
        try:
            query = self.db.query(Course).filter(
                Course.is_published == True,
                (Course.name.ilike(f'%{search_term}%') | Course.description.ilike(f'%{search_term}%'))
            ).order_by(Course.published_at.desc())

            if limit:
                query = query.limit(limit)

            return query.all()
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error searching courses: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error searching courses: {e}")
            raise

    def get_popular_courses(self, limit=10):
        """Get most popular courses by enrollment count"""
        try:
            return self.db.query(Course).filter(
                Course.is_published == True
            ).order_by(
                Course.enrollment_count.desc()
            ).limit(limit).all()
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error getting popular courses: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error getting popular courses: {e}")
            raise

    def get_available_categories(self):
        """Get list of all unique categories from published courses"""
        try:
            categories = self.db.query(Course.category).filter(
                Course.is_published == True,
                Course.category.isnot(None),
                Course.category != ''
            ).distinct().order_by(Course.category).all()

            # Extract category values from tuples and filter out None/empty
            return [cat[0] for cat in categories if cat[0]]
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error getting available categories: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error getting available categories: {e}")
            raise

    def increment_enrollment_count(self, course_id):
        """Increment the enrollment count for a course"""
        try:
            course = self.get_course_by_id(course_id)
            if course:
                course.enrollment_count += 1
                self.db.commit()
                return course
            return None
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error incrementing enrollment count: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error incrementing enrollment count: {e}")
            raise

    def decrement_enrollment_count(self, course_id):
        """Decrement the enrollment count for a course"""
        try:
            course = self.get_course_by_id(course_id)
            if course and course.enrollment_count > 0:
                course.enrollment_count -= 1
                self.db.commit()
                return course
            return None
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error decrementing enrollment count: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error decrementing enrollment count: {e}")
            raise