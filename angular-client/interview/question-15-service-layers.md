# Question 15: Explain the purpose of your various service layers (auth, course, content, chapter). How do they interact?

## Answer

### Service Architecture Overview

CourseWagon follows a layered service architecture where each service has a specific responsibility. Services interact through dependency injection and shared observables.

### 1. Service Layer Categories

```typescript
// 1. Authentication Services
- AuthService          // JWT token management, login/logout
- FirebaseAuthService  // Firebase/Google authentication
- AuthInterceptor      // HTTP request authentication

// 2. Data Services (Domain-specific)
- CourseService        // Course CRUD operations
- SubjectService       // Subject management
- ChapterService       // Chapter operations
- TopicService         // Topic management
- ContentService       // Content generation/retrieval

// 3. Feature Services
- AdminService         // Admin-specific operations
- TestimonialService   // Reviews and testimonials

// 4. Utility Services
- NavigationService    // Navigation helpers
- MathRendererService  // Mathematical content rendering
- MermaidService       // Diagram rendering
```

### 2. Core Service Interactions

#### Authentication Flow:
```typescript
// auth.service.ts - Central authentication
@Injectable({ providedIn: 'root' })
export class AuthService {
  currentUser$ = new BehaviorSubject<User>(null);
  
  constructor(
    private http: HttpClient,
    private firebaseAuth: FirebaseAuthService  // Depends on Firebase service
  ) {}
  
  login(email: string, password: string): Observable<any> {
    return this.http.post('/api/auth/login', { email, password })
      .pipe(tap(response => {
        this.storeToken(response.token);
        this.currentUser$.next(response.user);
      }));
  }
}

// course.service.ts - Uses auth for API calls
@Injectable({ providedIn: 'root' })
export class CourseService {
  constructor(
    private http: HttpClient,
    private authService: AuthService  // Depends on auth
  ) {}
  
  getMyCourses(): Observable<Course[]> {
    // AuthInterceptor automatically adds token
    return this.http.get<Course[]>('/api/courses/my-courses');
  }
  
  enrollInCourse(courseId: number): Observable<any> {
    const user = this.authService.getCurrentUser();
    if (!user) {
      throw new Error('User must be logged in to enroll');
    }
    
    return this.http.post(`/api/courses/${courseId}/enroll`, {
      user_id: user.id
    });
  }
}
```

### 3. Hierarchical Data Services

```typescript
// Services follow the data hierarchy:
// Course → Subject → Chapter → Topic → Content

// course.service.ts
@Injectable({ providedIn: 'root' })
export class CourseService {
  private apiUrl = `${environment.apiUrl}/courses`;
  
  constructor(
    private http: HttpClient,
    private subjectService: SubjectService  // Can trigger subject updates
  ) {}
  
  getCourse(courseId: number): Observable<Course> {
    return this.http.get<Course>(`${this.apiUrl}/${courseId}`);
  }
  
  createCourse(courseData: any): Observable<Course> {
    return this.http.post<Course>(this.apiUrl, courseData).pipe(
      tap(course => {
        // Notify subject service about new course
        this.subjectService.setCourseContext(course.id);
      })
    );
  }
}

// subject.service.ts
@Injectable({ providedIn: 'root' })
export class SubjectService {
  private apiUrl = `${environment.apiUrl}/subjects`;
  private currentCourseId: number;
  
  constructor(
    private http: HttpClient,
    private chapterService: ChapterService  // Can trigger chapter updates
  ) {}
  
  setCourseContext(courseId: number): void {
    this.currentCourseId = courseId;
  }
  
  getSubjectsForCourse(courseId: number): Observable<Subject[]> {
    return this.http.get<Subject[]>(`/api/courses/${courseId}/subjects`);
  }
  
  createSubject(subjectData: any): Observable<Subject> {
    return this.http.post<Subject>(
      `/api/courses/${this.currentCourseId}/subjects`, 
      subjectData
    ).pipe(
      tap(subject => {
        // Notify chapter service about new subject
        this.chapterService.setSubjectContext(subject.id);
      })
    );
  }
}

// chapter.service.ts
@Injectable({ providedIn: 'root' })
export class ChapterService {
  private currentSubjectId: number;
  
  constructor(
    private http: HttpClient,
    private topicService: TopicService  // Can trigger topic updates
  ) {}
  
  setSubjectContext(subjectId: number): void {
    this.currentSubjectId = subjectId;
  }
  
  getChaptersForSubject(subjectId: number): Observable<Chapter[]> {
    return this.http.get<Chapter[]>(`/api/subjects/${subjectId}/chapters`);
  }
}

// Similar pattern continues for TopicService and ContentService
```

