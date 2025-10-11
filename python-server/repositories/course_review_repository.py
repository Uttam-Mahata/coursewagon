# repositories/course_review_repository.py
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from models.course_review import CourseReview
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CourseReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_review(self, user_id: int, course_id: int, enrollment_id: int, rating: int, review_text: str = None) -> CourseReview:
        """Create a new course review"""
        try:
            review = CourseReview(
                user_id=user_id,
                course_id=course_id,
                enrollment_id=enrollment_id,
                rating=rating,
                review_text=review_text,
                is_visible=True
            )
            self.db.add(review)
            self.db.commit()
            self.db.refresh(review)
            return review
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating review: {str(e)}")
            raise

    def get_review_by_id(self, review_id: int) -> CourseReview:
        """Get review by ID"""
        return self.db.query(CourseReview).filter(CourseReview.id == review_id).first()

    def get_user_review(self, user_id: int, course_id: int) -> CourseReview:
        """Get user's review for a specific course"""
        return self.db.query(CourseReview).filter(
            CourseReview.user_id == user_id,
            CourseReview.course_id == course_id
        ).first()

    def check_user_has_reviewed(self, user_id: int, course_id: int) -> bool:
        """Check if user has already reviewed a course"""
        review = self.get_user_review(user_id, course_id)
        return review is not None

    def get_course_reviews(self, course_id: int, limit: int = 10, offset: int = 0, visible_only: bool = True):
        """Get paginated reviews for a course"""
        query = self.db.query(CourseReview).filter(CourseReview.course_id == course_id)

        if visible_only:
            query = query.filter(CourseReview.is_visible == True)

        return query.order_by(desc(CourseReview.created_at)).limit(limit).offset(offset).all()

    def get_course_reviews_count(self, course_id: int, visible_only: bool = True) -> int:
        """Get total count of reviews for a course"""
        query = self.db.query(CourseReview).filter(CourseReview.course_id == course_id)

        if visible_only:
            query = query.filter(CourseReview.is_visible == True)

        return query.count()

    def update_review(self, review_id: int, rating: int = None, review_text: str = None) -> CourseReview:
        """Update an existing review"""
        try:
            review = self.get_review_by_id(review_id)
            if review:
                if rating is not None:
                    review.rating = rating
                if review_text is not None:
                    review.review_text = review_text
                review.updated_at = datetime.utcnow()

                self.db.commit()
                self.db.refresh(review)
            return review
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating review: {str(e)}")
            raise

    def delete_review(self, review_id: int) -> bool:
        """Delete a review"""
        try:
            review = self.get_review_by_id(review_id)
            if review:
                self.db.delete(review)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting review: {str(e)}")
            raise

    def calculate_average_rating(self, course_id: int) -> float:
        """Calculate average rating for a course"""
        result = self.db.query(func.avg(CourseReview.rating)).filter(
            CourseReview.course_id == course_id,
            CourseReview.is_visible == True
        ).scalar()

        return round(float(result), 2) if result else 0.0

    def get_rating_distribution(self, course_id: int) -> dict:
        """Get rating distribution (count for each star rating 1-5)"""
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        results = self.db.query(
            CourseReview.rating,
            func.count(CourseReview.id).label('count')
        ).filter(
            CourseReview.course_id == course_id,
            CourseReview.is_visible == True
        ).group_by(CourseReview.rating).all()

        for rating, count in results:
            distribution[rating] = count

        return distribution

    def get_review_stats(self, course_id: int) -> dict:
        """Get comprehensive review statistics for a course"""
        avg_rating = self.calculate_average_rating(course_id)
        review_count = self.get_course_reviews_count(course_id, visible_only=True)
        distribution = self.get_rating_distribution(course_id)

        return {
            'average_rating': avg_rating,
            'review_count': review_count,
            'rating_distribution': distribution
        }

    def toggle_visibility(self, review_id: int, visible: bool = True) -> CourseReview:
        """Toggle review visibility (for moderation)"""
        try:
            review = self.get_review_by_id(review_id)
            if review:
                review.is_visible = visible
                self.db.commit()
                self.db.refresh(review)
            return review
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error toggling review visibility: {str(e)}")
            raise
