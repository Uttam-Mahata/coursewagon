from datetime import datetime, timedelta
from repositories.user_repository import UserRepository
from repositories.password_reset_repository import PasswordResetRepository
from werkzeug.security import generate_password_hash
from utils.encryption import EncryptionService
from services.email_service import EmailService
from middleware.auth_middleware import JWTAuth
from sqlalchemy.orm import Session
import logging
import os

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, db_session: Session = None):
        self.db_session = db_session
        self.user_repository = UserRepository(db_session)
        self.email_service = EmailService()
        self.password_reset_repository = PasswordResetRepository(db_session)
        try:
            self.encryption_service = EncryptionService()
        except ValueError as e:
            logger.warning(f"Encryption service not available: {str(e)}")
            self.encryption_service = None

    def _create_access_token(self, user_id: str):
        """Create access token using python-jose"""
        return JWTAuth.create_access_token(data={"sub": str(user_id)})

    def _create_refresh_token(self, user_id: str):
        """Create refresh token using python-jose"""
        return JWTAuth.create_refresh_token(data={"sub": str(user_id)})

    def register_user(self, email, password, first_name=None, last_name=None):
        if self.user_repository.get_user_by_email(email):
            raise ValueError("Email already exists")
        
        return self.user_repository.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

    def authenticate_user(self, email, password):
        user = self.user_repository.get_user_by_email(email)
        if not user or not user.check_password(password):
            raise ValueError("Invalid credentials")
        
        if not user.is_active:
            raise ValueError("Account is deactivated")

        self.user_repository.update_last_login(user)
        
        # Generate JWT tokens
        access_token = self._create_access_token(user.id)
        refresh_token = self._create_refresh_token(user.id)
        
        # Ensure tokens are strings, not bytes
        if isinstance(access_token, bytes):
            access_token = access_token.decode('utf-8')
        if isinstance(refresh_token, bytes):
            refresh_token = refresh_token.decode('utf-8')
        
        # Convert user.id to string to prevent JWT validation error
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }

    def refresh_token(self, user_id):
        user = self.user_repository.get_user_by_id(int(user_id) if isinstance(user_id, str) else user_id)
        if not user or not user.is_active:
            raise ValueError("Invalid user or inactive account")
        
        # Generate access token and ensure it's a string
        access_token = self._create_access_token(user.id)
        if isinstance(access_token, bytes):
            access_token = access_token.decode('utf-8')
        
        return access_token

    def update_user_profile(self, user_id, **kwargs):
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Password is handled directly by the model
        return self.user_repository.update_user(user, **kwargs)
    

    def is_admin(self, user_id):
        """Check if a user has admin privileges"""
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            return False
        return user.is_admin
    
    def get_all_users(self):
        """Admin: Get all users in the system"""
        return self.user_repository.get_all_users()
    
    def update_user_admin_status(self, admin_id, user_id, is_admin):
        """Update a user's admin status - only accessible by admins"""
        admin = self.user_repository.get_user_by_id(admin_id)
        if not admin or not admin.is_admin:
            raise ValueError("You don't have permission to perform this action")
            
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
            
        return self.user_repository.update_user(user, is_admin=is_admin)
    
    def update_user_active_status(self, admin_id, user_id, is_active):
        """Update a user's active status - only accessible by admins"""
        admin = self.user_repository.get_user_by_id(admin_id)
        if not admin or not admin.is_admin:
            raise ValueError("You don't have permission to perform this action")
            
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
            
        return self.user_repository.update_user(user, is_active=is_active)

    def request_password_reset(self, email, frontend_url=None):
        """Request a password reset for a user by email"""
        user = self.user_repository.get_user_by_email(email)
        if not user:
            logger.info(f"Password reset requested for non-existent email: {email}")
            return False
        
        # Create a password reset token
        reset = self.password_reset_repository.create_reset_token(user)
        
        # Send the password reset email
        if reset:
            self.email_service.send_password_reset_email(user, reset.token, frontend_url)
            logger.info(f"Password reset email sent to: {email}")
            return True
        return False
    
    def verify_reset_token(self, token):
        """Verify if a reset token is valid"""
        reset = self.password_reset_repository.get_by_token(token)
        if reset and reset.is_valid():
            return True
        return False
    
    def reset_password(self, token, new_password):
        """Reset a user's password using a valid token"""
        reset = self.password_reset_repository.get_by_token(token)
        
        # Check if token exists and is valid
        if not reset:
            raise ValueError("Invalid reset token")
            
        if not reset.is_valid():
            if reset.is_expired():
                raise ValueError("This password reset link has expired. Please request a new one.")
            else:
                raise ValueError("This password reset link has already been used. Please request a new one.")
        
        # Get the user
        user = self.user_repository.get_user_by_id(reset.user_id)
        if not user:
            raise ValueError("User not found")
        
        # Update the password
        self.user_repository.update_user(user, password=new_password)
        
        # Mark token as used
        reset.use_token()
        
        # Send confirmation email
        self.email_service.send_password_changed_email(user)
        
        logger.info(f"Password reset successful for user ID: {user.id}")
        return user
    
    def authenticate_google_user(self, firebase_token, user_data):
        """Authenticate or register a user via Google Firebase token"""
        try:
            # Import Google Auth libraries
            from google.oauth2 import id_token
            from google.auth.transport import requests
            import os
            
            # Verify the Firebase ID token
            # Note: You would need to set up Firebase Admin SDK for proper verification
            # For now, we'll trust the Firebase token from the frontend
            # In production, you should verify the token server-side
            
            email = user_data.get('email')
            if not email:
                raise ValueError("Email is required from Google authentication")
            
            # Check if user already exists
            user = self.user_repository.get_user_by_email(email)
            
            if user:
                # User exists, update last login and return auth data
                self.user_repository.update_last_login(user)
                
                # Update user info from Google if available
                update_data = {}
                if user_data.get('display_name') and not user.first_name:
                    # Parse display name into first and last name
                    name_parts = user_data['display_name'].split(' ', 1)
                    update_data['first_name'] = name_parts[0]
                    if len(name_parts) > 1:
                        update_data['last_name'] = name_parts[1]
                
                if update_data:
                    self.user_repository.update_user(user, **update_data)
                
                logger.info(f"Google login successful for existing user: {email}")
            else:
                # Create new user from Google data
                display_name = user_data.get('display_name', '')
                name_parts = display_name.split(' ', 1) if display_name else ['', '']
                first_name = name_parts[0] if name_parts else ''
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                # Generate a random password for Google users (they won't use it)
                import secrets
                import string
                random_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
                
                user = self.user_repository.create_user(
                    email=email,
                    password=random_password,
                    first_name=first_name,
                    last_name=last_name
                )
                
                logger.info(f"Google registration successful for new user: {email}")
                
                # Send welcome email
                try:
                    self.email_service.send_welcome_email(user)
                except Exception as e:
                    logger.error(f"Failed to send welcome email to Google user: {str(e)}")
            
            # Generate JWT tokens
            access_token = self._create_access_token(user.id)
            refresh_token = self._create_refresh_token(user.id)
            
            # Ensure tokens are strings, not bytes
            if isinstance(access_token, bytes):
                access_token = access_token.decode('utf-8')
            if isinstance(refresh_token, bytes):
                refresh_token = refresh_token.decode('utf-8')
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Google authentication error: {str(e)}")
            raise ValueError(f"Google authentication failed: {str(e)}")