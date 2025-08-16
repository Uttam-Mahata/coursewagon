from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from services.email_service import EmailService
from middleware.auth_middleware import get_current_user_id, JWTAuth
from extensions import get_db
import logging

logger = logging.getLogger(__name__)

# Create FastAPI router
auth_router = APIRouter(prefix="/auth", tags=["authentication"])

# Dependency injection helpers
def get_auth_service(db: Session = Depends(get_db)):
    return AuthService(db)

def get_email_service():
    return EmailService()

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

@auth_router.post('/register', status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister, 
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
    email_service: EmailService = Depends(get_email_service)
):
    try:
        user = auth_service.register_user(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        
        # Send welcome email
        try:
            email_service.send_welcome_email(user)
            logger.info(f"Welcome email sent to {user.email}")
        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}")
        
        return {'message': 'User created successfully', 'user': user.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='Internal server error')

@auth_router.post('/login')
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    try:
        logger.debug(f"Login attempt for {login_data.email}, remember_me={login_data.remember_me}")
        
        auth_service = AuthService(db)
        auth_data = auth_service.authenticate_user(
            email=login_data.email,
            password=login_data.password
        )
        
        # If remember_me is True, generate a longer-lived token
        if login_data.remember_me:
            from datetime import timedelta
            # Create longer-lived token (30 days)
            access_token = JWTAuth.create_access_token(
                data={"sub": str(auth_data['user']['id'])},
                expires_delta=timedelta(days=30)
            )
            auth_data['access_token'] = access_token
            
        return auth_data
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='Internal server error')

@auth_router.post('/refresh')
async def refresh():
    try:
        # For now, return an error as refresh tokens need to be implemented with proper token verification
        raise HTTPException(status_code=501, detail="Refresh token endpoint needs to be updated for new JWT implementation")
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

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

