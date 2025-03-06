# repositories/content_repo.py
from models.content import Content
from extensions import db

class ContentRepository:
    def __init__(self):
        self.db = db

    def add_content(self, content):
        self.db.session.add(content)
        self.db.session.commit()
    
    def get_content_by_subtopic_id(self, subtopic_id):
        return self.db.session.query(Content).filter(Content.subtopic_id == subtopic_id).first()