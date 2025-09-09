# services/course_service.py
from repositories.course_repo import CourseRepository
from models.course import Course
from models.schemas import CourseContent
from utils.gemini_helper import GeminiHelper
from utils.gemini_image_generation_helper import GeminiImageGenerator
from utils.unified_storage_helper import storage_helper
from sqlalchemy.orm import Session
import logging
import asyncio

logger = logging.getLogger(__name__)

class CourseService:
    def __init__(self, db: Session):
        self.course_repo = CourseRepository(db)
        self.storage_helper = storage_helper

    def add_course(self, course_name, user_id):
        try:
            # Initialize GeminiHelper using environment variables
            gemini_helper = GeminiHelper()
            
            prompt = f"""Generate a course name and description(max 100 words) based on '{course_name}'.
            The description should be comprehensive and educational.
            Return only the course details without any additional text."""
            
            response = gemini_helper.generate_content(
                prompt,
                response_schema=CourseContent
            )
            
            course = Course(
                name=response['name'],
                description=response['description'],
                user_id=user_id
            )
            created_course = self.course_repo.add_course(course)
            
            # Try to generate an image for the course
            try:
                # Initialize image generator using environment variables
                image_generator = GeminiImageGenerator()
                
                # Generate image
                image_bytes = image_generator.generate_course_image(created_course.name, created_course.description)
                
                if image_bytes:
                    # Upload to storage (GCS primary, Azure/Firebase fallback)
                    image_path = f"courses/{created_course.id}/cover"
                    image_url = self.storage_helper.upload_image(image_bytes, image_path)
                    
                    # Update course with image URL
                    self.course_repo.update_course_image(created_course.id, image_url)
            except Exception as img_error:
                # Log but don't fail if image generation fails
                logger.error(f"Error generating course image: {str(img_error)}")
            
            return {"message": "Course created successfully", "course_id": created_course.id}
                
        except Exception as e:
            logger.error(f"Error creating course: {str(e)}")
            raise Exception(f"Error creating course: {e}")

    def get_all_courses(self):
        courses = self.course_repo.get_all_courses()
        return [course.to_dict() for course in courses]
    
    def get_user_courses(self, user_id):
        courses = self.course_repo.get_user_courses(user_id)
        return [course.to_dict() for course in courses]
    
    def get_course_by_id(self, course_id):
      course = self.course_repo.get_course_by_id(course_id)
      if course:
        return course.to_dict()
      else:
        return None

    # New CRUD methods
    def create_course_manual(self, name, description, user_id):
        logger.info(f"Manually creating course for user_id: {user_id}")
        
        try:
            # Create the course
            course = self.course_repo.create_course(name, description, user_id)
            
            # Try to generate an image using environment API key
            try:
                # Initialize image generator using environment variables
                image_generator = GeminiImageGenerator()
                
                # Generate image
                image_bytes = image_generator.generate_course_image(course.name, course.description)
                
                if image_bytes:
                    # Upload to storage (GCS primary, Azure/Firebase fallback)
                    image_path = f"courses/{course.id}/cover"
                    image_url = self.storage_helper.upload_image(image_bytes, image_path)
                    
                    # Update course with image URL
                    self.course_repo.update_course_image(course.id, image_url)
            except Exception as img_error:
                # Log but don't fail if image generation fails
                logger.error(f"Error generating course image: {str(img_error)}")
            
            return course.to_dict()
        except Exception as e:
            logger.error(f"Error creating course: {str(e)}")
            raise Exception(f"Error creating course: {str(e)}")

    def update_course(self, course_id, name, description=None):
        logger.info(f"Updating course id: {course_id}")
        
        try:
            course = self.course_repo.update_course(course_id, name, description)
            if course:
                return course.to_dict()
            else:
                logger.error(f"Course not found for id: {course_id}")
                raise Exception("Course not found")
        except Exception as e:
            logger.error(f"Error updating course: {str(e)}")
            raise Exception(f"Error updating course: {str(e)}")
            
    def delete_course(self, course_id):
        logger.info(f"Deleting course id: {course_id}")
        
        try:
            success = self.course_repo.delete_course(course_id)
            if success:
                return {"message": "Course deleted successfully"}
            else:
                logger.error(f"Course not found for id: {course_id}")
                raise Exception("Course not found")
        except Exception as e:
            logger.error(f"Error deleting course: {str(e)}")
            raise Exception(f"Error deleting course: {str(e)}")
    
    def add_course_from_audio(self, audio_file_path, user_id):
        """
        Create a course from audio description using Gemini Live Helper
        
        Args:
            audio_file_path: Path to the audio file containing course description
            user_id: ID of the user creating the course
            
        Returns:
            dict: Course creation result
        """
        try:
            logger.info(f"Creating course from audio for user_id: {user_id}")
            
            # Use GeminiLiveHelper to process the audio and get course content
            from utils.gemini_live_helper import GeminiLiveHelper
            
            gemini_live = GeminiLiveHelper()
            
            # Get transcribed text from audio using synchronous method
            transcribed_text = gemini_live.audio_to_text_sync(audio_file_path)
            
            if not transcribed_text:
                raise ValueError("No text could be extracted from the audio")
            
            logger.info(f"Transcribed text: {transcribed_text[:100]}...")
            
            # Use the same course generation logic as text-based course creation
            gemini_helper = GeminiHelper()
            
            prompt = f"""Generate a course name and description(max 100 words) based on '{transcribed_text}'.
            The description should be comprehensive and educational.
            Return only the course details without any additional text."""
            
            response = gemini_helper.generate_content(
                prompt,
                response_schema=CourseContent
            )
            
            course = Course(
                name=response['name'],
                description=response['description'],
                user_id=user_id
            )
            created_course = self.course_repo.add_course(course)
            
            # Try to generate an image for the course
            try:
                # Initialize image generator using environment variables
                image_generator = GeminiImageGenerator()
                
                # Generate image
                image_bytes = image_generator.generate_course_image(created_course.name, created_course.description)
                
                if image_bytes:
                    # Upload to storage (GCS primary, Azure/Firebase fallback)
                    image_path = f"courses/{created_course.id}/cover"
                    image_url = self.storage_helper.upload_image(image_bytes, image_path)
                    
                    # Update course with image URL
                    self.course_repo.update_course_image(created_course.id, image_url)
            except Exception as img_error:
                # Log but don't fail if image generation fails
                logger.error(f"Error generating course image: {str(img_error)}")
            
            return {"message": "Course created successfully from audio", "course_id": created_course.id}
            
        except Exception as e:
            logger.error(f"Error creating course from audio: {str(e)}")
            raise Exception(f"Error creating course from audio: {e}")