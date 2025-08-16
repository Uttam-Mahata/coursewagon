# models/media.py
from extensions import db, Base
from datetime import datetime


class Media(Base):
    __tablename__ = 'media'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id', ondelete='CASCADE'), nullable=False)
    file_url = db.Column(db.String(500), nullable=False)  # Azure storage URL
    file_type = db.Column(db.Enum('image', 'video'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)  # File size in bytes
    mime_type = db.Column(db.String(100))
    position = db.Column(db.Integer)  # Position in content for ordering
    caption = db.Column(db.Text)  # Optional caption for the media
    alt_text = db.Column(db.String(255))  # Alt text for accessibility
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'content_id': self.content_id,
            'file_url': self.file_url,
            'file_type': self.file_type,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'position': self.position,
            'caption': self.caption,
            'alt_text': self.alt_text,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }