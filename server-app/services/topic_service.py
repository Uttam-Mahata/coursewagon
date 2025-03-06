import logging
from repositories.topic_repo import TopicRepository
from models.topic import Topic
from models.schemas import TopicContent
from repositories.chapter_repo import ChapterRepository
from repositories.module_repo import ModuleRepository
from repositories.subject_repo import SubjectRepository
from repositories.course_repo import CourseRepository
from utils.gemini_helper import GeminiHelper

logger = logging.getLogger(__name__)

class TopicService:
    def __init__(self):
        self.topic_repo = TopicRepository()
        self.chapter_repo = ChapterRepository()
        self.module_repo = ModuleRepository()
        self.subject_repo = SubjectRepository()
        self.course_repo = CourseRepository()
        self.gemini_helper = GeminiHelper()

    def generate_topics(self, course_id, subject_id, module_id, chapter_id):
        try:
            logger.info(f"Starting topic generation for chapter_id: {chapter_id}")
            
            chapter = self.chapter_repo.get_chapters_by_module_id(module_id)
            if not chapter:
                logger.error(f"Chapter not found for module_id: {module_id}")
                raise Exception("Chapter not found")
            
            chapter_info = [item for item in chapter if item.id == chapter_id][0]
            logger.debug(f"Found chapter: {chapter_info.name}")

            module = self.module_repo.get_module_by_id(module_id)
            if not module:
                logger.error(f"Module not found with id: {module_id}")
                raise Exception("Module not found")
            
            subject = self.subject_repo.get_subjects_by_course_id(course_id)
            if not subject:
                logger.error(f"Subject not found for course_id: {course_id}")
                raise Exception("Subject not Found")
            subject_name = [item for item in subject if item.id == subject_id][0].name

            prompt = f"""Generate a detailed list of topics for the chapter '{chapter_info.name}' 
            in module '{module.name}' under subject '{subject_name}'.
            Requirements:
            1. Each topic should be a specific learning point
            2. Topics should progress logically from basic to advanced
            3. Include 5-10 topics per chapter
            4. Include relevant mind maps where appropriate
            5. Topics should be more specific than chapter content
            6. Use clear, concise academic terminology
            7. Ensure comprehensive coverage of the chapter
            """
            
            logger.debug("Calling Gemini API for content generation")
            response = self.gemini_helper.generate_content(
                prompt,
                response_schema=TopicContent
            )
            logger.debug(f"Received response from Gemini: {response}")
            
            topics_added = 0
            for topic_name in response['topics']:
                topic = Topic(
                    chapter_id=chapter_id,
                    name=topic_name
                )
                self.topic_repo.add_topic(topic)
                topics_added += 1
            
            logger.info(f"Successfully added {topics_added} topics")
            return {"message": f"Successfully generated {topics_added} topics"}
            
        except Exception as e:
            logger.error(f"Error in generate_topics: {str(e)}", exc_info=True)
            raise Exception(f"Error generating topics: {str(e)}")

    def get_topics_by_chapter_id(self, chapter_id):
        return [topic.to_dict() for topic in self.topic_repo.get_topics_by_chapter_id(chapter_id)]
    
    def get_topic_by_id(self, topic_id):
        topic = self.topic_repo.get_topic_by_id(topic_id)
        return topic.to_dict() if topic else None