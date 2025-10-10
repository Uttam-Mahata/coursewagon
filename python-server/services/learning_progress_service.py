# services/learning_progress_service.py
from sqlalchemy.orm import Session
from repositories.learning_progress_repository import LearningProgressRepository
from repositories.enrollment_repository import EnrollmentRepository
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class LearningProgressService:
    def __init__(self, db: Session):
        self.db = db
        self.progress_repo = LearningProgressRepository(db)
        self.enrollment_repo = EnrollmentRepository(db)

    def track_progress(self, user_id: int, enrollment_id: int, topic_id: int,
                       content_id: int = None, completed: bool = False,
                       time_spent_seconds: int = 0, last_position: str = None):
        """Track learning progress for a topic"""
        try:
            # Verify enrollment belongs to user
            enrollment = self.enrollment_repo.get_enrollment_by_id(enrollment_id)
            if not enrollment or enrollment.user_id != user_id:
                raise HTTPException(status_code=403, detail="Not authorized")

            # Create or update progress
            progress = self.progress_repo.create_or_update_progress(
                enrollment_id=enrollment_id,
                topic_id=topic_id,
                content_id=content_id,
                completed=completed,
                time_spent_seconds=time_spent_seconds,
                last_position=last_position
            )

            # Update last accessed time for enrollment
            self.enrollment_repo.update_last_accessed(enrollment_id)

            return {
                "success": True,
                "progress": progress.to_dict()
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error tracking progress: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def mark_topic_complete(self, user_id: int, enrollment_id: int, topic_id: int):
        """Mark a topic as completed"""
        try:
            # Verify enrollment belongs to user
            enrollment = self.enrollment_repo.get_enrollment_by_id(enrollment_id)
            if not enrollment or enrollment.user_id != user_id:
                raise HTTPException(status_code=403, detail="Not authorized")

            progress = self.progress_repo.mark_topic_complete(enrollment_id, topic_id)

            return {
                "success": True,
                "message": "Topic marked as complete",
                "progress": progress.to_dict()
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error marking topic complete: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_course_progress(self, user_id: int, enrollment_id: int):
        """Get all progress for a course enrollment"""
        try:
            # Verify enrollment belongs to user
            enrollment = self.enrollment_repo.get_enrollment_by_id(enrollment_id)
            if not enrollment or enrollment.user_id != user_id:
                raise HTTPException(status_code=403, detail="Not authorized")

            progress_records = self.progress_repo.get_progress_by_enrollment(enrollment_id)

            return {
                "enrollment_id": enrollment_id,
                "course_id": enrollment.course_id,
                "progress_percentage": enrollment.progress_percentage,
                "completed_topics": self.progress_repo.get_completed_topics_count(enrollment_id),
                "total_time_spent_seconds": self.progress_repo.get_total_time_spent(enrollment_id),
                "progress_records": [p.to_dict() for p in progress_records]
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting course progress: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_last_accessed_topic(self, user_id: int, enrollment_id: int):
        """Get the most recently accessed topic for resume functionality"""
        try:
            # Verify enrollment belongs to user
            enrollment = self.enrollment_repo.get_enrollment_by_id(enrollment_id)
            if not enrollment or enrollment.user_id != user_id:
                raise HTTPException(status_code=403, detail="Not authorized")

            last_topic = self.progress_repo.get_last_accessed_topic(enrollment_id)

            if last_topic:
                return {
                    "has_progress": True,
                    "last_topic": last_topic.to_dict()
                }
            else:
                return {
                    "has_progress": False,
                    "last_topic": None
                }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting last accessed topic: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
