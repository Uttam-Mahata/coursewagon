import os
from google.cloud import storage
from google.oauth2 import service_account
from io import BytesIO
import time
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class GCSStorageHelper:
    """Google Cloud Storage helper class for handling file uploads and downloads"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GCSStorageHelper, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        try:
            # Google Cloud Storage configuration
            self.project_id = os.environ.get('GCP_PROJECT_ID', 'mitra-348d9')
            self.bucket_name = os.environ.get('GCS_BUCKET_NAME', 'coursewagon-storage-bucket')
            
            # Initialize the client
            credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            
            # Handle relative paths from the project root
            if credentials_path and not os.path.isabs(credentials_path):
                # Make path relative to the current file's directory (utils/)
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(current_dir)  # Go up one level from utils/
                credentials_path = os.path.join(project_root, credentials_path)
            
            if credentials_path and os.path.exists(credentials_path):
                # Use service account credentials
                credentials = service_account.Credentials.from_service_account_file(credentials_path)
                self.client = storage.Client(credentials=credentials, project=self.project_id)
                logger.info(f"GCS initialized with service account credentials from: {credentials_path}")
            else:
                # Use Application Default Credentials (ADC)
                try:
                    self.client = storage.Client(project=self.project_id)
                    logger.info("GCS initialized with Application Default Credentials")
                except Exception as adc_error:
                    logger.error(f"Failed to initialize with ADC: {str(adc_error)}")
                    if credentials_path:
                        logger.error(f"Service account file not found at: {credentials_path}")
                    raise
            
            # Get or create the bucket
            try:
                self.bucket = self.client.bucket(self.bucket_name)
                # Check if bucket exists
                if not self.bucket.exists():
                    # Create bucket with appropriate location and settings
                    self.bucket = self.client.create_bucket(
                        self.bucket_name,
                        location='US',  # or specify your preferred location
                    )
                    logger.info(f"Created GCS bucket: {self.bucket_name}")
                else:
                    logger.info(f"Using existing GCS bucket: {self.bucket_name}")
            except Exception as e:
                logger.error(f"Could not create/access bucket {self.bucket_name}: {str(e)}")
                raise
            
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Cloud Storage: {str(e)}")
            raise
    
    def upload_image(self, image_bytes, path):
        """
        Upload an image to Google Cloud Storage
        
        Args:
            image_bytes: Image data as bytes
            path: Path where the image will be stored in GCS
            
        Returns:
            The public URL of the uploaded blob
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
            
            # Ensure path doesn't start with '/'
            if path.startswith('/'):
                path = path[1:]
            
            logger.info(f"Uploading image to GCS: path={path}, size={len(image_bytes)} bytes")
            
            # Debug check - verify byte data
            if len(image_bytes) < 1000:
                logger.warning(f"Image data seems too small ({len(image_bytes)} bytes), might not be a valid image")
            
            # Create blob and upload
            blob = self.bucket.blob(path)
            
            # Set content type and cache control
            blob.content_type = 'image/png'
            blob.cache_control = 'public, max-age=31536000'  # Cache for 1 year
            
            # Upload the image
            blob.upload_from_string(
                data=image_bytes,
                content_type='image/png'
            )
            
            # Make the blob publicly readable
            blob.make_public()
            
            # Get the public URL
            public_url = blob.public_url
            
            # Log successful upload with URL
            logger.info(f"Image successfully uploaded to GCS. URL: {public_url}")
            
            return public_url
            
        except Exception as e:
            logger.error(f"Failed to upload image to GCS: {str(e)}", exc_info=True)
            raise
    
    def delete_image(self, image_url):
        """
        Delete an image from Google Cloud Storage
        
        Args:
            image_url: The URL of the image to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract the blob path from the URL
            if not image_url:
                return False
                
            # Parse the blob path from the URL
            if 'storage.googleapis.com' in image_url:
                # URL format: https://storage.googleapis.com/bucket-name/path
                url_parts = image_url.split('/')
                if len(url_parts) >= 5:
                    # Extract path after bucket name
                    bucket_index = 4  # Index of bucket name in URL
                    path = '/'.join(url_parts[bucket_index + 1:])
                else:
                    logger.warning(f"Invalid GCS URL format: {image_url}")
                    return False
            else:
                # Can't parse URL
                logger.warning(f"Invalid GCS URL format: {image_url}")
                return False
            
            # Get blob and delete
            blob = self.bucket.blob(path)
            if blob.exists():
                blob.delete()
                logger.info(f"Successfully deleted image from GCS: {path}")
                return True
            else:
                logger.warning(f"Image not found in GCS: {path}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to delete image from GCS: {str(e)}")
            return False
    
    def get_blob_url(self, blob_path):
        """
        Get the public URL for a blob
        
        Args:
            blob_path: Path to the blob in storage
            
        Returns:
            The public URL of the blob
        """
        return f"https://storage.googleapis.com/{self.bucket_name}/{blob_path}"
    
    def upload_file(self, file_bytes, path, content_type=None):
        """
        Upload any file to Google Cloud Storage
        
        Args:
            file_bytes: File data as bytes
            path: Path where the file will be stored in GCS
            content_type: MIME type of the file
            
        Returns:
            The public URL of the uploaded blob
        """
        try:
            # Create a unique filename with timestamp
            timestamp = int(time.time())
            if '.' not in path:
                path = f"{path}_{timestamp}"
            else:
                # Insert timestamp before file extension
                name, ext = path.rsplit('.', 1)
                path = f"{name}_{timestamp}.{ext}"
            
            # Ensure path doesn't start with '/'
            if path.startswith('/'):
                path = path[1:]
            
            logger.info(f"Uploading file to GCS: path={path}, size={len(file_bytes)} bytes")
            
            # Create blob and upload
            blob = self.bucket.blob(path)
            
            # Set content type if provided
            if content_type:
                blob.content_type = content_type
            
            blob.cache_control = 'public, max-age=31536000'  # Cache for 1 year
            
            # Upload the file
            blob.upload_from_string(
                data=file_bytes,
                content_type=content_type
            )
            
            # Make the blob publicly readable
            blob.make_public()
            
            # Get the public URL
            public_url = blob.public_url
            
            # Log successful upload with URL
            logger.info(f"File successfully uploaded to GCS. URL: {public_url}")
            
            return public_url
            
        except Exception as e:
            logger.error(f"Failed to upload file to GCS: {str(e)}", exc_info=True)
            raise
    
    def download_file(self, blob_path):
        """
        Download a file from Google Cloud Storage
        
        Args:
            blob_path: Path to the blob in storage
            
        Returns:
            File content as bytes
        """
        try:
            blob = self.bucket.blob(blob_path)
            if blob.exists():
                content = blob.download_as_bytes()
                logger.info(f"Downloaded file from GCS: {blob_path}, size: {len(content)} bytes")
                return content
            else:
                logger.warning(f"File not found in GCS: {blob_path}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to download file from GCS: {str(e)}")
            raise
    
    def list_files(self, prefix=None):
        """
        List files in the bucket
        
        Args:
            prefix: Optional prefix to filter files
            
        Returns:
            List of blob names
        """
        try:
            blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            logger.error(f"Failed to list files in GCS: {str(e)}")
            raise
