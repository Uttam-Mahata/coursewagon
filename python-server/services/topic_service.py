import logging
from repositories.topic_repo import TopicRepository
from models.topic import Topic
from models.schemas import TopicContent
from repositories.chapter_repo import ChapterRepository
from repositories.subject_repo import SubjectRepository
from repositories.course_repo import CourseRepository
from utils.gemini_helper import GeminiHelper
from utils.cache_helper import cache_helper, invalidate_cache
from sqlalchemy.orm import Session
import json
from agents.curriculum_agents import get_topic_agent
from utils.async_helper import run_async_in_sync

logger = logging.getLogger(__name__)

class TopicService:
    def __init__(self, db: Session):
        self.topic_repo = TopicRepository(db)
        self.chapter_repo = ChapterRepository(db)
        self.subject_repo = SubjectRepository(db)
        self.course_repo = CourseRepository(db)

    def generate_topics(self, course_id, subject_id, chapter_id):
        try:
            logger.info(f"Starting topic generation for chapter_id: {chapter_id}")
            
            chapter = self.chapter_repo.get_chapter_by_id(chapter_id)
            if not chapter:
                logger.error(f"Chapter not found for id: {chapter_id}")
                raise Exception("Chapter not found")
            
            logger.debug(f"Found chapter: {chapter.name}")

            subject = self.subject_repo.get_subjects_by_course_id(course_id)
            if not subject:
                logger.error(f"Subject not found for course_id: {course_id}")
                raise Exception("Subject not Found")
            subject_name = [item for item in subject if item.id == subject_id][0].name
            
            # Use ADK Agent
            agent = get_topic_agent()
            prompt = f"""
            Subject Name: {subject_name}
            Chapter Name: {chapter.name}

            Generate topics for this chapter.
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
            
            # If updating, clear existing topics first
            if chapter.has_topics:
                self.topic_repo.delete_topics_by_chapter_id(chapter_id)
            
            topics_added = 0
            for topic_name in response_data['topics']:
                topic = Topic(
                    chapter_id=chapter_id,
                    name=topic_name
                )
                self.topic_repo.add_topic(topic)
                topics_added += 1
            
            # Mark that the chapter has topics
            self.chapter_repo.set_has_topics(chapter_id, True)
            
            # Invalidate caches
            invalidate_cache(f"topics:chapter:{chapter_id}")
            invalidate_cache(f"chapter:{chapter_id}")
            
            logger.info(f"Successfully added {topics_added} topics")
            return {"message": f"Successfully generated {topics_added} topics"}
            
        except Exception as e:
            logger.error(f"Error in generate_topics: {str(e)}", exc_info=True)
            raise Exception(f"Error generating topics: {str(e)}")

    def get_topics_by_chapter_id(self, chapter_id):
        # Cache topics for 5 minutes
        cache_key = f"topics:chapter:{chapter_id}"
        cached = cache_helper.get(cache_key)
        if cached is not None:
            logger.debug(f"Returning cached topics for chapter {chapter_id}")
            return cached
        
        topics = self.topic_repo.get_topics_by_chapter_id(chapter_id)
        result = [topic.to_dict() for topic in topics]
        cache_helper.set(cache_key, result, ttl=300)
        return result
    
    def get_topic_by_id(self, topic_id):
        # Cache individual topic for 5 minutes
        cache_key = f"topic:{topic_id}"
        cached = cache_helper.get(cache_key)
        if cached is not None:
            logger.debug(f"Returning cached topic {topic_id}")
            return cached
        
        topic = self.topic_repo.get_topic_by_id(topic_id)
        if topic:
            result = topic.to_dict()
            cache_helper.set(cache_key, result, ttl=300)
            return result
        return None

    # New CRUD methods
    def create_topic(self, chapter_id, name):
        logger.info(f"Creating new topic for chapter_id: {chapter_id}")
        
        # Verify chapter exists
        chapter = self.chapter_repo.get_chapter_by_id(chapter_id)
        if not chapter:
            logger.error(f"Chapter not found for id: {chapter_id}")
            raise Exception("Chapter not found")
            
        try:
            topic = self.topic_repo.create_topic(chapter_id, name)
            
            # If this is first topic, mark chapter as having topics
            if not chapter.has_topics:
                self.chapter_repo.set_has_topics(chapter_id, True)
            
            # Invalidate caches
            invalidate_cache(f"topics:chapter:{chapter_id}")
                
            return topic.to_dict()
        except Exception as e:
            logger.error(f"Error creating topic: {str(e)}")
            raise Exception(f"Error creating topic: {str(e)}")

    def update_topic(self, topic_id, name):
        logger.info(f"Updating topic id: {topic_id}")
        
        try:
            topic = self.topic_repo.update_topic(topic_id, name)
            if topic:
                # Invalidate caches
                invalidate_cache(f"topic:{topic_id}")
                invalidate_cache(f"topics:chapter:{topic.chapter_id}")
                return topic.to_dict()
            else:
                logger.error(f"Topic not found for id: {topic_id}")
                raise Exception("Topic not found")
        except Exception as e:
            logger.error(f"Error updating topic: {str(e)}")
            raise Exception(f"Error updating topic: {str(e)}")
            
    def delete_topic(self, topic_id):
        logger.info(f"Deleting topic id: {topic_id}")
        
        try:
            # Get topic before deleting to invalidate chapter cache
            topic = self.topic_repo.get_topic_by_id(topic_id)
            success = self.topic_repo.delete_topic(topic_id)
            if success:
                # Invalidate caches
                invalidate_cache(f"topic:{topic_id}")
                if topic:
                    invalidate_cache(f"topics:chapter:{topic.chapter_id}")
                return {"message": "Topic deleted successfully"}
            else:
                logger.error(f"Topic not found for id: {topic_id}")
                raise Exception("Topic not found")
        except Exception as e:
            logger.error(f"Error deleting topic: {str(e)}")
            raise Exception(f"Error deleting topic: {str(e)}")