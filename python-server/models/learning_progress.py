# models/learning_progress.py
from extensions import db, Base
from datetime import datetime

class LearningProgress(Base):
    __tablename__ = 'learning_progress'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.id', ondelete='CASCADE'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id', ondelete='CASCADE'), nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id', ondelete='CASCADE'), nullable=True)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    time_spent_seconds = db.Column(db.Integer, default=0, nullable=False)  # Time spent in seconds
    last_position = db.Column(db.Text, nullable=True)  # JSON string storing scroll position or other state
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    last_accessed_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    enrollment = db.relationship('Enrollment', backref='progress_records')
    topic = db.relationship('Topic', backref='progress_records')
    content = db.relationship('Content', backref='progress_records')

    def to_dict(self):
        return {
            'id': self.id,
            'enrollment_id': self.enrollment_id,
            'topic_id': self.topic_id,
            'content_id': self.content_id,
            'completed': self.completed,
            'time_spent_seconds': self.time_spent_seconds,
            'last_position': self.last_position,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'last_accessed_at': self.last_accessed_at.isoformat() if self.last_accessed_at else None
        }
