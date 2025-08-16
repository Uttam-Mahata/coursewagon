from utils.gemini_image_generation_helper import GeminiImageGenerator
from PIL import Image
from io import BytesIO
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_image_generation():
    # Create instance of the helper
    generator = GeminiImageGenerator()
    
    # Generate a test image
    print("Generating test image...")
    image_bytes = generator.generate_course_image(
        "Python Programming", 
        "Learn Python programming from scratch with practical examples"
    )
    
    if image_bytes:
        print(f"Image generated successfully! Size: {len(image_bytes)} bytes")
        
        # Save the image
        image = Image.open(BytesIO(image_bytes))
        image.save('test_course_image.png')
        print("Image saved to test_course_image.png")
        
        # Try to display the image
        try:
            image.show()
        except Exception as e:
            print(f"Could not display image: {e}")
    else:
        print("Failed to generate image")

if __name__ == "__main__":
    test_image_generation()
