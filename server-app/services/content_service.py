# services/content_service.py
from repositories.content_repo import ContentRepository
from models.content import Content
from repositories.subtopic_repo import SubtopicRepository
from repositories.topic_repo import TopicRepository
from repositories.chapter_repo import ChapterRepository
from repositories.module_repo import ModuleRepository
from repositories.subject_repo import SubjectRepository
from repositories.course_repo import CourseRepository
from utils.gemini_helper import GeminiHelper, mermaid_content
class ContentService:
    def __init__(self):
        self.content_repo = ContentRepository()
        self.subtopic_repo = SubtopicRepository()
        self.topic_repo = TopicRepository()
        self.chapter_repo = ChapterRepository()
        self.module_repo = ModuleRepository()
        self.subject_repo = SubjectRepository()
        self.course_repo = CourseRepository()

        self.gemini_helper = GeminiHelper()
        

    def generate_content(self, course_id, subject_id, module_id, chapter_id, topic_id, subtopic_id):
        subtopic = self.subtopic_repo.get_subtopics_by_topic_id(topic_id)
        if not subtopic:
           raise Exception("Subtopic Not Found")
        subtopic_name = [item for item in subtopic if item.id == subtopic_id][0].name
        
        topic = self.topic_repo.get_topic_by_id(topic_id)
        if not topic:
            raise Exception("Topic Not Found")
        topic_name = topic.name
        
        chapter = self.chapter_repo.get_chapters_by_module_id(module_id)
        if not chapter:
             raise Exception("Chapter Not Found")
        chapter_name = [item for item in chapter if item.id == chapter_id][0].name

        module = self.module_repo.get_module_by_id(module_id)
        if not module:
             raise Exception("Module Not Found")
        module_name = module.name
        
        subject = self.subject_repo.get_subjects_by_course_id(course_id)

        if not subject:
            raise Exception("Subject not Found")
        subject_name = [item for item in subject if item.id == subject_id][0].name


        course = self.course_repo.get_course_by_id(course_id)
        if not course:
            raise Exception("Course Not Found")
        course_name = course.name


        prompt = f"""     
            
Generate detailed in-depth content as well as tutorial for the subtopic {subtopic_name} under the topic {topic_name}, under chapter '{chapter_name}'in module '{module_name}' 
under subject '{subject_name}' for course '{course_name}'
 using subtopic id {subtopic_id} and topic id {topic_id}. Dont add subtopic id and topic id in content.
the content should adhere to the following detailed approach:
Delve deeply into the core concepts related to the subtopic, defining key terms, principles, and theories. Include any historical context or real-world relevance to ground the material.
Examples: Include  relevant examples to illustrate the concepts. The examples should be diverse, including:
Numerical examples that explain complex ideas step-by-step using equations, tables, or graphs.
Draw Diagram (if you have 100% confidence on you that your code for diagram will work else do not need to draw) as per content using mermaid js as it is integrated in ngx-markdown if possible or it is relevant to the content 
Take diagram syntax help from Mermaid JS and Ngx markdown. 
These are possible in Markdown Flowchart, Sequence Diagram, Class Diagram, State Diagram, Entity Relationship Diagram, 
User Journey, Gantt, Pie Chart, Quadrant Chart, Requirement Diagram, Gitgraph (Git) Diagram, C4 Diagram, MindMaps, Timeline, ZenUML, Sankey, XY Chart, Block Diagram, Packet, Architecture.
Draw Standard Diagrams as per the content. To draw the standard diagram you can take help from book.
USe this Mermaid format:
<pre class="mermaid">
    graph LR
    A --- B
    B-->C[fa:fa-ban forbidden]
    B-->D(fa:fa-spinner);
</pre>
This is an example
Another Example:
<pre class="mermaid">
sequenceDiagram
    Alice->>John: Hello John, how are you?
    John-->>Alice: Great!
    Alice-)John: See you later!
</pre>
If you are not sure about the syntax of some diagram don't include it. You may create diagram for other relevant part of the content.
Most of the cases take help from book or internet to draw the diagram.Use relevant examples. Do not use any sample attributes.
Carefully draw the diagrams. Take help from mermaid js documentation. and there should not be any syntax error in mermaid code.
 For other diagrams like flowchart, sequence diagram, class diagram, state diagram, entity relationship diagram, 
ser journey, gantt, pie chart, quadrant chart, requirement diagram, gitgraph (git) diagram, c4 diagram, mindmaps, timeline, zenuml, sankey, xy chart, block diagram, packet, architecture use mermaid js.
Always Write Mathematical formula in Latex  $$ $$ , $ $ format.
Assignments: Include at least 10 assignments or problems related to the topic if the topic/subtopic is about assignment . These assignments should cover a range of difficulty levels, from basic to advanced, to test the reader's understanding of the material.
Mathematical Notations & Formulas:
If Subtopic is related to Assignment or any other task, then use the following approach:
Ensure all notations are standard to the field. For example, when explaining algorithms or data structures, use appropriate pseudocode and flowcharts if necessary.
Provide detailed mathematical derivations for complex formulas or theories to ensure clarity.
Tables and Data: make the table colorful and attractive.
When presenting comparisons or listing key differences between concepts, use tables to organize information clearly.
For numerical examples, you can summarize the data in tabular form to enhance readability. make table colorful and attractive.
Ensure each table is labeled clearly, with relevant rows and columns, and is referenced in the body text.
Resources:
For advanced readers, provide references to research papers, books, or PDFs that offer further reading. Use appropriate citation formats and include links to reliable resources, such as Google Scholar articles, official university research papers, or technical documentation.
Provide downloadable links to PDFs whenever you reference any extensive technical documentation.
Generate everything in markdown content.
"""
        response = self.gemini_helper.generate_content(prompt)
        content = Content(subtopic_id=subtopic_id, content=response)
        self.content_repo.add_content(content)
        return {"message": "Content generated successfully"}
    
    def get_content_by_subtopic_id(self, subtopic_id):
      content = self.content_repo.get_content_by_subtopic_id(subtopic_id)
      if content:
        return mermaid_content(content.content)
      else:
        return None