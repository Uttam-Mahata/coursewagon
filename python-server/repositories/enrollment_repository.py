# repositories/enrollment_repository.py
from sqlalchemy.orm import Session
from models.enrollment import Enrollment
from models.course import Course
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EnrollmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def enroll_user(self, user_id: int, course_id: int) -> Enrollment:
        """Enroll a user in a course"""
        try:
            enrollment = Enrollment(
                user_id=user_id,
                course_id=course_id,
                status='active',
                progress_percentage=0.0
            )
            self.db.add(enrollment)
            self.db.commit()
            self.db.refresh(enrollment)
            return enrollment
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error enrolling user: {str(e)}")
            raise

    def get_enrollment_by_id(self, enrollment_id: int) -> Enrollment:
        """Get enrollment by ID"""
        return self.db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()

    def get_enrollment(self, user_id: int, course_id: int) -> Enrollment:
        """Get enrollment for a specific user and course"""
        return self.db.query(Enrollment).filter(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id
        ).first()

    def check_enrollment_exists(self, user_id: int, course_id: int) -> bool:
        """Check if user is already enrolled in a course"""
        enrollment = self.get_enrollment(user_id, course_id)
        return enrollment is not None

    def get_user_enrollments(self, user_id: int, status: str = None):
        """Get all enrollments for a user, optionally filtered by status"""
        query = self.db.query(Enrollment).filter(Enrollment.user_id == user_id)

        if status:
            query = query.filter(Enrollment.status == status)

        return query.order_by(Enrollment.enrolled_at.desc()).all()

    def get_course_enrollments(self, course_id: int, status: str = None):
        """Get all enrollments for a course, optionally filtered by status"""
        query = self.db.query(Enrollment).filter(Enrollment.course_id == course_id)

        if status:
            query = query.filter(Enrollment.status == status)

        return query.order_by(Enrollment.enrolled_at.desc()).all()

    def update_enrollment_status(self, enrollment_id: int, status: str) -> Enrollment:
        """Update enrollment status (active, completed, dropped)"""
        try:
            enrollment = self.get_enrollment_by_id(enrollment_id)
            if enrollment:
                enrollment.status = status
                if status == 'completed':
                    enrollment.completed_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(enrollment)
            return enrollment
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating enrollment status: {str(e)}")
            raise

    def update_progress(self, enrollment_id: int, progress_percentage: float) -> Enrollment:
        """Update enrollment progress percentage"""
        try:
            enrollment = self.get_enrollment_by_id(enrollment_id)
            if enrollment:
                enrollment.progress_percentage = progress_percentage
                enrollment.last_accessed_at = datetime.utcnow()

                # Auto-complete if progress reaches 100%
                if progress_percentage >= 100 and enrollment.status != 'completed':
                    enrollment.status = 'completed'
                    enrollment.completed_at = datetime.utcnow()

                self.db.commit()
                self.db.refresh(enrollment)
            return enrollment
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating enrollment progress: {str(e)}")
            raise

    def unenroll_user(self, user_id: int, course_id: int) -> bool:
        """Unenroll a user from a course"""
        try:
            enrollment = self.get_enrollment(user_id, course_id)
            if enrollment:
                self.db.delete(enrollment)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error unenrolling user: {str(e)}")
            raise

    def get_enrollment_count(self, course_id: int, status: str = 'active') -> int:
        """Get count of enrollments for a course"""
        return self.db.query(Enrollment).filter(
            Enrollment.course_id == course_id,
            Enrollment.status == status
        ).count()

    def update_last_accessed(self, enrollment_id: int) -> Enrollment:
        """Update the last accessed time for an enrollment"""
        try:
            enrollment = self.get_enrollment_by_id(enrollment_id)
            if enrollment:
                enrollment.last_accessed_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(enrollment)
            return enrollment
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating last accessed: {str(e)}")
            raise
