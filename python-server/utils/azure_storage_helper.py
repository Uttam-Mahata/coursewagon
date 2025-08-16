import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContentSettings, generate_blob_sas, BlobSasPermissions
from azure.identity import DefaultAzureCredential
from io import BytesIO
import time
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class AzureStorageHelper:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AzureStorageHelper, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        try:
            # Azure Storage configuration
            self.account_name = os.environ.get('AZURE_STORAGE_ACCOUNT_NAME')
            self.container_name = os.environ.get('AZURE_STORAGE_CONTAINER_NAME', 'coursewagon-images')
            self.account_key = None  # Will be extracted from connection string
            
            # Method 1: Using connection string (most common for development)
            connection_string = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
            
            # Method 2: Using Azure credential (for production with managed identity)
            account_url = f"https://{self.account_name}.blob.core.windows.net"
            
            if connection_string:
                # Initialize with connection string
                self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
                # Extract account key from connection string for SAS generation
                for part in connection_string.split(';'):
                    if part.startswith('AccountKey='):
                        self.account_key = part.split('=', 1)[1]
                        break
                logger.info("Azure Storage initialized with connection string")
            elif self.account_name:
                # Initialize with Azure credentials (for managed identity/service principal)
                credential = DefaultAzureCredential()
                self.blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)
                logger.info("Azure Storage initialized with DefaultAzureCredential")
            else:
                raise ValueError("Azure Storage configuration missing. Set AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_ACCOUNT_NAME")
            
            # Create container if it doesn't exist
            try:
                container_client = self.blob_service_client.get_container_client(self.container_name)
                if not container_client.exists():
                    # Create container without public access (more secure)
                    container_client.create_container()
                    logger.info(f"Created Azure Storage container: {self.container_name}")
            except Exception as e:
                logger.warning(f"Could not create/verify container {self.container_name}: {str(e)}")
            
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure Storage: {str(e)}")
            raise
    
    def upload_image(self, image_bytes, path):
        """
        Upload an image to Azure Blob Storage
        
        Args:
            image_bytes: Image data as bytes
            path: Path where the image will be stored in Azure Storage
            
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
            
            logger.info(f"Uploading image to Azure Storage: path={path}, size={len(image_bytes)} bytes")
            
            # Debug check - verify byte data
            if len(image_bytes) < 1000:
                logger.warning(f"Image data seems too small ({len(image_bytes)} bytes), might not be a valid image")
            
            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=path
            )
            
            # Upload the image with content type
            from azure.storage.blob import ContentSettings
            
            content_settings = ContentSettings(
                content_type='image/png',
                cache_control='public, max-age=31536000'  # Cache for 1 year
            )
            
            blob_client.upload_blob(
                data=image_bytes,
                content_settings=content_settings,
                overwrite=True
            )
            
            # Generate the public URL with SAS token for secure access
            if self.account_key:
                # Generate SAS URL that expires in 1 year
                sas_token = generate_blob_sas(
                    account_name=self.account_name,
                    container_name=self.container_name,
                    blob_name=path,
                    account_key=self.account_key,
                    permission=BlobSasPermissions(read=True),
                    expiry=datetime.utcnow() + timedelta(days=365)
                )
                public_url = f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{path}?{sas_token}"
            else:
                # Fallback to direct URL (may not work if container is private)
                public_url = f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{path}"
            
            # Log successful upload with URL
            logger.info(f"Image successfully uploaded to Azure Storage. URL: {public_url}")
            
            return public_url
            
        except Exception as e:
            logger.error(f"Failed to upload image to Azure Storage: {str(e)}", exc_info=True)
            raise
    
    def delete_image(self, image_url):
        """
        Delete an image from Azure Blob Storage
        
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
            if 'blob.core.windows.net' in image_url:
                # URL format: https://accountname.blob.core.windows.net/container/path
                url_parts = image_url.split('/')
                if len(url_parts) >= 5:
                    # Extract path after container name
                    container_index = 4  # Index of container name in URL
                    path = '/'.join(url_parts[container_index + 1:])
                else:
                    logger.warning(f"Invalid Azure Storage URL format: {image_url}")
                    return False
            else:
                # Can't parse URL
                logger.warning(f"Invalid Azure Storage URL format: {image_url}")
                return False
            
            # Get blob client and delete
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=path
            )
            blob_client.delete_blob()
            
            logger.info(f"Successfully deleted image from Azure Storage: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete image from Azure Storage: {str(e)}")
            return False
    
    def get_blob_url(self, blob_path):
        """
        Get the public URL for a blob
        
        Args:
            blob_path: Path to the blob in storage
            
        Returns:
            The public URL of the blob
        """
        return f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob_path}"
