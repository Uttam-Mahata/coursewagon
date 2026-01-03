import logging
from repositories.chapter_repo import ChapterRepository
from models.chapter import Chapter
from models.schemas import ChapterContent
from repositories.subject_repo import SubjectRepository
from repositories.course_repo import CourseRepository
from utils.gemini_helper import GeminiHelper, extract_sql_query
from sqlalchemy.orm import Session
import json
from agents.curriculum_agents import get_chapter_agent
from utils.async_helper import run_async_in_sync

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ChapterService:
    def __init__(self, db: Session):
        self.chapter_repo = ChapterRepository(db)
        self.subject_repo = SubjectRepository(db)
        self.course_repo = CourseRepository(db)

    def generate_chapters(self, course_id, subject_id):
        try:
            logger.info(f"Starting chapter generation for subject_id: {subject_id}, course_id: {course_id}")
            
            subject = self.subject_repo.get_subjects_by_course_id(course_id)
            if not subject:
                logger.error(f"No subjects found for course_id: {course_id}")
                raise Exception("Subject not Found")
                
            subject_info = [item for item in subject if item.id == subject_id][0]
            subject_name = subject_info.name
            logger.debug(f"Found subject: {subject_name}")
            
            course = self.course_repo.get_course_by_id(course_id)
            if not course:
                logger.error(f"Course not found with id: {course_id}")
                raise Exception("Course Not Found")
            
            logger.debug(f"Found course: {course.name}")
            
            # Use ADK Agent
            agent = get_chapter_agent()
            prompt = f"""
            Course Name: {course.name}
            Course Description: {course.description}
            Subject Name: {subject_name}

            Generate chapters for this subject.
            """
            
            logger.debug("Calling Gemini API via ADK agent")

            # Helper to run async agent synchronously
            async def run_agent():
                final_response = None
                async for event in agent.run_async(prompt):
                    if event.turn_complete:
                         if event.content and event.content.parts:
                             final_response = event.content.parts[0].text
                return final_response

            response_text = run_async_in_sync(run_agent())

            response_data = json.loads(response_text)
            logger.debug(f"Received response from Gemini via ADK: {response_data}")
            
            # If updating, clear existing chapters first
            if subject_info.has_chapters:
                self.chapter_repo.delete_chapters_by_subject_id(subject_id)
            
            chapters_added = 0
            for chapter_name in response_data['chapters']:
                chapter = Chapter(
                    subject_id=subject_id,
                    name=chapter_name
                )
                self.chapter_repo.add_chapter(chapter)
                chapters_added += 1
            
            # Mark that the subject has chapters
            self.subject_repo.set_has_chapters(subject_id, True)
            
            logger.info(f"Successfully added {chapters_added} chapters")
            return {"message": f"Successfully generated {chapters_added} chapters"}
            
        except Exception as e:
            logger.error(f"Error in generate_chapters: {str(e)}", exc_info=True)
            raise Exception(f"Error generating chapters: {str(e)}")

    def get_chapters_by_subject_id(self, subject_id):  # Changed from module_id to subject_id
        chapters = self.chapter_repo.get_chapters_by_subject_id(subject_id)
        return [chapter.to_dict() for chapter in chapters]
        
    def get_chapter_by_id(self, chapter_id):
        chapter = self.chapter_repo.get_chapter_by_id(chapter_id)
        return chapter.to_dict() if chapter else None

    # New CRUD methods
    def create_chapter(self, subject_id, name):
        logger.info(f"Creating new chapter for subject_id: {subject_id}")
        
        # Verify subject exists
        subject = self.subject_repo.get_subject_by_id(subject_id)
        if not subject:
            logger.error(f"Subject not found for id: {subject_id}")
            raise Exception("Subject not found")
            
        try:
            chapter = self.chapter_repo.create_chapter(subject_id, name)
            
            # If this is first chapter, mark subject as having chapters
            if not subject.has_chapters:
                self.subject_repo.set_has_chapters(subject_id, True)
                
            return chapter.to_dict()
        except Exception as e:
            logger.error(f"Error creating chapter: {str(e)}")
            raise Exception(f"Error creating chapter: {str(e)}")

    def update_chapter(self, chapter_id, name):
        logger.info(f"Updating chapter id: {chapter_id}")
        
        try:
            chapter = self.chapter_repo.update_chapter(chapter_id, name)
            if chapter:
                return chapter.to_dict()
            else:
                logger.error(f"Chapter not found for id: {chapter_id}")
                raise Exception("Chapter not found")
        except Exception as e:
            logger.error(f"Error updating chapter: {str(e)}")
            raise Exception(f"Error updating chapter: {str(e)}")
            
    def delete_chapter(self, chapter_id):
        logger.info(f"Deleting chapter id: {chapter_id}")
        
        try:
            success = self.chapter_repo.delete_chapter(chapter_id)
            if success:
                return {"message": "Chapter deleted successfully"}
            else:
                logger.error(f"Chapter not found for id: {chapter_id}")
                raise Exception("Chapter not found")
        except Exception as e:
            logger.error(f"Error deleting chapter: {str(e)}")
            raise Exception(f"Error deleting chapter: {str(e)}")