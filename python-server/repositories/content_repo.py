# repositories/content_repo.py
from models.content import Content
from sqlalchemy.orm import Session

class ContentRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_content(self, content):
        existing_content = self.get_content_by_topic_id(content.topic_id)
        if existing_content:
            existing_content.content = content.content
            self.db.commit()
            return existing_content
        else:
            self.db.add(content)
            self.db.commit()
            return content
    
    def get_content_by_topic_id(self, topic_id):
        return self.db.query(Content).filter(Content.topic_id == topic_id).first()
        
    def delete_content_by_topic_id(self, topic_id):
        self.db.query(Content).filter(Content.topic_id == topic_id).delete()
        self.db.commit()
        
    # New CRUD operations
    def update_content(self, topic_id, content_text):
        content = self.get_content_by_topic_id(topic_id)
        if content:
            content.content = content_text
            self.db.commit()
            return content
        return None

    def create_content(self, topic_id, content_text):
        content = Content(topic_id=topic_id, content=content_text)
        self.db.add(content)
        self.db.commit()
        return content

    # Video URL operations
    def update_video_url(self, topic_id, video_url):
        """Update or set the video URL for content"""
        content = self.get_content_by_topic_id(topic_id)
        if content:
            content.video_url = video_url
            self.db.commit()
            return content
        return None

    def remove_video_url(self, topic_id):
        """Remove the video URL from content"""
        content = self.get_content_by_topic_id(topic_id)
        if content:
            content.video_url = None
            self.db.commit()
            return content
        return None