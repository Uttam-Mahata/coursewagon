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

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'has_subjects': self.has_subjects,
            'image_url': self.image_url
        }