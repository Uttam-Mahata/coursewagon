# repositories/chapter_repo.py
from models.chapter import Chapter
from sqlalchemy.orm import Session

class ChapterRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def add_chapter(self, chapter):
        self.db.add(chapter)
        self.db.commit()
        return chapter
    
    def get_chapters_by_subject_id(self, subject_id):
        return self.db.query(Chapter).filter(Chapter.subject_id == subject_id).all()
    
    def get_chapter_by_id(self, chapter_id):
        return self.db.query(Chapter).filter(Chapter.id == chapter_id).first()
        
    def delete_chapters_by_subject_id(self, subject_id):
        self.db.query(Chapter).filter(Chapter.subject_id == subject_id).delete()
        self.db.commit()
        
    def set_has_topics(self, chapter_id, has_topics):
        chapter = self.get_chapter_by_id(chapter_id)
        if chapter:
            chapter.has_topics = has_topics
            self.db.commit()
            
    # New CRUD operations
    def update_chapter(self, chapter_id, name):
        chapter = self.get_chapter_by_id(chapter_id)
        if chapter:
            chapter.name = name
            self.db.commit()
            return chapter
        return None
        
    def delete_chapter(self, chapter_id):
        chapter = self.get_chapter_by_id(chapter_id)
        if chapter:
            self.db.delete(chapter)
            self.db.commit()
            return True
        return False
        
    def create_chapter(self, subject_id, name):
        chapter = Chapter(subject_id=subject_id, name=name)
        self.db.add(chapter)
        self.db.commit()
        return chapter