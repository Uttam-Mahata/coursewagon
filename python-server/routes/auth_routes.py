from fastapi import APIRouter, HTTPException, Depends, status, Response, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from services.email_service import EmailService
from middleware.auth_middleware import get_current_user_id, JWTAuth
from extensions import get_db
from utils.email_validator import validate_email
from datetime import timedelta
import logging
import os
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

# Cookie configuration
IS_PRODUCTION = os.environ.get('ENVIRONMENT', 'development') == 'production'
# For cross-site cookies (frontend on different domain than backend), we need:
# - SameSite='none' to allow cross-site cookies
# - Secure=True (required when SameSite='none', works because both frontend and backend use HTTPS)
COOKIE_SECURE = True  # Always True for production (HTTPS required for cross-site cookies)
COOKIE_SAMESITE = 'none'  # Allow cross-site cookies (frontend and backend on different domains)
FRONTEND_DOMAIN = os.environ.get('FRONTEND_URL', 'localhost')

# Create FastAPI router
auth_router = APIRouter(prefix="/auth", tags=["authentication"])

# Dependency injection helpers
def get_auth_service(db: Session = Depends(get_db)):
    return AuthService(db)

def get_email_service():
    return EmailService()

def set_auth_cookies(response: Response, access_token: str, refresh_token: str, remember_me: bool = False):
    """
    Set secure HttpOnly cookies for authentication tokens

    Args:
        response: FastAPI Response object
        access_token: JWT access token
        refresh_token: JWT refresh token
        remember_me: If True, set longer expiry for cookies
    """
    # Access token cookie (short-lived)
    access_max_age = 2592000 if remember_me else 3600  # 30 days or 1 hour

    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=access_max_age,
        httponly=True,  # Cannot be accessed by JavaScript
        secure=COOKIE_SECURE,  # Only send over HTTPS in production
        samesite=COOKIE_SAMESITE,  # CSRF protection
        path="/"
    )

    # Refresh token cookie (long-lived)
    refresh_max_age = 2592000 if remember_me else 604800  # 30 days or 7 days

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=refresh_max_age,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path="/api/auth/refresh"  # Only sent to refresh endpoint
    )

    logger.debug(f"Auth cookies set with remember_me={remember_me}")

def clear_auth_cookies(response: Response):
    """Clear authentication cookies on logout"""
    # Must match the same attributes used when setting cookies
    response.delete_cookie(
        key="access_token",
        path="/",
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE
    )
    response.delete_cookie(
        key="refresh_token",
        path="/api/auth/refresh",
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE
    )
    logger.debug("Auth cookies cleared")

# Pydantic models for request/response validation
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False

class ForgotPassword(BaseModel):
    email: EmailStr
    frontend_url: Optional[str] = None

class ResetPasswordRequest(BaseModel):
    token: str
    password: str

class VerifyResetToken(BaseModel):
    token: str

class ChangePassword(BaseModel):
    current_password: str
    new_password: str

class GoogleAuth(BaseModel):
    firebase_token: str
    user_data: dict

class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    # Add other profile fields as needed

class CheckEmail(BaseModel):
    email: EmailStr

class VerifyEmail(BaseModel):
    token: str

class ResendVerification(BaseModel):
    email: EmailStr

@auth_router.post('/check-email')
async def check_email(
    email_data: CheckEmail,
    db: Session = Depends(get_db)
):
    """Check if an email address is already registered"""
    try:
        user_repo = UserRepository(db)
        user = user_repo.get_user_by_email(email_data.email)

        return {
            'exists': user is not None,
            'available': user is None
        }
    except Exception as e:
        logger.error(f"Error checking email: {str(e)}")
        raise HTTPException(status_code=500, detail='Internal server error')

@auth_router.post('/validate-email')
async def validate_email_endpoint(email_data: CheckEmail):
    """
    Validate if an email address is deliverable by checking:
    - Email format
    - DNS MX records
    - Domain validity
    - Not a disposable email service
    """
    try:
        is_valid, error_message = validate_email(email_data.email, check_smtp=False)

        if not is_valid:
            return {
                'valid': False,
                'deliverable': False,
                'message': error_message
            }

        return {
            'valid': True,
            'deliverable': True,
            'message': 'Email address is valid and deliverable'
        }
    except Exception as e:
        logger.error(f"Error validating email: {str(e)}")
        # Don't fail validation on errors - allow registration
        return {
            'valid': True,
            'deliverable': True,
            'message': 'Email validation service unavailable'
        }

