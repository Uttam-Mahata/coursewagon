#!/usr/bin/env python3

"""
Test script for Azure Storage integration
Run this after setting up Azure Storage to verify everything works
"""

import os
import sys
from io import BytesIO
from PIL import Image
import logging

# Add the server directory to Python path
sys.path.append('/home/uttam/CourseWagon/server')

from utils.azure_storage_helper import AzureStorageHelper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_image():
    """Create a simple test image"""
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()

def test_azure_storage():
    """Test Azure Storage upload and delete functionality"""
    try:
        logger.info("Testing Azure Storage integration...")
        
        # Check if Azure Storage is configured
        if not os.environ.get('AZURE_STORAGE_CONNECTION_STRING') and not os.environ.get('AZURE_STORAGE_ACCOUNT_NAME'):
            logger.error("Azure Storage not configured. Please set AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_ACCOUNT_NAME")
            return False
        
        # Initialize Azure Storage
        azure_storage = AzureStorageHelper()
        logger.info("✅ Azure Storage helper initialized successfully")
        
        # Create test image
        test_image_bytes = create_test_image()
        logger.info(f"✅ Created test image ({len(test_image_bytes)} bytes)")
        
        # Upload test image
        test_path = "test/test_image"
        image_url = azure_storage.upload_image(test_image_bytes, test_path)
        logger.info(f"✅ Image uploaded successfully: {image_url}")
        
        # Test delete (optional - comment out if you want to keep the test image)
        # delete_success = azure_storage.delete_image(image_url)
        # logger.info(f"✅ Image deleted: {delete_success}")
        
        logger.info("🎉 Azure Storage integration test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Azure Storage test failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    success = test_azure_storage()
    exit(0 if success else 1)
