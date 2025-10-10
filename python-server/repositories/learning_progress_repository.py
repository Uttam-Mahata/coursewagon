# repositories/learning_progress_repository.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.learning_progress import LearningProgress
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LearningProgressRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_or_update_progress(self, enrollment_id: int, topic_id: int,
                                   content_id: int = None, completed: bool = False,
                                   time_spent_seconds: int = 0, last_position: str = None) -> LearningProgress:
        """Create or update learning progress for a topic"""
        try:
            # Check if progress record already exists
            progress = self.db.query(LearningProgress).filter(
                LearningProgress.enrollment_id == enrollment_id,
                LearningProgress.topic_id == topic_id
            ).first()

            if progress:
                # Update existing progress
                progress.content_id = content_id if content_id else progress.content_id
                progress.completed = completed
                progress.time_spent_seconds += time_spent_seconds
                progress.last_position = last_position if last_position else progress.last_position
                progress.last_accessed_at = datetime.utcnow()

                if completed and not progress.completed_at:
                    progress.completed_at = datetime.utcnow()
            else:
                # Create new progress record
                progress = LearningProgress(
                    enrollment_id=enrollment_id,
                    topic_id=topic_id,
                    content_id=content_id,
                    completed=completed,
                    time_spent_seconds=time_spent_seconds,
                    last_position=last_position
                )
                if completed:
                    progress.completed_at = datetime.utcnow()

                self.db.add(progress)

            self.db.commit()
            self.db.refresh(progress)
            return progress

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating/updating progress: {str(e)}")
            raise

    def get_progress_by_enrollment(self, enrollment_id: int):
        """Get all progress records for an enrollment"""
        return self.db.query(LearningProgress).filter(
            LearningProgress.enrollment_id == enrollment_id
        ).all()

    def get_progress_for_topic(self, enrollment_id: int, topic_id: int) -> LearningProgress:
        """Get progress for a specific topic in an enrollment"""
        return self.db.query(LearningProgress).filter(
            LearningProgress.enrollment_id == enrollment_id,
            LearningProgress.topic_id == topic_id
        ).first()

    def mark_topic_complete(self, enrollment_id: int, topic_id: int) -> LearningProgress:
        """Mark a topic as completed"""
        try:
            progress = self.get_progress_for_topic(enrollment_id, topic_id)

            if progress:
                progress.completed = True
                progress.completed_at = datetime.utcnow()
            else:
                progress = LearningProgress(
                    enrollment_id=enrollment_id,
                    topic_id=topic_id,
                    completed=True,
                    completed_at=datetime.utcnow()
                )
                self.db.add(progress)

            self.db.commit()
            self.db.refresh(progress)
            return progress

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error marking topic complete: {str(e)}")
            raise

    def get_completed_topics_count(self, enrollment_id: int) -> int:
        """Get count of completed topics for an enrollment"""
        return self.db.query(LearningProgress).filter(
            LearningProgress.enrollment_id == enrollment_id,
            LearningProgress.completed == True
        ).count()

    def get_total_time_spent(self, enrollment_id: int) -> int:
        """Get total time spent (in seconds) for an enrollment"""
        result = self.db.query(
            func.sum(LearningProgress.time_spent_seconds)
        ).filter(
            LearningProgress.enrollment_id == enrollment_id
        ).scalar()

        return result if result else 0

    def calculate_course_progress(self, enrollment_id: int, total_topics: int) -> float:
        """Calculate progress percentage for a course"""
        if total_topics == 0:
            return 0.0

        completed_count = self.get_completed_topics_count(enrollment_id)
        progress_percentage = (completed_count / total_topics) * 100
        return round(progress_percentage, 2)

    def delete_progress(self, enrollment_id: int, topic_id: int) -> bool:
        """Delete progress record for a topic"""
        try:
            progress = self.get_progress_for_topic(enrollment_id, topic_id)
            if progress:
                self.db.delete(progress)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting progress: {str(e)}")
            raise

    def get_last_accessed_topic(self, enrollment_id: int) -> LearningProgress:
        """Get the most recently accessed topic for an enrollment"""
        return self.db.query(LearningProgress).filter(
            LearningProgress.enrollment_id == enrollment_id
        ).order_by(
            LearningProgress.last_accessed_at.desc()
        ).first()

    def reset_progress(self, enrollment_id: int) -> bool:
        """Reset all progress for an enrollment"""
        try:
            self.db.query(LearningProgress).filter(
                LearningProgress.enrollment_id == enrollment_id
            ).delete()
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error resetting progress: {str(e)}")
            raise
