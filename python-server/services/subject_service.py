# services/subject_service.py
from repositories.subject_repo import SubjectRepository
from models.subject import Subject
from models.schemas import SubjectContent
from repositories.course_repo import CourseRepository
from utils.gemini_helper import GeminiHelper, extract_sql_query
from utils.gemini_image_generation_helper import GeminiImageGenerator
from utils.unified_storage_helper import storage_helper
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

class SubjectService:
    def __init__(self, db: Session):
        self.subject_repo = SubjectRepository(db)
        self.course_repo = CourseRepository(db)
        self.storage_helper = storage_helper

    def generate_subjects(self, course_id):
        course = self.course_repo.get_course_by_id(course_id)
        gemini_helper = GeminiHelper()

        if not course:
            raise Exception("Course not found")

        prompt = f"""Based on the course '{course.name}' with description '{course.description}', 
        generate a list of  relevant subjects that should be included in this course.
        Consider the following:
        1. If it's a school/college/university course, align with their typical curriculum
        2. Don't include the course name as a subject
        3. Keep subjects relevant and practical
        4. Generate maximum 5 core subjects for the course
        """
        
        try:
            response = gemini_helper.generate_content(
                prompt,
                response_schema=SubjectContent
            )
            
            # If updating, clear existing subjects first
            if course.has_subjects:
                self.subject_repo.delete_subjects_by_course_id(course_id)
            
            # Initialize image generator
            image_generator = GeminiImageGenerator()
            created_subjects = []
            
            for subject_name in response['subjects']:
                subject = Subject(
                    course_id=course_id,
                    name=subject_name
                )
                created_subject = self.subject_repo.add_subject(subject)
                created_subjects.append(created_subject)
                
                # Try to generate an image for each subject
                try:
                    # Generate image
                    image_bytes = image_generator.generate_subject_image(subject_name, course.name)
                    
                    if image_bytes:
                        # Upload to Azure Storage
                        image_path = f"courses/{course_id}/subjects/{created_subject.id}/cover"
                        image_url = self.storage_helper.upload_image(image_bytes, image_path)
                        
                        # Update subject with image URL
                        self.subject_repo.update_subject_image(created_subject.id, image_url)
                except Exception as img_error:
                    # Log but don't fail if image generation fails
                    logger.error(f"Error generating subject image: {str(img_error)}")
            
            # Mark that the course has subjects
            self.course_repo.set_has_subjects(course_id, True)

            return {"message": "Subjects generated successfully"}
            
        except Exception as e:
            raise Exception(f"Error generating subjects: {e}")

    def get_subjects_by_course_id(self, course_id):
        subjects = self.subject_repo.get_subjects_by_course_id(course_id)
        return [subject.to_dict() for subject in subjects]

    def create_subject(self, course_id, name):
        logger.info(f"Creating new subject for course_id: {course_id}")
        
        # Verify course exists
        course = self.course_repo.get_course_by_id(course_id)
        if not course:
            logger.error(f"Course not found for id: {course_id}")
            raise Exception("Course not found")
            
        try:
            subject = self.subject_repo.create_subject(course_id, name)
            
            # If this is first subject, mark course as having subjects
            if not course.has_subjects:
                self.course_repo.set_has_subjects(course_id, True)
                
            # Try to generate an image using environment API key
            try:
                # Initialize image generator
                image_generator = GeminiImageGenerator()
                
                # Generate image
                image_bytes = image_generator.generate_subject_image(name, course.name)
                
                if image_bytes:
                    # Upload to Azure Storage
                    image_path = f"courses/{course_id}/subjects/{subject.id}/cover"
                    image_url = self.storage_helper.upload_image(image_bytes, image_path)
                    
                    # Update subject with image URL
                    self.subject_repo.update_subject_image(subject.id, image_url)
            except Exception as img_error:
                # Log but don't fail if image generation fails
                logger.error(f"Error generating subject image: {str(img_error)}")
                
            return subject.to_dict()
        except Exception as e:
            logger.error(f"Error creating subject: {str(e)}")
            raise Exception(f"Error creating subject: {str(e)}")

    def update_subject(self, subject_id, name):
        logger.info(f"Updating subject id: {subject_id}")
        
        try:
            subject = self.subject_repo.update_subject(subject_id, name)
            if subject:
                return subject.to_dict()
            else:
                logger.error(f"Subject not found for id: {subject_id}")
                raise Exception("Subject not found")
        except Exception as e:
            logger.error(f"Error updating subject: {str(e)}")
            raise Exception(f"Error updating subject: {str(e)}")
            
    def delete_subject(self, subject_id):
        logger.info(f"Deleting subject id: {subject_id}")
        
        try:
            success = self.subject_repo.delete_subject(subject_id)
            if success:
                return {"message": "Subject deleted successfully"}
            else:
                logger.error(f"Subject not found for id: {subject_id}")
                raise Exception("Subject not found")
        except Exception as e:
            logger.error(f"Error deleting subject: {str(e)}")
            raise Exception(f"Error deleting subject: {str(e)}")