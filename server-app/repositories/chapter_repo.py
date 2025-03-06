# repositories/chapter_repo.py
from models.chapter import Chapter
from extensions import db

class ChapterRepository:
    def __init__(self):
        self.db = db
    
    def add_chapter(self, chapter):
        self.db.session.add(chapter)
        self.db.session.commit()
    
    def get_chapters_by_module_id(self, module_id):
        return self.db.session.query(Chapter).filter(Chapter.module_id == module_id).all()