# models/content.py
from extensions import db, Base


class Content(Base):
    __tablename__ = 'content'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id', ondelete='CASCADE'), nullable=False)  # Changed from subtopic_id to topic_id
    content = db.Column(db.Text, nullable=False)
    
    def to_dict(self):
      return{
        'id': self.id,
        'topic_id': self.topic_id,  # Updated key
        'content': self.content
      }