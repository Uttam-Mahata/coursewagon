import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject, throwError, of } from 'rxjs';
import { environment } from '../../environments/environment';
import { tap, catchError, shareReplay } from 'rxjs/operators';
import { AuthService } from './auth/auth.service';
import { CacheService } from './cache.service';

@Injectable({
  providedIn: 'root'
})
export class CourseService {
  private apiUrl = environment.courseApiUrl;
  private imageApiUrl = environment.apiBaseUrl + '/images';
  
  // Create BehaviorSubjects to cache data and notify components when it changes
  private myCoursesSubject = new BehaviorSubject<any[]>([]);
  public myCourses$ = this.myCoursesSubject.asObservable();
  
  // Track current user ID to detect user changes
  private currentUserId: number | null = null;
  
  // Observable cache for shared requests
  private courseDetailsCache = new Map<number, Observable<any>>();
  
  constructor(
    private http: HttpClient, 
    private authService: AuthService,
    private cacheService: CacheService
  ) {
    console.log('CourseService initialized with apiUrl:', this.apiUrl);
    
    // Subscribe to auth state changes to handle user switching
    this.authService.currentUser$.subscribe(user => {
      const newUserId = user?.id || null;
      
      // If user changed (or logged out/in), reset courses cache
      if (this.currentUserId !== newUserId) {
        console.log('User changed, resetting courses cache');
        this.currentUserId = newUserId;
        this.myCoursesSubject.next([]);
        
        // Clear cache when user changes
        this.cacheService.invalidate('courses:');
        this.courseDetailsCache.clear();
        
        // Only load courses if there is a logged-in user
        if (newUserId) {
          this.refreshMyCourses();
        }
      }
    });
  }
  
  // Refresh the courses cache
  refreshMyCourses() {
    // Only fetch courses if there's a logged-in user
    if (!this.authService.getCurrentUser()) {
      console.log('No logged-in user, skipping course refresh');
      this.myCoursesSubject.next([]);
      return;
    }

    this.http.get<any[]>(`${this.apiUrl}/my-courses`).subscribe({
      next: (courses) => {
        this.myCoursesSubject.next(courses);
      },
      error: (error) => {
        console.error('Error fetching courses:', error);
        // Reset the subject to empty array on error
        this.myCoursesSubject.next([]);
      }
    });
  }
  
  addCourse(name: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/add_course`, { name }).pipe(
      tap(() => {
        this.refreshMyCourses();
        // Invalidate cache
        this.cacheService.invalidate('courses:');
      })
    );
  }
  
  addCourseFromAudio(audioBlob: Blob): Observable<any> {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'course_audio.wav');
    
    return this.http.post(`${this.apiUrl}/add_course_audio`, formData).pipe(
      tap(() => this.refreshMyCourses()) // Refresh the courses after adding one
    );
  }
  
  // Get all courses (public and user's own)
  getCourses(): Observable<any> {
    return this.http.get(this.apiUrl);
  }
  
  // Get only user's courses - either from cache or fresh from backend
  getMyCourses(forceRefresh = false): Observable<any> {
    // If not logged in, return empty array
    if (!this.authService.getCurrentUser()) {
      return of([]);
    }

    if (forceRefresh || this.myCoursesSubject.value.length === 0) {
      this.refreshMyCourses();
    }
    return this.myCourses$;
  }
  
  // Get course details by ID with shareReplay for deduplication
  getCourseDetails(courseId: number, forceRefresh = false): Observable<any> {
    console.log(`Fetching course details for ID: ${courseId}`);
    
    // First try to get from in-memory cache
    const cachedCourse = this.myCoursesSubject.value.find(c => c.id === courseId);
    if (cachedCourse && !forceRefresh) {
      return of(cachedCourse);
    }
    
    // Check if we already have a pending request for this course
    if (!forceRefresh && this.courseDetailsCache.has(courseId)) {
      console.log(`Using shared request for course ${courseId}`);
      return this.courseDetailsCache.get(courseId)!;
    }
    
    // Create new request with shareReplay to prevent duplicate requests
    const headers = forceRefresh ? new HttpHeaders({ 'X-Skip-Cache': 'true' }) : undefined;
    const request$ = this.http.get(`${this.apiUrl}/${courseId}`, { headers }).pipe(
      shareReplay(1), // Share the result with multiple subscribers
      tap(() => {
        // Remove from cache after completion
        this.courseDetailsCache.delete(courseId);
      }),
      catchError(error => {
        // Remove from cache on error
        this.courseDetailsCache.delete(courseId);
        return throwError(() => error);
      })
    );
    
    // Store the observable for deduplication
    this.courseDetailsCache.set(courseId, request$);
    
    return request$;
  }
  
  // New CRUD operations
  createCourseManual(name: string, description: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/create-manual`, { name, description }).pipe(
      tap(() => {
        this.refreshMyCourses();
        this.cacheService.invalidate('courses:');
      })
    );
  }
  
  updateCourse(courseId: number, name: string, description?: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/${courseId}`, { name, description }).pipe(
      tap(() => {
        this.refreshMyCourses();
        this.cacheService.invalidate('courses:');
        this.cacheService.delete(`course:${courseId}`);
      })
    );
  }
  
  deleteCourse(courseId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${courseId}`).pipe(
      tap(() => {
        this.refreshMyCourses();
        this.cacheService.invalidate('courses:');
        this.cacheService.delete(`course:${courseId}`);
      })
    );
  }

  // Image generation endpoint
  generateCourseImage(courseId: number): Observable<any> {
    console.log(`Generating image for course ${courseId}`);
    return this.http.post(`${this.imageApiUrl}/courses/${courseId}/generate`, {}).pipe(
      tap((updatedCourse: any) => {
        console.log('Course image generated:', updatedCourse);
        
        // Check if we received a valid image URL
        if (updatedCourse && updatedCourse.image_url) {
          console.log('Updating image URL in cache:', updatedCourse.image_url);
          
          // Add a timestamp query parameter to force browser to reload the image
          const timestamp = new Date().getTime();
          const imageUrlWithTimestamp = updatedCourse.image_url.includes('?') 
            ? `${updatedCourse.image_url}&t=${timestamp}` 
            : `${updatedCourse.image_url}?t=${timestamp}`;
          
          // Update the image URL in the cache with forced timestamp
          const courses = this.myCoursesSubject.value.map(course => {
            if (course.id === courseId) {
              // Create a new object to trigger Angular change detection
              return { 
                ...course, 
                image_url: imageUrlWithTimestamp,
                isGeneratingImage: false
              };
            }
            return course;
          });
          
          // Update the subject with the new course array
          this.myCoursesSubject.next(courses);
        } else {
          console.warn('No image URL received from server');
          
          // Still need to reset isGeneratingImage flag even on error
          const courses = this.myCoursesSubject.value.map(course => {
            if (course.id === courseId) {
              return { ...course, isGeneratingImage: false };
            }
            return course;
          });
          this.myCoursesSubject.next(courses);
        }
      }),
      catchError(error => {
        console.error('Error generating course image:', error);
        
        // Reset isGeneratingImage flag on error
        const courses = this.myCoursesSubject.value.map(course => {
          if (course.id === courseId) {
            return { ...course, isGeneratingImage: false };
          }
          return course;
        });
        this.myCoursesSubject.next(courses);
        
        return throwError(() => new Error('Failed to generate image'));
      })
    );
  }
}