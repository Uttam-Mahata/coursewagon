import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { environment } from '../../environments/environment';
import { tap, catchError } from 'rxjs/operators';
import { CourseService } from './course.service';

@Injectable({
  providedIn: 'root'
})
export class SubjectService {
  private apiUrl = environment.courseApiUrl;
  private imageApiUrl = environment.apiBaseUrl + '/images';
  
  constructor(
    private http: HttpClient,
    private courseService: CourseService
  ) { }
  
  generateSubjects(courseId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/${courseId}/generate_subjects`, {}).pipe(
      tap(() => {
        // Update the course in cache to show it now has subjects
        const courses = this.courseService['myCoursesSubject'].value;
        const course = courses.find(c => c.id === courseId);
        if (course) {
          course.has_subjects = true;
          this.courseService['myCoursesSubject'].next([...courses]); // Trigger update with a new array reference
        }
      })
    );
  }
  
  getSubjects(courseId: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/${courseId}/subjects`);
  }
  
  // Get subject details by ID
  getSubjectDetails(courseId: number, subjectId: number): Observable<any> {
    console.log(`Fetching subject details for course: ${courseId}, subject: ${subjectId}`);
    return this.http.get(`${this.apiUrl}/${courseId}/subjects/${subjectId}`);
  }
  
  // CRUD operations
  createSubject(courseId: number, name: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/${courseId}/subjects`, { name });
  }
  
  updateSubject(courseId: number, subjectId: number, name: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/${courseId}/subjects/${subjectId}`, { name });
  }
  
  deleteSubject(courseId: number, subjectId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${courseId}/subjects/${subjectId}`);
  }
  
  // Image generation endpoints
  generateSubjectImage(courseId: number, subjectId: number): Observable<any> {
    return this.http.post(
      `${this.imageApiUrl}/courses/${courseId}/subjects/${subjectId}/generate`, 
      {}
    ).pipe(
      tap(updatedSubject => {
        console.log('Subject image updated:', updatedSubject);
      }),
      catchError(error => {
        console.error('Error generating subject image:', error);
        return throwError(() => error);
      })
    );
  }

  generateAllSubjectImages(courseId: number): Observable<any> {
    return this.http.post(
      `${this.imageApiUrl}/courses/${courseId}/subjects/generate-all`,
      {}
    ).pipe(
      tap(response => {
        console.log('All subject images generated:', response);
      }),
      catchError(error => {
        console.error('Error generating all subject images:', error);
        return throwError(() => error);
      })
    );
  }
}
