# repositories/subject_repo.py
from models.subject import Subject
from extensions import db

class SubjectRepository:
    def __init__(self):
        self.db = db
    
    def add_subject(self, subject):
        self.db.session.add(subject)
        self.db.session.commit()
    
    def get_subjects_by_course_id(self, course_id):
        return self.db.session.query(Subject).filter(Subject.course_id == course_id).all()