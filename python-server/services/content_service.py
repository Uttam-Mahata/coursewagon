# services/content_service.py
from repositories.content_repo import ContentRepository
from models.content import Content
from repositories.topic_repo import TopicRepository
from repositories.chapter_repo import ChapterRepository
from repositories.subject_repo import SubjectRepository
from repositories.course_repo import CourseRepository
from utils.gemini_helper import GeminiHelper, mermaid_content, chart_content, extract_markdown
from utils.unified_storage_helper import storage_helper
from utils.cache_helper import cache_helper, invalidate_cache
from sqlalchemy.orm import Session
import logging
import time
from services.adk_content_service import ADKContentService

logger = logging.getLogger(__name__)

class ContentService:
    def __init__(self, db: Session):
        self.content_repo = ContentRepository(db)
        self.topic_repo = TopicRepository(db)
        self.chapter_repo = ChapterRepository(db)
        self.subject_repo = SubjectRepository(db)
        self.course_repo = CourseRepository(db)

    def generate_content(self, course_id, subject_id, chapter_id, topic_id):
        topic = self.topic_repo.get_topic_by_id(topic_id)
        if not topic:
            raise Exception("Topic Not Found")
        topic_name = topic.name
        
        chapter = self.chapter_repo.get_chapter_by_id(chapter_id)
        if not chapter:
            raise Exception("Chapter Not Found")
        chapter_name = chapter.name

        subject = self.subject_repo.get_subjects_by_course_id(course_id)
        if not subject:
            raise Exception("Subject not Found")
        subject_name = [item for item in subject if item.id == subject_id][0].name

        course = self.course_repo.get_course_by_id(course_id)
        if not course:
            raise Exception("Course Not Found")
        course_name = course.name
        
        # Use ADK Service
        adk_service = ADKContentService()

        context_data = {
            "course_name": course_name,
            "subject_name": subject_name,
            "chapter_name": chapter_name,
            "topic_name": topic_name,
            "topic_id": topic_id
        }

        generated_text = adk_service.generate_content(context_data)

        content = Content(topic_id=topic_id, content=generated_text)
        content.content = extract_markdown(content.content)
        self.content_repo.add_content(content)
        
        # Invalidate cache
        invalidate_cache(f"content:topic:{topic_id}")
        
        return {"message": "Content generated successfully"}
    
    def get_content_by_topic_id(self, topic_id):
        # Cache content for 10 minutes (content is expensive to generate)
        cache_key = f"content:topic:{topic_id}"
        cached = cache_helper.get(cache_key)
        if cached is not None:
            logger.debug(f"Returning cached content for topic {topic_id}")
            return cached
        
        content = self.content_repo.get_content_by_topic_id(topic_id)
        if content:
            # Process both mermaid and chart content
            processed_content = mermaid_content(content.content)
            processed_content = chart_content(processed_content)
            
            # Return object with both content and video_url
            result = {
                "content": processed_content,
                "video_url": content.video_url
            }
            cache_helper.set(cache_key, result, ttl=600)
            return result
        else:
            return None

    # New CRUD methods
    def create_content_manual(self, topic_id, content_text):
        logger.info(f"Creating manual content for topic_id: {topic_id}")
        
        topic = self.topic_repo.get_topic_by_id(topic_id)
        if not topic:
            logger.error(f"Topic not found for id: {topic_id}")
            raise Exception("Topic not found")
        
        try:
            content = self.content_repo.create_content(topic_id, content_text)
            
            # Mark the topic as having content
            self.topic_repo.set_has_content(topic_id, True)
            
            # Invalidate cache
            invalidate_cache(f"content:topic:{topic_id}")
            
            return content.content
        except Exception as e:
            logger.error(f"Error creating content: {str(e)}")
            raise Exception(f"Error creating content: {str(e)}")

    def update_content(self, topic_id, content_text):
        logger.info(f"Updating content for topic_id: {topic_id}")
        
        topic = self.topic_repo.get_topic_by_id(topic_id)
        if not topic:
            logger.error(f"Topic not found for id: {topic_id}")
            raise Exception("Topic not found")
        
        try:
            content = self.content_repo.update_content(topic_id, content_text)
            if content:
                # Invalidate cache
                invalidate_cache(f"content:topic:{topic_id}")
                return content.content
            else:
                # If no content exists yet, create it
                return self.create_content_manual(topic_id, content_text)
        except Exception as e:
            logger.error(f"Error updating content: {str(e)}")
            raise Exception(f"Error updating content: {str(e)}")
            
    def delete_content(self, topic_id):
        logger.info(f"Deleting content for topic_id: {topic_id}")

        try:
            self.content_repo.delete_content_by_topic_id(topic_id)

            # Update topic to reflect it no longer has content
            self.topic_repo.set_has_content(topic_id, False)
            
            # Invalidate cache
            invalidate_cache(f"content:topic:{topic_id}")

            return {"message": "Content deleted successfully"}
        except Exception as e:
            logger.error(f"Error deleting content: {str(e)}")
            raise Exception(f"Error deleting content: {str(e)}")

    # Video upload methods
    def upload_video(self, topic_id, video_file_bytes, filename):
        """
        Upload a video file to GCS and save the URL in the database

        Args:
            topic_id: ID of the topic
            video_file_bytes: Video file content as bytes
            filename: Original filename

        Returns:
            Public URL of the uploaded video
        """
        logger.info(f"Uploading video for topic_id: {topic_id}, filename: {filename}")

        try:
            # Validate file size (100MB max)
            max_size = 100 * 1024 * 1024  # 100MB in bytes
            if len(video_file_bytes) > max_size:
                raise Exception(f"Video file size exceeds maximum allowed size of 100MB")

            # Validate file extension
            allowed_extensions = ['.mp4', '.webm', '.ogg', '.mov', '.avi']
            file_extension = filename[filename.rfind('.'):].lower() if '.' in filename else ''
            if file_extension not in allowed_extensions:
                raise Exception(f"Invalid video format. Allowed formats: {', '.join(allowed_extensions)}")

            # Generate storage path
            timestamp = int(time.time())
            storage_path = f"videos/content/topic_{topic_id}_{timestamp}{file_extension}"

            # Determine content type
            content_type_map = {
                '.mp4': 'video/mp4',
                '.webm': 'video/webm',
                '.ogg': 'video/ogg',
                '.mov': 'video/quicktime',
                '.avi': 'video/x-msvideo'
            }
            content_type = content_type_map.get(file_extension, 'video/mp4')

            # Upload to GCS using unified storage helper
            video_url = storage_helper.upload_file(
                file_bytes=video_file_bytes,
                path=storage_path,
                content_type=content_type
            )

            # Save video URL to database
            content = self.content_repo.update_video_url(topic_id, video_url)
            if not content:
                # If content doesn't exist, create it with empty text content
                content = self.content_repo.create_content(topic_id, "")
                content = self.content_repo.update_video_url(topic_id, video_url)

            # Invalidate content cache
            invalidate_cache(f"content:topic:{topic_id}")
            
            logger.info(f"Video uploaded successfully: {video_url}")
            return {"video_url": video_url, "message": "Video uploaded successfully"}

        except Exception as e:
            logger.error(f"Error uploading video: {str(e)}")
            raise Exception(f"Error uploading video: {str(e)}")

    def delete_video(self, topic_id):
        """
        Delete the video associated with a topic

        Args:
            topic_id: ID of the topic

        Returns:
            Success message
        """
        logger.info(f"Deleting video for topic_id: {topic_id}")

        try:
            # Get current content to retrieve video URL
            content = self.content_repo.get_content_by_topic_id(topic_id)
            if not content or not content.video_url:
                raise Exception("No video found for this topic")

            # Delete from storage
            video_url = content.video_url
            try:
                storage_helper.delete_image(video_url)  # This works for any file type, not just images
                logger.info(f"Video deleted from storage: {video_url}")
            except Exception as storage_error:
                logger.warning(f"Could not delete video from storage: {str(storage_error)}")
                # Continue anyway to remove URL from database

            # Remove video URL from database
            self.content_repo.remove_video_url(topic_id)

            return {"message": "Video deleted successfully"}

        except Exception as e:
            logger.error(f"Error deleting video: {str(e)}")
            raise Exception(f"Error deleting video: {str(e)}")