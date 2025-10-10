# routes/enrollment_routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from middleware.auth_middleware import get_current_user_id
from services.enrollment_service import EnrollmentService
from extensions import get_db
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

# Create FastAPI router
enrollment_router = APIRouter(prefix="/enrollments", tags=["enrollments"])

# Pydantic models
class EnrollRequest(BaseModel):
    course_id: int

@enrollment_router.post('/enroll')
async def enroll_in_course(
    enrollment_data: EnrollRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Enroll the current user in a course"""
    try:
        enrollment_service = EnrollmentService(db)
        result = enrollment_service.enroll_in_course(current_user_id, enrollment_data.course_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enrolling in course: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@enrollment_router.delete('/unenroll/{course_id}')
async def unenroll_from_course(
    course_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Unenroll the current user from a course"""
    try:
        enrollment_service = EnrollmentService(db)
        result = enrollment_service.unenroll_from_course(current_user_id, course_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unenrolling from course: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@enrollment_router.get('/my-enrollments')
async def get_my_enrollments(
    status: Optional[str] = Query(None, description="Filter by status: active, completed, dropped"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get all enrollments for the current user"""
    try:
        enrollment_service = EnrollmentService(db)
        enrollments = enrollment_service.get_my_enrollments(current_user_id, status)
        return enrollments
    except Exception as e:
        logger.error(f"Error getting user enrollments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@enrollment_router.get('/check/{course_id}')
async def check_enrollment(
    course_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Check if the current user is enrolled in a course"""
    try:
        enrollment_service = EnrollmentService(db)
        result = enrollment_service.check_enrollment(current_user_id, course_id)
        return result
    except Exception as e:
        logger.error(f"Error checking enrollment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@enrollment_router.get('/course/{course_id}')
async def get_course_enrollments(
    course_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get all enrollments for a course (creator only)"""
    try:
        enrollment_service = EnrollmentService(db)
        enrollments = enrollment_service.get_course_enrollments(course_id, current_user_id)
        return enrollments
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting course enrollments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@enrollment_router.put('/{enrollment_id}/update-progress')
async def update_enrollment_progress(
    enrollment_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Recalculate and update enrollment progress"""
    try:
        enrollment_service = EnrollmentService(db)
        result = enrollment_service.update_enrollment_progress(enrollment_id, current_user_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating enrollment progress: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