### 4. Cross-Service Communication

```typescript
// admin.service.ts - Orchestrates multiple services
@Injectable({ providedIn: 'root' })
export class AdminService {
  constructor(
    private http: HttpClient,
    private authService: AuthService,
    private courseService: CourseService,
    private testimonialService: TestimonialService
  ) {}
  
  getDashboardData(): Observable<DashboardData> {
    // Combine data from multiple services
    return forkJoin({
      user: this.authService.currentUser$,
      totalCourses: this.courseService.getCourseCount(),
      pendingTestimonials: this.testimonialService.getPendingCount(),
      stats: this.http.get<Stats>('/api/admin/stats')
    }).pipe(
      map(data => ({
        currentUser: data.user,
        courseCount: data.totalCourses,
        pendingReviews: data.pendingTestimonials,
        statistics: data.stats
      }))
    );
  }
  
  approveCourse(courseId: number): Observable<any> {
    return this.http.post(`/api/admin/courses/${courseId}/approve`, {}).pipe(
      tap(() => {
        // Notify course service to refresh
        this.courseService.refreshCourses();
      })
    );
  }
}
```

### 5. Content Generation Service Chain

```typescript
// content.service.ts - Complex service interactions
@Injectable({ providedIn: 'root' })
export class ContentService {
  constructor(
    private http: HttpClient,
    private mathRenderer: MathRendererService,
    private mermaidService: MermaidService
  ) {}
  
  generateContent(topicId: number, prompt: string): Observable<Content> {
    // 1. Call AI API to generate content
    return this.http.post<RawContent>(`/api/content/generate`, {
      topic_id: topicId,
      prompt: prompt
    }).pipe(
      // 2. Process mathematical content
      switchMap(rawContent => {
        return from(this.mathRenderer.processContent(rawContent.text)).pipe(
          map(processedMath => ({
            ...rawContent,
            text: processedMath
          }))
        );
      }),
      // 3. Process diagrams
      switchMap(content => {
        return from(this.mermaidService.processDiagrams(content.text)).pipe(
          map(processedContent => ({
            ...content,
            text: processedContent
          }))
        );
      }),
      // 4. Save processed content
      switchMap(processedContent => {
        return this.saveContent(topicId, processedContent);
      })
    );
  }
  
  private saveContent(topicId: number, content: any): Observable<Content> {
    return this.http.post<Content>(`/api/topics/${topicId}/content`, content);
  }
}
```

### 6. Service State Management

```typescript
// course.service.ts - Managing shared state
@Injectable({ providedIn: 'root' })
export class CourseService {
  // Private state
  private coursesSource = new BehaviorSubject<Course[]>([]);
  private selectedCourseSource = new BehaviorSubject<Course | null>(null);
  private loadingSource = new BehaviorSubject<boolean>(false);
  
  // Public observables
  courses$ = this.coursesSource.asObservable();
  selectedCourse$ = this.selectedCourseSource.asObservable();
  loading$ = this.loadingSource.asObservable();
  
  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {
    // React to auth changes
    this.authService.isLoggedIn$.subscribe(isLoggedIn => {
      if (isLoggedIn) {
        this.loadUserCourses();
      } else {
        this.clearCourses();
      }
    });
  }
  
  private loadUserCourses(): void {
    this.loadingSource.next(true);
    
    this.http.get<Course[]>('/api/courses/my-courses').subscribe({
      next: courses => {
        this.coursesSource.next(courses);
        this.loadingSource.next(false);
      },
      error: error => {
        console.error('Failed to load courses:', error);
        this.loadingSource.next(false);
      }
    });
  }
  
  selectCourse(courseId: number): void {
    const course = this.coursesSource.value.find(c => c.id === courseId);
    this.selectedCourseSource.next(course || null);
  }
  
  private clearCourses(): void {
    this.coursesSource.next([]);
    this.selectedCourseSource.next(null);
  }
}
```

