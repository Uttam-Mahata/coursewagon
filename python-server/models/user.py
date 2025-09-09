from extensions import db, Base
from datetime import datetime
import bcrypt

class User(Base):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    password_salt = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)  # New field for admin role
    last_login = db.Column(db.DateTime)
    welcome_email_sent = db.Column(db.Boolean, default=False)  # Track if welcome email has been sent
    
    # Relationship with courses
    courses = db.relationship('Course', backref='creator', lazy=True)

    def set_password(self, password):
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        self.password_salt = salt.decode('utf-8')
        self.password_hash = password_hash.decode('utf-8')

    def check_password(self, password):
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'), 
            self.password_salt.encode('utf-8')
        ).decode('utf-8')
        return self.password_hash == password_hash

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'welcome_email_sent': self.welcome_email_sent
        }
