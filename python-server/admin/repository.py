from models.user import User
from models.course import Course
from models.subject import Subject
from models.chapter import Chapter
from models.topic import Topic
from models.content import Content
from models.testimonial import Testimonial
from admin.models import AdminStats
from sqlalchemy import func
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

class AdminRepository:
    """Repository for admin-related database operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_user_stats(self):
        """Get user statistics"""
        try:
            total_users = self.db.query(User).count()
            active_users = self.db.query(User).filter_by(is_active=True).count()
            recent_users = self.db.query(User).order_by(User.created_at.desc()).limit(10).all()
            recent_users_list = [user.to_dict() for user in recent_users]

            return {
                'total_users': total_users,
                'active_users': active_users,
                'recent_users': recent_users_list
            }
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            raise

    def get_course_stats(self):
        """Get course statistics"""
        try:
            total_courses = self.db.query(Course).count()
            recent_courses = self.db.query(Course).order_by(Course.created_at.desc()).limit(10).all()
            recent_courses_list = [course.to_dict() for course in recent_courses]

            return {
                'total_courses': total_courses,
                'recent_courses': recent_courses_list
            }
        except Exception as e:
            logger.error(f"Error getting course stats: {str(e)}")
            raise

    def get_content_stats(self):
        """Get detailed content statistics across all hierarchy levels"""
        try:
            total_subjects = self.db.query(Subject).count()
            total_chapters = self.db.query(Chapter).count()
            total_topics = self.db.query(Topic).count()
            total_content = self.db.query(Content).count()

            return {
                'total_subjects': total_subjects,
                'total_chapters': total_chapters,
                'total_topics': total_topics,
                'total_content': total_content
            }
        except Exception as e:
            logger.error(f"Error getting content stats: {str(e)}")
            raise

    def get_course_breakdown(self):
        """Get detailed breakdown of each course with content counts"""
        try:
            courses = self.db.query(Course).order_by(Course.created_at.desc()).all()
            breakdown = []

            for course in courses:
                # Count subjects for this course
                subjects_count = self.db.query(Subject).filter_by(course_id=course.id).count()

                # Count chapters across all subjects in this course
                chapters_count = self.db.query(func.count(Chapter.id))\
                    .join(Subject, Chapter.subject_id == Subject.id)\
                    .filter(Subject.course_id == course.id)\
                    .scalar() or 0

                # Count topics across all chapters in this course
                topics_count = self.db.query(func.count(Topic.id))\
                    .join(Chapter, Topic.chapter_id == Chapter.id)\
                    .join(Subject, Chapter.subject_id == Subject.id)\
                    .filter(Subject.course_id == course.id)\
                    .scalar() or 0

                # Count content across all topics in this course
                content_count = self.db.query(func.count(Content.id))\
                    .join(Topic, Content.topic_id == Topic.id)\
                    .join(Chapter, Topic.chapter_id == Chapter.id)\
                    .join(Subject, Chapter.subject_id == Subject.id)\
                    .filter(Subject.course_id == course.id)\
                    .scalar() or 0

                breakdown.append({
                    'course_id': course.id,
                    'course_name': course.name,
                    'course_description': course.description,
                    'created_at': course.created_at.isoformat() if course.created_at else None,
                    'subjects_count': subjects_count,
                    'chapters_count': chapters_count,
                    'topics_count': topics_count,
                    'content_count': content_count,
                    'image_url': course.image_url
                })

            return breakdown
        except Exception as e:
            logger.error(f"Error getting course breakdown: {str(e)}")
            raise

    def get_user_course_breakdown(self, user_id: int):
        """Get detailed breakdown of courses for a specific user"""
        try:
            courses = self.db.query(Course).filter_by(user_id=user_id).order_by(Course.created_at.desc()).all()
            breakdown = []

            for course in courses:
                # Count subjects for this course
                subjects_count = self.db.query(Subject).filter_by(course_id=course.id).count()

                # Count chapters across all subjects in this course
                chapters_count = self.db.query(func.count(Chapter.id))\
                    .join(Subject, Chapter.subject_id == Subject.id)\
                    .filter(Subject.course_id == course.id)\
                    .scalar() or 0

                # Count topics across all chapters in this course
                topics_count = self.db.query(func.count(Topic.id))\
                    .join(Chapter, Topic.chapter_id == Chapter.id)\
                    .join(Subject, Chapter.subject_id == Subject.id)\
                    .filter(Subject.course_id == course.id)\
                    .scalar() or 0

                # Count content across all topics in this course
                content_count = self.db.query(func.count(Content.id))\
                    .join(Topic, Content.topic_id == Topic.id)\
                    .join(Chapter, Topic.chapter_id == Chapter.id)\
                    .join(Subject, Chapter.subject_id == Subject.id)\
                    .filter(Subject.course_id == course.id)\
                    .scalar() or 0

                breakdown.append({
                    'course_id': course.id,
                    'course_name': course.name,
                    'course_description': course.description,
                    'created_at': course.created_at.isoformat() if course.created_at else None,
                    'subjects_count': subjects_count,
                    'chapters_count': chapters_count,
                    'topics_count': topics_count,
                    'content_count': content_count,
                    'image_url': course.image_url
                })

            return breakdown
        except Exception as e:
            logger.error(f"Error getting user course breakdown: {str(e)}")
            raise

    def get_testimonial_stats(self):
        """Get testimonial statistics"""
        try:
            total_testimonials = self.db.query(Testimonial).count()
            pending_testimonials = self.db.query(Testimonial).filter_by(is_approved=False).count()

            return {
                'total_testimonials': total_testimonials,
                'pending_testimonials': pending_testimonials
            }
        except Exception as e:
            logger.error(f"Error getting testimonial stats: {str(e)}")
            raise

    def get_pending_testimonials(self):
        """Get all pending testimonials"""
        try:
            testimonials = self.db.query(Testimonial).filter_by(is_approved=False).all()
            return [testimonial.to_dict() for testimonial in testimonials]
        except Exception as e:
            logger.error(f"Error getting pending testimonials: {str(e)}")
            raise

    def toggle_user_status(self, user_id, is_active):
        """Enable or disable a user account"""
        try:
            user = self.db.query(User).filter_by(id=user_id).first()
            if not user:
                return None

            user.is_active = is_active
            self.db.commit()
            return user.to_dict()
        except Exception as e:
            logger.error(f"Error toggling user status: {str(e)}")
            self.db.rollback()
            raise

    def toggle_admin_status(self, user_id, is_admin):
        """Grant or revoke admin privileges"""
        try:
            user = self.db.query(User).filter_by(id=user_id).first()
            if not user:
                return None

            user.is_admin = is_admin
            self.db.commit()
            return user.to_dict()
        except Exception as e:
            logger.error(f"Error toggling admin status: {str(e)}")
            self.db.rollback()
            raise
