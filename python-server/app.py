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

# Application version for health checks
APP_VERSION = "1.0.3"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("FastAPI application starting up")
    
    # Run database migrations
    try:
        from migrations.add_welcome_email_sent_column import add_welcome_email_sent_column
        from migrations.add_email_verification import run_migration as run_email_verification_migration
        from migrations.add_learner_functionality import run_all_migrations

        add_welcome_email_sent_column()
        run_email_verification_migration()
        run_all_migrations()  # New learner functionality migrations
        logger.info("Database migrations completed successfully")
    except Exception as e:
        logger.error(f"Database migration failed: {str(e)}")
        # Don't fail startup for migration errors in production
    
    # Initialize background task service
    try:
        from services.background_task_service import background_task_service
        logger.info("Background task service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize background task service: {str(e)}")
    
    yield
    
    # Shutdown
    logger.info("FastAPI application shutting down")
    
    # Cleanup background task service
    try:
        from services.background_task_service import background_task_service
        background_task_service.shutdown()
        logger.info("Background task service shutdown completed")
    except Exception as e:
        logger.error(f"Error shutting down background task service: {str(e)}")

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
from routes.enrollment_routes import enrollment_router
from routes.learning_routes import learning_router
from admin.routes import admin_router
from routes.utility_routes import utility_router
from routes.test_auth_routes import test_auth_router

# Create FastAPI app
app = FastAPI(
    title="Course Wagon API",
    description="API for Course Wagon application",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
# Note: When allow_credentials=True, cannot use allow_origins=["*"]
# Must specify exact origins for cookie-based authentication
# SECURITY: Different origins for production vs development to prevent cookie theft
IS_PRODUCTION = os.environ.get('ENVIRONMENT', 'development') == 'production'

if IS_PRODUCTION:
    # Production: ONLY allow production domains (NO localhost!)
    allowed_origins = [
        "https://www.coursewagon.live",
        "https://coursewagon.web.app"
    ]
    logger.info("CORS configured for PRODUCTION - localhost access disabled")
else:
    # Development: Allow localhost for local testing
    allowed_origins = [
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "https://www.coursewagon.live",
        "https://coursewagon.web.app"
    ]
    logger.info("CORS configured for DEVELOPMENT - localhost access enabled")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,  # Required for HttpOnly cookies
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Accept",
        "Origin",
        "Cookie"
    ],
    expose_headers=["Set-Cookie"]
)

# Database error handling middleware
@app.middleware("http")
async def handle_database_errors(request, call_next):
    try:
        response = await call_next(request)
        return response
    except OperationalError as e:
        logger.error(f"Database operational error: {str(e)}")
        # Reset the database connection pool on operational errors
        from extensions import engine, SessionLocal
        engine.dispose()
        return JSONResponse(
            status_code=503,
            content={"error": "Database connection error. Please try again."}
        )
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Database error occurred. Please try again."}
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
app.include_router(enrollment_router, prefix="/api")
app.include_router(learning_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(utility_router, prefix="/api")
app.include_router(test_auth_router, prefix="/api")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": APP_VERSION}




if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, host='0.0.0.0', port=port)
