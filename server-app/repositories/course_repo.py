# repositories/course_repo.py
from models.course import Course
from extensions import db

class CourseRepository:
    def __init__(self):
        self.db = db

    def add_course(self, course):
        self.db.session.add(course)
        self.db.session.commit()

    def get_all_courses(self):
        return self.db.session.query(Course).all()

    def get_course_by_id(self, course_id):
        return self.db.session.query(Course).filter(Course.id == course_id).first()