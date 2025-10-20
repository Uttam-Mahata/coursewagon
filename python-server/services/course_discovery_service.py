# services/course_discovery_service.py
from sqlalchemy.orm import Session
from repositories.course_repo import CourseRepository
from repositories.subject_repo import SubjectRepository
from repositories.chapter_repo import ChapterRepository
from repositories.topic_repo import TopicRepository
from fastapi import HTTPException
from utils.cache_helper import cache_helper
import logging

logger = logging.getLogger(__name__)

class CourseDiscoveryService:
    def __init__(self, db: Session):
        self.db = db
        self.course_repo = CourseRepository(db)
        self.subject_repo = SubjectRepository(db)
        self.chapter_repo = ChapterRepository(db)
        self.topic_repo = TopicRepository(db)

    def get_published_courses(self, limit: int = 20, offset: int = 0):
        """Get all published courses for browsing (cached for 3 minutes)"""
        cache_key = f"published_courses:limit:{limit}:offset:{offset}"
        cached = cache_helper.get(cache_key)
        if cached is not None:
            logger.debug(f"Returning cached published courses (limit={limit}, offset={offset})")
            return cached
        
        try:
            courses = self.course_repo.get_published_courses(limit=limit, offset=offset)
            result = [course.to_dict() for course in courses]
            
            # Cache for 3 minutes
            cache_helper.set(cache_key, result, ttl=180)
            return result

        except Exception as e:
            logger.error(f"Error getting published courses: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def search_courses(self, search_term: str, limit: int = 20):
        """Search published courses"""
        try:
            courses = self.course_repo.search_courses(search_term, limit=limit)
            return [course.to_dict() for course in courses]

        except Exception as e:
            logger.error(f"Error searching courses: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_courses_by_category(self, category: str, limit: int = 20):
        """Get published courses by category"""
        try:
            courses = self.course_repo.get_courses_by_category(category, limit=limit)
            return [course.to_dict() for course in courses]

        except Exception as e:
            logger.error(f"Error getting courses by category: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_popular_courses(self, limit: int = 10):
        """Get most popular courses by enrollment count (cached for 5 minutes)"""
        cache_key = f"popular_courses:limit:{limit}"
        cached = cache_helper.get(cache_key)
        if cached is not None:
            logger.debug(f"Returning cached popular courses (limit={limit})")
            return cached
        
        try:
            courses = self.course_repo.get_popular_courses(limit=limit)
            result = [course.to_dict() for course in courses]
            
            # Cache for 5 minutes (popular courses don't change frequently)
            cache_helper.set(cache_key, result, ttl=300)
            return result

        except Exception as e:
            logger.error(f"Error getting popular courses: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_course_preview(self, course_id: int):
        """Get course preview including structure (subjects with flattened topics) but not detailed content (cached for 5 minutes)"""
        cache_key = f"course_preview:{course_id}"
        cached = cache_helper.get(cache_key)
        if cached is not None:
            logger.debug(f"Returning cached course preview for course {course_id}")
            return cached
        
        try:
            course = self.course_repo.get_course_by_id(course_id)
            if not course:
                raise HTTPException(status_code=404, detail="Course not found")

            if not course.is_published:
                raise HTTPException(status_code=403, detail="Course is not published")

            # Use optimized query to get all structure data at once
            from sqlalchemy.orm import joinedload
            from models.subject import Subject
            from models.chapter import Chapter
            from models.topic import Topic
            
            # Load subjects with eager loading of chapters and topics
            subjects = self.db.query(Subject).filter(
                Subject.course_id == course_id
            ).options(
                joinedload(Subject.chapters).joinedload(Chapter.topics)
            ).all()

            structure = []
            for subject in subjects:
                subject_dict = subject.to_dict()
                
                # Flatten all topics from all chapters into a single list
                all_topics = []
                for chapter in subject.chapters:
                    all_topics.extend([topic.to_dict() for topic in chapter.topics])

                subject_dict['topics'] = all_topics
                structure.append(subject_dict)

            result = {
                "course": course.to_dict(),
                "structure": structure
            }
            
            # Cache for 5 minutes
            cache_helper.set(cache_key, result, ttl=300)
            return result

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting course preview: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_course_structure_for_learning(self, course_id: int):
        """Get full course structure optimized for learning view (cached for 5 minutes)"""
        cache_key = f"course_structure:learning:{course_id}"
        cached = cache_helper.get(cache_key)
        if cached is not None:
            logger.debug(f"Returning cached course structure for learning for course {course_id}")
            return cached
        
        try:
            course = self.course_repo.get_course_by_id(course_id)
            if not course:
                raise HTTPException(status_code=404, detail="Course not found")

            # Use optimized query to get all structure data at once
            from sqlalchemy.orm import joinedload
            from models.subject import Subject
            from models.chapter import Chapter
            from models.topic import Topic
            
            # Load subjects with eager loading of chapters and topics
            subjects = self.db.query(Subject).filter(
                Subject.course_id == course_id
            ).options(
                joinedload(Subject.chapters).joinedload(Chapter.topics)
            ).all()

            # Build complete structure with full hierarchy
            structure = []
            for subject in subjects:
                subject_dict = subject.to_dict()
                
                # Build chapters with their topics
                chapters_list = []
                for chapter in subject.chapters:
                    chapter_dict = chapter.to_dict()
                    chapter_dict['topics'] = [topic.to_dict() for topic in chapter.topics]
                    chapters_list.append(chapter_dict)
                
                subject_dict['chapters'] = chapters_list
                structure.append(subject_dict)

            result = {
                "course": course.to_dict(),
                "subjects": structure
            }
            
            # Cache for 5 minutes
            cache_helper.set(cache_key, result, ttl=300)
            return result

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting course structure for learning: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
