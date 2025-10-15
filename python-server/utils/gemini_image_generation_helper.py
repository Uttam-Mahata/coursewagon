from google import genai  # Import directly from google
from google.genai import types
from PIL import Image
from io import BytesIO
import base64
import logging
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class GeminiImageGenerator:
    def __init__(self, api_key=None):
        # Always use API key from environment variables
        self.api_key = os.environ.get('GEMINI_IMAGE_GENERATION_API_KEY') or os.environ.get('API_KEY')
        
        if not self.api_key:
            logger.warning("No API_KEY found in environment variables. Image generation functionality will not work.")
            
        self.model_name = "gemini-2.5-flash-image"
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            if not self.api_key:
                raise ValueError("No API key available for Gemini. Set API_KEY in environment variables.")
            self._client = genai.Client(api_key=self.api_key)
        return self._client
    
    def generate_course_image(self, course_name, course_description=None):
        """
        Generate a cover image for a course based on its name and description
        """
        try:
            if not self.api_key:
                logger.error("Cannot generate image: No API key available")
                return None
                
            # Create a prompt for the image generation
            prompt = f"Create a professional, educational 3D rendered cover image for a course titled '{course_name}'."
            
            if course_description:
                # Add brief description context if available
                shortened_desc = course_description[:200] + ('...' if len(course_description) > 200 else '')
                prompt += f" The course is about: {shortened_desc}"
                
            prompt += " The image should be vibrant, inspiring, with subtle educational symbols, and suitable as a course thumbnail."
            
            # Generate the image
            logger.info(f"Generating image for course: {course_name}")
            return self._generate_image(prompt, f"course_{course_name.replace(' ', '_')}")
            
        except Exception as e:
            logger.error(f"Error generating course image: {str(e)}")
            return None
    
    def generate_subject_image(self, subject_name, course_name=None):
        """
        Generate a cover image for a subject based on its name and course
        """
        try:
            if not self.api_key:
                logger.error("Cannot generate image: No API key available")
                return None
                
            # Create a prompt for the image generation
            if course_name:
                prompt = f"Create a professional, educational 3D rendered cover image for a subject titled '{subject_name}' which is part of a course about '{course_name}'."
            else:
                prompt = f"Create a professional, educational 3D rendered cover image for a subject titled '{subject_name}'."
                
            prompt += " The image should be visually appealing, contain relevant educational symbols, and be suitable for an e-learning platform."
            
            # Generate the image
            logger.info(f"Generating image for subject: {subject_name}")
            return self._generate_image(prompt, f"subject_{subject_name.replace(' ', '_')}")
            
        except Exception as e:
            logger.error(f"Error generating subject image: {str(e)}")
            return None
    
    def _generate_image(self, prompt, prefix="image"):
        """
        Generate an image using Google Gemini - exact same approach as working image_gen.py
        """
        try:
            # Create a request identical to the working sample
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['TEXT', 'IMAGE']
                )
            )
            
            local_path = None
            
            # Process the response exactly like the working sample script
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    logger.info(f"Image generation text response: {part.text[:100]}...")
                elif part.inline_data is not None:
                    # This is critical - we need to handle the image data exactly like in image_gen.py
                    try:
                        # Create a unique filename for local debugging
                        unique_id = uuid.uuid4().hex[:8]
                        temp_filename = f"{prefix}_{unique_id}.png"
                        local_path = os.path.join('/tmp', temp_filename)
                        
                        # Save the image directly from the inline_data bytes
                        # This is the exact same approach as in the working image_gen.py
                        image = Image.open(BytesIO(part.inline_data.data))
                        image.save(local_path)
                        logger.info(f"Saved debug image to {local_path}, size: {os.path.getsize(local_path)} bytes")
                        
                        # Read the file back as bytes - this ensures we're using the exact same format that worked
                        with open(local_path, 'rb') as f:
                            image_bytes = f.read()
                            
                        logger.info(f"Successfully processed image, size: {len(image_bytes)} bytes")
                        return image_bytes
                    except Exception as img_err:
                        logger.error(f"Error processing image data: {str(img_err)}", exc_info=True)
                        return None
            
            logger.warning("No image was found in the response")
            return None
            
        except Exception as e:
            logger.error(f"Error in image generation: {str(e)}", exc_info=True)
            return None
        finally:
            # Clean up temp file if it exists
            if local_path and os.path.exists(local_path):
                try:
                    os.remove(local_path)
                except Exception:
                    pass
                    
            # Clear the client reference
            self._client = None
