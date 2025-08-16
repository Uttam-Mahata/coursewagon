# models/topic.py
from extensions import db, Base

class Topic(Base):
    __tablename__ = 'topics'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    has_content = db.Column(db.Boolean, default=False)  # Track if content was generated
    
    def to_dict(self):
        return {
            'id': self.id,
            'chapter_id': self.chapter_id,
            'name': self.name,
            'has_content': self.has_content
        }