#!/usr/bin/env python3
"""
Test script to verify Google Cloud Storage integration
"""

import os
import sys
sys.path.append('/home/uttam/coursewagon/python-server')

from utils.unified_storage_helper import storage_helper
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_storage_integration():
    """Test the unified storage helper"""
    try:
        # Check available providers
        providers = storage_helper.get_available_providers()
        primary = storage_helper.get_primary_provider_name()
        
        logger.info(f"Available storage providers: {providers}")
        logger.info(f"Primary storage provider: {primary}")
        
        # Test with a small image (create a simple PNG)
        from PIL import Image
        from io import BytesIO
        
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        test_image_bytes = img_bytes.getvalue()
        
        logger.info(f"Created test image: {len(test_image_bytes)} bytes")
        
        # Test upload
        test_path = "test/storage_test_image"
        logger.info(f"Uploading test image to path: {test_path}")
        
        image_url = storage_helper.upload_image(test_image_bytes, test_path)
        logger.info(f"✅ Upload successful! URL: {image_url}")
        
        # Test deletion
        logger.info("Testing image deletion...")
        delete_result = storage_helper.delete_image(image_url)
        logger.info(f"✅ Delete result: {delete_result}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Storage test failed: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting storage integration test...")
    success = test_storage_integration()
    
    if success:
        logger.info("🎉 Storage integration test completed successfully!")
    else:
        logger.error("💥 Storage integration test failed!")
        sys.exit(1)
