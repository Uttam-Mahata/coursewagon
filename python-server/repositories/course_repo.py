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