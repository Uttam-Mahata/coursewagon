from repositories.testimonial_repo import TestimonialRepository
from repositories.course_repo import CourseRepository
from models.testimonial import Testimonial
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

class TestimonialService:
    def __init__(self, db_session: Session = None):
        self.db_session = db_session
        self.testimonial_repo = TestimonialRepository(db_session)
        self.course_repo = CourseRepository(db_session) if hasattr(CourseRepository, '__init__') and 'db_session' in CourseRepository.__init__.__code__.co_varnames else CourseRepository()
    
    def create_testimonial(self, user_id, quote, rating):
        """Create a new testimonial after checking eligibility"""
        try:
            # Check if user has created courses
            user_courses = self.course_repo.get_user_courses(user_id)
            if not user_courses:
                raise ValueError("You must create at least one course before leaving a testimonial")
            
            # Check if user already has a testimonial
            if self.testimonial_repo.check_user_has_testimonial(user_id):
                raise ValueError("You have already submitted a testimonial")
            
            # Validate rating
            if not 1 <= rating <= 5:
                raise ValueError("Rating must be between 1 and 5")
            
            # Create and save testimonial
            testimonial = Testimonial(
                user_id=user_id,
                quote=quote,
                rating=rating,
                is_approved=False  # Needs admin approval by default
            )
            
            result = self.testimonial_repo.add_testimonial(testimonial)
            return result.to_dict()
            
        except Exception as e:
            logger.error(f"Error creating testimonial: {str(e)}")
            raise Exception(f"Error creating testimonial: {str(e)}")
    
    def get_approved_testimonials(self):
        """Get all approved testimonials for public display"""
        try:
            testimonials = self.testimonial_repo.get_approved_testimonials()
            return [t.to_dict() for t in testimonials]
        except Exception as e:
            logger.error(f"Error getting testimonials: {str(e)}")
            raise Exception(f"Error getting testimonials: {str(e)}")
    
    def get_user_testimonial(self, user_id):
        """Get testimonial for a specific user"""
        try:
            testimonials = self.testimonial_repo.get_user_testimonials(user_id)
            if testimonials:
                return testimonials[0].to_dict()
            return None
        except Exception as e:
            logger.error(f"Error getting user testimonial: {str(e)}")
            raise Exception(f"Error getting user testimonial: {str(e)}")
    
    def update_user_testimonial(self, user_id, testimonial_id, quote=None, rating=None):
        """Update a user's testimonial"""
        try:
            testimonial = self.testimonial_repo.get_testimonial_by_id(testimonial_id)
            
            # Check if testimonial exists and belongs to the user
            if not testimonial:
                raise ValueError("Testimonial not found")
            
            if testimonial.user_id != user_id:
                raise ValueError("You don't have permission to update this testimonial")
            
            # Validate rating if provided
            if rating is not None and not 1 <= rating <= 5:
                raise ValueError("Rating must be between 1 and 5")
            
            # Update requires re-approval
            result = self.testimonial_repo.update_testimonial(
                testimonial_id, 
                quote=quote, 
                rating=rating,
                is_approved=False
            )
            
            if result:
                return result.to_dict()
            return None
            
        except Exception as e:
            logger.error(f"Error updating testimonial: {str(e)}")
            raise Exception(f"Error updating testimonial: {str(e)}")
    
    def delete_user_testimonial(self, user_id, testimonial_id):
        """Delete a user's testimonial"""
        try:
            testimonial = self.testimonial_repo.get_testimonial_by_id(testimonial_id)
            
            # Check if testimonial exists and belongs to the user
            if not testimonial:
                raise ValueError("Testimonial not found")
            
            if testimonial.user_id != user_id:
                raise ValueError("You don't have permission to delete this testimonial")
            
            return self.testimonial_repo.delete_testimonial(testimonial_id)
            
        except Exception as e:
            logger.error(f"Error deleting testimonial: {str(e)}")
            raise Exception(f"Error deleting testimonial: {str(e)}")
    
    # Admin methods
    def get_all_testimonials(self):
        """Admin: Get all testimonials including unapproved ones"""
        try:
            testimonials = self.testimonial_repo.get_all_testimonials()
            return [t.to_dict() for t in testimonials]
        except Exception as e:
            logger.error(f"Error getting all testimonials: {str(e)}")
            raise Exception(f"Error getting all testimonials: {str(e)}")
    
    def approve_testimonial(self, testimonial_id, approved=True):
        """Admin: Approve or disapprove a testimonial"""
        try:
            result = self.testimonial_repo.update_testimonial(
                testimonial_id, 
                is_approved=approved
            )
            
            if result:
                return result.to_dict()
            raise ValueError("Testimonial not found")
            
        except Exception as e:
            logger.error(f"Error approving testimonial: {str(e)}")
            raise Exception(f"Error approving testimonial: {str(e)}")
