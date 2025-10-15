from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from middleware.auth_middleware import get_current_user_id, get_current_admin_user_id
from services.testimonial_service import TestimonialService
from utils.cache_helper import invalidate_cache
from utils.rate_limiter import limiter, get_public_rate_limit, get_content_rate_limit
from extensions import get_db

testimonial_router = APIRouter(prefix='/testimonials', tags=['testimonials'])

# Pydantic models for request validation
class TestimonialCreate(BaseModel):
    quote: str
    rating: int

class TestimonialUpdate(BaseModel):
    quote: Optional[str] = None
    rating: Optional[int] = None

class TestimonialApproval(BaseModel):
    approved: bool = True

@testimonial_router.get('')
@limiter.limit(get_public_rate_limit("get_content"))
async def get_approved_testimonials(request: Request, response: Response, db: Session = Depends(get_db)):
    """Get all approved testimonials for public display"""
    try:
        testimonial_service = TestimonialService(db)
        testimonials = testimonial_service.get_approved_testimonials()
        return testimonials
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@testimonial_router.get('/my-testimonial')
@limiter.limit(get_public_rate_limit("get_content"))
async def get_my_testimonial(
    request: Request,
    response: Response,
    current_user_id: int = Depends(get_current_user_id), 
    db: Session = Depends(get_db)
):
    """Get the current user's testimonial"""
    try:
        testimonial_service = TestimonialService(db)
        testimonial = testimonial_service.get_user_testimonial(current_user_id)
        if testimonial:
            return testimonial
        else:
            raise HTTPException(status_code=404, detail="No testimonial found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@testimonial_router.post('', status_code=201)
@limiter.limit(get_content_rate_limit("update_content"))
async def create_testimonial(
    request: Request,
    response: Response,
    testimonial_data: TestimonialCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a new testimonial"""
    try:
        if not testimonial_data.quote or not testimonial_data.rating:
            raise HTTPException(status_code=400, detail="Quote and rating are required")

        testimonial_service = TestimonialService(db)
        result = testimonial_service.create_testimonial(
            current_user_id,
            testimonial_data.quote,
            testimonial_data.rating
        )
        # Invalidate admin dashboard cache
        invalidate_cache("admin:*")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@testimonial_router.put('/{testimonial_id}')
@limiter.limit(get_content_rate_limit("update_content"))
async def update_testimonial(
    request: Request,
    response: Response,
    testimonial_id: int,
    testimonial_data: TestimonialUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update an existing testimonial"""
    try:
        if not testimonial_data.quote and testimonial_data.rating is None:
            raise HTTPException(status_code=400, detail="At least one field (quote or rating) is required")

        testimonial_service = TestimonialService(db)
        result = testimonial_service.update_user_testimonial(
            current_user_id,
            testimonial_id,
            quote=testimonial_data.quote,
            rating=testimonial_data.rating
        )
        # Invalidate admin dashboard cache
        invalidate_cache("admin:*")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@testimonial_router.delete('/{testimonial_id}')
@limiter.limit(get_content_rate_limit("delete_content"))
async def delete_testimonial(
    request: Request,
    response: Response,
    testimonial_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete a testimonial"""
    try:
        testimonial_service = TestimonialService(db)
        result = testimonial_service.delete_user_testimonial(current_user_id, testimonial_id)
        if result:
            # Invalidate admin dashboard cache
            invalidate_cache("admin:*")
            return {"message": "Testimonial deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Testimonial not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Admin routes
@testimonial_router.get('/admin/all')
@limiter.limit(get_public_rate_limit("get_content"))
async def admin_get_all_testimonials(
    request: Request,
    response: Response,
    admin_user_id: int = Depends(get_current_admin_user_id),
    db: Session = Depends(get_db)
):
    """Admin: Get all testimonials including unapproved ones"""
    try:
        testimonial_service = TestimonialService(db)
        testimonials = testimonial_service.get_all_testimonials()
        return testimonials
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@testimonial_router.put('/admin/{testimonial_id}/approve')
@limiter.limit(get_content_rate_limit("update_content"))
async def admin_approve_testimonial(
    request: Request,
    response: Response,
    testimonial_id: int,
    approval_data: TestimonialApproval,
    admin_user_id: int = Depends(get_current_admin_user_id),
    db: Session = Depends(get_db)
):
    """Admin: Approve a testimonial"""
    try:
        testimonial_service = TestimonialService(db)
        result = testimonial_service.approve_testimonial(testimonial_id, approval_data.approved)
        # Invalidate admin dashboard cache
        invalidate_cache("admin:*")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
