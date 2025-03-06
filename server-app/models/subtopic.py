# models/subtopic.py
from extensions import db

class Subtopic(db.Model):
    __tablename__ = 'subtopics'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    
    def to_dict(self):
      return {
          'id': self.id,
          'topic_id': self.topic_id,
          'name': self.name
      }