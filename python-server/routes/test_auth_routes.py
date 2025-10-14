"""
Test authentication endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.orm import Session
from services.auth_service import AuthService
from services.email_service import EmailService
from services.background_task_service import background_task_service
from extensions import get_db
from utils.rate_limiter import limiter, get_public_rate_limit
import logging

logger = logging.getLogger(__name__)

# Create router for test endpoints
test_auth_router = APIRouter(prefix="/test", tags=["test"])

def get_auth_service(db: Session = Depends(get_db)):
    return AuthService(db)

def get_email_service():
    return EmailService()

@test_auth_router.post('/send-test-welcome-email')
@limiter.limit(get_public_rate_limit("get_content"))
async def test_welcome_email(
    request: Request,
    email: str,
    auth_service: AuthService = Depends(get_auth_service),
    email_service: EmailService = Depends(get_email_service)
):
    """Test endpoint to send a welcome email"""
    try:
        # Find user by email
        user = auth_service.user_repository.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Send welcome email asynchronously
        future = background_task_service.send_email_async(
            email_service, 
            'send_welcome_email', 
            user
        )
        
        return {
            "message": f"Welcome email scheduled for {email}",
            "user_id": user.id,
            "email": user.email
        }
        
    except Exception as e:
        logger.error(f"Test welcome email error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@test_auth_router.post('/send-test-reset-email')
@limiter.limit(get_public_rate_limit("get_content"))
async def test_reset_email(
    request: Request,
    email: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Test endpoint to send a password reset email"""
    try:
        result = auth_service.request_password_reset(email)
        
        return {
            "message": f"Password reset email scheduled for {email}",
            "success": result
        }
        
    except Exception as e:
        logger.error(f"Test reset email error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@test_auth_router.get('/email-config')
@limiter.limit(get_public_rate_limit("get_content"))
async def test_email_config(request: Request, email_service: EmailService = Depends(get_email_service)):
    """Test endpoint to check email configuration"""
    try:
        config_status = {
            "is_configured": email_service.is_configured,
            "smtp_server": email_service.smtp_server,
            "smtp_port": email_service.smtp_port,
            "sender_email": email_service.sender_email,
            "use_tls": email_service.use_tls,
            "has_username": bool(email_service.smtp_username),
            "has_password": bool(email_service.smtp_password)
        }
        
        return config_status
        
    except Exception as e:
        logger.error(f"Email config test error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@test_auth_router.post('/test-smtp-connection')
@limiter.limit(get_public_rate_limit("get_content"))
async def test_smtp_connection(request: Request, email_service: EmailService = Depends(get_email_service)):
    """Test SMTP connection"""
    try:
        result = email_service.test_smtp_connection()
        return {"smtp_connection_test": result}
        
    except Exception as e:
        logger.error(f"SMTP connection test error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@test_auth_router.get('/firebase-auth-test')
@limiter.limit(get_public_rate_limit("get_content"))
async def test_firebase_auth(request: Request):
    """Test Firebase Admin authentication setup"""
    try:
        from services.firebase_admin_service import firebase_admin_service
        
        # Test if Firebase is properly initialized
        test_result = {
            "firebase_initialized": False,
            "error": None
        }
        
        try:
            # Try to verify a dummy token (will fail but shows if service is working)
            firebase_admin_service.verify_id_token("dummy_token")
        except Exception as e:
            if "Invalid" in str(e) or "Decoding" in str(e):
                # This is expected for a dummy token
                test_result["firebase_initialized"] = True
                test_result["message"] = "Firebase Admin SDK is properly initialized"
            else:
                test_result["error"] = str(e)
        
        return test_result
        
    except Exception as e:
        logger.error(f"Firebase auth test error: {str(e)}")
        return {
            "firebase_initialized": False,
            "error": str(e),
            "message": "Firebase Admin SDK not properly configured"
        }

@test_auth_router.post('/verify-firebase-token')
@limiter.limit(get_public_rate_limit("get_content"))
async def test_verify_firebase_token(request: Request, firebase_token: str):
    """Test Firebase token verification"""
    try:
        from services.firebase_admin_service import firebase_admin_service
        
        result = firebase_admin_service.verify_id_token(firebase_token)
        
        if result:
            return {
                "valid": True,
                "user_info": {
                    "uid": result.get('uid'),
                    "email": result.get('email'),
                    "email_verified": result.get('email_verified'),
                    "name": result.get('name')
                }
            }
        else:
            return {"valid": False, "error": "Invalid token"}
            
    except Exception as e:
        logger.error(f"Firebase token verification error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
