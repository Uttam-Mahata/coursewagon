# services/course_service.py
from repositories.course_repo import CourseRepository
from models.course import Course
from models.schemas import CourseContent
from utils.gemini_helper import GeminiHelper


class CourseService:
    def __init__(self):
        self.course_repo = CourseRepository()
        self.gemini_helper = GeminiHelper()

    def add_course(self, course_name):
        prompt = f"""Generate a course name and description based on '{course_name}'.
        The description should be comprehensive and educational.
        Return only the course details without any additional text."""
        
        try:
            response = self.gemini_helper.generate_content(
                prompt,
                response_schema=CourseContent
            )
            
            course = Course(
                name=response['name'],
                description=response['description']
            )
            self.course_repo.add_course(course)
            return {"message": "Course created successfully"}
            
        except Exception as e:
            raise Exception(f"Error creating course: {e}")

    def get_all_courses(self):
        courses = self.course_repo.get_all_courses()
        return [course.to_dict() for course in courses]
    
    def get_course_by_id(self, course_id):
      course = self.course_repo.get_course_by_id(course_id)
      if course:
        return course.to_dict()
      else:
        return None