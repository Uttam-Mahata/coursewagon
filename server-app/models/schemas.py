import typing_extensions as typing

class CourseContent(typing.TypedDict):
    name: str
    description: str

class SubjectContent(typing.TypedDict):
    course_id: int
    subjects: list[str]

class ModuleContent(typing.TypedDict):
    subject_id: int
    modules: list[str]

class ChapterContent(typing.TypedDict):
    module_id: int
    chapters: list[str]

class TopicContent(typing.TypedDict):
    chapter_id: int
    topics: list[str]

class SubtopicContent(typing.TypedDict):
    topic_id: int
    subtopics: list[str]




