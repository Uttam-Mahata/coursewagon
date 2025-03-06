# services/subject_service.py
from repositories.subject_repo import SubjectRepository
from models.subject import Subject
from models.schemas import SubjectContent
from repositories.course_repo import CourseRepository
from utils.gemini_helper import GeminiHelper, extract_sql_query


class SubjectService:
    def __init__(self):
        self.subject_repo = SubjectRepository()
        self.course_repo = CourseRepository()
        self.gemini_helper = GeminiHelper()

    def generate_subjects(self, course_id):
        course = self.course_repo.get_course_by_id(course_id)

        if not course:
            raise Exception("Course not found")

        prompt = f"""Based on the course '{course.name}' with description '{course.description}', 
        generate a list of relevant subjects that should be included in this course.
        Consider the following:
        1. If it's a school/college/university course, align with their typical curriculum
        2. Don't include the course name as a subject
        3. Keep subjects relevant and practical
        4. Generate at least 4-6 core subjects for the course
        """
        
        try:
            response = self.gemini_helper.generate_content(
                prompt,
                response_schema=SubjectContent
            )
            
            for subject_name in response['subjects']:
                subject = Subject(
                    course_id=course_id,
                    name=subject_name
                )
                self.subject_repo.add_subject(subject)

            return {"message": "Subjects generated successfully"}
            
        except Exception as e:
            raise Exception(f"Error generating subjects: {e}")

    def get_subjects_by_course_id(self, course_id):
        subjects = self.subject_repo.get_subjects_by_course_id(course_id)
        return [subject.to_dict() for subject in subjects]