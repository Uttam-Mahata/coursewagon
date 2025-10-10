# services/course_discovery_service.py
from sqlalchemy.orm import Session
from repositories.course_repo import CourseRepository
from repositories.subject_repo import SubjectRepository
from repositories.chapter_repo import ChapterRepository
from repositories.topic_repo import TopicRepository
from fastapi import HTTPException
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
        """Get all published courses for browsing"""
        try:
            courses = self.course_repo.get_published_courses(limit=limit, offset=offset)
            return [course.to_dict() for course in courses]

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
        """Get most popular courses by enrollment count"""
        try:
            courses = self.course_repo.get_popular_courses(limit=limit)
            return [course.to_dict() for course in courses]

        except Exception as e:
            logger.error(f"Error getting popular courses: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_course_preview(self, course_id: int):
        """Get course preview including structure (subjects, chapters, topics) but not detailed content"""
        try:
            course = self.course_repo.get_course_by_id(course_id)
            if not course:
                raise HTTPException(status_code=404, detail="Course not found")

            if not course.is_published:
                raise HTTPException(status_code=403, detail="Course is not published")

            # Get course structure
            subjects = self.subject_repo.get_subjects_by_course_id(course_id)

            structure = []
            for subject in subjects:
                subject_dict = subject.to_dict()
                chapters = self.chapter_repo.get_chapters_by_subject_id(subject.id)

                subject_dict['chapters'] = []
                for chapter in chapters:
                    chapter_dict = chapter.to_dict()
                    topics = self.topic_repo.get_topics_by_chapter_id(chapter.id)
                    chapter_dict['topics'] = [topic.to_dict() for topic in topics]
                    subject_dict['chapters'].append(chapter_dict)

                structure.append(subject_dict)

            return {
                "course": course.to_dict(),
                "structure": structure
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting course preview: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
