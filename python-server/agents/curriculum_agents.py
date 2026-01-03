from google.adk.agents import LlmAgent
from agents.schemas import CourseOutput, SubjectListOutput, ChapterListOutput, TopicListOutput

# --- Course Agent ---
COURSE_INSTRUCTION = """
You are an expert curriculum designer.
Your goal is to generate a course name and a comprehensive, educational description based on the user's input.
"""

def get_course_agent(model_name: str = "gemini-2.5-flash-lite"):
    return LlmAgent(
        name="CourseDesigner",
        model=model_name,
        instruction=COURSE_INSTRUCTION,
        output_schema=CourseOutput
    )

# --- Subject Agent ---
SUBJECT_INSTRUCTION = """
You are an expert curriculum designer.
Your task is to generate a list of relevant subjects for a given course.
Consider the course name and description.
Align with typical academic curricula (school/college/university).
Do not include the course name itself as a subject.
Keep subjects practical and relevant.
Generate a maximum of 5 core subjects.
"""

def get_subject_agent(model_name: str = "gemini-2.5-flash-lite"):
    return LlmAgent(
        name="SubjectDesigner",
        model=model_name,
        instruction=SUBJECT_INSTRUCTION,
        output_schema=SubjectListOutput
    )

# --- Chapter Agent ---
CHAPTER_INSTRUCTION = """
You are an expert curriculum designer.
Your task is to generate a comprehensive list of chapters for a specific subject within a course.
Consider the Course Name, Course Description, and Subject Name.
Chapters should:
1. Progress from basic to advanced.
2. Be distinct topics within the subject.
3. Follow a logical learning progression.
4. Use standard academic terminology.
5. Provide 8-15 chapters depending on scope.
"""

def get_chapter_agent(model_name: str = "gemini-2.5-flash-lite"):
    return LlmAgent(
        name="ChapterDesigner",
        model=model_name,
        instruction=CHAPTER_INSTRUCTION,
        output_schema=ChapterListOutput
    )

# --- Topic Agent ---
TOPIC_INSTRUCTION = """
You are an expert curriculum designer.
Your task is to generate a detailed list of topics for a specific chapter.
Consider the Course, Subject, and Chapter context.
Topics should:
1. Be specific learning points (atomic knowledge units).
2. Progress logically.
3. Include 5-10 topics per chapter.
4. Use clear, concise academic terminology.
5. Ensure comprehensive coverage of the chapter.
"""

def get_topic_agent(model_name: str = "gemini-2.5-flash-lite"):
    return LlmAgent(
        name="TopicDesigner",
        model=model_name,
        instruction=TOPIC_INSTRUCTION,
        output_schema=TopicListOutput
    )
