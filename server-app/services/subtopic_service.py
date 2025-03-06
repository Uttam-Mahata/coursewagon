import logging
from repositories.subtopic_repo import SubtopicRepository
from models.subtopic import Subtopic
from models.schemas import SubtopicContent
from repositories.topic_repo import TopicRepository
from repositories.chapter_repo import ChapterRepository
from repositories.module_repo import ModuleRepository
from repositories.subject_repo import SubjectRepository
from repositories.course_repo import CourseRepository
from utils.gemini_helper import GeminiHelper

logger = logging.getLogger(__name__)

class SubtopicService:
    def __init__(self):
        self.subtopic_repo = SubtopicRepository()
        self.topic_repo = TopicRepository()
        self.chapter_repo = ChapterRepository()
        self.module_repo = ModuleRepository()
        self.subject_repo = SubjectRepository()
        self.course_repo = CourseRepository()
        self.gemini_helper = GeminiHelper()

    def generate_subtopics(self, course_id, subject_id, module_id, chapter_id, topic_id):
        try:
            logger.info(f"Starting subtopic generation for topic_id: {topic_id}")
            
            topic = self.topic_repo.get_topic_by_id(topic_id)
            if not topic:
                logger.error(f"Topic not found with id: {topic_id}")
                raise Exception("Topic Not Found")
            
            chapter = self.chapter_repo.get_chapters_by_module_id(module_id)
            if not chapter:
                logger.error(f"Chapter not found for module_id: {module_id}")
                raise Exception("Chapter Not Found")
            chapter_name = [item for item in chapter if item.id == chapter_id][0].name
            
            module = self.module_repo.get_module_by_id(module_id)
            if not module:
                logger.error("Module Not Found")
                raise Exception("Module Not Found")
            
            subject = self.subject_repo.get_subjects_by_course_id(course_id)
            if not subject:
                logger.error(f"Subject not found for course_id: {course_id}")
                raise Exception("Subject not Found")
            subject_name = [item for item in subject if item.id == subject_id][0].name

            prompt = f"""Generate a comprehensive list of subtopics for the topic '{topic.name}' 
            in chapter '{chapter_name}' under module '{module.name}' in subject '{subject_name}'.
            
            Requirements:
            1. Each subtopic should be a detailed learning point
            2. Progress from foundational to advanced concepts
            3. Include 6-12 subtopics per topic
            4. Must include:
               - Detailed concept explanations
               - Solved Examples
               - Practice Assignments
               - Video Tutorial references
            5. Use clear academic terminology
            6. Keep names concise but descriptive
            7. Ensure logical flow between subtopics
            """
            
            logger.debug("Calling Gemini API for content generation")
            response = self.gemini_helper.generate_content(
                prompt,
                response_schema=SubtopicContent
            )
            logger.debug(f"Received response from Gemini: {response}")
            
            subtopics_added = 0
            for subtopic_name in response['subtopics']:
                subtopic = Subtopic(
                    topic_id=topic_id,
                    name=subtopic_name
                )
                self.subtopic_repo.add_subtopic(subtopic)
                subtopics_added += 1
            
            logger.info(f"Successfully added {subtopics_added} subtopics")
            return {"message": f"Successfully generated {subtopics_added} subtopics"}
            
        except Exception as e:
            logger.error(f"Error in generate_subtopics: {str(e)}", exc_info=True)
            raise Exception(f"Error generating subtopics: {str(e)}")

    def get_subtopics_by_topic_id(self, topic_id):
        subtopics = self.subtopic_repo.get_subtopics_by_topic_id(topic_id)
        return [subtopic.to_dict() for subtopic in subtopics]