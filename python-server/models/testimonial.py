from extensions import db, Base
from datetime import datetime

class Testimonial(Base):
    __tablename__ = 'testimonials'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    quote = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # Rating from 1-5
    is_approved = db.Column(db.Boolean, default=False)  # Admin approval status
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # User relationship
    user = db.relationship('User', backref='testimonials')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'author': f"{self.user.first_name} {self.user.last_name}" if self.user.first_name and self.user.last_name else self.user.email,
            'quote': self.quote,
            'rating': self.rating,
            'is_approved': self.is_approved,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
