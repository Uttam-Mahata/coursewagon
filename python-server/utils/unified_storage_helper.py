import os
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class UnifiedStorageHelper:
    """
    Unified storage helper that prioritizes Google Cloud Storage,
    with fallback to Azure Storage and Firebase Storage
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UnifiedStorageHelper, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.storage_providers = []
        self.primary_provider = None
        
        # Try to initialize storage providers in order of priority
        self._initialize_storage_providers()
        self._initialized = True
    
    def _initialize_storage_providers(self):
        """Initialize storage providers in order of priority"""
        
        # 1st Priority: Google Cloud Storage
        try:
            from utils.gcs_storage_helper import GCSStorageHelper
            gcs_helper = GCSStorageHelper()
            self.storage_providers.append(('gcs', gcs_helper))
            if not self.primary_provider:
                self.primary_provider = ('gcs', gcs_helper)
            logger.info("Google Cloud Storage initialized successfully (Primary)")
        except Exception as e:
            logger.warning(f"Failed to initialize Google Cloud Storage: {str(e)}")
        
        # 2nd Priority: Azure Storage
        try:
            from utils.azure_storage_helper import AzureStorageHelper
            azure_helper = AzureStorageHelper()
            self.storage_providers.append(('azure', azure_helper))
            if not self.primary_provider:
                self.primary_provider = ('azure', azure_helper)
            logger.info("Azure Storage initialized successfully" + 
                       (" (Primary)" if not self.primary_provider else " (Fallback)"))
        except Exception as e:
            logger.warning(f"Failed to initialize Azure Storage: {str(e)}")
        
        # 3rd Priority: Firebase Storage
        try:
            from utils.firebase_helper import FirebaseHelper
            firebase_helper = FirebaseHelper()
            self.storage_providers.append(('firebase', firebase_helper))
            if not self.primary_provider:
                self.primary_provider = ('firebase', firebase_helper)
            logger.info("Firebase Storage initialized successfully" + 
                       (" (Primary)" if not self.primary_provider else " (Fallback)"))
        except Exception as e:
            logger.warning(f"Failed to initialize Firebase Storage: {str(e)}")
        
        if not self.storage_providers:
            raise RuntimeError("No storage providers could be initialized")
        
        logger.info(f"Initialized {len(self.storage_providers)} storage provider(s). "
                   f"Primary: {self.primary_provider[0] if self.primary_provider else 'None'}")
    
    def upload_image(self, image_bytes, path):
        """
        Upload an image using the primary storage provider with fallback
        
        Args:
            image_bytes: Image data as bytes
            path: Path where the image will be stored
            
        Returns:
            The public URL of the uploaded image
        """
        if not self.primary_provider:
            raise RuntimeError("No storage providers available")
        
        # Try primary provider first
        provider_name, provider = self.primary_provider
        try:
            url = provider.upload_image(image_bytes, path)
            logger.info(f"Image uploaded successfully using {provider_name}: {url}")
            return url
        except Exception as e:
            logger.error(f"Failed to upload image using {provider_name}: {str(e)}")
            
            # Try fallback providers
            for fallback_name, fallback_provider in self.storage_providers:
                if fallback_name == provider_name:
                    continue  # Skip the primary provider we just tried
                    
                try:
                    url = fallback_provider.upload_image(image_bytes, path)
                    logger.info(f"Image uploaded successfully using fallback {fallback_name}: {url}")
                    return url
                except Exception as fallback_e:
                    logger.error(f"Failed to upload image using fallback {fallback_name}: {str(fallback_e)}")
                    continue
            
            # If all providers failed, raise the original exception
            raise Exception(f"All storage providers failed. Primary error: {str(e)}")
    
    def delete_image(self, image_url):
        """
        Delete an image from storage
        
        Args:
            image_url: The URL of the image to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not image_url:
            return False
        
        # Determine which provider to use based on URL
        provider_to_use = None
        
        if 'storage.googleapis.com' in image_url:
            provider_to_use = self._get_provider('gcs')
        elif 'blob.core.windows.net' in image_url:
            provider_to_use = self._get_provider('azure')
        elif 'firebasestorage.app' in image_url or 'googleapis.com' in image_url:
            provider_to_use = self._get_provider('firebase')
        
        if provider_to_use:
            provider_name, provider = provider_to_use
            try:
                result = provider.delete_image(image_url)
                logger.info(f"Image deleted using {provider_name}: {result}")
                return result
            except Exception as e:
                logger.error(f"Failed to delete image using {provider_name}: {str(e)}")
                return False
        else:
            logger.warning(f"Could not determine storage provider for URL: {image_url}")
            return False
    
    def _get_provider(self, provider_name):
        """Get a specific provider by name"""
        for name, provider in self.storage_providers:
            if name == provider_name:
                return (name, provider)
        return None
    
    def upload_file(self, file_bytes, path, content_type=None):
        """
        Upload any file using the primary storage provider
        
        Args:
            file_bytes: File data as bytes
            path: Path where the file will be stored
            content_type: MIME type of the file
            
        Returns:
            The public URL of the uploaded file
        """
        if not self.primary_provider:
            raise RuntimeError("No storage providers available")
        
        provider_name, provider = self.primary_provider
        
        # Check if provider supports upload_file method
        if hasattr(provider, 'upload_file'):
            try:
                url = provider.upload_file(file_bytes, path, content_type)
                logger.info(f"File uploaded successfully using {provider_name}: {url}")
                return url
            except Exception as e:
                logger.error(f"Failed to upload file using {provider_name}: {str(e)}")
                raise
        else:
            # Fallback to upload_image for providers that don't support upload_file
            try:
                url = provider.upload_image(file_bytes, path)
                logger.info(f"File uploaded as image using {provider_name}: {url}")
                return url
            except Exception as e:
                logger.error(f"Failed to upload file using {provider_name}: {str(e)}")
                raise
    
    def get_primary_provider_name(self):
        """Get the name of the primary storage provider"""
        return self.primary_provider[0] if self.primary_provider else None
    
    def get_available_providers(self):
        """Get list of available storage provider names"""
        return [name for name, _ in self.storage_providers]


# Create a global instance
storage_helper = UnifiedStorageHelper()
