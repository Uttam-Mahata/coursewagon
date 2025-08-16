# services/content_service.py
from repositories.content_repo import ContentRepository
from models.content import Content
from repositories.topic_repo import TopicRepository
from repositories.chapter_repo import ChapterRepository
from repositories.subject_repo import SubjectRepository
from repositories.course_repo import CourseRepository
from repositories.media_repo import MediaRepository
from utils.gemini_helper import GeminiHelper, mermaid_content, extract_markdown
from sqlalchemy.orm import Session
import logging
import re

logger = logging.getLogger(__name__)

class ContentService:
    def __init__(self, db: Session):
        self.content_repo = ContentRepository(db)
        self.topic_repo = TopicRepository(db)
        self.chapter_repo = ChapterRepository(db)
        self.subject_repo = SubjectRepository(db)
        self.course_repo = CourseRepository(db)
        self.media_repo = MediaRepository(db)

    def generate_content(self, course_id, subject_id, chapter_id, topic_id, include_media_placeholders=True):
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

        # Check if there are existing media files for this topic
        existing_media = self.media_repo.get_media_by_content_id(topic_id)
        media_placeholders = ""
        
        if include_media_placeholders and existing_media:
            media_placeholders = self._generate_media_placeholders(existing_media)

        prompt = f"""
            
    Generate detailed, in-depth content as well as a tutorial for the topic "{topic_name}", under the chapter "{chapter_name}",
    under the subject "{subject_name}" for the course "{course_name}"
    using topic id {topic_id}. Do not include the topic id in the content.
    
    {media_placeholders}
    
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
        
        # Process media placeholders if they exist
        if include_media_placeholders and existing_media:
            content.content = self._process_media_placeholders(content.content, existing_media)
        
        self.content_repo.add_content(content)
        return {"message": "Content generated successfully"}

    def _generate_media_placeholders(self, media_files):
        """Generate media placeholder instructions for Gemini"""
        placeholders = "\n\n**MEDIA PLACEMENT INSTRUCTIONS:**\n"
        placeholders += "The following media files are available for this topic. Please integrate them naturally into the content where appropriate:\n\n"
        
        for i, media in enumerate(media_files, 1):
            media_type = "image" if media.file_type == "image" else "video"
            placeholders += f"{i}. **{media_type.title()}**: {media.file_name}"
            if media.caption:
                placeholders += f" - {media.caption}"
            placeholders += f"\n   - Use placeholder: {{MEDIA_{media.id}}} where you want this {media_type} to appear\n"
            placeholders += f"   - File URL: {media.file_url}\n"
            if media.alt_text:
                placeholders += f"   - Alt text: {media.alt_text}\n"
            placeholders += "\n"
        
        placeholders += "**IMPORTANT**: Replace the placeholders {MEDIA_X} with appropriate markdown/HTML code for the media files. For images, use: ![alt_text](url). For videos, use: <video controls><source src='url'></video>\n\n"
        return placeholders

    def _process_media_placeholders(self, content, media_files):
        """Replace media placeholders with actual embed codes"""
        for media in media_files:
            placeholder = f"{{MEDIA_{media.id}}}"
            if placeholder in content:
                embed_code = self._generate_embed_code(media)
                content = content.replace(placeholder, embed_code)
        return content

    def _generate_embed_code(self, media):
        """Generate appropriate embed code for media file"""
        if media.file_type == "image":
            embed_code = f"![{media.alt_text or media.file_name}]({media.file_url})"
            if media.caption:
                embed_code += f"\n*{media.caption}*"
        else:  # video
            embed_code = f'<video controls width="100%">\n  <source src="{media.file_url}" type="{media.mime_type or "video/mp4"}">\n  Your browser does not support the video tag.\n</video>'
            if media.caption:
                embed_code += f"\n*{media.caption}*"
        return embed_code

    def generate_content_with_media_suggestions(self, course_id, subject_id, chapter_id, topic_id):
        """Generate content with suggestions for where media should be placed"""
        topic = self.topic_repo.get_topic_by_id(topic_id)
        if not topic:
            raise Exception("Topic Not Found")
        
        gemini_helper = GeminiHelper()
        
        prompt = f"""
        Analyze the topic "{topic.name}" and suggest where images or videos would be most beneficial for learning.
        
        Provide suggestions in the following format:
        
        ## Media Placement Suggestions
        
        ### 1. [Section Name]
        **Suggested Media Type**: [image/video]
        **Purpose**: [explain why this media would help learning]
        **Recommended Content**: [describe what the media should show]
        **Placement**: [where in the content this should appear]
        
        ### 2. [Section Name]
        **Suggested Media Type**: [image/video]
        **Purpose**: [explain why this media would help learning]
        **Recommended Content**: [describe what the media should show]
        **Placement**: [where in the content this should appear]
        
        Continue for 3-5 suggestions based on the topic content.
        """
        
        response = gemini_helper.generate_content(prompt)
        return {"media_suggestions": response}

    def insert_media_at_position(self, topic_id, media_id, position, section_identifier=None):
        """Insert a specific media file at a particular position in the content"""
        content = self.content_repo.get_content_by_topic_id(topic_id)
        if not content:
            raise Exception("Content not found")
        
        media = self.media_repo.get_media_by_id(media_id)
        if not media:
            raise Exception("Media not found")
        
        # If section identifier is provided, find that section
        if section_identifier:
            content_text = self._insert_media_in_section(content.content, media, section_identifier)
        else:
            # Insert at specific position
            content_text = self._insert_media_at_position(content.content, media, position)
        
        # Update the content
        self.content_repo.update_content(topic_id, content_text)
        return {"message": "Media inserted successfully"}

    def _insert_media_in_section(self, content, media, section_identifier):
        """Insert media within a specific section of the content"""
        # Find the section (e.g., "## Introduction", "### Key Concepts")
        section_pattern = rf"(^#+\s*{re.escape(section_identifier)}.*?)(?=^#+\s|$)"
        match = re.search(section_pattern, content, re.MULTILINE | re.DOTALL)
        
        if match:
            section_start = match.start()
            section_end = match.end()
            section_content = match.group(1)
            
            # Insert media at the end of the section
            embed_code = self._generate_embed_code(media)
            new_section = section_content.rstrip() + "\n\n" + embed_code + "\n"
            
            return content[:section_start] + new_section + content[section_end:]
        else:
            # If section not found, append to the end
            embed_code = self._generate_embed_code(media)
            return content + "\n\n" + embed_code

    def _insert_media_at_position(self, content, media, position):
        """Insert media at a specific character position"""
        embed_code = self._generate_embed_code(media)
        
        if position >= len(content):
            # Append to the end
            return content + "\n\n" + embed_code
        else:
            # Insert at specific position
            return content[:position] + "\n\n" + embed_code + "\n\n" + content[position:]

    def get_content_by_topic_id(self, topic_id):
      content = self.content_repo.get_content_by_topic_id(topic_id)
      if content:
        # Get the content with media files
        content_dict = content.to_dict()
        
        # Apply mermaid processing to the content text
        content_dict['content'] = mermaid_content(content.content)
        
        return content_dict
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