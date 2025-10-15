from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from middleware.auth_middleware import get_current_user_id
from services.image_service import ImageService
from services.auth_service import AuthService
from services.course_service import CourseService
from extensions import get_db
from sqlalchemy.orm import Session
from utils.rate_limiter import limiter, get_ai_rate_limit
import logging

logger = logging.getLogger(__name__)

# Convert Flask Blueprint to FastAPI Router
image_router = APIRouter(prefix='/images', tags=['images'])

# Use dependency injection for database session
def get_image_service(db: Session = Depends(get_db)):
    return ImageService(db)

def get_auth_service(db: Session = Depends(get_db)):
    return AuthService(db)

def get_course_service(db: Session = Depends(get_db)):
    return CourseService(db)

# Pydantic model for request validation
class ImageUrlCheck(BaseModel):
    url: str

@image_router.post('/courses/{course_id}/generate')
@limiter.limit(get_ai_rate_limit("generate_course_image"))
async def generate_course_image(
    request: Request,
    response: Response,
    course_id: int,
    current_user_id: int = Depends(get_current_user_id),
    image_service: ImageService = Depends(get_image_service),
    course_service: CourseService = Depends(get_course_service)
):
    try:
        # Verify course ownership
        course = course_service.get_course_by_id(course_id)
        if not course or course.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Course not found or you don't have permission")

        result = image_service.generate_course_image(course_id)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating course image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@image_router.post('/courses/{course_id}/subjects/{subject_id}/generate')
@limiter.limit(get_ai_rate_limit("generate_subject_image"))
async def generate_subject_image(
    request: Request,
    response: Response,
    course_id: int,
    subject_id: int,
    current_user_id: int = Depends(get_current_user_id),
    image_service: ImageService = Depends(get_image_service),
    course_service: CourseService = Depends(get_course_service)
):
    try:
        # Verify course ownership
        course = course_service.get_course_by_id(course_id)
        if not course or course.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Course not found or you don't have permission")
            
        result = image_service.generate_subject_image(course_id, subject_id)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating subject image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@image_router.post('/courses/{course_id}/subjects/generate-all')
@limiter.limit(get_ai_rate_limit("generate_image"))
async def generate_all_subject_images(
    request: Request,
    response: Response,
    course_id: int,
    current_user_id: int = Depends(get_current_user_id),
    image_service: ImageService = Depends(get_image_service),
    course_service: CourseService = Depends(get_course_service)
):
    try:
        # Verify course ownership
        course = course_service.get_course_by_id(course_id)
        if not course or course.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Course not found or you don't have permission")
            
        results = image_service.generate_images_for_subjects(course_id)
        return {"results": results}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating subject images: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@image_router.post('/check-url')
async def check_image_url(
    image_data: ImageUrlCheck,
    image_service: ImageService = Depends(get_image_service)
):
    """Check if an image URL is valid and accessible"""
    try:
        if not image_data.url:
            raise HTTPException(status_code=400, detail="URL is required")
            
        result = image_service.check_image_url(image_data.url)
        if not result.get('valid'):
            raise HTTPException(status_code=400, detail=result.get('error', 'Invalid URL'))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking image URL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
