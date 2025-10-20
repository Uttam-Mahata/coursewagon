"""
Middleware to validate Origin/Referer headers for public API endpoints.
This ensures that API endpoints are only accessible from allowed frontend domains.
"""
import os
import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class OriginValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate that requests to public API endpoints come from allowed origins.
    Checks both Origin and Referer headers to ensure requests originate from trusted frontends.
    """
    
    def __init__(self, app, allowed_origins: list):
        super().__init__(app)
        self.allowed_origins = allowed_origins
        logger.info(f"Origin validation middleware initialized with origins: {allowed_origins}")
    
    async def dispatch(self, request: Request, call_next):
        # Skip validation for health check endpoint
        if request.url.path == "/health":
            return await call_next(request)
        
        # Skip validation for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # For /docs, /redoc, and /openapi.json endpoints, always block in production
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            is_production = os.environ.get('ENVIRONMENT', 'development') == 'production'
            if is_production:
                logger.warning(f"Blocked access to {request.url.path} in production")
                return JSONResponse(
                    status_code=403,
                    content={"error": "Access forbidden"}
                )
        
        # For API endpoints, validate origin/referer
        if request.url.path.startswith("/api/"):
            # Check if endpoint requires authentication (has Authorization or Cookie)
            has_auth = (
                request.headers.get("Authorization") or 
                request.cookies.get("access_token")
            )
            
            # If endpoint has authentication, let the auth middleware handle it
            # Only validate origin for public (unauthenticated) requests
            if not has_auth:
                origin = request.headers.get("Origin") or request.headers.get("Referer", "")
                
                # Clean up referer to get just the origin
                if origin.startswith("http"):
                    # Extract just the protocol and domain from referer
                    from urllib.parse import urlparse
                    parsed = urlparse(origin)
                    origin = f"{parsed.scheme}://{parsed.netloc}"
                
                # Check if origin is in allowed list
                if not any(allowed in origin for allowed in self.allowed_origins):
                    logger.warning(
                        f"Blocked request to {request.url.path} from unauthorized origin: {origin}"
                    )
                    return JSONResponse(
                        status_code=403,
                        content={"error": "Access forbidden. This API is only accessible from authorized frontends."}
                    )
        
        # Continue processing the request
        response = await call_next(request)
        return response
