from datetime import datetime
from typing import Optional, Dict, List, Any

class AdminStats:
    """Data model for admin dashboard statistics"""
    
    def __init__(self, 
                 total_users: int = 0,
                 active_users: int = 0, 
                 total_courses: int = 0,
                 total_testimonials: int = 0,
                 pending_testimonials: int = 0,
                 recent_users: Optional[List[Dict]] = None,
                 recent_courses: Optional[List[Dict]] = None):
        self.total_users = total_users
        self.active_users = active_users
        self.total_courses = total_courses
        self.total_testimonials = total_testimonials  
        self.pending_testimonials = pending_testimonials
        self.recent_users = recent_users or []
        self.recent_courses = recent_courses or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'total_users': self.total_users,
            'active_users': self.active_users,
            'total_courses': self.total_courses,
            'total_testimonials': self.total_testimonials,
            'pending_testimonials': self.pending_testimonials,
            'recent_users': self.recent_users,
            'recent_courses': self.recent_courses
        }
