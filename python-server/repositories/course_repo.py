# repositories/course_repo.py
from models.course import Course
from sqlalchemy.orm import Session

class CourseRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_course(self, course):
        self.db.add(course)
        self.db.commit()
        return course

    def get_all_courses(self):
        return self.db.query(Course).all()
    
    def get_user_courses(self, user_id):
        return self.db.query(Course).filter(Course.user_id == user_id).all()

    def get_course_by_id(self, course_id):
        return self.db.query(Course).filter(Course.id == course_id).first()
        
    def set_has_subjects(self, course_id, has_subjects):
        course = self.get_course_by_id(course_id)
        if course:
            course.has_subjects = has_subjects
            self.db.commit()
            
    # New CRUD operations
    def update_course(self, course_id, name, description=None):
        course = self.get_course_by_id(course_id)
        if course:
            course.name = name
            if description:
                course.description = description
            self.db.commit()
            return course
        return None
        
    def delete_course(self, course_id):
        course = self.get_course_by_id(course_id)
        if course:
            self.db.delete(course)
            self.db.commit()
            return True
        return False
        
    def create_course(self, name, description, user_id):
        course = Course(name=name, description=description, user_id=user_id)
        self.db.add(course)
        self.db.commit()
        return course
        
    # Image-related operations
    def update_course_image(self, course_id, image_url):
        """Update the image URL for a course"""
        course = self.get_course_by_id(course_id)
        if course:
            course.image_url = image_url
            self.db.commit()
            return course
        return None
        
    def get_course_image_url(self, course_id):
        """Get the image URL for a course"""
        course = self.get_course_by_id(course_id)
        if course:
            return course.image_url
        return None