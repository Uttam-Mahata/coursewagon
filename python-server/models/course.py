# models/course.py
from extensions import db, Base

class Course(Base):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    # Add relationship with user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    has_subjects = db.Column(db.Boolean, default=False)  # Track if subjects were generated
    image_url = db.Column(db.String(512), nullable=True)  # Store the cover image URL

    # Publishing and discovery fields
    is_published = db.Column(db.Boolean, default=False, nullable=False)  # Whether course is published for learners
    published_at = db.Column(db.DateTime, nullable=True)  # When the course was published
    category = db.Column(db.String(100), nullable=True)  # Course category (e.g., Programming, Math, Science)
    difficulty_level = db.Column(db.String(50), nullable=True)  # beginner, intermediate, advanced
    estimated_duration_hours = db.Column(db.Integer, nullable=True)  # Estimated time to complete in hours
    enrollment_count = db.Column(db.Integer, default=0, nullable=False)  # Number of enrolled learners

    # Reviews and ratings
    average_rating = db.Column(db.Float, default=0.0, nullable=False)  # Average rating from reviews (0.0 - 5.0)
    review_count = db.Column(db.Integer, default=0, nullable=False)  # Total number of reviews

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'has_subjects': self.has_subjects,
            'image_url': self.image_url,
            'is_published': self.is_published,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'category': self.category,
            'difficulty_level': self.difficulty_level,
            'estimated_duration_hours': self.estimated_duration_hours,
            'enrollment_count': self.enrollment_count,
            'average_rating': self.average_rating,
            'review_count': self.review_count
        }