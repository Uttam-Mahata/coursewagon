import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface CourseDetail {
  course_id: number;
  course_name: string;
  course_description: string;
  created_at: string;
  subjects_count: number;
  chapters_count: number;
  topics_count: number;
  content_count: number;
  image_url?: string;
  is_published?: boolean;
}

export interface UserCourseStats {
  total_courses: number;
  total_subjects: number;
  total_chapters: number;
  total_topics: number;
  total_content: number;
  courses_with_details: CourseDetail[];
}

@Injectable({
  providedIn: 'root'
})
export class CourseStatsService {
  private apiUrl = `${environment.apiUrl}/courses`;

  constructor(private http: HttpClient) { }

  /**
   * Get current user's course statistics
   */
  getMyCourseStatistics(): Observable<UserCourseStats> {
    return this.http.get<UserCourseStats>(`${this.apiUrl}/my-courses/statistics`);
  }
}
