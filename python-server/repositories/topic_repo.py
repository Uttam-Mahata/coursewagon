# repositories/topic_repo.py
from models.topic import Topic
from sqlalchemy.orm import Session

class TopicRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def add_topic(self, topic):
        self.db.add(topic)
        self.db.commit()
        return topic
    
    def get_topics_by_chapter_id(self, chapter_id):
        return self.db.query(Topic).filter(Topic.chapter_id == chapter_id).all()
    
    def get_topic_by_id(self, topic_id):
        return self.db.query(Topic).filter(Topic.id == topic_id).first()
        
    def delete_topics_by_chapter_id(self, chapter_id):
        self.db.query(Topic).filter(Topic.chapter_id == chapter_id).delete()
        self.db.commit()
        
    def set_has_content(self, topic_id, has_content):
        topic = self.get_topic_by_id(topic_id)
        if topic:
            topic.has_content = has_content
            self.db.commit()
            
    # New CRUD operations
    def update_topic(self, topic_id, name):
        topic = self.get_topic_by_id(topic_id)
        if topic:
            topic.name = name
            self.db.commit()
            return topic
        return None
        
    def delete_topic(self, topic_id):
        topic = self.get_topic_by_id(topic_id)
        if topic:
            self.db.delete(topic)
            self.db.commit()
            return True
        return False
        
    def create_topic(self, chapter_id, name):
        topic = Topic(chapter_id=chapter_id, name=name)
        self.db.add(topic)
        self.db.commit()
        return topic