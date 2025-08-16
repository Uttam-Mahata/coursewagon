# models/chapter.py
from extensions import db, Base


class Chapter(Base):
    __tablename__ = 'chapters'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    has_topics = db.Column(db.Boolean, default=False)  # Track if topics were generated
    
    def __init__(self, subject_id, name):  # Updated parameter
        self.subject_id = subject_id  # Updated assignment
        self.name = name
    
    def to_dict(self):
        return {
            'id': self.id,
            'subject_id': self.subject_id,  # Updated key
            'name': self.name,
            'has_topics': self.has_topics
        }