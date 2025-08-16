import os
import sys
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import our components
from utils.gemini_image_generation_helper import GeminiImageGenerator
from utils.firebase_helper import FirebaseHelper

def test_image_pipeline():
    # Get API key from environment
    api_key = os.environ.get('API_KEY')
    if not api_key:
        logger.error("API_KEY environment variable not set")
        return False
    
    try:
        # Step 1: Generate an image
        generator = GeminiImageGenerator(api_key=api_key)
        image_bytes = generator.generate_course_image("Test Course", "This is a test course to verify image generation and storage")
        
        if not image_bytes:
            logger.error("Failed to generate image")
            return False
            
        logger.info(f"Generated image successfully, size: {len(image_bytes)} bytes")
        
        # Step 2: Save the image locally to verify it's valid
        with open("test_image.png", "wb") as f:
            f.write(image_bytes)
        logger.info("Saved image to test_image.png")
        
        # Step 3: Upload to Firebase
        firebase = FirebaseHelper()
        image_path = "test/test_image"
        image_url = firebase.upload_image(image_bytes, image_path)
        
        logger.info(f"Uploaded image to Firebase: {image_url}")
        print(f"Image URL: {image_url}")
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_image_pipeline()
    print(f"Test {'succeeded' if success else 'failed'}")
    sys.exit(0 if success else 1)
