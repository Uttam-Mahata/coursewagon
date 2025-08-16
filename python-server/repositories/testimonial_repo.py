from models.testimonial import Testimonial
from extensions import get_db
import logging
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class TestimonialRepository:
    def __init__(self, db_session: Session = None):
        self.db_session = db_session
    
    def _get_session(self):
        """Get database session"""
        if self.db_session:
            return self.db_session
        # Fallback - create new session (should be avoided in production)
        from extensions import SessionLocal
        return SessionLocal()
    
    def add_testimonial(self, testimonial):
        """Add a new testimonial"""
        session = self._get_session()
        try:
            session.add(testimonial)
            session.commit()
            session.refresh(testimonial)
            return testimonial
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding testimonial: {e}")
            raise
        finally:
            if not self.db_session:  # Only close if we created the session
                session.close()
    
    def get_all_testimonials(self):
        """Get all testimonials"""
        session = self._get_session()
        try:
            return session.query(Testimonial).all()
        except Exception as e:
            logger.error(f"Error getting all testimonials: {e}")
            raise
        finally:
            if not self.db_session:
                session.close()
    
    def get_approved_testimonials(self):
        """Get only approved testimonials"""
        session = self._get_session()
        try:
            return session.query(Testimonial).filter(Testimonial.is_approved == True).all()
        except Exception as e:
            logger.error(f"Error getting approved testimonials: {e}")
            raise
        finally:
            if not self.db_session:
                session.close()
    
    def get_testimonial_by_id(self, testimonial_id):
        """Get testimonial by ID"""
        session = self._get_session()
        try:
            return session.query(Testimonial).filter(Testimonial.id == testimonial_id).first()
        except Exception as e:
            logger.error(f"Error getting testimonial by ID: {e}")
            raise
        finally:
            if not self.db_session:
                session.close()
    
    def get_user_testimonials(self, user_id):
        """Get testimonials by user ID"""
        session = self._get_session()
        try:
            return session.query(Testimonial).filter(Testimonial.user_id == user_id).all()
        except Exception as e:
            logger.error(f"Error getting user testimonials: {e}")
            raise
        finally:
            if not self.db_session:
                session.close()
    
    def update_testimonial(self, testimonial_id, quote=None, rating=None, is_approved=None):
        """Update an existing testimonial"""
        session = self._get_session()
        try:
            testimonial = session.query(Testimonial).filter(Testimonial.id == testimonial_id).first()
            if testimonial:
                if quote is not None:
                    testimonial.quote = quote
                if rating is not None:
                    testimonial.rating = rating
                if is_approved is not None:
                    testimonial.is_approved = is_approved
                
                session.commit()
                session.refresh(testimonial)
                return testimonial
            return None
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating testimonial: {e}")
            raise
        finally:
            if not self.db_session:
                session.close()
    
    def delete_testimonial(self, testimonial_id):
        """Delete a testimonial"""
        session = self._get_session()
        try:
            testimonial = session.query(Testimonial).filter(Testimonial.id == testimonial_id).first()
            if testimonial:
                session.delete(testimonial)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting testimonial: {e}")
            raise
        finally:
            if not self.db_session:
                session.close()
    
    def check_user_has_testimonial(self, user_id):
        """Check if user already has a testimonial"""
        session = self._get_session()
        try:
            count = session.query(Testimonial).filter(Testimonial.user_id == user_id).count()
            return count > 0
        except Exception as e:
            logger.error(f"Error checking user testimonial: {e}")
            raise
        finally:
            if not self.db_session:
                session.close()