@auth_router.post('/register', status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister, 
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register new user"""
    try:
        user = auth_service.register_user(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        
        logger.info(f"User registered successfully: {user.email}")
        return {
            'message': 'Registration successful! Please check your email to verify your account.',
            'user': user.to_dict()
        }
        
    except ValueError as e:
        logger.warning(f"Registration failed for {user_data.email}: {str(e)}")
        raise HTTPException(status_code=400, detail={'error': str(e)})
    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={'error': 'Registration failed. Please try again later.'})

@auth_router.post('/login')
async def login(login_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    """Login user with email and password"""
    try:
        logger.debug(f"Login attempt for {login_data.email}, remember_me={login_data.remember_me}")

        auth_service = AuthService(db)
        auth_data = auth_service.authenticate_user(
            email=login_data.email,
            password=login_data.password
        )

        # Set HttpOnly cookies with tokens
        set_auth_cookies(
            response=response,
            access_token=auth_data['access_token'],
            refresh_token=auth_data['refresh_token'],
            remember_me=login_data.remember_me
        )

        logger.info(f"User logged in: {login_data.email}")

        # Return user data only (tokens are in cookies)
        return {
            'user': auth_data['user'],
            'message': 'Login successful'
        }
    except ValueError as e:
        logger.warning(f"Login failed for {login_data.email}: {str(e)}")
        raise HTTPException(status_code=401, detail={'error': str(e)})
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={'error': 'An unexpected error occurred. Please try again later.'})

@auth_router.post('/refresh')
async def refresh_token_endpoint(request: Request, response: Response, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token from HttpOnly cookie
    """
    try:
        # Get refresh token from cookie
        refresh_token = request.cookies.get('refresh_token')
        if not refresh_token:
            raise HTTPException(status_code=401, detail='Refresh token not found')

        # Verify refresh token
        try:
            user_id = JWTAuth.verify_token(refresh_token)
        except Exception as e:
            logger.error(f"Refresh token verification failed: {str(e)}")
            raise HTTPException(status_code=401, detail='Invalid or expired refresh token')

        # Generate new access token
        auth_service = AuthService(db)
        new_access_token = auth_service.refresh_token(user_id)

        # Set new access token in cookie
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            max_age=3600,  # 1 hour
            httponly=True,
            secure=COOKIE_SECURE,
            samesite=COOKIE_SAMESITE,
            path="/"
        )

        return {'message': 'Token refreshed successfully'}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='Token refresh failed')

@auth_router.get('/profile')
async def get_profile(
    current_user_id: int = Depends(get_current_user_id), 
    db: Session = Depends(get_db)
):
    try:
        user_repo = UserRepository(db)
        user = user_repo.get_user_by_id(current_user_id)
        return user.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail='Internal server error')

