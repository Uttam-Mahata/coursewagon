# repositories/topic_repo.py
from models.topic import Topic
from extensions import db

class TopicRepository:
    def __init__(self):
        self.db = db
    
    def add_topic(self, topic):
        self.db.session.add(topic)
        self.db.session.commit()
    
    def get_topics_by_chapter_id(self, chapter_id):
        return self.db.session.query(Topic).filter(Topic.chapter_id == chapter_id).all()
    
    def get_topic_by_id(self, topic_id):
        return self.db.session.query(Topic).filter(Topic.id == topic_id).first()