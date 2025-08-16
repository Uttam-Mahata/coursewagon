# routes/media_routes.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional, Dict
from pydantic import BaseModel
from middleware.auth_middleware import get_current_user_id
from services.media_service import MediaService
from services.content_service import ContentService
from services.course_service import CourseService
from extensions import get_db
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

# Create FastAPI router
media_router = APIRouter(prefix="/courses", tags=["media"])

# Dependency injection
def get_media_service(db: Session = Depends(get_db)):
    return MediaService(db)

def get_content_service(db: Session = Depends(get_db)):
    return ContentService(db)

def get_course_service(db: Session = Depends(get_db)):
    return CourseService(db)

# Pydantic models
class MediaUpdateRequest(BaseModel):
    caption: Optional[str] = None
    alt_text: Optional[str] = None
    position: Optional[int] = None

class MediaReorderRequest(BaseModel):
    media_order: Dict[str, int]  # {media_id: position}


@media_router.post(
    '/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/topics/{topic_id}/media'
)
async def upload_media(
    course_id: int,
    subject_id: int,
    chapter_id: int,
    topic_id: int,
    file: UploadFile = File(...),
    file_type: str = Form(default='image'),
    position: Optional[int] = Form(None),
    caption: Optional[str] = Form(None),
    alt_text: Optional[str] = Form(None),
    current_user_id: int = Depends(get_current_user_id),
    media_service: MediaService = Depends(get_media_service),
    content_service: ContentService = Depends(get_content_service),
    course_service: CourseService = Depends(get_course_service)
):
    """Upload a media file (image or video) to content"""
    try:
        # Verify course ownership
        course = course_service.get_course_by_id(course_id)
        if not course or course.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Course not found or you don't have permission")
        
        # Get content by topic ID
        content_data = content_service.get_content_by_topic_id(topic_id)
        if not content_data:
            raise HTTPException(status_code=404, detail="Content not found for this topic")
        
        content_id = content_data.get('id')
        
        # Validate file type
        if file_type not in ['image', 'video']:
            raise HTTPException(status_code=400, detail="Invalid file type. Must be 'image' or 'video'")
        
        # Read file data
        file_data = await file.read()
        
        # Upload media
        result = media_service.upload_media(
            content_id=content_id,
            file_data=file_data,
            file_name=file.filename,
            file_type=file_type,
            position=position,
            caption=caption,
            alt_text=alt_text
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading media: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@media_router.get(
    '/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/topics/{topic_id}/media'
)
async def get_content_media(
    course_id: int,
    subject_id: int,
    chapter_id: int,
    topic_id: int,
    media_service: MediaService = Depends(get_media_service),
    content_service: ContentService = Depends(get_content_service)
):
    """Get all media files for a content"""
    try:
        # Get content by topic ID
        content_data = content_service.get_content_by_topic_id(topic_id)
        if not content_data:
            return []
        
        content_id = content_data.get('id')
        media_files = media_service.get_media_by_content(content_id)
        return media_files
    except Exception as e:
        logger.error(f"Error getting media: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@media_router.put(
    '/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/topics/{topic_id}/media/{media_id}'
)
async def update_media(
    course_id: int,
    subject_id: int,
    chapter_id: int,
    topic_id: int,
    media_id: int,
    media_data: MediaUpdateRequest,
    current_user_id: int = Depends(get_current_user_id),
    media_service: MediaService = Depends(get_media_service),
    content_service: ContentService = Depends(get_content_service),
    course_service: CourseService = Depends(get_course_service)
):
    """Update media metadata"""
    try:
        # Verify course ownership
        course = course_service.get_course_by_id(course_id)
        if not course or course.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Course not found or you don't have permission")
        
        # Get content by topic ID
        content_data = content_service.get_content_by_topic_id(topic_id)
        if not content_data:
            raise HTTPException(status_code=404, detail="Content not found for this topic")
        
        content_id = content_data.get('id')
        
        # Update media
        result = media_service.update_media_metadata(
            media_id=media_id,
            content_id=content_id,
            caption=media_data.caption,
            alt_text=media_data.alt_text,
            position=media_data.position
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Media not found")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating media: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@media_router.delete(
    '/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/topics/{topic_id}/media/{media_id}'
)
async def delete_media(
    course_id: int,
    subject_id: int,
    chapter_id: int,
    topic_id: int,
    media_id: int,
    current_user_id: int = Depends(get_current_user_id),
    media_service: MediaService = Depends(get_media_service),
    content_service: ContentService = Depends(get_content_service),
    course_service: CourseService = Depends(get_course_service)
):
    """Delete a media file"""
    try:
        # Verify course ownership
        course = course_service.get_course_by_id(course_id)
        if not course or course.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Course not found or you don't have permission")
        
        # Get content by topic ID
        content_data = content_service.get_content_by_topic_id(topic_id)
        if not content_data:
            raise HTTPException(status_code=404, detail="Content not found for this topic")
        
        content_id = content_data.get('id')
        
        # Delete media
        result = media_service.delete_media(media_id, content_id)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting media: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@media_router.post(
    '/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/topics/{topic_id}/media/reorder'
)
async def reorder_media(
    course_id: int,
    subject_id: int,
    chapter_id: int,
    topic_id: int,
    reorder_data: MediaReorderRequest,
    current_user_id: int = Depends(get_current_user_id),
    media_service: MediaService = Depends(get_media_service),
    content_service: ContentService = Depends(get_content_service),
    course_service: CourseService = Depends(get_course_service)
):
    """Reorder media files for a content"""
    try:
        # Verify course ownership
        course = course_service.get_course_by_id(course_id)
        if not course or course.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Course not found or you don't have permission")
        
        # Get content by topic ID
        content_data = content_service.get_content_by_topic_id(topic_id)
        if not content_data:
            raise HTTPException(status_code=404, detail="Content not found for this topic")
        
        content_id = content_data.get('id')
        
        # Reorder media
        result = media_service.reorder_media(content_id, reorder_data.media_order)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reordering media: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@media_router.get('/media/supported-formats')
async def get_supported_formats(
    media_service: MediaService = Depends(get_media_service)
):
    """Get list of supported media formats"""
    return media_service.get_supported_formats()