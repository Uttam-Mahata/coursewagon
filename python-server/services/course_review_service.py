# services/course_review_service.py
from repositories.course_review_repository import CourseReviewRepository
from repositories.enrollment_repository import EnrollmentRepository
from repositories.course_repo import CourseRepository
from models.course_review import CourseReview
from sqlalchemy.orm import Session
from fastapi import HTTPException
from utils.cache_helper import cached, invalidate_cache
import logging

logger = logging.getLogger(__name__)

# Minimum progress percentage required to write a review
MINIMUM_PROGRESS_FOR_REVIEW = 50.0

class CourseReviewService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.review_repo = CourseReviewRepository(db_session)
        self.enrollment_repo = EnrollmentRepository(db_session)
        self.course_repo = CourseRepository(db_session)

    def can_user_review(self, user_id: int, course_id: int) -> dict:
        """
        Check if user is eligible to review a course
        Requirements:
        - User must be enrolled in the course
        - Enrollment must be active
        - User must have completed at least MINIMUM_PROGRESS_FOR_REVIEW% of the course
        - User has not already reviewed the course
        """
        # Check enrollment
        enrollment = self.enrollment_repo.get_enrollment(user_id, course_id)

        if not enrollment:
            return {
                'can_review': False,
                'reason': 'You must be enrolled in this course to review it'
            }

        if enrollment.status != 'active' and enrollment.status != 'completed':
            return {
                'can_review': False,
                'reason': 'Your enrollment is not active'
            }

        # Check progress
        if enrollment.progress_percentage < MINIMUM_PROGRESS_FOR_REVIEW:
            return {
                'can_review': False,
                'reason': f'You must complete at least {MINIMUM_PROGRESS_FOR_REVIEW}% of the course to review it',
                'progress_percentage': enrollment.progress_percentage,
                'minimum_required': MINIMUM_PROGRESS_FOR_REVIEW
            }

        # Check if already reviewed
        if self.review_repo.check_user_has_reviewed(user_id, course_id):
            return {
                'can_review': False,
                'reason': 'You have already reviewed this course. You can edit your existing review.'
            }

        return {
            'can_review': True,
            'progress_percentage': enrollment.progress_percentage
        }

    def create_review(self, user_id: int, course_id: int, rating: int, review_text: str = None) -> dict:
        """Create a new course review"""
        try:
            # Validate rating
            if not 1 <= rating <= 5:
                raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

            # Check eligibility
            eligibility = self.can_user_review(user_id, course_id)
            if not eligibility['can_review']:
                raise HTTPException(status_code=403, detail=eligibility['reason'])

            # Get enrollment ID
            enrollment = self.enrollment_repo.get_enrollment(user_id, course_id)
            if not enrollment:
                raise HTTPException(status_code=404, detail="Enrollment not found")

            # Create review
            review = self.review_repo.create_review(
                user_id=user_id,
                course_id=course_id,
                enrollment_id=enrollment.id,
                rating=rating,
                review_text=review_text
            )

            # Update course rating statistics
            self._update_course_rating(course_id)

            # Invalidate caches
            self._invalidate_review_caches(course_id)

            return {
                'success': True,
                'message': 'Review created successfully',
                'review': review.to_dict()
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating review: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def update_review(self, user_id: int, review_id: int, rating: int = None, review_text: str = None) -> dict:
        """Update an existing review"""
        try:
            # Get review
            review = self.review_repo.get_review_by_id(review_id)
            if not review:
                raise HTTPException(status_code=404, detail="Review not found")

            # Verify ownership
            if review.user_id != user_id:
                raise HTTPException(status_code=403, detail="You don't have permission to update this review")

            # Validate rating if provided
            if rating is not None and not 1 <= rating <= 5:
                raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

            # Update review
            updated_review = self.review_repo.update_review(
                review_id=review_id,
                rating=rating,
                review_text=review_text
            )

            # Update course rating statistics
            self._update_course_rating(review.course_id)

            # Invalidate caches
            self._invalidate_review_caches(review.course_id)

            return {
                'success': True,
                'message': 'Review updated successfully',
                'review': updated_review.to_dict()
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating review: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def delete_review(self, user_id: int, review_id: int) -> dict:
        """Delete a review"""
        try:
            # Get review
            review = self.review_repo.get_review_by_id(review_id)
            if not review:
                raise HTTPException(status_code=404, detail="Review not found")

            # Verify ownership
            if review.user_id != user_id:
                raise HTTPException(status_code=403, detail="You don't have permission to delete this review")

            course_id = review.course_id

            # Delete review
            success = self.review_repo.delete_review(review_id)

            if success:
                # Update course rating statistics
                self._update_course_rating(course_id)

                # Invalidate caches
                self._invalidate_review_caches(course_id)

                return {
                    'success': True,
                    'message': 'Review deleted successfully'
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to delete review")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting review: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_course_reviews(self, course_id: int, page: int = 1, limit: int = 10) -> dict:
        """Get paginated reviews for a course"""
        try:
            offset = (page - 1) * limit

            reviews = self.review_repo.get_course_reviews(
                course_id=course_id,
                limit=limit,
                offset=offset,
                visible_only=True
            )

            total_count = self.review_repo.get_course_reviews_count(course_id, visible_only=True)

            return {
                'reviews': [review.to_dict() for review in reviews],
                'total_count': total_count,
                'page': page,
                'limit': limit,
                'total_pages': (total_count + limit - 1) // limit
            }

        except Exception as e:
            logger.error(f"Error getting course reviews: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_user_review(self, user_id: int, course_id: int) -> dict:
        """Get user's review for a course"""
        review = self.review_repo.get_user_review(user_id, course_id)

        if review:
            return review.to_dict()
        return None

    def get_review_stats(self, course_id: int) -> dict:
        """Get review statistics for a course"""
        try:
            stats = self.review_repo.get_review_stats(course_id)
            return stats
        except Exception as e:
            logger.error(f"Error getting review stats: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def _update_course_rating(self, course_id: int):
        """Internal method to update course average rating and review count"""
        try:
            # Calculate new average rating
            avg_rating = self.review_repo.calculate_average_rating(course_id)
            review_count = self.review_repo.get_course_reviews_count(course_id, visible_only=True)

            # Update course
            course = self.course_repo.get_course_by_id(course_id)
            if course:
                course['average_rating'] = avg_rating
                course['review_count'] = review_count

                # Update in database
                from models.course import Course
                db_course = self.db_session.query(Course).filter(Course.id == course_id).first()
                if db_course:
                    db_course.average_rating = avg_rating
                    db_course.review_count = review_count
                    self.db_session.commit()

                logger.info(f"Updated course {course_id} rating: {avg_rating} ({review_count} reviews)")

        except Exception as e:
            logger.error(f"Error updating course rating: {str(e)}")
            # Don't raise exception here, just log it

    def _invalidate_review_caches(self, course_id: int):
        """Invalidate review and course caches"""
        try:
            invalidate_cache(f"reviews:course:{course_id}:*")
            invalidate_cache(f"course:{course_id}:*")
            invalidate_cache("courses:*")
            logger.debug(f"Invalidated review caches for course {course_id}")
        except Exception as e:
            logger.error(f"Error invalidating caches: {str(e)}")
