from datetime import datetime, timedelta
from repositories.user_repository import UserRepository
from repositories.password_reset_repository import PasswordResetRepository
from repositories.email_verification_repository import EmailVerificationRepository
from werkzeug.security import generate_password_hash
from utils.encryption import EncryptionService
from utils.email_validator import validate_email
from services.email_service import EmailService
from services.background_task_service import background_task_service
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
        self.email_verification_repository = EmailVerificationRepository(db_session)
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
        # Check if email is already registered
        if self.user_repository.get_user_by_email(email):
            raise ValueError("Email already exists")

        # Validate email deliverability
        is_valid, error_message = validate_email(email, check_smtp=False)
        if not is_valid:
            logger.warning(f"Email validation failed for {email}: {error_message}")
            raise ValueError(f"Invalid email address: {error_message}")

        # Create the user with email_verified=False
        user = self.user_repository.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Create verification token and send verification email
        if user:
            try:
                verification = self.email_verification_repository.create_verification_token(user)

                logger.info(f"Scheduling verification email for new user: {email}")
                background_task_service.send_email_async(
                    self.email_service,
                    'send_verification_email',
                    user,
                    verification.token
                )

                # Update email_verification_sent_at timestamp
                self.user_repository.update_user(user, email_verification_sent_at=datetime.utcnow())
                logger.debug(f"Verification email scheduled for user: {email}")
            except Exception as e:
                logger.error(f"Failed to send verification email: {str(e)}")

        return user

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
            # Return True for security (don't reveal if email exists)
            return True
        
        # Create a password reset token
        reset = self.password_reset_repository.create_reset_token(user)
        
        # Send the password reset email asynchronously
        if reset:
            logger.info(f"Scheduling password reset email for: {email}")
            background_task_service.send_email_async(
                self.email_service, 
                'send_password_reset_email', 
                user, 
                reset.token, 
                frontend_url
            )
            logger.info(f"Password reset email scheduled for: {email}")
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
        self.password_reset_repository.invalidate_token(token)
        
        # Send confirmation email asynchronously
        logger.info(f"Scheduling password changed email for user ID: {user.id}")
        background_task_service.send_email_async(
            self.email_service, 
            'send_password_changed_email', 
            user
        )
        
        logger.info(f"Password reset successful for user ID: {user.id}")
        return user

    def verify_email(self, token):
        """Verify a user's email using the verification token"""
        verification = self.email_verification_repository.get_by_token(token)

        # Check if token exists and is valid
        if not verification:
            raise ValueError("Invalid verification token")

        if not verification.is_valid():
            if verification.is_expired():
                raise ValueError("This verification link has expired. Please request a new one.")
            else:
                raise ValueError("This verification link has already been used. Please request a new one.")

        # Get the user
        user = self.user_repository.get_user_by_id(verification.user_id)
        if not user:
            raise ValueError("User not found")

        # Check if already verified
        if user.email_verified:
            logger.info(f"Email already verified for user ID: {user.id}")
            return user

        # Mark email as verified
        self.user_repository.update_user(user, email_verified=True)

        # Mark token as used
        self.email_verification_repository.invalidate_token(token)

        # Send welcome email after verification
        logger.info(f"Scheduling welcome email for verified user: {user.email}")
        background_task_service.send_email_async(
            self.email_service,
            'send_welcome_email',
            user
        )
        self.user_repository.update_user(user, welcome_email_sent=True)

        logger.info(f"Email verification successful for user ID: {user.id}")
        return user

    def resend_verification_email(self, email):
        """Resend verification email to a user"""
        user = self.user_repository.get_user_by_email(email)
        if not user:
            logger.info(f"Verification email requested for non-existent email: {email}")
            # Return True for security (don't reveal if email exists)
            return True

        # Check if already verified
        if user.email_verified:
            logger.info(f"Verification email requested for already verified user: {email}")
            return True

        # Create a new verification token
        verification = self.email_verification_repository.create_verification_token(user)

        # Send the verification email asynchronously
        if verification:
            logger.info(f"Scheduling verification email resend for: {email}")
            background_task_service.send_email_async(
                self.email_service,
                'send_verification_email',
                user,
                verification.token
            )

            # Update email_verification_sent_at timestamp
            self.user_repository.update_user(user, email_verification_sent_at=datetime.utcnow())
            logger.info(f"Verification email resent for: {email}")
            return True
        return False

    def authenticate_google_user(self, firebase_token, user_data):
        """Authenticate or register a user via Google Firebase token"""
        try:
            # Import Firebase Admin service
            from services.firebase_admin_service import firebase_admin_service
            
            # Verify the Firebase ID token
            firebase_user = firebase_admin_service.verify_id_token(firebase_token)
            if not firebase_user:
                raise ValueError("Invalid Firebase token")
            
            # Extract email from verified token
            email = firebase_user.get('email')
            if not email:
                raise ValueError("Email is required from Google authentication")
            
            # Ensure email matches the user data (security check)
            if user_data.get('email') and user_data.get('email') != email:
                raise ValueError("Email mismatch between token and user data")
            
            logger.info(f"Firebase token verified for email: {email}")
            
            # Validate email deliverability (only for new users)
            user = self.user_repository.get_user_by_email(email)

            if not user:
                # Validate email before creating new user
                is_valid, error_message = validate_email(email, check_smtp=False)
                if not is_valid:
                    logger.warning(f"Email validation failed for Google user {email}: {error_message}")
                    raise ValueError(f"Invalid email address: {error_message}")

            if user:
                # User exists, update last login and return auth data
                self.user_repository.update_last_login(user)
                
                # Update user info from verified Firebase data if available
                update_data = {}
                firebase_name = firebase_user.get('name')
                if firebase_name and not user.first_name:
                    # Parse display name into first and last name
                    name_parts = firebase_name.split(' ', 1)
                    update_data['first_name'] = name_parts[0]
                    if len(name_parts) > 1:
                        update_data['last_name'] = name_parts[1]
                
                if update_data:
                    self.user_repository.update_user(user, **update_data)
                
                logger.info(f"Google login successful for existing user: {email}")
            else:
                # Create new user from verified Firebase data
                firebase_name = firebase_user.get('name') or user_data.get('displayName', '')
                name_parts = firebase_name.split(' ', 1) if firebase_name else ['', '']
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

                # Google-authenticated users have verified emails (verified by Google)
                # Mark as verified and send welcome email
                try:
                    self.user_repository.update_user(user, email_verified=True)
                    logger.info(f"Marked email as verified for Google user: {email}")

                    # Send welcome email for Google users (they don't need verification)
                    if not user.welcome_email_sent:
                        background_task_service.send_email_async(
                            self.email_service,
                            'send_welcome_email',
                            user
                        )
                        self.user_repository.update_user(user, welcome_email_sent=True)
                        logger.debug(f"Welcome email sent for Google user: {email}")
                except Exception as e:
                    logger.error(f"Failed to update email verification status for Google user: {str(e)}")
            
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