# repositories/media_repo.py
from models.media import Media
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class MediaRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_media(self, content_id, file_url, file_type, file_name, 
                     file_size=None, mime_type=None, position=None, 
                     caption=None, alt_text=None):
        """Create a new media record"""
        try:
            media = Media(
                content_id=content_id,
                file_url=file_url,
                file_type=file_type,
                file_name=file_name,
                file_size=file_size,
                mime_type=mime_type,
                position=position,
                caption=caption,
                alt_text=alt_text
            )
            self.db.add(media)
            self.db.commit()
            self.db.refresh(media)
            return media
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating media: {str(e)}")
            raise
    
    def get_media_by_id(self, media_id):
        """Get a media record by ID"""
        return self.db.query(Media).filter(Media.id == media_id).first()
    
    def get_media_by_content_id(self, content_id):
        """Get all media files for a specific content"""
        return self.db.query(Media).filter(Media.content_id == content_id).order_by(Media.position).all()
    
    def update_media(self, media_id, **kwargs):
        """Update media metadata"""
        try:
            media = self.get_media_by_id(media_id)
            if media:
                for key, value in kwargs.items():
                    if hasattr(media, key) and value is not None:
                        setattr(media, key, value)
                self.db.commit()
                self.db.refresh(media)
            return media
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating media: {str(e)}")
            raise
    
    def delete_media(self, media_id):
        """Delete a media record"""
        try:
            media = self.get_media_by_id(media_id)
            if media:
                self.db.delete(media)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting media: {str(e)}")
            raise
    
    def reorder_media(self, content_id, media_positions):
        """Reorder media files for a content by updating their positions"""
        try:
            for media_id, position in media_positions.items():
                media = self.db.query(Media).filter(
                    Media.id == media_id,
                    Media.content_id == content_id
                ).first()
                if media:
                    media.position = position
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error reordering media: {str(e)}")
            raise