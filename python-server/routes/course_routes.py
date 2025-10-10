import asyncio
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
from middleware.auth_middleware import get_current_user_id
from services.course_service import CourseService
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from utils.gemini_live_helper import GeminiLiveHelper
from extensions import get_db
from sqlalchemy.orm import Session
import logging
import tempfile
import os

logger = logging.getLogger(__name__)

# Create FastAPI router instead of Flask Blueprint
course_router = APIRouter(prefix="/courses", tags=["courses"])

# Pydantic models for request/response
class CourseCreate(BaseModel):
    name: str

class CourseCreateManual(BaseModel):
    name: str
    description: Optional[str] = ''

class CourseUpdate(BaseModel):
    name: str
    description: Optional[str] = None

@course_router.post('/add_course')
async def add_course(
    course_data: CourseCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    if not course_data.name:
        raise HTTPException(status_code=400, detail="Course name is required")

    try:
        course_service = CourseService(db)
        result = course_service.add_course(course_data.name, current_user_id)
        return result
    except Exception as e:
        logger.error(f"Error creating course: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@course_router.get('/my-courses')
async def get_my_courses(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    try:
        course_service = CourseService(db)
        courses = course_service.get_user_courses(current_user_id)
        return courses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@course_router.get('/my-courses/statistics')
async def get_my_courses_statistics(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get detailed statistics for the current user's courses"""
    try:
        from admin.service import AdminService
        admin_service = AdminService(db)
        stats = admin_service.get_user_course_stats(current_user_id)
        return stats
    except Exception as e:
        logger.error(f"Error getting user course statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@course_router.get('')
async def get_courses(db: Session = Depends(get_db)):
    try:
        course_service = CourseService(db)
        courses = course_service.get_all_courses()
        return courses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@course_router.get('/{course_id}')
async def get_course(course_id: int, db: Session = Depends(get_db)):
    try:
        course_service = CourseService(db)
        course = course_service.get_course_by_id(course_id)
        if course:
            return course
        else:
            raise HTTPException(status_code=404, detail="Course Not Found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@course_router.post('/create-manual')
async def create_course_manual(
    course_data: CourseCreateManual,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    try:
        if not course_data.name:
            raise HTTPException(status_code=400, detail="Course name is required")
        
        course_service = CourseService(db)
        result = course_service.create_course_manual(
            course_data.name, 
            course_data.description, 
            current_user_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@course_router.put('/{course_id}')
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    try:
        course_service = CourseService(db)
        # Verify course ownership
        course = course_service.get_course_by_id(course_id)
        if not course or course.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Course not found or you don't have permission")
            
        if not course_data.name:
            raise HTTPException(status_code=400, detail="Course name is required")
            
        result = course_service.update_course(course_id, course_data.name, course_data.description)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@course_router.delete('/{course_id}')
async def delete_course(
    course_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    try:
        course_service = CourseService(db)
        # Verify course ownership
        course = course_service.get_course_by_id(course_id)
        if not course or course.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Course not found or you don't have permission")
            
        result = course_service.delete_course(course_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@course_router.post('/add_course_audio')
async def add_course_audio(
    audio: UploadFile = File(...),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Create a course from audio description
    """
    try:
        # Check if audio file is provided
        if not audio or audio.filename == '':
            raise HTTPException(status_code=400, detail="Audio file is required")

        # Save the uploaded audio file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            content = await audio.read()
            temp_file.write(content)
            temp_audio_path = temp_file.name

        try:
            # Use the new course service method for audio-based course creation
            course_service = CourseService(db)
            result = course_service.add_course_from_audio(temp_audio_path, current_user_id)
            
            return result
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)

    except Exception as e:
        logger.error(f"Error creating course from audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))