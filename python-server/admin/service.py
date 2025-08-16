from admin.repository import AdminRepository
from admin.models import AdminStats
from repositories.user_repository import UserRepository
import logging

logger = logging.getLogger(__name__)

class AdminService:
    """Service class for admin functionality"""
    
    def __init__(self):
        self.admin_repo = AdminRepository()
        self.user_repo = UserRepository()
    
    def get_dashboard_stats(self):
        """Get consolidated statistics for admin dashboard"""
        try:
            # Collect all stats from different sources
            user_stats = self.admin_repo.get_user_stats()
            course_stats = self.admin_repo.get_course_stats()
            testimonial_stats = self.admin_repo.get_testimonial_stats()
            
            # Combine into one object
            admin_stats = AdminStats(
                total_users=user_stats['total_users'],
                active_users=user_stats['active_users'],
                total_courses=course_stats['total_courses'],
                total_testimonials=testimonial_stats['total_testimonials'],
                pending_testimonials=testimonial_stats['pending_testimonials'],
                recent_users=user_stats['recent_users'],
                recent_courses=course_stats['recent_courses']
            )
            
            return admin_stats.to_dict()
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {str(e)}")
            raise Exception(f"Error retrieving admin dashboard data: {str(e)}")
    
    def get_all_users(self):
        """Get all users in the system"""
        try:
            users = self.user_repo.get_all_users()
            return [user.to_dict() for user in users]
        except Exception as e:
            logger.error(f"Error getting all users: {str(e)}")
            raise Exception(f"Error retrieving user list: {str(e)}")
    
    def get_pending_testimonials(self):
        """Get all pending testimonials"""
        try:
            return self.admin_repo.get_pending_testimonials()
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
