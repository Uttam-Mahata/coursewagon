from admin.repository import AdminRepository
from admin.models import AdminStats, UserCourseStats
from repositories.user_repository import UserRepository
from sqlalchemy.orm import Session
from utils.cache_helper import cache_helper, invalidate_cache
import logging

logger = logging.getLogger(__name__)

class AdminService:
    """Service class for admin functionality"""

    def __init__(self, db: Session):
        self.db = db
        self.admin_repo = AdminRepository(db)
        self.user_repo = UserRepository(db)

    def get_dashboard_stats(self):
        """Get consolidated statistics for admin dashboard (cached for 3 minutes)"""
        cache_key = "admin:dashboard:stats"

        # Try to get from cache first
        cached_stats = cache_helper.get(cache_key)
        if cached_stats is not None:
            logger.debug(f"Returning cached dashboard stats")
            return cached_stats

        try:
            # Collect all stats from different sources
            user_stats = self.admin_repo.get_user_stats()
            course_stats = self.admin_repo.get_course_stats()
            content_stats = self.admin_repo.get_content_stats()
            testimonial_stats = self.admin_repo.get_testimonial_stats()
            course_breakdown = self.admin_repo.get_course_breakdown()

            # Combine into one object
            admin_stats = AdminStats(
                total_users=user_stats['total_users'],
                active_users=user_stats['active_users'],
                total_courses=course_stats['total_courses'],
                total_subjects=content_stats['total_subjects'],
                total_chapters=content_stats['total_chapters'],
                total_topics=content_stats['total_topics'],
                total_content=content_stats['total_content'],
                total_testimonials=testimonial_stats['total_testimonials'],
                pending_testimonials=testimonial_stats['pending_testimonials'],
                recent_users=user_stats['recent_users'],
                recent_courses=course_stats['recent_courses'],
                course_breakdown=course_breakdown
            )

            result = admin_stats.to_dict()

            # Cache the result for 3 minutes (180 seconds)
            cache_helper.set(cache_key, result, ttl=180)
            logger.debug(f"Cached dashboard stats for 3 minutes")

            return result
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {str(e)}")
            raise Exception(f"Error retrieving admin dashboard data: {str(e)}")

    def get_user_course_stats(self, user_id: int):
        """Get course statistics for a specific user (course creator dashboard)"""
        try:
            # Get user's course breakdown
            courses_breakdown = self.admin_repo.get_user_course_breakdown(user_id)

            # Calculate totals
            total_courses = len(courses_breakdown)
            total_subjects = sum(c['subjects_count'] for c in courses_breakdown)
            total_chapters = sum(c['chapters_count'] for c in courses_breakdown)
            total_topics = sum(c['topics_count'] for c in courses_breakdown)
            total_content = sum(c['content_count'] for c in courses_breakdown)

            user_stats = UserCourseStats(
                total_courses=total_courses,
                total_subjects=total_subjects,
                total_chapters=total_chapters,
                total_topics=total_topics,
                total_content=total_content,
                courses_with_details=courses_breakdown
            )

            return user_stats.to_dict()
        except Exception as e:
            logger.error(f"Error getting user course stats: {str(e)}")
            raise Exception(f"Error retrieving user course stats: {str(e)}")
    
    def get_all_users(self):
        """Get all users in the system (cached for 3 minutes)"""
        cache_key = "admin:users:all"

        # Try to get from cache first
        cached_users = cache_helper.get(cache_key)
        if cached_users is not None:
            logger.debug(f"Returning cached users list")
            return cached_users

        try:
            users = self.user_repo.get_all_users()
            result = [user.to_dict() for user in users]

            # Cache the result for 3 minutes (180 seconds)
            cache_helper.set(cache_key, result, ttl=180)
            logger.debug(f"Cached users list for 3 minutes")

            return result
        except Exception as e:
            logger.error(f"Error getting all users: {str(e)}")
            raise Exception(f"Error retrieving user list: {str(e)}")
    
    def get_pending_testimonials(self):
        """Get all pending testimonials (cached for 3 minutes)"""
        cache_key = "admin:testimonials:pending"

        # Try to get from cache first
        cached_testimonials = cache_helper.get(cache_key)
        if cached_testimonials is not None:
            logger.debug(f"Returning cached pending testimonials")
            return cached_testimonials

        try:
            result = self.admin_repo.get_pending_testimonials()

            # Cache the result for 3 minutes (180 seconds)
            cache_helper.set(cache_key, result, ttl=180)
            logger.debug(f"Cached pending testimonials for 3 minutes")

            return result
        except Exception as e:
            logger.error(f"Error getting pending testimonials: {str(e)}")
            raise Exception(f"Error retrieving pending testimonials: {str(e)}")
    
    def toggle_user_status(self, admin_id, user_id, is_active):
        """Enable/disable a user account"""
        try:
            # Check that requester is an admin
            admin = self.user_repo.get_user_by_id(admin_id)
            if not admin or not admin.is_admin:
                raise ValueError("You don't have administrator privileges")
                
            result = self.admin_repo.toggle_user_status(user_id, is_active)
            if not result:
                raise ValueError(f"User with ID {user_id} not found")
                
            return result
        except Exception as e:
            logger.error(f"Error toggling user status: {str(e)}")
            raise
    
    def toggle_admin_status(self, admin_id, user_id, is_admin):
        """Grant/revoke admin privileges"""
        try:
            # Check that requester is an admin
            admin = self.user_repo.get_user_by_id(admin_id)
            if not admin or not admin.is_admin:
                raise ValueError("You don't have administrator privileges")
                
            # Prevent admin from removing their own admin privileges
            if int(admin_id) == int(user_id) and not is_admin:
                raise ValueError("You cannot remove your own admin privileges")
                
            result = self.admin_repo.toggle_admin_status(user_id, is_admin)
            if not result:
                raise ValueError(f"User with ID {user_id} not found")
                
            return result
        except Exception as e:
            logger.error(f"Error toggling admin status: {str(e)}")
            raise
