from utils.gemini_image_generation_helper import GeminiImageGenerator
from utils.gemini_image_generation_helper import GeminiImageGenerator
from utils.azure_storage_helper import AzureStorageHelper
from repositories.course_repo import CourseRepository
from repositories.subject_repo import SubjectRepository
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

class ImageService:
    def __init__(self, db: Session):
        self.course_repo = CourseRepository(db)
        self.subject_repo = SubjectRepository(db)
        self.azure_storage = AzureStorageHelper()
        
    def generate_course_image(self, course_id):
        """Generate and store a cover image for a course"""
        try:
            # Get course details
            course = self.course_repo.get_course_by_id(course_id)
            if not course:
                raise ValueError(f"Course not found: {course_id}")
                
            # Initialize the image generator using environment variables
            generator = GeminiImageGenerator()
            
            # Generate the image
            logger.info(f"Generating image for course '{course.name}' (ID: {course_id})")
            image_bytes = generator.generate_course_image(course.name, course.description)
            if not image_bytes:
                raise ValueError("Failed to generate image")
            
            logger.info(f"Image generated successfully, size: {len(image_bytes)} bytes")
            
            # Save a local copy for debugging
            local_debug_path = f"/tmp/course_{course_id}_image_debug.png"
            try:
                with open(local_debug_path, 'wb') as f:
                    f.write(image_bytes)
                logger.info(f"Debug image saved to {local_debug_path}")
            except Exception as save_err:
                logger.warning(f"Could not save debug image: {str(save_err)}")
            
            # Upload the image to Azure Storage
            image_path = f"courses/{course_id}/cover"
            logger.info(f"Uploading image to Azure Storage path: {image_path}")
            image_url = self.azure_storage.upload_image(image_bytes, image_path)
            logger.info(f"Image uploaded successfully, URL: {image_url}")
            
            # Delete old image if it exists
            old_image_url = self.course_repo.get_course_image_url(course_id)
            if old_image_url:
                logger.info(f"Deleting old image: {old_image_url}")
                self.azure_storage.delete_image(old_image_url)
            
            # Update the course with the new image URL
            logger.info(f"Updating course with new image URL: {image_url}")
            updated_course = self.course_repo.update_course_image(course_id, image_url)
            
            return updated_course.to_dict() if updated_course else None
            
        except Exception as e:
            logger.error(f"Error generating course image: {str(e)}")
            raise
            
    def generate_subject_image(self, course_id, subject_id):
        """Generate and store a cover image for a subject"""
        try:
            # Get subject details
            subject = self.subject_repo.get_subject_by_id(subject_id)
            if not subject:
                raise ValueError(f"Subject not found: {subject_id}")
                
            # Get course name for context
            course = self.course_repo.get_course_by_id(course_id)
            if not course:
                raise ValueError(f"Course not found: {course_id}")
                
            # Initialize the image generator using environment variables
            generator = GeminiImageGenerator()
            
            # Generate the image
            image_bytes = generator.generate_subject_image(subject.name, course.name)
            if not image_bytes:
                raise ValueError("Failed to generate image")
                
            # Upload the image to Azure Storage
            image_path = f"courses/{course_id}/subjects/{subject_id}/cover"
            image_url = self.azure_storage.upload_image(image_bytes, image_path)
            
            # Delete old image if it exists
            old_image_url = self.subject_repo.get_subject_image_url(subject_id)
            if old_image_url:
                self.azure_storage.delete_image(old_image_url)
            
            # Update the subject with the new image URL
            updated_subject = self.subject_repo.update_subject_image(subject_id, image_url)
            
            return updated_subject.to_dict() if updated_subject else None
            
        except Exception as e:
            logger.error(f"Error generating subject image: {str(e)}")
            raise
            
    def generate_images_for_subjects(self, course_id):
        """Generate images for all subjects in a course"""
        try:
            # Get all subjects for the course
            subjects = self.subject_repo.get_subjects_by_course_id(course_id)
            
            results = []
            for subject in subjects:
                try:
                    result = self.generate_subject_image(course_id, subject.id)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error generating image for subject {subject.id}: {str(e)}")
                    results.append({"id": subject.id, "error": str(e)})
                    
            return results
            
        except Exception as e:
            logger.error(f"Error generating images for subjects: {str(e)}")
            raise

    def check_image_url(self, image_url):
        """Check if an image URL is valid and accessible"""
        try:
            import requests
            from PIL import Image
            from io import BytesIO
            
            # Try to fetch the image
            response = requests.get(image_url, timeout=5)
            response.raise_for_status()
            
            # Try to open it as an image
            Image.open(BytesIO(response.content))
            
            # If we got here, it's a valid image
            return {"valid": True, "message": "Image is valid"}
        except Exception as e:
            logger.error(f"Image URL check failed: {str(e)}")
            return {"valid": False, "error": str(e)}
