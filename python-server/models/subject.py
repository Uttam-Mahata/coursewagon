# models/subject.py
from extensions import db, Base

class Subject(Base):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    has_chapters = db.Column(db.Boolean, default=False)  # Track if chapters were generated
    image_url = db.Column(db.String(512), nullable=True)  # Store the cover image URL

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'name': self.name,
            'has_chapters': self.has_chapters,
            'image_url': self.image_url
        }