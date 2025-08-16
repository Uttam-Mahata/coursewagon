# repositories/subject_repo.py
from models.subject import Subject
from sqlalchemy.orm import Session

class SubjectRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def add_subject(self, subject):
        self.db.add(subject)
        self.db.commit()
        return subject
    
    def get_subjects_by_course_id(self, course_id):
        return self.db.query(Subject).filter(Subject.course_id == course_id).all()
    
    def get_subject_by_id(self, subject_id):
        return self.db.query(Subject).filter(Subject.id == subject_id).first()
        
    def set_has_chapters(self, subject_id, has_chapters):
        subject = self.get_subject_by_id(subject_id)
        if subject:
            subject.has_chapters = has_chapters
            self.db.commit()
    
    def delete_subjects_by_course_id(self, course_id):
        self.db.query(Subject).filter(Subject.course_id == course_id).delete()
        self.db.commit()
        
    # New CRUD operations
    def update_subject(self, subject_id, name):
        subject = self.get_subject_by_id(subject_id)
        if subject:
            subject.name = name
            self.db.commit()
            return subject
        return None
        
    def delete_subject(self, subject_id):
        subject = self.get_subject_by_id(subject_id)
        if subject:
            self.db.delete(subject)
            self.db.commit()
            return True
        return False
        
    def create_subject(self, course_id, name):
        subject = Subject(course_id=course_id, name=name)
        self.db.add(subject)
        self.db.commit()
        return subject
        
    # Image-related operations
    def update_subject_image(self, subject_id, image_url):
        """Update the image URL for a subject"""
        subject = self.get_subject_by_id(subject_id)
        if subject:
            subject.image_url = image_url
            self.db.commit()
            return subject
        return None
        
    def get_subject_image_url(self, subject_id):
        """Get the image URL for a subject"""
        subject = self.get_subject_by_id(subject_id)
        if subject:
            return subject.image_url
        return None