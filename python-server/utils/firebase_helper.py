import firebase_admin
from firebase_admin import credentials, storage
import os
from io import BytesIO
import time
import logging

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class FirebaseHelper:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseHelper, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        try:
            # Initialize Firebase if not already done
            if not firebase_admin._apps:
                # Look for credentials file - try in utils folder first, then root
                cred_path = os.environ.get('FIREBASE_CREDENTIALS_PATH', 'utils/coursewagon-firebase-adminsdk-biym7-69f7d55e79.json')
                
                # If not found in first location, try root folder
                if not os.path.exists(cred_path):
                    alt_path = 'coursewagon-firebase-adminsdk-biym7-69f7d55e79.json'
                    if os.path.exists(alt_path):
                        cred_path = alt_path
                
                if os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    storage_bucket = os.environ.get('FIREBASE_STORAGE_BUCKET', 'coursewagon.firebasestorage.app')
                    
                    # Use the bucket name exactly as configured in Firebase
                    self.app = firebase_admin.initialize_app(cred, {
                        'storageBucket': storage_bucket
                    })
                    logger.info(f"Firebase initialized successfully with bucket: {storage_bucket}")
                else:
                    logger.error(f"Firebase credentials file not found at {cred_path}")
                    raise FileNotFoundError(f"Firebase credentials file not found at {cred_path}")
            
            self.bucket = storage.bucket()
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {str(e)}")
            raise
    
    def upload_image(self, image_bytes, path):
        """
        Upload an image to Firebase Storage
        
        Args:
            image_bytes: Image data as bytes
            path: Path where the image will be stored in Firebase Storage
            
        Returns:
            The public URL of the uploaded image
        """
        try:
            # Create a unique filename with timestamp
            timestamp = int(time.time())
            if '.' not in path:
                path = f"{path}_{timestamp}.png"
            else:
                # Insert timestamp before file extension
                name, ext = path.rsplit('.', 1)
                path = f"{name}_{timestamp}.{ext}"
            
            logger.info(f"Uploading image to Firebase: path={path}, size={len(image_bytes)} bytes")
            
            # Debug check - verify byte data
            if len(image_bytes) < 1000:
                logger.warning(f"Image data seems too small ({len(image_bytes)} bytes), might not be a valid image")
            
            # Create a blob in Firebase Storage
            blob = self.bucket.blob(path)
            
            # Upload using blob.upload_from_file with BytesIO
            blob.upload_from_file(BytesIO(image_bytes), content_type='image/png')
            
            # Make the file publicly accessible
            blob.make_public()
            
            # Get the public URL
            public_url = blob.public_url
            
            # Log successful upload with URL
            logger.info(f"Image successfully uploaded to Firebase. URL: {public_url}")
            
            return public_url
            
        except Exception as e:
            logger.error(f"Failed to upload image to Firebase: {str(e)}", exc_info=True)
            raise
    
    def delete_image(self, image_url):
        """
        Delete an image from Firebase Storage
        
        Args:
            image_url: The URL of the image to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract the path from the URL
            if not image_url:
                return False
                
            # Parse the blob path from the URL
            if 'googleapis.com' in image_url:
                # URL format: https://storage.googleapis.com/BUCKET_NAME/PATH
                path = image_url.split('/', 4)[-1]
            else:
                # Can't parse URL
                logger.warning(f"Invalid Firebase URL format: {image_url}")
                return False
            
            # Delete the blob
            blob = self.bucket.blob(path)
            blob.delete()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete image from Firebase: {str(e)}")
            return False
