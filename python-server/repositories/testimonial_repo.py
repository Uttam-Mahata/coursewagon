from models.testimonial import Testimonial
from extensions import get_db
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

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
    
    def _close_session_if_needed(self, session):
        """Close session only if it's not the injected session"""
        if not self.db_session and session:
            try:
                session.close()
            except Exception as e:
                logger.error(f"Error closing session: {e}")
    
    def add_testimonial(self, testimonial):
        """Add a new testimonial"""
        session = self._get_session()
        try:
            session.add(testimonial)
            session.commit()
            session.refresh(testimonial)
            return testimonial
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error adding testimonial: {e}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding testimonial: {e}")
            raise
        finally:
            self._close_session_if_needed(session)
    
    def get_all_testimonials(self):
        """Get all testimonials"""
        session = self._get_session()
        try:
            return session.query(Testimonial).all()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error getting all testimonials: {e}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error getting all testimonials: {e}")
            raise
        finally:
            self._close_session_if_needed(session)
    
    def get_approved_testimonials(self):
        """Get only approved testimonials"""
        session = self._get_session()
        try:
            return session.query(Testimonial).filter(Testimonial.is_approved == True).all()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error getting approved testimonials: {e}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error getting approved testimonials: {e}")
            raise
        finally:
            self._close_session_if_needed(session)
    
    def get_testimonial_by_id(self, testimonial_id):
        """Get testimonial by ID"""
        session = self._get_session()
        try:
            return session.query(Testimonial).filter(Testimonial.id == testimonial_id).first()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error getting testimonial by ID: {e}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error getting testimonial by ID: {e}")
            raise
        finally:
            self._close_session_if_needed(session)
    
    def get_user_testimonials(self, user_id):
        """Get testimonials by user ID"""
        session = self._get_session()
        try:
            return session.query(Testimonial).filter(Testimonial.user_id == user_id).all()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error getting user testimonials: {e}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error getting user testimonials: {e}")
            raise
        finally:
            self._close_session_if_needed(session)
    
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
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error updating testimonial: {e}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating testimonial: {e}")
            raise
        finally:
            self._close_session_if_needed(session)
    
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
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error deleting testimonial: {e}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting testimonial: {e}")
            raise
        finally:
            self._close_session_if_needed(session)
    
    def check_user_has_testimonial(self, user_id):
        """Check if user already has a testimonial"""
        session = self._get_session()
        try:
            count = session.query(Testimonial).filter(Testimonial.user_id == user_id).count()
            return count > 0
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error checking user testimonial: {e}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error checking user testimonial: {e}")
            raise
        finally:
            self._close_session_if_needed(session)
