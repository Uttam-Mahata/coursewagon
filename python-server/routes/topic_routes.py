from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from middleware.auth_middleware import get_current_user_id
from services.topic_service import TopicService
from services.course_service import CourseService
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from extensions import get_db
from sqlalchemy.orm import Session
from utils.rate_limiter import limiter, get_content_rate_limit, get_public_rate_limit

topic_router = APIRouter(prefix='/courses', tags=['topics'])

# Use dependency injection for database session
def get_topic_service(db: Session = Depends(get_db)):
    return TopicService(db)

def get_course_service(db: Session = Depends(get_db)):
    return CourseService(db)

def get_auth_service(db: Session = Depends(get_db)):
    return AuthService(db)

# Pydantic models for request validation
class TopicCreate(BaseModel):
    name: str

class TopicUpdate(BaseModel):
    name: str

@topic_router.post(
    '/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/generate_topics',
    status_code=201)
@limiter.limit(get_content_rate_limit("update_content"))
async def generate_topics(
    request: Request,
    response: Response,
    course_id: int,
    subject_id: int,
    chapter_id: int,
    current_user_id: int = Depends(get_current_user_id),
    topic_service: TopicService = Depends(get_topic_service),
    course_service: CourseService = Depends(get_course_service)
):
    try:
        # Verify course ownership
        course = course_service.get_course_by_id(course_id)
        if not course or course.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Course not found or you don't have permission")
            
        result = topic_service.generate_topics(course_id, subject_id, chapter_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@topic_router.get(
    '/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/topics')
@limiter.limit(get_public_rate_limit("get_content"))
async def get_topics(
    request: Request,
    response: Response,
    course_id: int, 
    subject_id: int, 
    chapter_id: int,
    topic_service: TopicService = Depends(get_topic_service)
):
    try:
        topics = topic_service.get_topics_by_chapter_id(chapter_id)
        return topics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@topic_router.get('/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/topics/{topic_id}')
@limiter.limit(get_public_rate_limit("get_content"))
async def get_topic(
    request: Request,
    response: Response,
    course_id: int, 
    subject_id: int, 
    chapter_id: int, 
    topic_id: int,
    topic_service: TopicService = Depends(get_topic_service)
):
    try:
       topic = topic_service.get_topic_by_id(topic_id)
       if topic:
          return topic
       else:
         raise HTTPException(status_code=404, detail="Topic Not Found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@topic_router.post(
    '/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/topics',
    status_code=201)
@limiter.limit(get_content_rate_limit("update_content"))
async def create_topic(
    request: Request,
    response: Response,
    course_id: int,
    subject_id: int,
    chapter_id: int,
    topic_data: TopicCreate,
    current_user_id: int = Depends(get_current_user_id),
    topic_service: TopicService = Depends(get_topic_service),
    course_service: CourseService = Depends(get_course_service)
):
    try:
        # Verify course ownership
        course = course_service.get_course_by_id(course_id)
        if not course or course.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Course not found or you don't have permission")
            
        if not topic_data.name:
            raise HTTPException(status_code=400, detail="Topic name is required")
            
        result = topic_service.create_topic(chapter_id, topic_data.name)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@topic_router.put(
    '/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/topics/{topic_id}')
@limiter.limit(get_content_rate_limit("update_content"))
async def update_topic(
    request: Request,
    response: Response,
    course_id: int,
    subject_id: int,
    chapter_id: int,
    topic_id: int,
    topic_data: TopicUpdate,
    current_user_id: int = Depends(get_current_user_id),
    topic_service: TopicService = Depends(get_topic_service),
    course_service: CourseService = Depends(get_course_service)
):
    try:
        # Verify course ownership
        course = course_service.get_course_by_id(course_id)
        if not course or course.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Course not found or you don't have permission")
            
        if not topic_data.name:
            raise HTTPException(status_code=400, detail="Topic name is required")
            
        result = topic_service.update_topic(topic_id, topic_data.name)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@topic_router.delete(
    '/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/topics/{topic_id}')
@limiter.limit(get_content_rate_limit("delete_content"))
async def delete_topic(
    request: Request,
    response: Response,
    course_id: int,
    subject_id: int,
    chapter_id: int,
    topic_id: int,
    current_user_id: int = Depends(get_current_user_id),
    topic_service: TopicService = Depends(get_topic_service),
    course_service: CourseService = Depends(get_course_service)
):
    try:
        # Verify course ownership
        course = course_service.get_course_by_id(course_id)
        if not course or course.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Course not found or you don't have permission")
            
        result = topic_service.delete_topic(topic_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
