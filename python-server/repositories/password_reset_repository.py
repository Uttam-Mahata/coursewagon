from models.password_reset import PasswordReset
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PasswordResetRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_reset_token(self, user, expires_in_hours=24):
        """Create a password reset token for a user"""
        # Invalidate any existing active tokens first
        self.invalidate_user_tokens(user.id)
        
        # Create a new token
        reset_token = PasswordReset.create_for_user(user, expires_in_hours)
        logger.info(f"Created password reset token for user ID {user.id}")
        return reset_token
    
    def get_by_token(self, token):
        """Get a password reset entry by token"""
        return self.db.query(PasswordReset).filter_by(token=token).first()
    
    def invalidate_token(self, token):
        """Mark a token as used"""
        reset = self.db.query(PasswordReset).filter_by(token=token).first()
        if reset:
            reset.used = True
            self.db.commit()
            logger.info(f"Invalidated password reset token for user ID {reset.user_id}")
            return True
        return False
    
    def invalidate_user_tokens(self, user_id):
        """Invalidate all active tokens for a user"""
        resets = self.db.query(PasswordReset).filter_by(user_id=user_id, used=False).all()
        for reset in resets:
            reset.used = True
        
        if resets:
            self.db.commit()
            logger.info(f"Invalidated {len(resets)} password reset tokens for user ID {user_id}")
        
        return len(resets)
    
    def cleanup_expired_tokens(self, days=7):
        """Remove expired tokens older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        expired_tokens = self.db.query(PasswordReset).filter(
            (PasswordReset.expires_at < datetime.utcnow()) & 
            (PasswordReset.created_at < cutoff_date)
        ).all()
        
        for token in expired_tokens:
            self.db.delete(token)
        
        count = len(expired_tokens)
        if count:
            self.db.commit()
            logger.info(f"Cleaned up {count} expired password reset tokens")
        
        return count
