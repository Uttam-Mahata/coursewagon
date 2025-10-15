"""
Rate Limiter Utility Module

Provides configurable rate limiting for different API endpoint categories.
Uses slowapi for FastAPI integration with Redis backend support.
"""

import os
import logging
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# Rate limit configurations for different endpoint types
# Format: "count/period" where period can be second, minute, hour, or day

# Authentication endpoints - stricter limits to prevent abuse
AUTH_RATE_LIMITS = {
    "check_email": "10/minute",  # Email enumeration protection
    "validate_email": "10/minute",  # Email validation checks
    "register": "5/hour",  # User registration
    "login": "10/minute",  # Login attempts
    "forgot_password": "3/hour",  # Password reset requests
    "reset_password": "5/hour",  # Password reset submissions
    "refresh_token": "30/minute",  # Token refresh
    "verify_email": "10/hour",  # Email verification
    "resend_verification": "3/hour",  # Resend verification email
}

# AI/Image generation endpoints - strict limits due to compute cost
AI_RATE_LIMITS = {
    "generate_image": "10/hour",  # AI image generation
    "generate_course_image": "20/hour",  # Course-specific image generation
    "generate_subject_image": "30/hour",  # Subject image generation
}

# Utility/Proxy endpoints - moderate limits
UTILITY_RATE_LIMITS = {
    "proxy_image": "60/minute",  # Image proxy
    "check_image": "30/minute",  # Image availability check
    "direct_image": "20/hour",  # Direct image generation
}

# Admin endpoints - moderate limits for dashboard access
ADMIN_RATE_LIMITS = {
    "dashboard": "60/minute",  # Admin dashboard
    "user_management": "30/minute",  # User management operations
}

# Content creation endpoints - reasonable limits for creators
CONTENT_RATE_LIMITS = {
    "create_course": "20/hour",  # Course creation
    "update_content": "100/hour",  # Content updates
    "delete_content": "50/hour",  # Content deletion
}

# Public/read endpoints - generous limits
PUBLIC_RATE_LIMITS = {
    "get_courses": "100/minute",  # Browse courses
    "get_content": "200/minute",  # View content
    "search": "50/minute",  # Search functionality
}

# Default rate limit for unspecified endpoints
DEFAULT_RATE_LIMIT = "100/minute"


def get_rate_limit_key(request: Request) -> str:
    """
    Generate rate limit key based on IP address or user ID if authenticated.
    
    This ensures that authenticated users are rate limited per account
    rather than per IP, which is more accurate and prevents sharing of
    rate limits across multiple users behind the same IP.
    """
    # Try to get user ID from request state (set by auth middleware)
    user_id = getattr(request.state, "user_id", None)
    
    if user_id:
        # Rate limit by user ID for authenticated requests
        return f"user:{user_id}"
    else:
        # Rate limit by IP address for unauthenticated requests
        return get_remote_address(request)


# Initialize limiter with Redis backend if available, otherwise use in-memory
redis_host = os.environ.get('REDIS_HOST')
redis_port = os.environ.get('REDIS_PORT', '6379')
redis_password = os.environ.get('REDIS_PASSWORD')

# Handle None/empty string for redis_password
if redis_password and redis_password.lower() in ('none', 'null', ''):
    redis_password = None

storage_uri = None
if redis_host:
    # Use Redis for distributed rate limiting (recommended for production)
    if redis_password:
        storage_uri = f"redis://:{redis_password}@{redis_host}:{redis_port}"
    else:
        storage_uri = f"redis://{redis_host}:{redis_port}"
    logger.info(f"Rate limiter using Redis storage at {redis_host}:{redis_port}")
else:
    # Use in-memory storage (fallback for development)
    storage_uri = "memory://"
    logger.warning("Rate limiter using in-memory storage. Use Redis for production.")

# Create limiter instance
limiter = Limiter(
    key_func=get_rate_limit_key,
    storage_uri=storage_uri,
    default_limits=[DEFAULT_RATE_LIMIT],
    headers_enabled=True,  # Add rate limit info to response headers
    swallow_errors=True,  # Don't crash on rate limiter errors
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded errors.
    
    Returns a JSON response with clear error message and retry information.
    """
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": f"Too many requests. Please try again later.",
            "retry_after": exc.detail if hasattr(exc, 'detail') else None,
        },
        headers={
            "Retry-After": str(exc.detail) if hasattr(exc, 'detail') else "60",
        }
    )


def get_auth_rate_limit(endpoint_name: str) -> str:
    """Get rate limit for authentication endpoints"""
    return AUTH_RATE_LIMITS.get(endpoint_name, DEFAULT_RATE_LIMIT)


def get_ai_rate_limit(endpoint_name: str) -> str:
    """Get rate limit for AI endpoints"""
    return AI_RATE_LIMITS.get(endpoint_name, DEFAULT_RATE_LIMIT)


def get_utility_rate_limit(endpoint_name: str) -> str:
    """Get rate limit for utility endpoints"""
    return UTILITY_RATE_LIMITS.get(endpoint_name, DEFAULT_RATE_LIMIT)


def get_admin_rate_limit(endpoint_name: str) -> str:
    """Get rate limit for admin endpoints"""
    return ADMIN_RATE_LIMITS.get(endpoint_name, DEFAULT_RATE_LIMIT)


def get_content_rate_limit(endpoint_name: str) -> str:
    """Get rate limit for content endpoints"""
    return CONTENT_RATE_LIMITS.get(endpoint_name, DEFAULT_RATE_LIMIT)


def get_public_rate_limit(endpoint_name: str) -> str:
    """Get rate limit for public endpoints"""
    return PUBLIC_RATE_LIMITS.get(endpoint_name, DEFAULT_RATE_LIMIT)
