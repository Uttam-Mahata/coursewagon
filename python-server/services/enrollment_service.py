# services/enrollment_service.py
from sqlalchemy.orm import Session
from repositories.enrollment_repository import EnrollmentRepository
from repositories.course_repo import CourseRepository
from repositories.learning_progress_repository import LearningProgressRepository
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class EnrollmentService:
    def __init__(self, db: Session):
        self.db = db
        self.enrollment_repo = EnrollmentRepository(db)
        self.course_repo = CourseRepository(db)
        self.progress_repo = LearningProgressRepository(db)

    def enroll_in_course(self, user_id: int, course_id: int):
        """Enroll a user in a course"""
        try:
            # Check if course exists
            course = self.course_repo.get_course_by_id(course_id)
            if not course:
                raise HTTPException(status_code=404, detail="Course not found")

            # Check if course is published
            if not course.is_published:
                raise HTTPException(status_code=403, detail="Cannot enroll in unpublished course")

            # Check if already enrolled
            if self.enrollment_repo.check_enrollment_exists(user_id, course_id):
                raise HTTPException(status_code=400, detail="User already enrolled in this course")

            # Create enrollment
            enrollment = self.enrollment_repo.enroll_user(user_id, course_id)

            # Increment enrollment count for the course
            self.course_repo.increment_enrollment_count(course_id)
            
            # Invalidate caches related to course enrollment counts
            from utils.cache_helper import invalidate_cache
            invalidate_cache(f"course:{course_id}")
            invalidate_cache("published_courses:*")
            invalidate_cache("popular_courses:*")

            return {
                "success": True,
                "message": "Successfully enrolled in course",
                "enrollment": enrollment.to_dict()
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error enrolling in course: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def unenroll_from_course(self, user_id: int, course_id: int):
        """Unenroll a user from a course"""
        try:
            # Check if enrollment exists
            if not self.enrollment_repo.check_enrollment_exists(user_id, course_id):
                raise HTTPException(status_code=404, detail="Enrollment not found")

            # Delete enrollment
            success = self.enrollment_repo.unenroll_user(user_id, course_id)

            if success:
                # Decrement enrollment count
                self.course_repo.decrement_enrollment_count(course_id)

                return {
                    "success": True,
                    "message": "Successfully unenrolled from course"
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to unenroll")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error unenrolling from course: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_my_enrollments(self, user_id: int, status: str = None):
        """Get all enrollments for a user with course details"""
        try:
            enrollments = self.enrollment_repo.get_user_enrollments(user_id, status)

            result = []
            for enrollment in enrollments:
                course = self.course_repo.get_course_by_id(enrollment.course_id)
                enrollment_dict = enrollment.to_dict()
                enrollment_dict['course'] = course.to_dict() if course else None
                result.append(enrollment_dict)

            return result

        except Exception as e:
            logger.error(f"Error getting user enrollments: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def check_enrollment(self, user_id: int, course_id: int):
        """Check if user is enrolled in a course"""
        try:
            enrollment = self.enrollment_repo.get_enrollment(user_id, course_id)
            if enrollment:
                return {
                    "enrolled": True,
                    "enrollment": enrollment.to_dict()
                }
            else:
                return {
                    "enrolled": False,
                    "enrollment": None
                }

        except Exception as e:
            logger.error(f"Error checking enrollment: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def check_enrollments_batch(self, user_id: int, course_ids: list[int]):
        """Check enrollment status for multiple courses at once (batch operation)"""
        try:
            enrollments = self.enrollment_repo.get_enrollments_batch(user_id, course_ids)
            
            # Create a map of course_id -> enrollment
            enrollment_map = {e.course_id: e for e in enrollments}
            
            # Build result for all requested course_ids
            result = {}
            for course_id in course_ids:
                if course_id in enrollment_map:
                    result[str(course_id)] = {
                        "enrolled": True,
                        "enrollment": enrollment_map[course_id].to_dict()
                    }
                else:
                    result[str(course_id)] = {
                        "enrolled": False,
                        "enrollment": None
                    }
            
            return result

        except Exception as e:
            logger.error(f"Error checking batch enrollments: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_course_enrollments(self, course_id: int, user_id: int):
        """Get enrollments for a course (only if user owns the course)"""
        try:
            # Verify course ownership
            course = self.course_repo.get_course_by_id(course_id)
            if not course:
                raise HTTPException(status_code=404, detail="Course not found")

            if course.user_id != user_id:
                raise HTTPException(status_code=403, detail="Not authorized to view enrollments")

            enrollments = self.enrollment_repo.get_course_enrollments(course_id)

            return [enrollment.to_dict() for enrollment in enrollments]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting course enrollments: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def update_enrollment_progress(self, enrollment_id: int, user_id: int):
        """Recalculate and update enrollment progress based on completed topics"""
        try:
            enrollment = self.enrollment_repo.get_enrollment_by_id(enrollment_id)
            if not enrollment:
                raise HTTPException(status_code=404, detail="Enrollment not found")

            # Verify user owns the enrollment
            if enrollment.user_id != user_id:
                raise HTTPException(status_code=403, detail="Not authorized")

            # Get course to count total topics
            from repositories.topic_repo import TopicRepository
            from repositories.chapter_repo import ChapterRepository
            from repositories.subject_repo import SubjectRepository

            subject_repo = SubjectRepository(self.db)
            chapter_repo = ChapterRepository(self.db)
            topic_repo = TopicRepository(self.db)

            # Get all subjects for the course
            subjects = subject_repo.get_subjects_by_course_id(enrollment.course_id)

            # Count total topics
            total_topics = 0
            for subject in subjects:
                chapters = chapter_repo.get_chapters_by_subject_id(subject.id)
                for chapter in chapters:
                    topics = topic_repo.get_topics_by_chapter_id(chapter.id)
                    total_topics += len(topics)

            # Calculate progress
            progress_percentage = self.progress_repo.calculate_course_progress(
                enrollment_id, total_topics
            )

            # Update enrollment
            updated_enrollment = self.enrollment_repo.update_progress(
                enrollment_id, progress_percentage
            )

            return {
                "success": True,
                "progress_percentage": progress_percentage,
                "enrollment": updated_enrollment.to_dict()
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating enrollment progress: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
