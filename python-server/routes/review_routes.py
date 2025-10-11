# routes/review_routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.orm import Session
from middleware.auth_middleware import get_current_user_id
from services.course_review_service import CourseReviewService
from extensions import get_db
import logging

logger = logging.getLogger(__name__)

# Create FastAPI router
review_router = APIRouter(prefix="/reviews", tags=["reviews"])

# Pydantic models for request validation
class ReviewCreate(BaseModel):
    course_id: int = Field(..., description="ID of the course to review")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    review_text: Optional[str] = Field(None, max_length=500, description="Optional review text (max 500 characters)")

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating from 1 to 5 stars")
    review_text: Optional[str] = Field(None, max_length=500, description="Optional review text (max 500 characters)")

# Public endpoint - anyone can view reviews
@review_router.get('/course/{course_id}')
async def get_course_reviews(
    course_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page (max 50)"),
    db: Session = Depends(get_db)
):
    """Get paginated reviews for a course"""
    try:
        review_service = CourseReviewService(db)
        result = review_service.get_course_reviews(course_id, page, limit)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting course reviews: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Public endpoint - get review statistics
@review_router.get('/course/{course_id}/stats')
async def get_review_stats(
    course_id: int,
    db: Session = Depends(get_db)
):
    """Get review statistics for a course"""
    try:
        review_service = CourseReviewService(db)
        stats = review_service.get_review_stats(course_id)
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting review stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Protected endpoint - check if user can review
@review_router.get('/can-review/{course_id}')
async def can_review_course(
    course_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Check if current user can review a course"""
    try:
        review_service = CourseReviewService(db)
        eligibility = review_service.can_user_review(current_user_id, course_id)
        return eligibility
    except Exception as e:
        logger.error(f"Error checking review eligibility: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Protected endpoint - get user's review for a course
@review_router.get('/my-review/{course_id}')
async def get_my_review(
    course_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get current user's review for a specific course"""
    try:
        review_service = CourseReviewService(db)
        review = review_service.get_user_review(current_user_id, course_id)

        if review:
            return review
        else:
            raise HTTPException(status_code=404, detail="Review not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user review: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Protected endpoint - create review
@review_router.post('', status_code=201)
async def create_review(
    review_data: ReviewCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a new course review"""
    try:
        review_service = CourseReviewService(db)
        result = review_service.create_review(
            user_id=current_user_id,
            course_id=review_data.course_id,
            rating=review_data.rating,
            review_text=review_data.review_text
        )
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating review: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Protected endpoint - update review
@review_router.put('/{review_id}')
async def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update an existing review"""
    try:
        # At least one field must be provided
        if review_data.rating is None and review_data.review_text is None:
            raise HTTPException(
                status_code=400,
                detail="At least one field (rating or review_text) must be provided"
            )

        review_service = CourseReviewService(db)
        result = review_service.update_review(
            user_id=current_user_id,
            review_id=review_id,
            rating=review_data.rating,
            review_text=review_data.review_text
        )
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating review: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Protected endpoint - delete review
@review_router.delete('/{review_id}')
async def delete_review(
    review_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete a review"""
    try:
        review_service = CourseReviewService(db)
        result = review_service.delete_review(current_user_id, review_id)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting review: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
