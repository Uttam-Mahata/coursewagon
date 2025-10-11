from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from middleware.auth_middleware import get_current_user_id
from services.content_service import ContentService
from services.course_service import CourseService
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from extensions import get_db
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

# Create FastAPI router instead of Flask Blueprint
content_router = APIRouter(prefix="/courses", tags=["content"])

# Use dependency injection for database session
def get_content_service(db: Session = Depends(get_db)):
    return ContentService(db)

def get_course_service(db: Session = Depends(get_db)):
    return CourseService(db)

def get_auth_service(db: Session = Depends(get_db)):
    return AuthService(db)

# Pydantic models for request/response
class ContentCreate(BaseModel):
    content: str

class ContentUpdate(BaseModel):
    content: str

@content_router.post(
    '/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/topics/{topic_id}/generate_content'
)
async def generate_content(
    course_id: int,
    subject_id: int,
    chapter_id: int,
    topic_id: int,
    current_user_id: int = Depends(get_current_user_id),
    content_service: ContentService = Depends(get_content_service),
    course_service: CourseService = Depends(get_course_service)
):
    try:
        # Verify course ownership
        course = course_service.get_course_by_id(course_id)
        if not course or course.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Course not found or you don't have permission")

        result = content_service.generate_content(course_id, subject_id, chapter_id, topic_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating content for topic {topic_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@content_router.get(
    '/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/topics/{topic_id}/content'
)
async def get_content(
    course_id: int,
    subject_id: int,
    chapter_id: int,
    topic_id: int,
    content_service: ContentService = Depends(get_content_service)
):
    try:
        content = content_service.get_content_by_topic_id(topic_id)
        if content:
            return content
        else:
            raise HTTPException(status_code=404, detail="Content Not Found")
    except HTTPException:
        # Re-raise HTTP exceptions without modifying status code
        raise
    except Exception as e:
        # Only convert non-HTTP exceptions to 500
        logger.error(f"Error getting content for topic {topic_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@content_router.post(
    '/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/topics/{topic_id}/content'
)
async def create_content_manual(
    course_id: int,
    subject_id: int,
    chapter_id: int,
    topic_id: int,
    content_data: ContentCreate,
    current_user_id: int = Depends(get_current_user_id),
    content_service: ContentService = Depends(get_content_service),
    course_service: CourseService = Depends(get_course_service)
):
    try:
        # Verify course ownership
        course = course_service.get_course_by_id(course_id)
        if not course or course.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Course not found or you don't have permission")

        if not content_data.content:
            raise HTTPException(status_code=400, detail="Content is required")

        result = content_service.create_content_manual(topic_id, content_data.content)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating content for topic {topic_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@content_router.put(
    '/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/topics/{topic_id}/content'
)
async def update_content(
    course_id: int,
    subject_id: int,
    chapter_id: int,
    topic_id: int,
    content_data: ContentUpdate,
    current_user_id: int = Depends(get_current_user_id),
    content_service: ContentService = Depends(get_content_service),
    course_service: CourseService = Depends(get_course_service)
):
    try:
        # Verify course ownership
        course = course_service.get_course_by_id(course_id)
        if not course or course.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Course not found or you don't have permission")

        if not content_data.content:
            raise HTTPException(status_code=400, detail="Content is required")

        result = content_service.update_content(topic_id, content_data.content)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating content for topic {topic_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@content_router.delete(
    '/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/topics/{topic_id}/content'
)
async def delete_content(
    course_id: int,
    subject_id: int,
    chapter_id: int,
    topic_id: int,
    current_user_id: int = Depends(get_current_user_id),
    content_service: ContentService = Depends(get_content_service),
    course_service: CourseService = Depends(get_course_service)
):
    try:
        # Verify course ownership
        course = course_service.get_course_by_id(course_id)
        if not course or course.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Course not found or you don't have permission")

        result = content_service.delete_content(topic_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting content for topic {topic_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Video upload endpoints
@content_router.post(
    '/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/topics/{topic_id}/video'
)
async def upload_video(
    course_id: int,
    subject_id: int,
    chapter_id: int,
    topic_id: int,
    video: UploadFile = File(...),
    current_user_id: int = Depends(get_current_user_id),
    content_service: ContentService = Depends(get_content_service),
    course_service: CourseService = Depends(get_course_service)
):
    try:
        # Verify course ownership
        course = course_service.get_course_by_id(course_id)
        if not course or course.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Course not found or you don't have permission")

        # Read video file
        video_bytes = await video.read()

        # Upload video
        result = content_service.upload_video(topic_id, video_bytes, video.filename)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@content_router.delete(
    '/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/topics/{topic_id}/video'
)
async def delete_video(
    course_id: int,
    subject_id: int,
    chapter_id: int,
    topic_id: int,
    current_user_id: int = Depends(get_current_user_id),
    content_service: ContentService = Depends(get_content_service),
    course_service: CourseService = Depends(get_course_service)
):
    try:
        # Verify course ownership
        course = course_service.get_course_by_id(course_id)
        if not course or course.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Course not found or you don't have permission")

        result = content_service.delete_video(topic_id)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
