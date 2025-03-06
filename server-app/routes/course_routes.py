# routes/course_routes.py
from flask import Blueprint, request, jsonify
from services.course_service import CourseService
from services.subject_service import SubjectService
from services.module_service import ModuleService
from services.chapter_service import ChapterService
from services.topic_service import TopicService
from services.subtopic_service import SubtopicService
from services.content_service import ContentService

course_bp = Blueprint('course_bp', __name__, url_prefix='/courses')
course_service = CourseService()
subject_service = SubjectService()
module_service = ModuleService()
chapter_service = ChapterService()
topic_service = TopicService()
subtopic_service = SubtopicService()
content_service = ContentService()

@course_bp.route('/add_course', methods=['POST'])
def add_course():
    data = request.json
    course_name = data.get('name')

    if not course_name:
        return jsonify({"error": "Course name is required"}), 400

    try:
        result = course_service.add_course(course_name)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@course_bp.route('/<int:id>/generate_subjects', methods=['POST'])
def generate_subjects(id):
    try:
        result = subject_service.generate_subjects(id)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@course_bp.route('/<int:course_id>/subjects/<int:subject_id>/generate_modules', methods=['POST'])
def generate_modules(course_id, subject_id):
    try:
        result = module_service.generate_modules(course_id, subject_id)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@course_bp.route('/<int:course_id>/subjects/<int:subject_id>/modules/<int:module_id>/generate_chapters', methods=['POST'])
def generate_chapters(course_id, subject_id, module_id):
    try:
        result = chapter_service.generate_chapters(course_id, subject_id, module_id)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@course_bp.route(
    '/<int:course_id>/subjects/<int:subject_id>/modules/<int:module_id>/chapters/<int:chapter_id>/generate_topics',
    methods=['POST'])
def generate_topics(course_id, subject_id, module_id, chapter_id):
    try:
        result = topic_service.generate_topics(course_id, subject_id, module_id, chapter_id)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@course_bp.route(
    '/<int:course_id>/subjects/<int:subject_id>/modules/<int:module_id>/chapters/<int:chapter_id>/topics/<int:topic_id>/generate_subtopics',
    methods=['POST'])
def generate_subtopics(course_id, subject_id, module_id, chapter_id, topic_id):
    try:
       result = subtopic_service.generate_subtopics(course_id, subject_id, module_id, chapter_id, topic_id)
       return jsonify(result), 201
    except Exception as e:
       return jsonify({"error": str(e)}), 500

@course_bp.route(
    '/<int:course_id>/subjects/<int:subject_id>/modules/<int:module_id>/chapters/<int:chapter_id>/topics/<int:topic_id>/subtopics/<int:subtopic_id>/generate_content',
    methods=['POST'])
def generate_content(course_id, subject_id, module_id, chapter_id, topic_id, subtopic_id):
    try:
        result = content_service.generate_content(course_id, subject_id, module_id, chapter_id, topic_id, subtopic_id)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@course_bp.route('', methods=['GET'])
def get_courses():
    try:
        courses = course_service.get_all_courses()
        return jsonify(courses)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@course_bp.route('/<int:id>', methods=['GET'])
def get_course(id):
    try:
        course = course_service.get_course_by_id(id)
        if course:
           return jsonify(course)
        else:
          return jsonify({"error":"Course Not Found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@course_bp.route('/<int:id>/subjects', methods=['GET'])
def get_subjects(id):
    try:
        subjects = subject_service.get_subjects_by_course_id(id)
        return jsonify(subjects)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@course_bp.route('/<int:course_id>/subjects/<int:subject_id>/modules', methods=['GET'])
def get_modules(course_id, subject_id):
    try:
        modules = module_service.get_modules_by_subject_id(subject_id)
        return jsonify(modules)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@course_bp.route('/<int:course_id>/subjects/<int:subject_id>/modules/<int:module_id>', methods=['GET'])
def get_module(course_id, subject_id, module_id):
    try:
       module = module_service.get_module_by_id(module_id)
       if module:
         return jsonify(module)
       else:
          return jsonify({"error":"Module Not Found"}),404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@course_bp.route('/<int:course_id>/subjects/<int:subject_id>/modules/<int:module_id>/chapters', methods=['GET'])
def get_chapters(course_id, subject_id, module_id):
    try:
        chapters = chapter_service.get_chapters_by_module_id(module_id)
        return jsonify(chapters)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@course_bp.route(
    '/<int:course_id>/subjects/<int:subject_id>/modules/<int:module_id>/chapters/<int:chapter_id>/topics',
    methods=['GET'])
def get_topics(course_id, subject_id, module_id, chapter_id):
    try:
        topics = topic_service.get_topics_by_chapter_id(chapter_id)
        return jsonify(topics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@course_bp.route('/<int:course_id>/subjects/<int:subject_id>/modules/<int:module_id>/chapters/<int:chapter_id>/topics/<int:topic_id>', methods=['GET'])
def get_topic(course_id, subject_id, module_id, chapter_id, topic_id):
    try:
       topic = topic_service.get_topic_by_id(topic_id)
       if topic:
          return jsonify(topic)
       else:
         return jsonify({"error":"Topic Not Found"}),404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@course_bp.route(
    '/<int:course_id>/subjects/<int:subject_id>/modules/<int:module_id>/chapters/<int:chapter_id>/topics/<int:topic_id>/subtopics',
    methods=['GET'])
def get_subtopics(course_id, subject_id, module_id, chapter_id, topic_id):
    try:
        subtopics = subtopic_service.get_subtopics_by_topic_id(topic_id)
        return jsonify(subtopics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@course_bp.route(
    '/<int:course_id>/subjects/<int:subject_id>/modules/<int:module_id>/chapters/<int:chapter_id>/topics/<int:topic_id>/subtopics/<int:subtopic_id>/content',
    methods=['GET'])
def get_content(course_id, subject_id, module_id, chapter_id, topic_id, subtopic_id):
    try:
       content = content_service.get_content_by_subtopic_id(subtopic_id)
       if content:
         return jsonify(content)
       else:
         return jsonify({"error":"Content Not Found"}),404
    except Exception as e:
        return jsonify({"error": str(e)}), 500