### 7. Service Dependency Graph

```
                    AuthService
                    /    |    \
                   /     |     \
           CourseService |  AdminService
                /        |        \
        SubjectService   |    TestimonialService
              /          |
      ChapterService     |
            /            |
     TopicService   FirebaseAuthService
          /
   ContentService
       /    \
MathRenderer MermaidService
```

### 8. Error Handling Across Services

```typescript
// Base service with common error handling
export abstract class BaseService {
  protected handleError(operation = 'operation'): (error: any) => Observable<never> {
    return (error: any): Observable<never> => {
      console.error(`${operation} failed:`, error);
      
      // Send to logging service
      this.logError(error, operation);
      
      // User-friendly error message
      const message = error.error?.message || 'An error occurred';
      
      // Re-throw for component to handle
      return throwError(() => ({
        message,
        status: error.status,
        operation
      }));
    };
  }
  
  protected logError(error: any, operation: string): void {
    // Send to logging service
  }
}

// Services extend base for consistent error handling
@Injectable({ providedIn: 'root' })
export class CourseService extends BaseService {
  getCourses(): Observable<Course[]> {
    return this.http.get<Course[]>('/api/courses').pipe(
      catchError(this.handleError('getCourses'))
    );
  }
}
```

### 9. Service Testing Strategy

```typescript
// Testing service interactions
describe('CourseService', () => {
  let courseService: CourseService;
  let authService: jasmine.SpyObj<AuthService>;
  let httpMock: HttpTestingController;
  
  beforeEach(() => {
    const authSpy = jasmine.createSpyObj('AuthService', ['getCurrentUser']);
    
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        CourseService,
        { provide: AuthService, useValue: authSpy }
      ]
    });
    
    courseService = TestBed.inject(CourseService);
    authService = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    httpMock = TestBed.inject(HttpTestingController);
  });
  
  it('should interact with auth service for enrollment', () => {
    const mockUser = { id: 1, email: 'test@example.com' };
    authService.getCurrentUser.and.returnValue(mockUser);
    
    courseService.enrollInCourse(123).subscribe();
    
    const req = httpMock.expectOne('/api/courses/123/enroll');
    expect(req.request.body).toEqual({ user_id: 1 });
    expect(authService.getCurrentUser).toHaveBeenCalled();
  });
});
```

### 10. Service Best Practices in CourseWagon

```typescript
// 1. Single Responsibility
// Each service has one clear purpose
@Injectable({ providedIn: 'root' })
export class TopicService {
  // ONLY handles topic-related operations
}

// 2. Dependency Direction
// Lower-level services don't depend on higher-level ones
// ✅ CourseService → SubjectService
// ❌ SubjectService → CourseService (avoid circular)

// 3. Observable Patterns
// Use observables for reactive data
courses$ = this.coursesSource.asObservable();

// 4. Error Handling
// Consistent error handling across services
catchError(this.handleError('operation'))

// 5. State Management
// BehaviorSubjects for state that needs to be shared
private stateSource = new BehaviorSubject(initialState);
state$ = this.stateSource.asObservable();

// 6. API Abstraction
// Services abstract API complexity from components
getCourses() // Component doesn't know about HTTP
```

### Interview Talking Points

1. **Separation of Concerns**: Each service has specific responsibility
2. **Dependency Hierarchy**: Clear direction of dependencies
3. **State Management**: BehaviorSubjects for reactive state
4. **Service Composition**: Complex operations use multiple services
5. **Error Handling**: Consistent pattern across all services
6. **Testing Strategy**: Mock dependencies for isolation
7. **Observable Patterns**: Reactive programming throughout