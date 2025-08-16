from models.user import User
from extensions import get_db, SessionLocal
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self, db_session: Session = None):
        self.db_session = db_session
    
    def _get_session(self):
        """Get database session"""
        if self.db_session:
            return self.db_session
        # Fallback - create new session (should be avoided in production)
        return SessionLocal()
    
    def _close_session_if_needed(self, session):
        """Close session only if it's not the injected session"""
        if not self.db_session and session:
            try:
                session.close()
            except Exception as e:
                logger.error(f"Error closing session: {e}")
    
    def create_user(self, email, password, first_name=None, last_name=None):
        session = self._get_session()
        try:
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            user.set_password(password)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error creating user: {e}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating user: {e}")
            raise
        finally:
            self._close_session_if_needed(session)

    def get_user_by_email(self, email):
        session = self._get_session()
        try:
            return session.query(User).filter_by(email=email).first()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error getting user by email: {e}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error getting user by email: {e}")
            raise
        finally:
            self._close_session_if_needed(session)

    def get_user_by_id(self, user_id):
        session = self._get_session()
        try:
            return session.query(User).get(user_id)
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error getting user by ID: {e}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error getting user by ID: {e}")
            raise
        finally:
            self._close_session_if_needed(session)

    def update_last_login(self, user):
        session = self._get_session()
        try:
            # Re-attach user to session if needed
            if user not in session:
                user = session.merge(user)
            user.last_login = datetime.utcnow()
            session.commit()
            return user
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error updating last login: {e}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating last login: {e}")
            raise
        finally:
            self._close_session_if_needed(session)

    def update_user(self, user, **kwargs):
        session = self._get_session()
        try:
            # Re-attach user to session if needed
            if user not in session:
                user = session.merge(user)
                
            if 'password' in kwargs:
                user.set_password(kwargs.pop('password'))
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            session.commit()
            session.refresh(user)
            return user
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error updating user: {e}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating user: {e}")
            raise
        finally:
            self._close_session_if_needed(session)

    def get_all_users(self):
        """Get all users in the system"""
        session = self._get_session()
        try:
            return session.query(User).all()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error getting all users: {e}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error getting all users: {e}")
            raise
        finally:
            self._close_session_if_needed(session)
    
    def count_users(self):
        """Count total users in the system"""
        session = self._get_session()
        try:
            return session.query(User).count()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error counting users: {e}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error counting users: {e}")
            raise
        finally:
            self._close_session_if_needed(session)
    
    def get_recent_users(self, limit=10):
        """Get recently registered users"""
        session = self._get_session()
        try:
            return session.query(User).order_by(User.created_at.desc()).limit(limit).all()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error getting recent users: {e}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error getting recent users: {e}")
            raise
        finally:
            self._close_session_if_needed(session)
    
    def count_active_users(self):
        """Count active users"""
        session = self._get_session()
        try:
            return session.query(User).filter_by(is_active=True).count()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error counting active users: {e}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error counting active users: {e}")
            raise
        finally:
            self._close_session_if_needed(session)
