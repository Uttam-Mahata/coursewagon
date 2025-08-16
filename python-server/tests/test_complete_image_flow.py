"""
This script tests the complete image generation and upload flow
"""
import os
import logging
from dotenv import load_dotenv
from utils.gemini_image_generation_helper import GeminiImageGenerator
from utils.firebase_helper import FirebaseHelper

# Configure logging to see detailed information
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_image_generation_and_upload():
    try:
        # 1. Get the API key
        api_key = os.environ.get('API_KEY')
        if not api_key:
            logger.error("API_KEY not found in environment variables")
            return False
            
        # 2. Initialize image generator
        generator = GeminiImageGenerator(api_key=api_key)
        
        # 3. Generate an image
        logger.info("Generating test image...")
        image_bytes = generator.generate_course_image(
            "Machine Learning Fundamentals", 
            "Learn the basics of machine learning including algorithms, data processing, and model training"
        )
        
        if not image_bytes:
            logger.error("Failed to generate image")
            return False
            
        logger.info(f"Image generated successfully, size: {len(image_bytes)} bytes")
        
        # 4. Initialize Firebase
        firebase = FirebaseHelper()
        
        # 5. Upload the image to Firebase
        logger.info("Uploading image to Firebase...")
        storage_path = "test/test_course_image"
        image_url = firebase.upload_image(image_bytes, storage_path)
        
        logger.info(f"Image uploaded successfully to Firebase. URL: {image_url}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in test: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_image_generation_and_upload()
    if success:
        print("✅ Complete image flow test successful!")
    else:
        print("❌ Complete image flow test failed!")
