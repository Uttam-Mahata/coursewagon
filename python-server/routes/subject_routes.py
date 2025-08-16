from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from middleware.auth_middleware import get_current_user_id
from services.subject_service import SubjectService
from services.course_service import CourseService
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from extensions import get_db
from sqlalchemy.orm import Session

# Convert Flask Blueprint to FastAPI Router
subject_router = APIRouter(prefix='/courses', tags=['subjects'])

# Use dependency injection for database session
def get_subject_service(db: Session = Depends(get_db)):
    return SubjectService(db)

def get_course_service(db: Session = Depends(get_db)):
    return CourseService(db)

def get_auth_service(db: Session = Depends(get_db)):
    return AuthService(db)

# Pydantic models for request validation
class SubjectCreate(BaseModel):
    name: str

class SubjectUpdate(BaseModel):
    name: str

@subject_router.post('/{id}/generate_subjects', status_code=201)
async def generate_subjects(
    id: int,
    current_user_id: int = Depends(get_current_user_id),
    subject_service: SubjectService = Depends(get_subject_service),
    course_service: CourseService = Depends(get_course_service)
):
    try:
        # Verify course ownership
        course = course_service.get_course_by_id(id)
        if not course or course.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Course not found or you don't have permission")
            
        result = subject_service.generate_subjects(id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@subject_router.get('/{id}/subjects')
async def get_subjects(
    id: int, 
    subject_service: SubjectService = Depends(get_subject_service)
):
    try:
        subjects = subject_service.get_subjects_by_course_id(id)
        return subjects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@subject_router.get('/{course_id}/subjects/{subject_id}')
async def get_subject(
    course_id: int, 
    subject_id: int,
    subject_service: SubjectService = Depends(get_subject_service)
):
    try:
        # Get all subjects for the course
        subjects = subject_service.get_subjects_by_course_id(course_id)
        # Find the specific subject by ID
        subject = next((s for s in subjects if s['id'] == subject_id), None)
        if subject:
            return subject
        else:
            raise HTTPException(status_code=404, detail="Subject Not Found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@subject_router.post('/{course_id}/subjects', status_code=201)
async def create_subject(
    course_id: int,
    subject_data: SubjectCreate,
    current_user_id: int = Depends(get_current_user_id),
    subject_service: SubjectService = Depends(get_subject_service),
    course_service: CourseService = Depends(get_course_service)
):
    try:
        # Verify course ownership
        course = course_service.get_course_by_id(course_id)
        if not course or course.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Course not found or you don't have permission")
            
        if not subject_data.name:
            raise HTTPException(status_code=400, detail="Subject name is required")
            
        result = subject_service.create_subject(course_id, subject_data.name)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@subject_router.put('/{course_id}/subjects/{subject_id}')
async def update_subject(
    course_id: int,
    subject_id: int,
    subject_data: SubjectUpdate,
    current_user_id: int = Depends(get_current_user_id),
    subject_service: SubjectService = Depends(get_subject_service),
    course_service: CourseService = Depends(get_course_service)
):
    try:
        # Verify course ownership
        course = course_service.get_course_by_id(course_id)
        if not course or course.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Course not found or you don't have permission")
            
        if not subject_data.name:
            raise HTTPException(status_code=400, detail="Subject name is required")
            
        result = subject_service.update_subject(subject_id, subject_data.name)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@subject_router.delete('/{course_id}/subjects/{subject_id}')
async def delete_subject(
    course_id: int,
    subject_id: int,
    current_user_id: int = Depends(get_current_user_id),
    subject_service: SubjectService = Depends(get_subject_service),
    course_service: CourseService = Depends(get_course_service)
):
    try:
        # Verify course ownership
        course = course_service.get_course_by_id(course_id)
        if not course or course.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Course not found or you don't have permission")
            
        result = subject_service.delete_subject(subject_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
