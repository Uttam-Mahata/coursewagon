# services/content_service.py
from repositories.content_repo import ContentRepository
from models.content import Content
from repositories.topic_repo import TopicRepository
from repositories.chapter_repo import ChapterRepository
from repositories.subject_repo import SubjectRepository
from repositories.course_repo import CourseRepository
from utils.gemini_helper import GeminiHelper, mermaid_content, extract_markdown
from utils.unified_storage_helper import storage_helper
from sqlalchemy.orm import Session
import logging
import time

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
        
        gemini_helper = GeminiHelper()

        prompt = f"""
            
    Generate detailed, in-depth content as well as a tutorial for the topic "{topic_name}", under the chapter "{chapter_name}",
    under the subject "{subject_name}" for the course "{course_name}"
    using topic id {topic_id}. Do not include the topic id in the content.
    The content should adhere to the following detailed approach:
    Delve deeply into the core concepts related to the topic, defining key terms, principles, and theories. Include any historical context or real-world relevance to ground the material.
    Examples: Include relevant examples to illustrate the concepts. The examples should be diverse, including:
    Numerical examples that explain complex ideas step-by-step using equations, tables, or graphs.
    Draw diagrams (only if you are 100% confident that your code for the diagram will work; otherwise, you do not need to draw them) as per the content using Mermaid JS, as it is integrated in ngx-markdown, if possible or if it is relevant to the content.
    Take diagram syntax help from Mermaid JS and Ngx markdown. 
    These are possible in Markdown: Flowchart, Sequence Diagram, Class Diagram, State Diagram, Entity Relationship Diagram, 
    User Journey, Gantt, Pie Chart, Quadrant Chart, Requirement Diagram, Gitgraph (Git) Diagram, C4 Diagram, MindMaps, Timeline, ZenUML, Sankey, XY Chart, Block Diagram, Packet, Architecture.
    Draw standard diagrams as per the content. To draw the standard diagram, you can take help from books.
    Use this Mermaid format:
    <pre class="mermaid">
        graph LR
        A --- B
        B-->C[fa:fa-ban forbidden]
        B-->D(fa:fa-spinner);
    </pre>
    This is an example.
    Another example:
    <pre class="mermaid">
    sequenceDiagram
        Alice->>John: Hello John, how are you?
        John-->>Alice: Great!
        Alice-)John: See you later!
    </pre>
    If you are not sure about the syntax of any diagram, do not include it. You may create diagrams for other relevant parts of the content.
    In most cases, take help from books or the internet to draw the diagrams. Use relevant examples. Do not use any sample attributes.
    Carefully draw the diagrams. Take help from Mermaid JS documentation, and ensure there are no syntax errors in the Mermaid code.
    For other diagrams like flowchart, sequence diagram, class diagram, state diagram, entity relationship diagram, 
    user journey, gantt, pie chart, quadrant chart, requirement diagram, gitgraph (git) diagram, c4 diagram, mindmaps, timeline, zenuml, sankey, xy chart, block diagram, packet, architecture, use Mermaid JS.
    Always write mathematical formulas in LaTeX $$ $$ or $ $ format.

    For multiline equation always use this format : $$your equation$$.
    
    Assignments: Include at least 10 assignments or problems related to the topic if the topic is about assignments. These assignments should cover a range of difficulty levels, from basic to advanced, to test the reader's understanding of the material.
    Mathematical Notations & Formulas:
    If the topic is related to assignments or any other task, then use the following approach:
    Ensure all notations are standard to the field. For example, when explaining algorithms or data structures, use appropriate pseudocode and flowcharts if necessary.
    Provide detailed mathematical derivations for complex formulas or theories to ensure clarity.
    Tables and Data: Make the tables colorful and attractive.
    When presenting comparisons or listing key differences between concepts, use tables to organize information clearly.
    For numerical examples, you can summarize the data in tabular form to enhance readability. Make tables colorful and attractive.
    Ensure each table is labeled clearly, with relevant rows and columns, and is referenced in the body text.
    Resources:
    For advanced readers, provide references to research papers, books, or PDFs that offer further reading. Use appropriate citation formats and include links to reliable resources, such as Google Scholar articles, official university research papers, or technical documentation.
    Provide downloadable links to PDFs whenever you reference any extensive technical documentation.
    Generate everything in markdown content.
    """
        response = gemini_helper.generate_content(prompt)
        content = Content(topic_id=topic_id, content=response)
        content.content = extract_markdown(content.content)
        self.content_repo.add_content(content)
        return {"message": "Content generated successfully"}
    
    def get_content_by_topic_id(self, topic_id):
      content = self.content_repo.get_content_by_topic_id(topic_id)
      if content:
        # Return object with both content and video_url
        return {
          "content": mermaid_content(content.content),
          "video_url": content.video_url
        }
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