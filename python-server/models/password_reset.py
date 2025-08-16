from extensions import db, Base
from datetime import datetime, timedelta
import uuid

class PasswordReset(Base):
    __tablename__ = 'password_reset'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    
    # Relationship with user
    user = db.relationship('User', backref='password_resets', lazy=True)
    
    @staticmethod
    def generate_token():
        """Generate a unique token for password reset"""
        return str(uuid.uuid4())
    
    @staticmethod
    def create_for_user(user, expires_in_hours=24):
        """Create a new password reset token for a user"""
        token = PasswordReset.generate_token()
        reset = PasswordReset(
            user_id=user.id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours)
        )
        db.session.add(reset)
        db.session.commit()
        return reset
    
    def is_expired(self):
        """Check if the token has expired"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        """Check if the token is valid (not expired and not used)"""
        return not self.used and not self.is_expired()
    
    def use_token(self):
        """Mark the token as used"""
        self.used = True
        db.session.commit()
        return True