@auth_router.put('/profile')
async def update_profile(
    profile_data: ProfileUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    try:
        auth_service = AuthService(db)
        user = auth_service.update_user_profile(
            current_user_id, 
            **profile_data.dict(exclude_unset=True)
        )
        return user.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@auth_router.post('/forgot-password')
async def forgot_password(forgot_data: ForgotPassword, db: Session = Depends(get_db)):
    """Request password reset email"""
    try:
        if not forgot_data.email:
            raise HTTPException(status_code=400, detail={'error': 'Email address is required.'})
            
        auth_service = AuthService(db)
        result = auth_service.request_password_reset(forgot_data.email, forgot_data.frontend_url)
        
        # Always return success message (even if email doesn't exist) for security
        return {'message': 'If an account with this email exists, a password reset link has been sent to your email.'}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing forgot password: {str(e)}")
        raise HTTPException(status_code=500, detail={'error': 'Failed to process password reset request. Please try again later.'})

@auth_router.post('/verify-reset-token')
async def verify_reset_token(token_data: VerifyResetToken, db: Session = Depends(get_db)):
    """Verify password reset token validity"""
    try:
        if not token_data.token:
            raise HTTPException(status_code=400, detail={'error': 'Reset token is required.'})
            
        auth_service = AuthService(db)
        is_valid = auth_service.verify_reset_token(token_data.token)
        
        return {'valid': is_valid}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying reset token: {str(e)}")
        raise HTTPException(status_code=500, detail={'error': 'Failed to verify reset token. Please try again later.'})

@auth_router.post('/reset-password')
async def reset_password(reset_data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password using reset token"""
    try:
        if not reset_data.token or not reset_data.password:
            raise HTTPException(status_code=400, detail={'error': 'Reset token and new password are required.'})
            
        # Reset password with token
        auth_service = AuthService(db)
        user = auth_service.reset_password(reset_data.token, reset_data.password)
        
        return {'message': 'Your password has been reset successfully! You can now log in with your new password.'}
    except ValueError as e:
        raise HTTPException(status_code=400, detail={'error': str(e)})
    except Exception as e:
        logger.error(f"Error resetting password: {str(e)}")
        raise HTTPException(status_code=500, detail={'error': 'Failed to reset password. Please try again or request a new reset link.'})

@auth_router.post('/change-password')
async def change_password(
    password_data: ChangePassword,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Change password for authenticated user"""
    try:
        if not password_data.current_password or not password_data.new_password:
            raise HTTPException(status_code=400, detail={'error': 'Current password and new password are required.'})
            
        # Get user
        user_repo = UserRepository(db)
        user = user_repo.get_user_by_id(current_user_id)
        if not user:
            raise HTTPException(status_code=404, detail={'error': 'User account not found.'})
            
        # Verify current password
        if not user.check_password(password_data.current_password):
            raise HTTPException(status_code=400, detail={'error': 'Current password is incorrect. Please try again.'})
            
        # Update password
        auth_service = AuthService(db)
        user = auth_service.update_user_profile(current_user_id, password=password_data.new_password)
        
        return {'message': 'Password changed successfully!'}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail={'error': str(e)})
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        raise HTTPException(status_code=500, detail={'error': 'Failed to change password. Please try again later.'})

@auth_router.post('/verify-email')
async def verify_email(verify_data: VerifyEmail, db: Session = Depends(get_db)):
    """Verify user's email address with token"""
    try:
        if not verify_data.token:
            raise HTTPException(status_code=400, detail={'error': 'Verification token is required.'})

        auth_service = AuthService(db)
        user = auth_service.verify_email(verify_data.token)

        return {
            'message': 'Email verified successfully! You can now log in to your account.',
            'user': user.to_dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail={'error': str(e)})
    except Exception as e:
        logger.error(f"Error verifying email: {str(e)}")
        raise HTTPException(status_code=500, detail={'error': 'Email verification failed. Please try again or request a new verification email.'})

@auth_router.post('/resend-verification')
async def resend_verification(resend_data: ResendVerification, db: Session = Depends(get_db)):
    """Resend verification email to user"""
    try:
        if not resend_data.email:
            raise HTTPException(status_code=400, detail={'error': 'Email address is required.'})

        auth_service = AuthService(db)
        result = auth_service.resend_verification_email(resend_data.email)

        # Always return success message (even if email doesn't exist) for security
        return {'message': 'If an account with this email exists and is not verified, a verification email has been sent to your inbox.'}
    except Exception as e:
        logger.error(f"Error resending verification: {str(e)}")
        raise HTTPException(status_code=500, detail={'error': 'Failed to resend verification email. Please try again later.'})

@auth_router.get('/verification-status')
async def verification_status(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Check if current user's email is verified"""
    try:
        user_repo = UserRepository(db)
        user = user_repo.get_user_by_id(current_user_id)
        if not user:
            raise HTTPException(status_code=404, detail='User not found')

        return {
            'email_verified': user.email_verified,
            'email': user.email
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking verification status: {str(e)}")
        raise HTTPException(status_code=500, detail='Internal server error')

@auth_router.post('/logout')
async def logout(response: Response):
    """Logout user by clearing auth cookies"""
    try:
        clear_auth_cookies(response)
        return {'message': 'Logged out successfully'}
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(status_code=500, detail='Logout failed')

@auth_router.post('/google-auth')
async def google_auth(
    google_data: GoogleAuth,
    response: Response,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Handle Google authentication via Firebase token"""
    try:
        if not google_data.firebase_token or not google_data.user_data:
            raise HTTPException(status_code=400, detail={'error': 'Google sign-in failed. Please try again.'})

        # Verify the Firebase token and process Google authentication
        result = auth_service.authenticate_google_user(google_data.firebase_token, google_data.user_data)

        logger.info(f"Google authentication successful for: {result['user']['email']}")

        # Set HttpOnly cookies with tokens
        set_auth_cookies(
            response=response,
            access_token=result['access_token'],
            refresh_token=result['refresh_token'],
            remember_me=False  # Google auth uses default expiry
        )

        # Return user data only (tokens are in cookies)
        return {
            'user': result['user'],
            'message': 'Google authentication successful'
        }

    except ValueError as e:
        logger.error(f"Google auth validation error: {str(e)}")
        raise HTTPException(status_code=400, detail={'error': str(e)})
    except Exception as e:
        logger.error(f"Google auth error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={'error': 'Google sign-in failed. Please try again later.'})