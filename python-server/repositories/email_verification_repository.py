from models.email_verification import EmailVerification
from sqlalchemy.orm import Session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EmailVerificationRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_verification_token(self, user):
        """Create a new email verification token for a user"""
        try:
            # Invalidate any existing unused tokens for this user
            existing_tokens = self.db_session.query(EmailVerification).filter_by(
                user_id=user.id,
                used=False
            ).all()

            for token in existing_tokens:
                token.used = True

            # Create new verification token (pass session to avoid db.session issue)
            verification = EmailVerification.create_for_user(user, self.db_session, expires_in_hours=24)
            self.db_session.commit()

            logger.info(f"Created email verification token for user {user.email}")
            return verification

        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error creating verification token: {str(e)}")
            raise

    def get_by_token(self, token):
        """Get email verification by token"""
        try:
            return self.db_session.query(EmailVerification).filter_by(token=token).first()
        except Exception as e:
            logger.error(f"Error getting verification by token: {str(e)}")
            return None

    def invalidate_token(self, token):
        """Mark a token as used"""
        try:
            verification = self.get_by_token(token)
            if verification:
                verification.used = True
                self.db_session.commit()
                logger.info(f"Invalidated verification token: {token[:10]}...")
                return True
            return False
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error invalidating token: {str(e)}")
            return False

    def delete_expired_tokens(self):
        """Delete expired verification tokens (cleanup)"""
        try:
            expired_tokens = self.db_session.query(EmailVerification).filter(
                EmailVerification.expires_at < datetime.utcnow()
            ).all()

            count = len(expired_tokens)
            for token in expired_tokens:
                self.db_session.delete(token)

            self.db_session.commit()
            logger.info(f"Deleted {count} expired verification tokens")
            return count

        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error deleting expired tokens: {str(e)}")
            return 0
