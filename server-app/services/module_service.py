# services/module_service.py
from repositories.module_repo import ModuleRepository
from models.module import Module
from models.schemas import ModuleContent
from repositories.subject_repo import SubjectRepository
from repositories.course_repo import CourseRepository

from utils.gemini_helper import GeminiHelper


class ModuleService:
    def __init__(self):
        self.module_repo = ModuleRepository()
        self.subject_repo = SubjectRepository()
        self.course_repo = CourseRepository()

        self.gemini_helper = GeminiHelper()

    def generate_modules(self, course_id, subject_id):
        subject = self.subject_repo.get_subjects_by_course_id(course_id)
        if not subject:
            raise Exception("Subject not found")
        subject_name = [item for item in subject if item.id == subject_id][0].name
        
        course = self.course_repo.get_course_by_id(course_id)
        if not course:
            raise Exception("Course Not Found")
        
        prompt = f"""Generate a comprehensive list of modules for the subject '{subject_name}' in the course '{course.name}'.
        Consider the following:
        1. Include modules from basic to advanced level
        2. Each module should be a distinct topic within the subject
        3. Modules should follow a logical learning progression
        4. Include 8-15 modules depending on the subject scope
        5. Modules should be different from chapters (modules are broader units)
        6. Use standard academic curriculum terminology
        """
        
        try:
            response = self.gemini_helper.generate_content(
                prompt,
                response_schema=ModuleContent
            )
            
            for module_name in response['modules']:
                module = Module(
                    subject_id=subject_id,
                    name=module_name
                )
                self.module_repo.add_module(module)

            return {"message": "Modules generated successfully"}
            
        except Exception as e:
            raise Exception(f"Error generating modules: {e}")

    def get_modules_by_subject_id(self, subject_id):
        modules = self.module_repo.get_modules_by_subject_id(subject_id)
        return [module.to_dict() for module in modules]
    
    def get_module_by_id(self, module_id):
        module = self.module_repo.get_module_by_id(module_id)
        return module.to_dict() if module else None