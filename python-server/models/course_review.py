# models/course_review.py
from extensions import db, Base
from datetime import datetime
from sqlalchemy import UniqueConstraint, Index, CheckConstraint

class CourseReview(Base):
    __tablename__ = 'course_reviews'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review_text = db.Column(db.Text, nullable=True)  # Optional review text
    is_visible = db.Column(db.Boolean, default=True, nullable=False)  # For moderation/hiding
    helpful_count = db.Column(db.Integer, default=0, nullable=False)  # Future feature: helpful votes
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User', backref='course_reviews')
    course = db.relationship('Course', backref='reviews')
    enrollment = db.relationship('Enrollment', backref='review')

    # Unique constraint: one review per user per course
    __table_args__ = (
        UniqueConstraint('user_id', 'course_id', name='unique_user_course_review'),
        Index('idx_course_visible', 'course_id', 'is_visible'),
        Index('idx_user_course', 'user_id', 'course_id'),
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    )

    def to_dict(self, include_user_info=True):
        """Convert review to dictionary with optional user information"""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'enrollment_id': self.enrollment_id,
            'rating': self.rating,
            'review_text': self.review_text,
            'is_visible': self.is_visible,
            'helpful_count': self.helpful_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_user_info and self.user:
            # Include reviewer name but protect privacy
            if self.user.first_name and self.user.last_name:
                result['author_name'] = f"{self.user.first_name} {self.user.last_name}"
            else:
                # Use first part of email as fallback
                result['author_name'] = self.user.email.split('@')[0] if self.user.email else 'Anonymous'

        return result