@auth_router.post('/update-api-key')
async def update_api_key(current_user_id: int = Depends(get_current_user_id)):
    try:
        raise HTTPException(
            status_code=400, 
            detail='API keys are now managed globally via environment variables. Individual user API keys are no longer supported.'
        )
    except Exception as e:
        logger.error(f"Error in update_api_key endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail='Internal server error')

@auth_router.get('/get-api-key')
async def get_api_key(current_user_id: int = Depends(get_current_user_id)):
    try:
        raise HTTPException(
            status_code=400, 
            detail='API keys are now managed globally via environment variables. Individual user API keys are no longer supported.'
        )
    except Exception as e:
        logger.error(f"Error in get_api_key endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail='Internal server error')

@auth_router.delete('/delete-api-key')
async def delete_api_key(current_user_id: int = Depends(get_current_user_id)):
    try:
        raise HTTPException(
            status_code=400, 
            detail='API keys are now managed globally via environment variables. Individual user API keys are no longer supported.'
        )
    except Exception as e:
        logger.error(f"Error in delete_api_key endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail='Internal server error')

@auth_router.post('/forgot-password')
async def forgot_password(forgot_data: ForgotPassword, db: Session = Depends(get_db)):
    try:
        if not forgot_data.email:
            raise HTTPException(status_code=400, detail='Email is required')
            
        auth_service = AuthService(db)
        result = auth_service.request_password_reset(forgot_data.email, forgot_data.frontend_url)
        
        # Always return success message (even if email doesn't exist) for security
        return {'message': 'If an account with this email exists, a password reset link has been sent.'}
    except Exception as e:
        logger.error(f"Error processing forgot password: {str(e)}")
        raise HTTPException(status_code=500, detail='Internal server error')

@auth_router.post('/verify-reset-token')
async def verify_reset_token(token_data: VerifyResetToken, db: Session = Depends(get_db)):
    try:
        if not token_data.token:
            raise HTTPException(status_code=400, detail='Token is required')
            
        auth_service = AuthService(db)
        is_valid = auth_service.verify_reset_token(token_data.token)
        
        return {'valid': is_valid}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying reset token: {str(e)}")
        raise HTTPException(status_code=500, detail='Internal server error')

@auth_router.post('/reset-password')
async def reset_password(reset_data: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        if not reset_data.token or not reset_data.password:
            raise HTTPException(status_code=400, detail='Token and password are required')
            
        # Reset password with token
        auth_service = AuthService(db)
        user = auth_service.reset_password(reset_data.token, reset_data.password)
        
        return {'message': 'Your password has been reset successfully. You can now log in with your new password.'}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error resetting password: {str(e)}")
        raise HTTPException(status_code=500, detail='Internal server error')

@auth_router.post('/change-password')
async def change_password(
    password_data: ChangePassword,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    try:
        if not password_data.current_password or not password_data.new_password:
            raise HTTPException(status_code=400, detail='Current password and new password are required')
            
        # Get user
        user_repo = UserRepository(db)
        user = user_repo.get_user_by_id(current_user_id)
        if not user:
            raise HTTPException(status_code=404, detail='User not found')
            
        # Verify current password
        if not user.check_password(password_data.current_password):
            raise HTTPException(status_code=400, detail='Current password is incorrect')
            
        # Update password
        auth_service = AuthService(db)
        user = auth_service.update_user_profile(current_user_id, password=password_data.new_password)
        
        return {'message': 'Password changed successfully'}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        raise HTTPException(status_code=500, detail='Internal server error')

@auth_router.post('/google-auth')
async def google_auth(
    google_data: GoogleAuth, 
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Handle Google authentication via Firebase token"""
    try:
        if not google_data.firebase_token or not google_data.user_data:
            raise HTTPException(status_code=400, detail='Firebase token and user data are required')
            
        # Verify the Firebase token and process Google authentication
        result = auth_service.authenticate_google_user(google_data.firebase_token, google_data.user_data)
        
        return {
            'access_token': result['access_token'],
            'refresh_token': result['refresh_token'],
            'user': result['user'],
            'message': 'Google authentication successful'
        }
        
    except ValueError as e:
        logger.error(f"Google auth validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Google auth error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='Google authentication failed')

@auth_router.post('/register', status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    try:
        user = auth_service.register_user(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        
        # Send welcome email
        try:
            email_service.send_welcome_email(user)
            logger.info(f"Welcome email sent to {user.email}")
        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}")
        
        return {'message': 'User created successfully', 'user': user.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='Internal server error')

@auth_router.post('/login')
async def login(
    login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        logger.debug(f"Login attempt for {login_data.email}, remember_me={login_data.remember_me}")
        
        auth_data = auth_service.authenticate_user(
            email=login_data.email,
            password=login_data.password
        )
        
        # If remember_me is True, generate a longer-lived token
        if login_data.remember_me:
            from datetime import timedelta
            # Create longer-lived token (30 days)
            access_token = JWTAuth.create_access_token(
                data={"sub": str(auth_data['user']['id'])},
                expires_delta=timedelta(days=30)
            )
            auth_data['access_token'] = access_token
            
        return auth_data
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='Internal server error')

@auth_router.post('/refresh')
async def refresh():
    try:
        # For now, return an error as refresh tokens need to be implemented with proper token verification
        raise HTTPException(status_code=501, detail="Refresh token endpoint needs to be updated for new JWT implementation")
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

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
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        user = auth_service.update_user_profile(
            current_user_id, 
            **profile_data.dict(exclude_unset=True)
        )
        return user.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@auth_router.post('/forgot-password')
async def forgot_password(
    forgot_data: ForgotPassword,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        if not forgot_data.email:
            raise HTTPException(status_code=400, detail='Email is required')
            
        # Use provided frontend_url or default
        frontend_url = forgot_data.frontend_url or 'https://coursewagon.live'
        
        # Process forgot password request
        auth_service.request_password_reset(forgot_data.email, frontend_url)
        
        # Always return success for security (don't reveal if email exists)
        return {'message': 'If your email exists in our system, you will receive a password reset link shortly.'}
    except Exception as e:
        logger.error(f"Error processing forgot password request: {str(e)}")
        raise HTTPException(status_code=500, detail='Internal server error')

@auth_router.post('/verify-reset-token')
async def verify_reset_token(
    token_data: VerifyResetToken,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        if not token_data.token:
            raise HTTPException(status_code=400, detail='Token is required')
            
        # Verify if token is valid
        is_valid = auth_service.verify_reset_token(token_data.token)
        
        if is_valid:
            return {'valid': True}
        else:
            raise HTTPException(status_code=400, detail='Invalid or expired token')
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying reset token: {str(e)}")
        raise HTTPException(status_code=500, detail='Internal server error')

@auth_router.post('/reset-password')
async def reset_password(
    reset_data: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        if not reset_data.token or not reset_data.password:
            raise HTTPException(status_code=400, detail='Token and password are required')
            
        # Reset password with token
        user = auth_service.reset_password(reset_data.token, reset_data.password)
        
        return {'message': 'Your password has been reset successfully. You can now log in with your new password.'}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error resetting password: {str(e)}")
        raise HTTPException(status_code=500, detail='Internal server error')

@auth_router.post('/change-password')
async def change_password(
    password_data: ChangePassword,
    current_user_id: int = Depends(get_current_user_id),
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        if not password_data.current_password or not password_data.new_password:
            raise HTTPException(status_code=400, detail='Current password and new password are required')
            
        # Get user
        user_repo = UserRepository()
        user = user_repo.get_user_by_id(current_user_id)
        if not user:
            raise HTTPException(status_code=404, detail='User not found')
            
        # Verify current password
        if not user.check_password(password_data.current_password):
            raise HTTPException(status_code=400, detail='Current password is incorrect')
            
        # Update password
        user = auth_service.update_user_profile(current_user_id, password=password_data.new_password)
        
        return {'message': 'Password changed successfully'}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        raise HTTPException(status_code=500, detail='Internal server error')
        
    except ValueError as e:
        logger.error(f"Google auth validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Google auth error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='Google authentication failed')