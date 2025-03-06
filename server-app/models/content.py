# models/content.py
from extensions import db


class Content(db.Model):
    __tablename__ = 'content'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subtopic_id = db.Column(db.Integer, db.ForeignKey('subtopics.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    def to_dict(self):
      return{
        'id': self.id,
        'subtopic_id': self.subtopic_id,
        'content': self.content
      }