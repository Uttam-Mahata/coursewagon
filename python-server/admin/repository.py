from extensions import db
from models.user import User
from models.course import Course
from models.testimonial import Testimonial
from admin.models import AdminStats
import logging

logger = logging.getLogger(__name__)

class AdminRepository:
    """Repository for admin-related database operations"""

    def get_user_stats(self):
        """Get user statistics"""
        try:
            total_users = User.query.count()
            active_users = User.query.filter_by(is_active=True).count()
            recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
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
            total_courses = Course.query.count()
            recent_courses = Course.query.order_by(Course.created_at.desc()).limit(10).all()
            recent_courses_list = [course.to_dict() for course in recent_courses]
            
            return {
                'total_courses': total_courses,
                'recent_courses': recent_courses_list
            }
        except Exception as e:
            logger.error(f"Error getting course stats: {str(e)}")
            raise
    
    def get_testimonial_stats(self):
        """Get testimonial statistics"""
        try:
            total_testimonials = Testimonial.query.count()
            pending_testimonials = Testimonial.query.filter_by(is_approved=False).count()
            
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
            testimonials = Testimonial.query.filter_by(is_approved=False).all()
            return [testimonial.to_dict() for testimonial in testimonials]
        except Exception as e:
            logger.error(f"Error getting pending testimonials: {str(e)}")
            raise
    
    def toggle_user_status(self, user_id, is_active):
        """Enable or disable a user account"""
        try:
            user = User.query.get(user_id)
            if not user:
                return None
                
            user.is_active = is_active
            db.session.commit()
            return user.to_dict()
        except Exception as e:
            logger.error(f"Error toggling user status: {str(e)}")
            db.session.rollback()
            raise
    
    def toggle_admin_status(self, user_id, is_admin):
        """Grant or revoke admin privileges"""
        try:
            user = User.query.get(user_id)
            if not user:
                return None
                
            user.is_admin = is_admin
            db.session.commit()
            return user.to_dict()
        except Exception as e:
            logger.error(f"Error toggling admin status: {str(e)}")
            db.session.rollback()
            raise
