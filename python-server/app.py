import os
import logging
from datetime import timedelta
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.DEBUG if os.environ.get('DEBUG', 'False') == 'True' else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("FastAPI application starting up")
    yield
    # Shutdown
    logger.info("FastAPI application shutting down")

# Import database and routers
from extensions import db
from routes.course_routes import course_router
from routes.subject_routes import subject_router
from routes.chapter_routes import chapter_router
from routes.topic_routes import topic_router
from routes.content_routes import content_router
from routes.auth_routes import auth_router
from routes.testimonial_routes import testimonial_router
from routes.image_routes import image_router
from admin.routes import admin_router
from routes.utility_routes import utility_router

# Create FastAPI app
app = FastAPI(
    title="Course Wagon API",
    description="API for Course Wagon application",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "https://coursewagon-backend.victoriousforest-3a334815.southeastasia.azurecontainerapps.io",
        "https://www.coursewagon.live",
        "https://coursewagon.web.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
)

# Global error handlers
@app.exception_handler(500)
async def handle_server_error(request, exc):
    logger.error(f"Internal server error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "details": str(exc)}
    )

@app.exception_handler(404)
async def handle_not_found(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Not found"}
    )

# Register routers with API prefix
app.include_router(course_router, prefix="/api")
app.include_router(subject_router, prefix="/api")
app.include_router(chapter_router, prefix="/api")
app.include_router(topic_router, prefix="/api")
app.include_router(content_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(testimonial_router, prefix="/api")
app.include_router(image_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(utility_router, prefix="/api")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, host='0.0.0.0', port=port)
