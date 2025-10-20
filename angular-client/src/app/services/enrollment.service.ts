import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Enrollment {
  id: number;
  user_id: number;
  course_id: number;
  enrolled_at: string;
  status: string;
  progress_percentage: number;
  last_accessed_at: string;
  completed_at: string | null;
  course?: any;
}

export interface EnrollmentResponse {
  success: boolean;
  message: string;
  enrollment?: Enrollment;
}

export interface EnrollmentCheck {
  enrolled: boolean;
  enrollment: Enrollment | null;
}

@Injectable({
  providedIn: 'root'
})
export class EnrollmentService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  /**
   * Enroll the current user in a course
   */
  enrollInCourse(courseId: number): Observable<EnrollmentResponse> {
    return this.http.post<EnrollmentResponse>(
      `${this.apiUrl}/enrollments/enroll`,
      { course_id: courseId }
    );
  }

  /**
   * Unenroll from a course
   */
  unenrollFromCourse(courseId: number): Observable<EnrollmentResponse> {
    return this.http.delete<EnrollmentResponse>(
      `${this.apiUrl}/enrollments/unenroll/${courseId}`
    );
  }

  /**
   * Get all enrollments for the current user
   */
  getMyEnrollments(status?: string): Observable<Enrollment[]> {
    let params = new HttpParams();
    if (status) {
      params = params.set('status', status);
    }
    return this.http.get<Enrollment[]>(
      `${this.apiUrl}/enrollments/my-enrollments`,
      { params }
    );
  }

  /**
   * Check if user is enrolled in a specific course
   */
  checkEnrollment(courseId: number): Observable<EnrollmentCheck> {
    return this.http.get<EnrollmentCheck>(
      `${this.apiUrl}/enrollments/check/${courseId}`
    );
  }

  /**
   * Get all enrollments for a course (creator only)
   */
  getCourseEnrollments(courseId: number): Observable<Enrollment[]> {
    return this.http.get<Enrollment[]>(
      `${this.apiUrl}/enrollments/course/${courseId}`
    );
  }

  /**
   * Update enrollment progress
   */
  updateEnrollmentProgress(enrollmentId: number): Observable<any> {
    return this.http.put(
      `${this.apiUrl}/enrollments/${enrollmentId}/update-progress`,
      {}
    );
  }

  /**
   * Check enrollment status for multiple courses at once (batch operation)
   */
  checkEnrollmentsBatch(courseIds: number[]): Observable<{ [courseId: string]: EnrollmentCheck }> {
    return this.http.post<{ [courseId: string]: EnrollmentCheck }>(
      `${this.apiUrl}/enrollments/check-batch`,
      courseIds
    );
  }
}
