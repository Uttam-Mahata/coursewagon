import logging
from repositories.chapter_repo import ChapterRepository
from models.chapter import Chapter
from models.schemas import ChapterContent
from repositories.module_repo import ModuleRepository
from repositories.subject_repo import SubjectRepository
from repositories.course_repo import CourseRepository
from utils.gemini_helper import GeminiHelper, extract_sql_query

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ChapterService:
    def __init__(self):
        self.chapter_repo = ChapterRepository()
        self.module_repo = ModuleRepository()
        self.subject_repo = SubjectRepository()
        self.course_repo = CourseRepository()

        self.gemini_helper = GeminiHelper()

    def generate_chapters(self, course_id, subject_id, module_id):
        try:
            logger.info(f"Starting chapter generation for module_id: {module_id}, subject_id: {subject_id}, course_id: {course_id}")
            
            module = self.module_repo.get_module_by_id(module_id)
            if not module:
                logger.error(f"Module not found with id: {module_id}")
                raise Exception(f"Module not found with id: {module_id}")
            
            logger.debug(f"Found module: {module.name}")
            
            subject = self.subject_repo.get_subjects_by_course_id(course_id)
            if not subject:
                logger.error(f"No subjects found for course_id: {course_id}")
                raise Exception("Subject not Found")
                
            subject_name = [item for item in subject if item.id == subject_id][0].name
            logger.debug(f"Found subject: {subject_name}")
            
            course = self.course_repo.get_course_by_id(course_id)
            if not course:
                logger.error(f"Course not found with id: {course_id}")
                raise Exception("Course Not Found")
            
            logger.debug(f"Found course: {course.name}")

            prompt = f"""Generate a comprehensive list of chapters for the module '{module.name}' 
            in the subject '{subject_name}' under course '{course.name}'.
            # ...existing prompt content...
            """
            
            logger.debug("Calling Gemini API for content generation")
            response = self.gemini_helper.generate_content(
                prompt,
                response_schema=ChapterContent
            )
            logger.debug(f"Received response from Gemini: {response}")
            
            chapters_added = 0
            for chapter_name in response['chapters']:
                chapter = Chapter(
                    module_id=module_id,
                    name=chapter_name
                )
                self.chapter_repo.add_chapter(chapter)
                chapters_added += 1
            
            logger.info(f"Successfully added {chapters_added} chapters")
            return {"message": f"Successfully generated {chapters_added} chapters"}
            
        except Exception as e:
            logger.error(f"Error in generate_chapters: {str(e)}", exc_info=True)
            raise Exception(f"Error generating chapters: {str(e)}")

    def get_chapters_by_module_id(self, module_id):
        chapters = self.chapter_repo.get_chapters_by_module_id(module_id)
        return [chapter.to_dict() for chapter in chapters]