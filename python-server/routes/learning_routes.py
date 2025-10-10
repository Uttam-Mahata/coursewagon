# routes/learning_routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from middleware.auth_middleware import get_current_user_id
from services.course_discovery_service import CourseDiscoveryService
from services.learning_progress_service import LearningProgressService
from services.course_service import CourseService
from extensions import get_db
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

# Create FastAPI router
learning_router = APIRouter(prefix="/learning", tags=["learning"])

# Pydantic models
class ProgressUpdate(BaseModel):
    enrollment_id: int
    topic_id: int
    content_id: Optional[int] = None
    completed: bool = False
    time_spent_seconds: int = 0
    last_position: Optional[str] = None

class TopicComplete(BaseModel):
    enrollment_id: int
    topic_id: int

# Course Discovery Routes
@learning_router.get('/courses')
async def browse_published_courses(
    limit: int = Query(20, description="Number of courses to return"),
    offset: int = Query(0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """Browse all published courses"""
    try:
        discovery_service = CourseDiscoveryService(db)
        courses = discovery_service.get_published_courses(limit=limit, offset=offset)
        return courses
    except Exception as e:
        logger.error(f"Error browsing courses: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@learning_router.get('/courses/search')
async def search_courses(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, description="Number of results"),
    db: Session = Depends(get_db)
):
    """Search published courses"""
    try:
        discovery_service = CourseDiscoveryService(db)
        courses = discovery_service.search_courses(q, limit=limit)
        return courses
    except Exception as e:
        logger.error(f"Error searching courses: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@learning_router.get('/courses/category/{category}')
async def get_courses_by_category(
    category: str,
    limit: int = Query(20, description="Number of courses"),
    db: Session = Depends(get_db)
):
    """Get courses by category"""
    try:
        discovery_service = CourseDiscoveryService(db)
        courses = discovery_service.get_courses_by_category(category, limit=limit)
        return courses
    except Exception as e:
        logger.error(f"Error getting courses by category: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@learning_router.get('/courses/popular')
async def get_popular_courses(
    limit: int = Query(10, description="Number of popular courses"),
    db: Session = Depends(get_db)
):
    """Get most popular courses"""
    try:
        discovery_service = CourseDiscoveryService(db)
        courses = discovery_service.get_popular_courses(limit=limit)
        return courses
    except Exception as e:
        logger.error(f"Error getting popular courses: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@learning_router.get('/courses/{course_id}/preview')
async def get_course_preview(
    course_id: int,
    db: Session = Depends(get_db)
):
    """Get course preview (structure without detailed content)"""
    try:
        discovery_service = CourseDiscoveryService(db)
        preview = discovery_service.get_course_preview(course_id)
        return preview
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting course preview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Progress Tracking Routes
@learning_router.post('/progress/track')
async def track_progress(
    progress_data: ProgressUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Track learning progress for a topic"""
    try:
        progress_service = LearningProgressService(db)
        result = progress_service.track_progress(
            user_id=current_user_id,
            enrollment_id=progress_data.enrollment_id,
            topic_id=progress_data.topic_id,
            content_id=progress_data.content_id,
            completed=progress_data.completed,
            time_spent_seconds=progress_data.time_spent_seconds,
            last_position=progress_data.last_position
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error tracking progress: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@learning_router.post('/progress/complete-topic')
async def mark_topic_complete(
    completion_data: TopicComplete,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Mark a topic as completed"""
    try:
        progress_service = LearningProgressService(db)
        result = progress_service.mark_topic_complete(
            user_id=current_user_id,
            enrollment_id=completion_data.enrollment_id,
            topic_id=completion_data.topic_id
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking topic complete: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@learning_router.get('/progress/enrollment/{enrollment_id}')
async def get_course_progress(
    enrollment_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get progress for a course enrollment"""
    try:
        progress_service = LearningProgressService(db)
        progress = progress_service.get_course_progress(current_user_id, enrollment_id)
        return progress
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting course progress: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@learning_router.get('/progress/enrollment/{enrollment_id}/resume')
async def get_resume_point(
    enrollment_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get last accessed topic for resume functionality"""
    try:
        progress_service = LearningProgressService(db)
        resume_point = progress_service.get_last_accessed_topic(current_user_id, enrollment_id)
        return resume_point
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting resume point: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Publishing Routes (for creators)
class PublishCourseRequest(BaseModel):
    category: Optional[str] = None
    difficulty_level: Optional[str] = None
    estimated_duration_hours: Optional[int] = None

@learning_router.post('/courses/{course_id}/publish')
async def publish_course(
    course_id: int,
    publish_data: PublishCourseRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Publish a course (creator only)"""
    try:
        course_service = CourseService(db)
        result = course_service.publish_course(
            course_id=course_id,
            user_id=current_user_id,
            category=publish_data.category,
            difficulty_level=publish_data.difficulty_level,
            estimated_duration_hours=publish_data.estimated_duration_hours
        )
        return result
    except Exception as e:
        logger.error(f"Error publishing course: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@learning_router.post('/courses/{course_id}/unpublish')
async def unpublish_course(
    course_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Unpublish a course (creator only)"""
    try:
        course_service = CourseService(db)
        result = course_service.unpublish_course(course_id, current_user_id)
        return result
    except Exception as e:
        logger.error(f"Error unpublishing course: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
