from pydantic import BaseModel, Field
from typing import List

class CourseOutput(BaseModel):
    name: str = Field(description="The name of the course")
    description: str = Field(description="A comprehensive and educational description of the course (max 100 words)")

class SubjectListOutput(BaseModel):
    subjects: List[str] = Field(description="List of relevant subjects for the course")

class ChapterListOutput(BaseModel):
    chapters: List[str] = Field(description="List of chapters for the subject")

class TopicListOutput(BaseModel):
    topics: List[str] = Field(description="List of topics for the chapter")
