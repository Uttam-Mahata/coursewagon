"""
Firebase Admin SDK service for server-side Firebase authentication
"""
import firebase_admin
from firebase_admin import credentials, auth
import os
import logging
from typing import Dict, Optional
import json

logger = logging.getLogger(__name__)

class FirebaseAdminService:
    """Service for Firebase Admin SDK operations"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseAdminService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialize_firebase()
        FirebaseAdminService._initialized = True
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase is already initialized
            if firebase_admin._apps:
                logger.info("Firebase Admin SDK already initialized")
                return
            
            # Try different credential sources
            cred = self._get_credentials()
            
            if cred:
                # Initialize with project ID from environment or credentials
                project_id = os.environ.get('FIREBASE_PROJECT_ID', 'coursewagon')
                
                firebase_admin.initialize_app(cred, {
                    'projectId': project_id
                })
                
                logger.info(f"Firebase Admin SDK initialized successfully for project: {project_id}")
            else:
                raise ValueError("No valid Firebase credentials found")
                
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {str(e)}")
            raise
    
    def _get_credentials(self):
        """Get Firebase credentials from various sources"""
        
        # Method 1: Environment variable with JSON content
        cred_json = os.environ.get('FIREBASE_ADMIN_CREDENTIALS')
        if cred_json:
            try:
                cred_dict = json.loads(cred_json)
                logger.info("Using Firebase credentials from environment variable")
                return credentials.Certificate(cred_dict)
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON in FIREBASE_ADMIN_CREDENTIALS: {e}")
        
        # Method 2: Service account key file path
        cred_path = os.environ.get('FIREBASE_CREDENTIALS_PATH')
        if cred_path and os.path.exists(cred_path):
            logger.info(f"Using Firebase credentials from file: {cred_path}")
            return credentials.Certificate(cred_path)
        
        # Method 3: Check common locations for service account file
        possible_paths = [
            'coursewagon-firebase-adminsdk.json',
            'utils/coursewagon-firebase-adminsdk.json',
            'firebase-adminsdk.json',
            'serviceAccountKey.json'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Using Firebase credentials from file: {path}")
                return credentials.Certificate(path)
        
        # Method 4: Try Application Default Credentials (for production)
        try:
            logger.info("Attempting to use Application Default Credentials")
            return credentials.ApplicationDefault()
        except Exception as e:
            logger.warning(f"Application Default Credentials not available: {e}")
        
        logger.error("No Firebase credentials found")
        return None
    
    def verify_id_token(self, id_token: str) -> Optional[Dict]:
        """
        Verify a Firebase ID token
        
        Args:
            id_token: The Firebase ID token to verify
            
        Returns:
            Dict containing user information if token is valid, None otherwise
        """
        try:
            # Verify the ID token
            decoded_token = auth.verify_id_token(id_token)
            
            logger.debug(f"Token verified for user: {decoded_token.get('uid')}")
            
            return {
                'uid': decoded_token.get('uid'),
                'email': decoded_token.get('email'),
                'email_verified': decoded_token.get('email_verified', False),
                'name': decoded_token.get('name'),
                'picture': decoded_token.get('picture'),
                'provider': decoded_token.get('firebase', {}).get('sign_in_provider'),
                'token': decoded_token
            }
            
        except auth.InvalidIdTokenError as e:
            logger.warning(f"Invalid Firebase ID token: {str(e)}")
            return None
        except auth.ExpiredIdTokenError as e:
            logger.warning(f"Expired Firebase ID token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error verifying Firebase ID token: {str(e)}")
            return None
    
    def get_user_by_uid(self, uid: str) -> Optional[Dict]:
        """
        Get user information by Firebase UID
        
        Args:
            uid: Firebase user UID
            
        Returns:
            Dict containing user information if found, None otherwise
        """
        try:
            user_record = auth.get_user(uid)
            
            return {
                'uid': user_record.uid,
                'email': user_record.email,
                'email_verified': user_record.email_verified,
                'display_name': user_record.display_name,
                'photo_url': user_record.photo_url,
                'disabled': user_record.disabled,
                'creation_time': user_record.user_metadata.creation_timestamp,
                'last_sign_in_time': user_record.user_metadata.last_sign_in_timestamp
            }
            
        except auth.UserNotFoundError:
            logger.warning(f"Firebase user not found: {uid}")
            return None
        except Exception as e:
            logger.error(f"Error getting Firebase user: {str(e)}")
            return None
    
    def create_custom_token(self, uid: str, additional_claims: Optional[Dict] = None) -> Optional[str]:
        """
        Create a custom token for a user
        
        Args:
            uid: User UID
            additional_claims: Additional claims to include in the token
            
        Returns:
            Custom token string if successful, None otherwise
        """
        try:
            custom_token = auth.create_custom_token(uid, additional_claims)
            return custom_token.decode('utf-8') if isinstance(custom_token, bytes) else custom_token
            
        except Exception as e:
            logger.error(f"Error creating custom token: {str(e)}")
            return None
    
    def revoke_refresh_tokens(self, uid: str) -> bool:
        """
        Revoke all refresh tokens for a user
        
        Args:
            uid: User UID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            auth.revoke_refresh_tokens(uid)
            logger.info(f"Revoked refresh tokens for user: {uid}")
            return True
            
        except Exception as e:
            logger.error(f"Error revoking refresh tokens: {str(e)}")
            return False

# Global instance
firebase_admin_service = FirebaseAdminService()
