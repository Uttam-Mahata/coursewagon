from utils.firebase_helper import FirebaseHelper
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_firebase_connection():
    """Test the Firebase Storage connection"""
    try:
        # Set the Firebase storage bucket
        os.environ['FIREBASE_STORAGE_BUCKET'] = 'coursewagon.appspot.com'  # Replace with your actual bucket
        
        # Initialize the Firebase helper
        firebase = FirebaseHelper()
        
        # Create a test file
        test_content = b"This is a test file"
        test_path = "test/connection_test.txt"
        
        # Try to upload the file
        url = firebase.upload_image(test_content, test_path)
        logger.info(f"File uploaded successfully. URL: {url}")
        
        # Try to delete the file
        result = firebase.delete_image(url)
        logger.info(f"File deleted: {result}")
        
        return True
    except Exception as e:
        logger.error(f"Firebase test failed: {str(e)}")
        return False

if __name__ == "__main__":
    if test_firebase_connection():
        print("Firebase connection test passed!")
    else:
        print("Firebase connection test failed. Check the logs for details.")
