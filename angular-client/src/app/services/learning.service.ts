import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface CoursePreview {
  course: any;
  structure: any[];
}

export interface ProgressTrackRequest {
  enrollment_id: number;
  topic_id: number;
  content_id?: number;
  completed?: boolean;
  time_spent_seconds?: number;
  last_position?: string;
}

export interface TopicCompleteRequest {
  enrollment_id: number;
  topic_id: number;
}

export interface CourseProgress {
  enrollment_id: number;
  course_id: number;
  progress_percentage: number;
  completed_topics: number;
  total_time_spent_seconds: number;
  progress_records: any[];
}

export interface PublishCourseRequest {
  category?: string;
  difficulty_level?: string;
  estimated_duration_hours?: number;
}

@Injectable({
  providedIn: 'root'
})
export class LearningService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // Course Discovery Methods

  /**
   * Browse all published courses
   */
  getPublishedCourses(limit: number = 20, offset: number = 0): Observable<any[]> {
    const params = new HttpParams()
      .set('limit', limit.toString())
      .set('offset', offset.toString());

    return this.http.get<any[]>(
      `${this.apiUrl}/learning/courses`,
      { params }
    );
  }

  /**
   * Search published courses
   */
  searchCourses(query: string, limit: number = 20): Observable<any[]> {
    const params = new HttpParams()
      .set('q', query)
      .set('limit', limit.toString());

    return this.http.get<any[]>(
      `${this.apiUrl}/learning/courses/search`,
      { params }
    );
  }

  /**
   * Get courses by category
   */
  getCoursesByCategory(category: string, limit: number = 20): Observable<any[]> {
    const params = new HttpParams().set('limit', limit.toString());

    return this.http.get<any[]>(
      `${this.apiUrl}/learning/courses/category/${category}`,
      { params }
    );
  }

  /**
   * Get popular courses
   */
  getPopularCourses(limit: number = 10): Observable<any[]> {
    const params = new HttpParams().set('limit', limit.toString());

    return this.http.get<any[]>(
      `${this.apiUrl}/learning/courses/popular`,
      { params }
    );
  }

  /**
   * Get course preview (structure without detailed content)
   */
  getCoursePreview(courseId: number): Observable<CoursePreview> {
    return this.http.get<CoursePreview>(
      `${this.apiUrl}/learning/courses/${courseId}/preview`
    );
  }

  /**
   * Get full course structure with subjects, chapters, and topics (for enrolled users)
   * This is optimized to reduce multiple API calls in the learning view
   */
  getCourseStructure(courseId: number): Observable<any> {
    return this.http.get(
      `${this.apiUrl}/learning/courses/${courseId}/structure`
    );
  }

  // Progress Tracking Methods

  /**
   * Track learning progress for a topic
   */
  trackProgress(data: ProgressTrackRequest): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/learning/progress/track`,
      data
    );
  }

  /**
   * Mark a topic as completed
   */
  markTopicComplete(data: TopicCompleteRequest): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/learning/progress/complete-topic`,
      data
    );
  }

  /**
   * Get progress for a course enrollment
   */
  getCourseProgress(enrollmentId: number): Observable<CourseProgress> {
    return this.http.get<CourseProgress>(
      `${this.apiUrl}/learning/progress/enrollment/${enrollmentId}`
    );
  }

  /**
   * Get resume point (last accessed topic)
   */
  getResumePoint(enrollmentId: number): Observable<any> {
    return this.http.get(
      `${this.apiUrl}/learning/progress/enrollment/${enrollmentId}/resume`
    );
  }

  // Publishing Methods (for creators)

  /**
   * Publish a course
   */
  publishCourse(courseId: number, data: PublishCourseRequest): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/learning/courses/${courseId}/publish`,
      data
    );
  }

  /**
   * Unpublish a course
   */
  unpublishCourse(courseId: number): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/learning/courses/${courseId}/unpublish`,
      {}
    );
  }
}
