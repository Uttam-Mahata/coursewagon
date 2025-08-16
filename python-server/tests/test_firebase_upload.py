import os
import logging
from dotenv import load_dotenv
from utils.firebase_helper import FirebaseHelper

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_firebase_upload():
    """Simple test for Firebase upload functionality"""
    try:
        # Create a simple test image
        test_image_path = "gemini-native-image.png"
        
        # Check if the test image exists
        if not os.path.exists(test_image_path):
            logger.error(f"Test image not found: {test_image_path}")
            return False
            
        # Read test image
        with open(test_image_path, 'rb') as f:
            image_bytes = f.read()
        
        logger.info(f"Loaded test image: {len(image_bytes)} bytes")
        
        # Initialize Firebase
        firebase = FirebaseHelper()
        
        # Upload the image
        storage_path = "test/test_image"
        image_url = firebase.upload_image(image_bytes, storage_path)
        
        logger.info(f"Image uploaded successfully! URL: {image_url}")
        
        return image_url
    
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    result = test_firebase_upload()
    if result:
        print(f"✅ Success! Image URL: {result}")
    else:
        print("❌ Test failed")
