# services/media_service.py
from utils.azure_storage_helper import AzureStorageHelper
from repositories.media_repo import MediaRepository
from repositories.content_repo import ContentRepository
from sqlalchemy.orm import Session
import logging
from io import BytesIO
import mimetypes
import os

logger = logging.getLogger(__name__)


class MediaService:
    def __init__(self, db: Session):
        self.media_repo = MediaRepository(db)
        self.content_repo = ContentRepository(db)
        self.azure_storage = AzureStorageHelper()
    
    def upload_media(self, content_id, file_data, file_name, file_type='image', position=None, caption=None, alt_text=None):
        """Upload a media file to Azure Storage and save metadata to database"""
        try:
            # Verify content exists
            content = self.content_repo.get_content_by_id(content_id)
            if not content:
                raise ValueError(f"Content not found: {content_id}")
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(file_name)
            if not mime_type:
                mime_type = 'application/octet-stream'
            
            # Validate file type based on MIME type
            if file_type == 'image' and not mime_type.startswith('image/'):
                raise ValueError("Invalid image file type")
            elif file_type == 'video' and not mime_type.startswith('video/'):
                raise ValueError("Invalid video file type")
            
            # Read file data if it's a file object
            if hasattr(file_data, 'read'):
                file_bytes = file_data.read()
            else:
                file_bytes = file_data
            
            file_size = len(file_bytes)
            
            # Generate path for Azure Storage
            topic_id = content.topic_id
            file_extension = os.path.splitext(file_name)[1]
            storage_path = f"content/{content_id}/media/{file_type}s/{file_name}"
            
            # Upload to Azure Storage
            logger.info(f"Uploading {file_type} to Azure Storage: {storage_path}")
            file_url = self.azure_storage.upload_image(file_bytes, storage_path)
            
            # Save metadata to database
            media = self.media_repo.create_media(
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
            
            logger.info(f"Media uploaded successfully: {media.id}")
            return media.to_dict()
            
        except Exception as e:
            logger.error(f"Error uploading media: {str(e)}")
            raise
    
    def delete_media(self, media_id, content_id=None):
        """Delete a media file from Azure Storage and database"""
        try:
            media = self.media_repo.get_media_by_id(media_id)
            if not media:
                raise ValueError(f"Media not found: {media_id}")
            
            # Verify content ownership if content_id provided
            if content_id and media.content_id != content_id:
                raise ValueError("Media does not belong to the specified content")
            
            # Delete from Azure Storage
            if media.file_url:
                self.azure_storage.delete_image(media.file_url)
            
            # Delete from database
            self.media_repo.delete_media(media_id)
            
            logger.info(f"Media deleted successfully: {media_id}")
            return {"message": "Media deleted successfully"}
            
        except Exception as e:
            logger.error(f"Error deleting media: {str(e)}")
            raise
    
    def get_media_by_content(self, content_id):
        """Get all media files for a specific content"""
        try:
            media_files = self.media_repo.get_media_by_content_id(content_id)
            return [media.to_dict() for media in media_files]
        except Exception as e:
            logger.error(f"Error getting media by content: {str(e)}")
            raise
    
    def update_media_metadata(self, media_id, content_id=None, **kwargs):
        """Update media metadata (caption, alt_text, position)"""
        try:
            media = self.media_repo.get_media_by_id(media_id)
            if not media:
                raise ValueError(f"Media not found: {media_id}")
            
            # Verify content ownership if content_id provided
            if content_id and media.content_id != content_id:
                raise ValueError("Media does not belong to the specified content")
            
            # Update allowed fields only
            allowed_fields = ['caption', 'alt_text', 'position']
            update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}
            
            updated_media = self.media_repo.update_media(media_id, **update_data)
            return updated_media.to_dict() if updated_media else None
            
        except Exception as e:
            logger.error(f"Error updating media metadata: {str(e)}")
            raise
    
    def reorder_media(self, content_id, media_order):
        """Reorder media files for a content"""
        try:
            # Verify all media belongs to the content
            media_ids = list(media_order.keys())
            media_files = self.media_repo.get_media_by_content_id(content_id)
            content_media_ids = [m.id for m in media_files]
            
            for media_id in media_ids:
                if int(media_id) not in content_media_ids:
                    raise ValueError(f"Media {media_id} does not belong to content {content_id}")
            
            # Update positions
            self.media_repo.reorder_media(content_id, media_order)
            
            return {"message": "Media reordered successfully"}
            
        except Exception as e:
            logger.error(f"Error reordering media: {str(e)}")
            raise
    
    def get_supported_formats(self):
        """Get list of supported media formats"""
        return {
            "image": ["jpg", "jpeg", "png", "gif", "webp", "svg"],
            "video": ["mp4", "webm", "avi", "mov", "mkv"]
        }