from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from middleware.auth_middleware import get_current_admin_user_id
from admin.service import AdminService
from services.auth_service import AuthService
from utils.cache_helper import invalidate_cache
import logging
from typing import Dict, Any, List
from extensions import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Create FastAPI router instead of Flask blueprint
admin_router = APIRouter(prefix="/admin", tags=["admin"])

# Dependency injection for services with database session
def get_admin_service(db: Session = Depends(get_db)):
    return AdminService(db)

def get_auth_service(db: Session = Depends(get_db)):
    return AuthService(db)

# Pydantic models for request validation
class UserStatusUpdate(BaseModel):
    is_active: bool

class AdminStatusUpdate(BaseModel):
    is_admin: bool

@admin_router.get('/dashboard')
async def get_dashboard(
    current_admin_id: int = Depends(get_current_admin_user_id),
    admin_service: AdminService = Depends(get_admin_service)
) -> Dict[str, Any]:
    """Get statistics for admin dashboard"""
    try:
        stats = admin_service.get_dashboard_stats()
        return stats
    except Exception as e:
        logger.error(f"Error in admin dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get('/users')
async def get_all_users(
    current_admin_id: int = Depends(get_current_admin_user_id),
    admin_service: AdminService = Depends(get_admin_service)
) -> List[Dict[str, Any]]:
    """Get all users in the system"""
    try:
        users = admin_service.get_all_users()
        return users
    except Exception as e:
        logger.error(f"Error getting all users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get('/testimonials/pending')
async def get_pending_testimonials(
    current_admin_id: int = Depends(get_current_admin_user_id),
    admin_service: AdminService = Depends(get_admin_service)
) -> List[Dict[str, Any]]:
    """Get all pending testimonials"""
    try:
        testimonials = admin_service.get_pending_testimonials()
        return testimonials
    except Exception as e:
        logger.error(f"Error getting pending testimonials: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.put('/users/{user_id}/status')
async def toggle_user_status(
    user_id: int,
    status_update: UserStatusUpdate,
    current_admin_id: int = Depends(get_current_admin_user_id),
    admin_service: AdminService = Depends(get_admin_service)
) -> Dict[str, Any]:
    """Enable/disable a user account"""
    try:
        result = admin_service.toggle_user_status(current_admin_id, user_id, status_update.is_active)
        # Invalidate admin dashboard cache
        invalidate_cache("admin:*")
        return result
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error toggling user status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.put('/users/{user_id}/admin')
async def toggle_admin_status(
    user_id: int,
    admin_update: AdminStatusUpdate,
    current_admin_id: int = Depends(get_current_admin_user_id),
    admin_service: AdminService = Depends(get_admin_service)
) -> Dict[str, Any]:
    """Grant/revoke admin privileges"""
    try:
        result = admin_service.toggle_admin_status(current_admin_id, user_id, admin_update.is_admin)
        # Invalidate admin dashboard cache
        invalidate_cache("admin:*")
        return result
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error toggling admin status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
