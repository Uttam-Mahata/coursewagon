import os
from PIL import Image
import logging
from dotenv import load_dotenv
from utils.firebase_helper import FirebaseHelper
import sys
from io import BytesIO

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_firebase_storage():
    try:
        # Get the image path from command line or use default
        image_path = sys.argv[1] if len(sys.argv) > 1 else 'gemini-native-image.png'
        
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return False
            
        # Initialize Firebase
        firebase = FirebaseHelper()
        
        # Read the image file as bytes
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
            
        logger.info(f"Image loaded: {image_path}, size: {len(image_bytes)} bytes")
        
        # Try uploading to Firebase
        storage_path = "test/upload_test"
        image_url = firebase.upload_image(image_bytes, storage_path)
        
        logger.info(f"Image uploaded successfully to Firebase")
        logger.info(f"Image URL: {image_url}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during Firebase storage test: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    if test_firebase_storage():
        print("✅ Firebase storage test successful!")
    else:
        print("❌ Firebase storage test failed!")
