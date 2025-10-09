from extensions import db, Base
from datetime import datetime, timedelta
import uuid

class EmailVerification(Base):
    __tablename__ = 'email_verification'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)

    # Relationship with user
    user = db.relationship('User', backref='email_verifications', lazy=True)

    @staticmethod
    def generate_token():
        """Generate a unique token for email verification"""
        return str(uuid.uuid4())

    @staticmethod
    def create_for_user(user, session, expires_in_hours=24):
        """Create a new email verification token for a user"""
        token = EmailVerification.generate_token()
        verification = EmailVerification(
            user_id=user.id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours)
        )
        session.add(verification)
        session.flush()  # Flush to get the ID without committing
        return verification

    def is_expired(self):
        """Check if the token has expired"""
        return datetime.utcnow() > self.expires_at

    def is_valid(self):
        """Check if the token is valid (not expired and not used)"""
        return not self.used and not self.is_expired()

    def use_token(self, session):
        """Mark the token as used"""
        self.used = True
        session.commit()
        return True
