import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface CourseReview {
  id: number;
  user_id: number;
  course_id: number;
  enrollment_id: number;
  rating: number;
  review_text?: string;
  author_name: string;
  is_visible: boolean;
  helpful_count: number;
  created_at: string;
  updated_at: string;
}

export interface ReviewStats {
  average_rating: number;
  review_count: number;
  rating_distribution: { [key: number]: number };
}

export interface CanReviewResponse {
  can_review: boolean;
  reason?: string;
  progress_percentage?: number;
  minimum_required?: number;
}

export interface ReviewsListResponse {
  reviews: CourseReview[];
  total_count: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface ReviewResponse {
  success: boolean;
  message: string;
  review?: CourseReview;
}

@Injectable({
  providedIn: 'root'
})
export class ReviewService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  /**
   * Get paginated reviews for a course (public endpoint)
   */
  getCourseReviews(courseId: number, page: number = 1, limit: number = 10): Observable<ReviewsListResponse> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('limit', limit.toString());

    return this.http.get<ReviewsListResponse>(
      `${this.apiUrl}/reviews/course/${courseId}`,
      { params }
    );
  }

  /**
   * Get review statistics for a course (public endpoint)
   */
  getReviewStats(courseId: number): Observable<ReviewStats> {
    return this.http.get<ReviewStats>(
      `${this.apiUrl}/reviews/course/${courseId}/stats`
    );
  }

  /**
   * Check if current user can review a course (protected endpoint)
   */
  canReview(courseId: number): Observable<CanReviewResponse> {
    return this.http.get<CanReviewResponse>(
      `${this.apiUrl}/reviews/can-review/${courseId}`
    );
  }

  /**
   * Get current user's review for a course (protected endpoint)
   */
  getMyReview(courseId: number): Observable<CourseReview> {
    return this.http.get<CourseReview>(
      `${this.apiUrl}/reviews/my-review/${courseId}`
    );
  }

  /**
   * Create a new review (protected endpoint)
   */
  createReview(courseId: number, rating: number, reviewText?: string): Observable<ReviewResponse> {
    return this.http.post<ReviewResponse>(
      `${this.apiUrl}/reviews`,
      {
        course_id: courseId,
        rating: rating,
        review_text: reviewText
      }
    );
  }

  /**
   * Update an existing review (protected endpoint)
   */
  updateReview(reviewId: number, rating?: number, reviewText?: string): Observable<ReviewResponse> {
    const payload: any = {};
    if (rating !== undefined) payload.rating = rating;
    if (reviewText !== undefined) payload.review_text = reviewText;

    return this.http.put<ReviewResponse>(
      `${this.apiUrl}/reviews/${reviewId}`,
      payload
    );
  }

  /**
   * Delete a review (protected endpoint)
   */
  deleteReview(reviewId: number): Observable<ReviewResponse> {
    return this.http.delete<ReviewResponse>(
      `${this.apiUrl}/reviews/${reviewId}`
    );
  }
}
