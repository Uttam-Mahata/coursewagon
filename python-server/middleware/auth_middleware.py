from functools import wraps
from typing import Optional
from datetime import datetime, timedelta
import os
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import logging

logger = logging.getLogger(__name__)

# Security scheme for JWT Bearer token
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-here')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

class JWTAuth:
    """JWT Authentication utility class"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)  # Refresh tokens last 7 days
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise JWTError("Token missing subject")
            return user_id
        except JWTError as e:
            logger.error(f"JWT verification failed: {str(e)}")
            raise HTTPException(status_code=401, detail="Invalid or expired token")

def get_current_user_id(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> int:
    """
    FastAPI dependency to verify JWT token and return current user ID.
    Reads token from HttpOnly cookie (preferred) or Authorization header (fallback).
    """
    try:
        # Try to get token from cookie first (HttpOnly - most secure)
        token = request.cookies.get('access_token')

        # Fallback to Authorization header for backward compatibility
        if not token and credentials:
            token = credentials.credentials

        if not token:
            raise HTTPException(status_code=401, detail="Authentication required")

        # Verify the JWT token
        user_id = JWTAuth.verify_token(token)
        logger.debug(f"Successfully authenticated user_id: {user_id}")

        # Convert user_id back to int if it's a string from JWT
        user_id = int(user_id) if isinstance(user_id, str) else user_id

        return user_id

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def require_auth(func):
    """
    Decorator for backward compatibility with existing Flask-style auth decorators.
    However, it's recommended to use the get_current_user_id dependency directly in FastAPI.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # This is mainly for compatibility - in FastAPI, prefer using Depends(get_current_user_id)
        return await func(*args, **kwargs)
    return wrapper

# Optional: Create a dependency that doesn't raise an exception for optional auth
def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[int]:
    """
    FastAPI dependency to optionally verify JWT token.
    Returns user ID if valid token is provided, None otherwise.
    Reads token from HttpOnly cookie (preferred) or Authorization header (fallback).
    """
    try:
        # Try to get token from cookie first
        token = request.cookies.get('access_token')

        # Fallback to Authorization header
        if not token and credentials:
            token = credentials.credentials

        if not token:
            return None

        user_id = JWTAuth.verify_token(token)
        return int(user_id) if isinstance(user_id, str) else user_id
    except Exception as e:
        logger.debug(f"Optional auth failed: {str(e)}")
        return None

def get_current_admin_user_id(
    current_user_id: int = Depends(get_current_user_id)
) -> int:
    """
    FastAPI dependency to verify JWT token and ensure user is admin.
    """
    from services.auth_service import AuthService
    auth_service = AuthService()
    
    if not auth_service.is_admin(current_user_id):
        logger.warning(f"Non-admin user {current_user_id} attempted to access admin endpoint")
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    return current_user_id
