from datetime import datetime
from typing import Optional, Dict, List, Any

class AdminStats:
    """Data model for admin dashboard statistics"""

    def __init__(self,
                 total_users: int = 0,
                 active_users: int = 0,
                 total_courses: int = 0,
                 total_subjects: int = 0,
                 total_chapters: int = 0,
                 total_topics: int = 0,
                 total_content: int = 0,
                 total_testimonials: int = 0,
                 pending_testimonials: int = 0,
                 recent_users: Optional[List[Dict]] = None,
                 recent_courses: Optional[List[Dict]] = None,
                 course_breakdown: Optional[List[Dict]] = None):
        self.total_users = total_users
        self.active_users = active_users
        self.total_courses = total_courses
        self.total_subjects = total_subjects
        self.total_chapters = total_chapters
        self.total_topics = total_topics
        self.total_content = total_content
        self.total_testimonials = total_testimonials
        self.pending_testimonials = pending_testimonials
        self.recent_users = recent_users or []
        self.recent_courses = recent_courses or []
        self.course_breakdown = course_breakdown or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'total_users': self.total_users,
            'active_users': self.active_users,
            'total_courses': self.total_courses,
            'total_subjects': self.total_subjects,
            'total_chapters': self.total_chapters,
            'total_topics': self.total_topics,
            'total_content': self.total_content,
            'total_testimonials': self.total_testimonials,
            'pending_testimonials': self.pending_testimonials,
            'recent_users': self.recent_users,
            'recent_courses': self.recent_courses,
            'course_breakdown': self.course_breakdown
        }


class UserCourseStats:
    """Data model for user's course statistics (course creator dashboard)"""

    def __init__(self,
                 total_courses: int = 0,
                 total_subjects: int = 0,
                 total_chapters: int = 0,
                 total_topics: int = 0,
                 total_content: int = 0,
                 courses_with_details: Optional[List[Dict]] = None):
        self.total_courses = total_courses
        self.total_subjects = total_subjects
        self.total_chapters = total_chapters
        self.total_topics = total_topics
        self.total_content = total_content
        self.courses_with_details = courses_with_details or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'total_courses': self.total_courses,
            'total_subjects': self.total_subjects,
            'total_chapters': self.total_chapters,
            'total_topics': self.total_topics,
            'total_content': self.total_content,
            'courses_with_details': self.courses_with_details
        }
