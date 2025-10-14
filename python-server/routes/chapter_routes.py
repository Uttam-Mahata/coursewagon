from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from middleware.auth_middleware import get_current_user_id
from services.chapter_service import ChapterService
from services.course_service import CourseService
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from extensions import get_db
from sqlalchemy.orm import Session
from utils.rate_limiter import limiter, get_content_rate_limit, get_public_rate_limit

# Create FastAPI router instead of Flask Blueprint
chapter_router = APIRouter(prefix="/courses", tags=["chapters"])

# Use dependency injection for database session
def get_chapter_service(db: Session = Depends(get_db)):
    return ChapterService(db)

def get_course_service(db: Session = Depends(get_db)):
    return CourseService(db)

def get_auth_service(db: Session = Depends(get_db)):
    return AuthService(db)

# Pydantic models for request/response
class ChapterCreate(BaseModel):
    name: str

class ChapterUpdate(BaseModel):
    name: str

@chapter_router.post('/{course_id}/subjects/{subject_id}/generate_chapters')
@limiter.limit(get_content_rate_limit("update_content"))
async def generate_chapters(
    request: Request,
    course_id: int,
    subject_id: int,
    current_user_id: int = Depends(get_current_user_id),
    chapter_service: ChapterService = Depends(get_chapter_service),
    course_service: CourseService = Depends(get_course_service)
):
    try:
        # Verify course ownership
        course = course_service.get_course_by_id(course_id)
        if not course or course.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Course not found or you don't have permission")
            
        result = chapter_service.generate_chapters(course_id, subject_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@chapter_router.get('/{course_id}/subjects/{subject_id}/chapters')
@limiter.limit(get_public_rate_limit("get_content"))
async def get_chapters(
    request: Request,
    course_id: int, 
    subject_id: int,
    chapter_service: ChapterService = Depends(get_chapter_service)
):
    try:
        chapters = chapter_service.get_chapters_by_subject_id(subject_id)
        return chapters
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@chapter_router.get('/{course_id}/subjects/{subject_id}/chapters/{chapter_id}')
@limiter.limit(get_public_rate_limit("get_content"))
async def get_chapter(
    request: Request,
    course_id: int, 
    subject_id: int, 
    chapter_id: int,
    chapter_service: ChapterService = Depends(get_chapter_service)
):
    try:
        chapter = chapter_service.get_chapter_by_id(chapter_id)
        if chapter:
            return chapter
        else:
            raise HTTPException(status_code=404, detail="Chapter Not Found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@chapter_router.post('/{course_id}/subjects/{subject_id}/chapters')
@limiter.limit(get_content_rate_limit("update_content"))
async def create_chapter(
    request: Request,
    course_id: int,
    subject_id: int,
    chapter_data: ChapterCreate,
    current_user_id: int = Depends(get_current_user_id),
    chapter_service: ChapterService = Depends(get_chapter_service),
    course_service: CourseService = Depends(get_course_service)
):
    try:
        # Verify course ownership
        course = course_service.get_course_by_id(course_id)
        if not course or course.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Course not found or you don't have permission")
            
        if not chapter_data.name:
            raise HTTPException(status_code=400, detail="Chapter name is required")
            
        result = chapter_service.create_chapter(subject_id, chapter_data.name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@chapter_router.put('/{course_id}/subjects/{subject_id}/chapters/{chapter_id}')
@limiter.limit(get_content_rate_limit("update_content"))
async def update_chapter(
    request: Request,
    course_id: int,
    subject_id: int,
    chapter_id: int,
    chapter_data: ChapterUpdate,
    current_user_id: int = Depends(get_current_user_id),
    chapter_service: ChapterService = Depends(get_chapter_service),
    course_service: CourseService = Depends(get_course_service)
):
    try:
        # Verify course ownership
        course = course_service.get_course_by_id(course_id)
        if not course or course.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Course not found or you don't have permission")
            
        if not chapter_data.name:
            raise HTTPException(status_code=400, detail="Chapter name is required")
            
        result = chapter_service.update_chapter(chapter_id, chapter_data.name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@chapter_router.delete('/{course_id}/subjects/{subject_id}/chapters/{chapter_id}')
@limiter.limit(get_content_rate_limit("delete_content"))
async def delete_chapter(
    request: Request,
    course_id: int,
    subject_id: int,
    chapter_id: int,
    current_user_id: int = Depends(get_current_user_id),
    chapter_service: ChapterService = Depends(get_chapter_service),
    course_service: CourseService = Depends(get_course_service)
):
    try:
        # Verify course ownership
        course = course_service.get_course_by_id(course_id)
        if not course or course.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Course not found or you don't have permission")
            
        result = chapter_service.delete_chapter(chapter_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
