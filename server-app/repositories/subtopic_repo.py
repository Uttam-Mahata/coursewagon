# repositories/subtopic_repo.py
from models.subtopic import Subtopic
from extensions import db

class SubtopicRepository:
    def __init__(self):
        self.db = db

    def add_subtopic(self, subtopic):
        self.db.session.add(subtopic)
        self.db.session.commit()
    
    def get_subtopics_by_topic_id(self, topic_id):
        return self.db.session.query(Subtopic).filter(Subtopic.topic_id == topic_id).all()