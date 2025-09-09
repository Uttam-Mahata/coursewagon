# Solutions for Questions 16-29: RxJS, State Management & TypeScript

## RxJS & Reactive Programming

### 16. What's the difference between `Subject`, `BehaviorSubject`, and `ReplaySubject`? Where have you used each?

**Answer:**

These are all types of Subjects in RxJS that act as both Observable and Observer, but with different behaviors:

**Subject:**
- Basic multicasting observable
- No initial value
- Late subscribers don't receive previously emitted values
- Emits only to current subscribers

```typescript
// Example from a notification service
export class NotificationService {
  private notificationSubject = new Subject<Notification>();
  public notifications$ = this.notificationSubject.asObservable();

  showNotification(message: string, type: 'success' | 'error') {
    this.notificationSubject.next({ message, type, timestamp: Date.now() });
  }
}
```

**BehaviorSubject:**
- Requires an initial value
- Stores and emits the last emitted value to new subscribers
- Perfect for state management
- Always has a value available via `.value` property

```typescript
// Example from AuthService - storing current user state
export class AuthService {
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor() {
    // Initialize with stored user if exists
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      this.currentUserSubject.next(JSON.parse(storedUser));
    }
  }

  login(credentials: LoginCredentials) {
    return this.http.post<User>('/api/auth/login', credentials)
      .pipe(
        tap(user => {
          this.currentUserSubject.next(user);
          localStorage.setItem('user', JSON.stringify(user));
        })
      );
  }

  get currentUserValue(): User | null {
    return this.currentUserSubject.value;
  }
}
```

**ReplaySubject:**
- Can replay a specified number of previous emissions to new subscribers
- Useful for caching or event sourcing
- Can specify buffer size and time window

```typescript
// Example: Caching recent search history
export class SearchService {
  // Replay last 5 searches to new subscribers
  private searchHistorySubject = new ReplaySubject<string>(5);
  public searchHistory$ = this.searchHistorySubject.asObservable();

  // Replay all events within last 10 seconds
  private recentActivitySubject = new ReplaySubject<Activity>(
    Number.POSITIVE_INFINITY, 
    10000 // 10 second window
  );

  performSearch(query: string) {
    this.searchHistorySubject.next(query);
    return this.http.get(`/api/search?q=${query}`);
  }
}
```

**Usage in CourseWagon:**
- **Subject**: Used for one-time events like notifications, alerts, modal triggers
- **BehaviorSubject**: Used for application state (user auth, selected course, theme preference)
- **ReplaySubject**: Used for activity logs, recent views, search history

---

### 17. Explain common RxJS operators you've used: `map`, `filter`, `switchMap`, `mergeMap`, `catchError`, `tap`

**Answer:**

**map** - Transforms emitted values:
```typescript
// Transform API response to domain model
getCourses(): Observable<Course[]> {
  return this.http.get<ApiCourseResponse[]>('/api/courses')
    .pipe(
      map(apiCourses => apiCourses.map(course => ({
        ...course,
        thumbnailUrl: this.buildImageUrl(course.thumbnail),
        enrollmentCount: course.students?.length || 0
      })))
    );
}
```

**filter** - Only emit values that pass a condition:
```typescript
// Only process authenticated users
this.authService.currentUser$
  .pipe(
    filter(user => user !== null && user.isVerified),
    tap(user => console.log('Verified user:', user))
  )
  .subscribe(user => this.loadUserData(user));
```

**switchMap** - Cancel previous inner observable and switch to new one:
```typescript
// Search with debounce - cancels previous search requests
searchCourses(searchTerm$: Observable<string>): Observable<Course[]> {
  return searchTerm$.pipe(
    debounceTime(300),
    distinctUntilChanged(),
    switchMap(term => {
      if (!term.trim()) {
        return of([]);
      }
      return this.http.get<Course[]>(`/api/courses/search?q=${term}`);
    })
  );
}

// Route params example - cancel previous data load
ngOnInit() {
  this.route.params.pipe(
    switchMap(params => this.courseService.getCourse(params['id']))
  ).subscribe(course => this.course = course);
}
```

**mergeMap** - Handle multiple concurrent observables without cancellation:
```typescript
// Upload multiple files concurrently
uploadFiles(files: File[]): Observable<UploadResult[]> {
  return from(files).pipe(
    mergeMap(file => this.uploadSingleFile(file), 3), // Max 3 concurrent uploads
    toArray()
  );
}

// Process multiple API calls in parallel
enrollInMultipleCourses(courseIds: string[]): Observable<Enrollment[]> {
  return from(courseIds).pipe(
    mergeMap(id => this.enrollInCourse(id)),
    toArray()
  );
}
```

**catchError** - Handle errors gracefully:
```typescript
// Error handling with fallback
getCourseWithFallback(id: string): Observable<Course> {
  return this.http.get<Course>(`/api/courses/${id}`).pipe(
    catchError(error => {
      console.error('Failed to load course:', error);
      
      if (error.status === 404) {
        this.router.navigate(['/courses']);
        return EMPTY;
      }
      
      // Return cached version if available
      const cached = this.getCachedCourse(id);
      if (cached) {
        return of(cached);
      }
      
      // Re-throw for global error handler
      return throwError(() => error);
    })
  );
}
```

**tap** - Side effects without modifying the stream:
```typescript
// Logging, caching, and analytics
saveCourse(course: Course): Observable<Course> {
  return this.http.post<Course>('/api/courses', course).pipe(
    tap(savedCourse => {
      console.log('Course saved:', savedCourse);
      this.cache.set(savedCourse.id, savedCourse);
      this.analytics.track('course_created', { courseId: savedCourse.id });
    }),
    tap(() => this.notificationService.show('Course saved successfully')),
    catchError(error => {
      this.notificationService.show('Failed to save course', 'error');
      return throwError(() => error);
    })
  );
}
```

---

### 18. How do you handle error handling in HTTP requests using RxJS?

**Answer:**

**Comprehensive error handling strategy:**

```typescript
// 1. Service-level error handling with retry logic
export class ApiService {
  private handleError<T>(operation = 'operation', fallback?: T) {
    return (error: HttpErrorResponse): Observable<T> => {
      // Log to console for development
      console.error(`${operation} failed:`, error);
      
      // Send to logging service
      this.logger.logError(error);
      
      // User-facing error message
      let message = 'An unexpected error occurred';
      
      if (error.error instanceof ErrorEvent) {
        // Client-side error
        message = `Client error: ${error.error.message}`;
      } else {
        // Server-side error
        switch (error.status) {
          case 400:
            message = error.error?.message || 'Invalid request';
            break;
          case 401:
            message = 'Please login to continue';
            this.authService.logout();
            this.router.navigate(['/login']);
            break;
          case 403:
            message = 'You do not have permission to perform this action';
            break;
          case 404:
            message = 'Resource not found';
            break;
          case 422:
            message = error.error?.errors ? 
              Object.values(error.error.errors).join(', ') : 
              'Validation failed';
            break;
          case 500:
            message = 'Server error. Please try again later';
            break;
          case 503:
            message = 'Service temporarily unavailable';
            break;
          default:
            message = `Server error: ${error.status}`;
        }
      }
      
      this.notificationService.showError(message);
      
      // Return fallback value or re-throw
      if (fallback !== undefined) {
        return of(fallback);
      }
      
      return throwError(() => ({
        message,
        status: error.status,
        details: error.error
      }));
    };
  }

  // 2. Retry strategy for transient failures
  getCourseWithRetry(id: string): Observable<Course> {
    return this.http.get<Course>(`/api/courses/${id}`).pipe(
      retry({
        count: 3,
        delay: (error, retryCount) => {
          if (error.status === 404 || error.status === 401) {
            // Don't retry on these errors
            return throwError(() => error);
          }
          
          // Exponential backoff: 1s, 2s, 4s
          const delay = Math.pow(2, retryCount - 1) * 1000;
          console.log(`Retry attempt ${retryCount} after ${delay}ms`);
          return timer(delay);
        }
      }),
      catchError(this.handleError<Course>('getCourse'))
    );
  }

  // 3. Global HTTP interceptor for error handling
}

@Injectable()
export class ErrorInterceptor implements HttpInterceptor {
  constructor(
    private notificationService: NotificationService,
    private authService: AuthService,
    private router: Router
  ) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(req).pipe(
      catchError((error: HttpErrorResponse) => {
        // Handle token expiration
        if (error.status === 401) {
          if (this.authService.isRefreshTokenValid()) {
            // Try to refresh token
            return this.authService.refreshToken().pipe(
              switchMap(() => {
                // Retry original request with new token
                const cloned = req.clone({
                  setHeaders: {
                    Authorization: `Bearer ${this.authService.getAccessToken()}`
                  }
                });
                return next.handle(cloned);
              }),
              catchError(refreshError => {
                this.authService.logout();
                this.router.navigate(['/login']);
                return throwError(() => refreshError);
              })
            );
          } else {
            this.authService.logout();
            this.router.navigate(['/login']);
          }
        }

        // Handle offline errors
        if (!navigator.onLine) {
          this.notificationService.showError('No internet connection');
          return throwError(() => ({ 
            message: 'No internet connection',
            offline: true 
          }));
        }

        return throwError(() => error);
      })
    );
  }
}

// 4. Component-level error handling
export class CourseDetailComponent implements OnInit {
  course$: Observable<Course>;
  error$ = new Subject<string>();
  loading = true;

  ngOnInit() {
    const courseId = this.route.snapshot.params['id'];
    
    this.course$ = this.courseService.getCourse(courseId).pipe(
      tap(() => this.loading = false),
      catchError(error => {
        this.loading = false;
        this.error$.next(error.message);
        return EMPTY;
      }),
      // Share to prevent multiple subscriptions
      shareReplay(1)
    );
  }

  retry() {
    this.error$.next('');
    this.loading = true;
    // Re-fetch the course
    this.ngOnInit();
  }
}
```

---

### 19. What's the difference between `subscribe()` and `async` pipe? When do you use each?

**Answer:**

**Async Pipe:**
- Automatically subscribes and unsubscribes
- Handles change detection
- Cleaner template code
- Prevents memory leaks
- Best for template-bound observables

```typescript
// Component using async pipe
export class CourseListComponent {
  courses$: Observable<Course[]>;
  loading$ = new BehaviorSubject<boolean>(true);
  
  constructor(private courseService: CourseService) {
    this.courses$ = this.courseService.getCourses().pipe(
      tap(() => this.loading$.next(false)),
      shareReplay(1) // Cache for multiple async pipes
    );
  }
}
```

```html
<!-- Template with async pipe -->
<div class="course-list">
  <div *ngIf="loading$ | async" class="spinner">Loading...</div>
  
  <div *ngFor="let course of courses$ | async" class="course-card">
    <h3>{{ course.title }}</h3>
    <p>{{ course.description }}</p>
  </div>
  
  <!-- Multiple subscriptions to same observable -->
  <div class="course-count">
    Total courses: {{ (courses$ | async)?.length || 0 }}
  </div>
</div>
```

**Manual subscribe():**
- More control over subscription timing
- Can perform side effects
- Access to subscription object
- Required for non-template operations
- Must manually unsubscribe

```typescript
export class CourseEditComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();
  course: Course;
  autoSaveSubscription: Subscription;
  
  ngOnInit() {
    // 1. When you need the actual data in component
    this.courseService.getCourse(this.courseId)
      .pipe(takeUntil(this.destroy$))
      .subscribe(course => {
        this.course = course;
        this.initializeForm(course);
        this.setupAutoSave();
      });
    
    // 2. For side effects without template binding
    this.form.valueChanges
      .pipe(
        debounceTime(1000),
        distinctUntilChanged(),
        takeUntil(this.destroy$)
      )
      .subscribe(values => {
        this.saveToLocalStorage(values);
        this.updatePreview(values);
      });
    
    // 3. When you need fine control over subscription
    this.autoSaveSubscription = interval(30000)
      .pipe(
        switchMap(() => this.saveCourseDraft()),
        takeUntil(this.destroy$)
      )
      .subscribe({
        next: () => console.log('Auto-saved'),
        error: (err) => {
          console.error('Auto-save failed:', err);
          this.autoSaveSubscription.unsubscribe();
          this.showRetryDialog();
        }
      });
    
    // 4. For imperative operations
    this.deleteButton.clicks
      .pipe(
        switchMap(() => this.showConfirmDialog()),
        filter(confirmed => confirmed),
        switchMap(() => this.courseService.deleteCourse(this.courseId)),
        takeUntil(this.destroy$)
      )
      .subscribe(() => {
        this.router.navigate(['/courses']);
        this.notificationService.show('Course deleted');
      });
  }
  
  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
```

**Best Practices:**
- Use **async pipe** when:
  - Displaying data in templates
  - Observable is used only in template
  - Want automatic subscription management
  
- Use **subscribe()** when:
  - Need data for calculations/logic in component
  - Performing side effects
  - Need subscription control (pause/resume)
  - Chaining multiple operations imperatively

---

### 20. How do you prevent memory leaks with subscriptions? Show your unsubscribe patterns.

**Answer:**

**Pattern 1: takeUntil with destroy$ Subject**
```typescript
export class CourseComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();
  
  ngOnInit() {
    // All subscriptions use takeUntil
    this.courseService.courses$
      .pipe(takeUntil(this.destroy$))
      .subscribe(courses => this.courses = courses);
    
    this.authService.user$
      .pipe(takeUntil(this.destroy$))
      .subscribe(user => this.user = user);
    
    // Even for combined observables
    combineLatest([
      this.route.params,
      this.route.queryParams
    ]).pipe(
      takeUntil(this.destroy$),
      switchMap(([params, query]) => 
        this.loadData(params['id'], query['filter'])
      )
    ).subscribe(data => this.processData(data));
  }
  
  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
```

**Pattern 2: Subscription management**
```typescript
export class DashboardComponent implements OnInit, OnDestroy {
  private subscriptions = new Subscription();
  
  ngOnInit() {
    // Add multiple subscriptions to parent
    this.subscriptions.add(
      this.dataService.getData()
        .subscribe(data => this.data = data)
    );
    
    this.subscriptions.add(
      interval(5000)
        .pipe(switchMap(() => this.refreshData()))
        .subscribe()
    );
    
    // Can add subscription later
    const sub = this.websocket.messages$
      .subscribe(msg => this.handleMessage(msg));
    this.subscriptions.add(sub);
  }
  
  ngOnDestroy() {
    this.subscriptions.unsubscribe();
  }
}
```

**Pattern 3: Async pipe (no manual unsubscribe needed)**
```typescript
export class ProfileComponent {
  user$ = this.authService.currentUser$;
  courses$ = this.courseService.getUserCourses();
  
  // Derived observables
  stats$ = this.courses$.pipe(
    map(courses => ({
      total: courses.length,
      completed: courses.filter(c => c.completed).length,
      inProgress: courses.filter(c => !c.completed).length
    }))
  );
}
```

```html
<div *ngIf="user$ | async as user">
  <h2>{{ user.name }}</h2>
  <div *ngIf="stats$ | async as stats">
    <p>Completed: {{ stats.completed }}/{{ stats.total }}</p>
  </div>
</div>
```

**Pattern 4: Take operators for limited subscriptions**
```typescript
export class LoginComponent {
  login(credentials: LoginCredentials) {
    this.authService.login(credentials)
      .pipe(
        take(1), // Auto-completes after first emission
        finalize(() => this.loading = false)
      )
      .subscribe({
        next: (user) => this.router.navigate(['/dashboard']),
        error: (error) => this.showError(error.message)
      });
  }
  
  // For specific number of values
  getRecentNotifications() {
    this.notificationService.notifications$
      .pipe(take(5)) // Get only 5 notifications
      .subscribe(notification => this.displayNotification(notification));
  }
}
```

**Pattern 5: Custom decorator for auto-unsubscribe**
```typescript
// Custom decorator
export function AutoUnsubscribe(blacklist: string[] = []) {
  return function(constructor: any) {
    const original = constructor.prototype.ngOnDestroy;
    
    constructor.prototype.ngOnDestroy = function() {
      for (const prop in this) {
        const property = this[prop];
        if (!blacklist.includes(prop) && property && property.unsubscribe) {
          property.unsubscribe();
        }
      }
      
      if (original && typeof original === 'function') {
        original.apply(this, arguments);
      }
    };
  };
}

// Usage
@Component({ selector: 'app-settings' })
@AutoUnsubscribe(['keepThisSubscription'])
export class SettingsComponent implements OnInit {
  subscription1: Subscription;
  subscription2: Subscription;
  keepThisSubscription: Subscription; // Won't be auto-unsubscribed
  
  ngOnInit() {
    this.subscription1 = this.service1.data$.subscribe();
    this.subscription2 = this.service2.data$.subscribe();
  }
  // No need for ngOnDestroy - decorator handles it
}
```

---

### 21. Explain how you handle race conditions with `switchMap` vs `mergeMap` in search functionality.

**Answer:**

**Race Condition Problem:**
When users type quickly, multiple API calls are triggered. Without proper handling, responses can arrive out of order.

**switchMap Solution (Preferred for search):**
```typescript
export class SearchComponent implements OnInit {
  searchControl = new FormControl('');
  searchResults$: Observable<SearchResult[]>;
  loading$ = new BehaviorSubject<boolean>(false);
  
  ngOnInit() {
    // switchMap cancels previous requests - prevents race conditions
    this.searchResults$ = this.searchControl.valueChanges.pipe(
      debounceTime(300), // Wait for user to stop typing
      distinctUntilChanged(), // Only if value changed
      tap(() => this.loading$.next(true)),
      switchMap(searchTerm => {
        if (!searchTerm?.trim()) {
          this.loading$.next(false);
          return of([]);
        }
        
        // This cancels any in-flight request when new search starts
        return this.searchService.search(searchTerm).pipe(
          // Handle errors for this specific search
          catchError(error => {
            console.error('Search failed:', error);
            this.loading$.next(false);
            return of([]);
          })
        );
      }),
      tap(() => this.loading$.next(false)),
      shareReplay(1) // Cache latest result
    );
  }
}

// Visual example of switchMap behavior:
// User types: "ang" -> waits 300ms -> API call 1
// User types: "angular" -> waits 300ms -> CANCELS API call 1 -> API call 2
// API call 2 returns -> Display results for "angular"
```

**mergeMap Problem (Race condition example):**
```typescript
// DON'T DO THIS for search - causes race conditions
export class BadSearchComponent {
  ngOnInit() {
    this.searchResults$ = this.searchControl.valueChanges.pipe(
      debounceTime(300),
      distinctUntilChanged(),
      mergeMap(searchTerm => {
        // ALL requests continue - results can arrive out of order
        return this.searchService.search(searchTerm);
      })
    );
  }
}

// Problem scenario:
// User types: "java" -> API call 1 (slow, takes 3 seconds)
// User types: "javascript" -> API call 2 (fast, takes 500ms)
// Result: "javascript" results appear first, then "java" results OVERRIDE them!
// User sees outdated "java" results even though they searched for "javascript"
```

**Advanced Pattern - Cancellation with Loading States:**
```typescript
export class AdvancedSearchComponent {
  private searchSubject = new Subject<string>();
  private cancelSearch$ = new Subject<void>();
  
  searchResults$: Observable<SearchState>;
  
  ngOnInit() {
    this.searchResults$ = this.searchSubject.pipe(
      tap(term => console.log('Search triggered:', term)),
      debounceTime(300),
      distinctUntilChanged(),
      // Create state object with loading flag
      switchMap(searchTerm => {
        if (!searchTerm?.trim()) {
          return of({ results: [], loading: false, term: '' });
        }
        
        // Start with loading state
        return concat(
          // Emit loading state immediately
          of({ results: [], loading: true, term: searchTerm }),
          // Then perform actual search
          this.searchService.search(searchTerm).pipe(
            map(results => ({ results, loading: false, term: searchTerm })),
            catchError(error => {
              console.error('Search error:', error);
              return of({ 
                results: [], 
                loading: false, 
                error: error.message,
                term: searchTerm 
              });
            })
          )
        );
      }),
      // Cancel on component destroy
      takeUntil(this.cancelSearch$),
      // Share subscription among multiple subscribers
      shareReplay(1)
    );
  }
  
  search(term: string) {
    this.searchSubject.next(term);
  }
  
  cancelSearch() {
    this.cancelSearch$.next();
  }
  
  ngOnDestroy() {
    this.cancelSearch$.next();
    this.cancelSearch$.complete();
  }
}
```

**When to use mergeMap (Parallel operations without order dependency):**
```typescript
export class BulkOperationsComponent {
  // Good use case for mergeMap - process all uploads in parallel
  uploadMultipleFiles(files: File[]) {
    return from(files).pipe(
      mergeMap(
        file => this.uploadFile(file).pipe(
          map(result => ({ file: file.name, ...result })),
          catchError(error => of({ 
            file: file.name, 
            error: error.message 
          }))
        ),
        3 // Limit to 3 concurrent uploads
      ),
      scan((acc, curr) => [...acc, curr], [] as UploadResult[]),
      tap(results => {
        const completed = results.filter(r => !r.error).length;
        const failed = results.filter(r => r.error).length;
        console.log(`Uploaded: ${completed}, Failed: ${failed}`);
      })
    );
  }
  
  // Process independent API calls
  loadDashboardData() {
    return combineLatest([
      this.courseService.getCourses(),
      this.userService.getProfile(),
      this.statsService.getStats()
    ]).pipe(
      map(([courses, profile, stats]) => ({
        courses,
        profile,
        stats
      }))
    );
  }
}
```

**Best Practices Summary:**
- **Use switchMap for**: Search, autocomplete, route params, any operation where only latest matters
- **Use mergeMap for**: Bulk operations, parallel processing, when all results matter
- **Use exhaustMap for**: Login/submit buttons (ignore new clicks until current completes)
- **Use concatMap for**: Ordered operations where sequence matters

## State Management

### 22. How do you manage application state without using NgRx/Akita? What patterns do you follow?

**Answer:**

**Service-based State Management Pattern:**

```typescript
// 1. Core State Service Pattern
@Injectable({ providedIn: 'root' })
export class AppStateService {
  // Private state
  private readonly _user$ = new BehaviorSubject<User | null>(null);
  private readonly _courses$ = new BehaviorSubject<Course[]>([]);
  private readonly _selectedCourse$ = new BehaviorSubject<Course | null>(null);
  private readonly _loading$ = new BehaviorSubject<boolean>(false);
  private readonly _errors$ = new Subject<AppError>();
  
  // Public observables (read-only)
  readonly user$ = this._user$.asObservable();
  readonly courses$ = this._courses$.asObservable();
  readonly selectedCourse$ = this._selectedCourse$.asObservable();
  readonly loading$ = this._loading$.asObservable();
  readonly errors$ = this._errors$.asObservable();
  
  // Computed/derived state
  readonly isAuthenticated$ = this.user$.pipe(
    map(user => !!user),
    distinctUntilChanged()
  );
  
  readonly enrolledCourses$ = combineLatest([
    this.user$,
    this.courses$
  ]).pipe(
    map(([user, courses]) => 
      courses.filter(course => 
        user?.enrolledCourseIds?.includes(course.id)
      )
    )
  );
  
  readonly courseProgress$ = this.selectedCourse$.pipe(
    filter(course => !!course),
    switchMap(course => 
      this.calculateProgress(course!).pipe(
        map(progress => ({ course, progress }))
      )
    ),
    shareReplay(1)
  );
  
  // State mutations (command methods)
  setUser(user: User | null) {
    this._user$.next(user);
    if (user) {
      localStorage.setItem('user', JSON.stringify(user));
    } else {
      localStorage.removeItem('user');
    }
  }
  
  updateCourses(courses: Course[]) {
    this._courses$.next(courses);
  }
  
  selectCourse(courseId: string) {
    const course = this._courses$.value.find(c => c.id === courseId);
    this._selectedCourse$.next(course || null);
  }
  
  addError(error: AppError) {
    this._errors$.next(error);
  }
  
  setLoading(loading: boolean) {
    this._loading$.next(loading);
  }
  
  // Complex state operations
  enrollInCourse(courseId: string) {
    const user = this._user$.value;
    if (!user) return throwError(() => new Error('User not authenticated'));
    
    this.setLoading(true);
    return this.courseApi.enroll(courseId).pipe(
      tap(enrollment => {
        // Update user's enrolled courses
        const updatedUser = {
          ...user,
          enrolledCourseIds: [...(user.enrolledCourseIds || []), courseId]
        };
        this.setUser(updatedUser);
        
        // Update course enrollment count
        const courses = this._courses$.value.map(course =>
          course.id === courseId
            ? { ...course, enrollmentCount: course.enrollmentCount + 1 }
            : course
        );
        this.updateCourses(courses);
      }),
      finalize(() => this.setLoading(false)),
      catchError(error => {
        this.addError({ message: 'Enrollment failed', details: error });
        return throwError(() => error);
      })
    );
  }
  
  // State persistence
  loadPersistedState() {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      this._user$.next(JSON.parse(savedUser));
    }
    
    const savedPreferences = localStorage.getItem('preferences');
    if (savedPreferences) {
      // Load preferences
    }
  }
  
  // State reset
  resetState() {
    this._user$.next(null);
    this._courses$.next([]);
    this._selectedCourse$.next(null);
    this._loading$.next(false);
    localStorage.clear();
  }
}
```

**2. Feature-specific State Services:**
```typescript
// Modular state management
@Injectable({ providedIn: 'root' })
export class CourseStateService {
  private store = new Map<string, Course>();
  private state$ = new BehaviorSubject<CourseState>({
    courses: [],
    loading: false,
    error: null,
    filters: {
      category: null,
      level: null,
      search: ''
    },
    sort: 'newest'
  });
  
  // Selectors
  courses$ = this.state$.pipe(
    map(state => state.courses),
    distinctUntilChanged()
  );
  
  filteredCourses$ = this.state$.pipe(
    map(state => this.applyFiltersAndSort(state)),
    distinctUntilChanged()
  );
  
  loading$ = this.state$.pipe(
    map(state => state.loading),
    distinctUntilChanged()
  );
  
  // Actions
  loadCourses() {
    this.updateState({ loading: true });
    
    return this.api.getCourses().pipe(
      tap(courses => {
        courses.forEach(c => this.store.set(c.id, c));
        this.updateState({ 
          courses, 
          loading: false,
          error: null 
        });
      }),
      catchError(error => {
        this.updateState({ 
          loading: false, 
          error: error.message 
        });
        return EMPTY;
      })
    );
  }
  
  setFilter(filter: Partial<CourseFilters>) {
    const currentState = this.state$.value;
    this.updateState({
      filters: { ...currentState.filters, ...filter }
    });
  }
  
  private updateState(partial: Partial<CourseState>) {
    const currentState = this.state$.value;
    this.state$.next({ ...currentState, ...partial });
  }
  
  private applyFiltersAndSort(state: CourseState): Course[] {
    let filtered = state.courses;
    
    // Apply filters
    if (state.filters.category) {
      filtered = filtered.filter(c => c.category === state.filters.category);
    }
    if (state.filters.level) {
      filtered = filtered.filter(c => c.level === state.filters.level);
    }
    if (state.filters.search) {
      const search = state.filters.search.toLowerCase();
      filtered = filtered.filter(c => 
        c.title.toLowerCase().includes(search) ||
        c.description.toLowerCase().includes(search)
      );
    }
    
    // Apply sort
    return this.sortCourses(filtered, state.sort);
  }
}
```

**3. Facade Pattern for Complex Features:**
```typescript
@Injectable({ providedIn: 'root' })
export class CourseFacade {
  constructor(
    private courseState: CourseStateService,
    private userState: UserStateService,
    private api: CourseApiService
  ) {}
  
  // Combine multiple state services
  readonly viewModel$ = combineLatest([
    this.courseState.filteredCourses$,
    this.userState.currentUser$,
    this.courseState.loading$
  ]).pipe(
    map(([courses, user, loading]) => ({
      courses,
      user,
      loading,
      canCreateCourse: user?.role === 'instructor',
      enrolledCourseIds: user?.enrolledCourseIds || []
    }))
  );
  
  // Orchestrate complex operations
  createCourse(courseData: CourseFormData) {
    return this.api.createCourse(courseData).pipe(
      tap(course => {
        this.courseState.addCourse(course);
        this.userState.addCreatedCourse(course.id);
      })
    );
  }
}
```

---

### 23. Explain how you handle caching in your services. Do you cache API responses?

**Answer:**

**Multi-level Caching Strategy:**

```typescript
// 1. Memory Cache with TTL
@Injectable({ providedIn: 'root' })
export class CacheService {
  private cache = new Map<string, CacheEntry>();
  private readonly DEFAULT_TTL = 5 * 60 * 1000; // 5 minutes
  
  set(key: string, data: any, ttl?: number): void {
    const expiresAt = Date.now() + (ttl || this.DEFAULT_TTL);
    this.cache.set(key, { data, expiresAt });
  }
  
  get<T>(key: string): T | null {
    const entry = this.cache.get(key);
    
    if (!entry) return null;
    
    if (Date.now() > entry.expiresAt) {
      this.cache.delete(key);
      return null;
    }
    
    return entry.data as T;
  }
  
  invalidate(pattern?: string): void {
    if (!pattern) {
      this.cache.clear();
      return;
    }
    
    // Invalidate keys matching pattern
    const regex = new RegExp(pattern);
    Array.from(this.cache.keys())
      .filter(key => regex.test(key))
      .forEach(key => this.cache.delete(key));
  }
  
  // Observable-based cache
  getOrFetch<T>(
    key: string, 
    fetcher: () => Observable<T>,
    ttl?: number
  ): Observable<T> {
    const cached = this.get<T>(key);
    
    if (cached) {
      return of(cached);
    }
    
    return fetcher().pipe(
      tap(data => this.set(key, data, ttl))
    );
  }
}

// 2. HTTP Cache with shareReplay
@Injectable({ providedIn: 'root' })
export class CourseService {
  private courseCache$ = new Map<string, Observable<Course>>();
  private coursesCache$: Observable<Course[]> | null = null;
  private cacheTime = 5 * 60 * 1000; // 5 minutes
  private lastFetch = 0;
  
  getCourses(forceRefresh = false): Observable<Course[]> {
    const now = Date.now();
    
    // Check if cache is expired or force refresh
    if (
      !this.coursesCache$ || 
      forceRefresh || 
      now - this.lastFetch > this.cacheTime
    ) {
      this.coursesCache$ = this.http.get<Course[]>('/api/courses').pipe(
        tap(() => this.lastFetch = now),
        shareReplay(1) // Share and replay to late subscribers
      );
    }
    
    return this.coursesCache$;
  }
  
  getCourse(id: string, forceRefresh = false): Observable<Course> {
    if (forceRefresh || !this.courseCache$.has(id)) {
      const course$ = this.http.get<Course>(`/api/courses/${id}`).pipe(
        shareReplay(1)
      );
      this.courseCache$.set(id, course$);
    }
    
    return this.courseCache$.get(id)!;
  }
  
  updateCourse(id: string, updates: Partial<Course>): Observable<Course> {
    return this.http.patch<Course>(`/api/courses/${id}`, updates).pipe(
      tap(updatedCourse => {
        // Invalidate caches
        this.courseCache$.delete(id);
        this.coursesCache$ = null;
        
        // Optionally update cache immediately
        this.courseCache$.set(id, of(updatedCourse));
      })
    );
  }
}

// 3. LocalStorage Cache for persistent data
@Injectable({ providedIn: 'root' })
export class PersistentCacheService {
  private readonly CACHE_PREFIX = 'app_cache_';
  
  setItem(key: string, data: any, ttlMinutes?: number): void {
    const cacheKey = this.CACHE_PREFIX + key;
    const entry: LocalStorageCache = {
      data,
      timestamp: Date.now(),
      ttl: ttlMinutes ? ttlMinutes * 60 * 1000 : null
    };
    
    try {
      localStorage.setItem(cacheKey, JSON.stringify(entry));
    } catch (e) {
      // Handle quota exceeded
      this.clearOldestEntries();
      localStorage.setItem(cacheKey, JSON.stringify(entry));
    }
  }
  
  getItem<T>(key: string): T | null {
    const cacheKey = this.CACHE_PREFIX + key;
    const item = localStorage.getItem(cacheKey);
    
    if (!item) return null;
    
    try {
      const entry: LocalStorageCache = JSON.parse(item);
      
      // Check TTL
      if (entry.ttl && Date.now() - entry.timestamp > entry.ttl) {
        localStorage.removeItem(cacheKey);
        return null;
      }
      
      return entry.data as T;
    } catch {
      return null;
    }
  }
  
  private clearOldestEntries(): void {
    const cacheEntries: Array<[string, LocalStorageCache]> = [];
    
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key?.startsWith(this.CACHE_PREFIX)) {
        const value = localStorage.getItem(key);
        if (value) {
          try {
            cacheEntries.push([key, JSON.parse(value)]);
          } catch {}
        }
      }
    }
    
    // Sort by timestamp and remove oldest 25%
    cacheEntries.sort((a, b) => a[1].timestamp - b[1].timestamp);
    const toRemove = Math.ceil(cacheEntries.length * 0.25);
    
    for (let i = 0; i < toRemove; i++) {
      localStorage.removeItem(cacheEntries[i][0]);
    }
  }
}

// 4. Smart Cache with Refresh Strategy
@Injectable({ providedIn: 'root' })
export class SmartCacheService {
  constructor(
    private http: HttpClient,
    private cache: CacheService
  ) {}
  
  // Stale-while-revalidate pattern
  getWithSWR<T>(
    url: string,
    cacheKey: string,
    ttl = 60000
  ): Observable<CacheResponse<T>> {
    const cached = this.cache.get<T>(cacheKey);
    
    // Return cached data immediately if available
    if (cached) {
      // Fetch fresh data in background
      this.http.get<T>(url).pipe(
        tap(fresh => this.cache.set(cacheKey, fresh, ttl)),
        catchError(() => EMPTY)
      ).subscribe();
      
      return of({ data: cached, fromCache: true });
    }
    
    // No cache, fetch fresh
    return this.http.get<T>(url).pipe(
      tap(data => this.cache.set(cacheKey, data, ttl)),
      map(data => ({ data, fromCache: false }))
    );
  }
  
  // Cache with background refresh
  getWithBackgroundRefresh<T>(
    url: string,
    cacheKey: string,
    refreshInterval = 60000
  ): Observable<T> {
    return new Observable<T>(observer => {
      // Get initial data
      this.getInitialData<T>(url, cacheKey)
        .subscribe(data => observer.next(data));
      
      // Set up background refresh
      const refreshTimer = interval(refreshInterval).pipe(
        switchMap(() => this.http.get<T>(url)),
        tap(data => {
          this.cache.set(cacheKey, data);
          observer.next(data);
        }),
        catchError(error => {
          console.error('Background refresh failed:', error);
          return EMPTY;
        })
      ).subscribe();
      
      return () => refreshTimer.unsubscribe();
    });
  }
  
  private getInitialData<T>(url: string, cacheKey: string): Observable<T> {
    const cached = this.cache.get<T>(cacheKey);
    
    if (cached) {
      return of(cached);
    }
    
    return this.http.get<T>(url).pipe(
      tap(data => this.cache.set(cacheKey, data))
    );
  }
}
```

---

### 24. How do you share state between unrelated components?

**Answer:**

**Multiple Patterns for State Sharing:**

```typescript
// 1. Shared Service with BehaviorSubject
@Injectable({ providedIn: 'root' })
export class SharedDataService {
  // State that needs to be shared
  private selectedTheme$ = new BehaviorSubject<Theme>('light');
  private notifications$ = new BehaviorSubject<Notification[]>([]);
  private globalSearch$ = new BehaviorSubject<string>('');
  
  // Public observables
  theme$ = this.selectedTheme$.asObservable();
  notifications$ = this.notifications$.asObservable();
  search$ = this.globalSearch$.asObservable();
  
  // Update methods
  setTheme(theme: Theme) {
    this.selectedTheme$.next(theme);
    localStorage.setItem('theme', theme);
  }
  
  addNotification(notification: Notification) {
    const current = this.notifications$.value;
    this.notifications$.next([...current, notification]);
  }
  
  updateSearch(term: string) {
    this.globalSearch$.next(term);
  }
}

// Component A - Header
@Component({
  selector: 'app-header',
  template: `
    <input 
      [(ngModel)]="searchTerm" 
      (ngModelChange)="onSearchChange($event)"
      placeholder="Global search...">
    
    <button (click)="toggleTheme()">
      {{ (theme$ | async) === 'dark' ? '☀️' : '🌙' }}
    </button>
  `
})
export class HeaderComponent {
  theme$ = this.sharedData.theme$;
  searchTerm = '';
  
  constructor(private sharedData: SharedDataService) {}
  
  onSearchChange(term: string) {
    this.sharedData.updateSearch(term);
  }
  
  toggleTheme() {
    const currentTheme = this.sharedData.theme$.value;
    this.sharedData.setTheme(currentTheme === 'dark' ? 'light' : 'dark');
  }
}

// Component B - Sidebar (unrelated to header)
@Component({
  selector: 'app-sidebar',
  template: `
    <div [class.dark-theme]="(theme$ | async) === 'dark'">
      <div *ngFor="let item of searchResults$ | async">
        {{ item.title }}
      </div>
    </div>
  `
})
export class SidebarComponent implements OnInit {
  theme$ = this.sharedData.theme$;
  searchResults$: Observable<SearchResult[]>;
  
  constructor(
    private sharedData: SharedDataService,
    private searchService: SearchService
  ) {}
  
  ngOnInit() {
    // React to global search changes
    this.searchResults$ = this.sharedData.search$.pipe(
      debounceTime(300),
      distinctUntilChanged(),
      switchMap(term => 
        term ? this.searchService.search(term) : of([])
      )
    );
  }
}

// 2. Event Bus Pattern for Decoupled Communication
@Injectable({ providedIn: 'root' })
export class EventBusService {
  private eventSubject = new Subject<AppEvent>();
  events$ = this.eventSubject.asObservable();
  
  emit(event: AppEvent) {
    this.eventSubject.next(event);
  }
  
  on<T extends AppEvent>(eventType: string): Observable<T> {
    return this.events$.pipe(
      filter(event => event.type === eventType),
      map(event => event as T)
    );
  }
}

// Usage in components
@Component({ selector: 'app-course-card' })
export class CourseCardComponent {
  constructor(private eventBus: EventBusService) {}
  
  onEnroll(courseId: string) {
    this.eventBus.emit({
      type: 'COURSE_ENROLLED',
      payload: { courseId, timestamp: Date.now() }
    });
  }
}

@Component({ selector: 'app-progress-tracker' })
export class ProgressTrackerComponent implements OnInit {
  enrollmentCount = 0;
  
  constructor(private eventBus: EventBusService) {}
  
  ngOnInit() {
    this.eventBus.on<CourseEnrolledEvent>('COURSE_ENROLLED')
      .pipe(takeUntil(this.destroy$))
      .subscribe(event => {
        this.enrollmentCount++;
        this.updateProgress(event.payload.courseId);
      });
  }
}

// 3. Router State for URL-based State Sharing
@Component({ selector: 'app-filter-panel' })
export class FilterPanelComponent {
  constructor(
    private router: Router,
    private route: ActivatedRoute
  ) {}
  
  updateFilter(filter: FilterOptions) {
    // Share state via URL query params
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: {
        category: filter.category,
        level: filter.level,
        sort: filter.sort
      },
      queryParamsHandling: 'merge'
    });
  }
}

@Component({ selector: 'app-course-list' })
export class CourseListComponent implements OnInit {
  courses$: Observable<Course[]>;
  
  constructor(
    private route: ActivatedRoute,
    private courseService: CourseService
  ) {}
  
  ngOnInit() {
    // React to URL state changes
    this.courses$ = this.route.queryParams.pipe(
      switchMap(params => {
        const filters = {
          category: params['category'],
          level: params['level'],
          sort: params['sort'] || 'newest'
        };
        return this.courseService.getFilteredCourses(filters);
      })
    );
  }
}

// 4. Window/SessionStorage for Cross-Tab Communication
@Injectable({ providedIn: 'root' })
export class CrossTabService {
  private storageEvent$ = new Subject<StorageEvent>();
  
  constructor() {
    // Listen to storage events from other tabs
    window.addEventListener('storage', (event) => {
      if (event.key?.startsWith('shared_')) {
        this.storageEvent$.next(event);
      }
    });
  }
  
  broadcast(key: string, data: any) {
    const storageKey = `shared_${key}`;
    const value = JSON.stringify({ data, timestamp: Date.now() });
    
    // This triggers storage event in OTHER tabs
    localStorage.setItem(storageKey, value);
    
    // Manually emit for same tab
    this.storageEvent$.next({
      key: storageKey,
      newValue: value,
      oldValue: null,
      storageArea: localStorage,
      url: window.location.href
    } as StorageEvent);
  }
  
  listen<T>(key: string): Observable<T> {
    const storageKey = `shared_${key}`;
    
    return this.storageEvent$.pipe(
      filter(event => event.key === storageKey),
      map(event => {
        if (event.newValue) {
          const parsed = JSON.parse(event.newValue);
          return parsed.data as T;
        }
        return null;
      }),
      filter(data => data !== null)
    );
  }
}

// 5. Hierarchical Injection for Scoped Sharing
// Share state only within a feature module
@Injectable() // Note: No providedIn: 'root'
export class FeatureStateService {
  private state$ = new BehaviorSubject<FeatureState>(initialState);
  
  // State methods...
}

@Component({
  selector: 'app-feature-container',
  providers: [FeatureStateService], // Provided at component level
  template: `
    <app-feature-header></app-feature-header>
    <router-outlet></router-outlet>
    <app-feature-footer></app-feature-footer>
  `
})
export class FeatureContainerComponent {
  // All child components share the same FeatureStateService instance
}
```

---

### 25. What's your approach to handling optimistic updates in the UI?

**Answer:**

**Optimistic Update Strategy:**

```typescript
// 1. Basic Optimistic Update Pattern
@Injectable({ providedIn: 'root' })
export class OptimisticCourseService {
  private courses$ = new BehaviorSubject<Course[]>([]);
  private rollbackStack: RollbackAction[] = [];
  
  updateCourseOptimistically(
    courseId: string, 
    updates: Partial<Course>
  ): Observable<Course> {
    // 1. Store current state for rollback
    const currentCourses = this.courses$.value;
    const originalCourse = currentCourses.find(c => c.id === courseId);
    
    if (!originalCourse) {
      return throwError(() => new Error('Course not found'));
    }
    
    // 2. Apply optimistic update immediately
    const optimisticCourse = { ...originalCourse, ...updates };
    const optimisticCourses = currentCourses.map(c =>
      c.id === courseId ? optimisticCourse : c
    );
    this.courses$.next(optimisticCourses);
    
    // 3. Show immediate feedback
    this.notificationService.show('Updating course...', 'info');
    
    // 4. Make actual API call
    return this.http.patch<Course>(`/api/courses/${courseId}`, updates).pipe(
      tap(serverCourse => {
        // 5. Replace optimistic data with server response
        const finalCourses = this.courses$.value.map(c =>
          c.id === courseId ? serverCourse : c
        );
        this.courses$.next(finalCourses);
        this.notificationService.show('Course updated successfully', 'success');
      }),
      catchError(error => {
        // 6. Rollback on error
        this.courses$.next(currentCourses);
        this.notificationService.show('Update failed. Changes reverted.', 'error');
        
        return throwError(() => error);
      })
    );
  }
  
  // Advanced: Optimistic delete with undo
  deleteCourseOptimistically(courseId: string): Observable<void> {
    const currentCourses = this.courses$.value;
    const courseToDelete = currentCourses.find(c => c.id === courseId);
    
    if (!courseToDelete) {
      return throwError(() => new Error('Course not found'));
    }
    
    // Optimistically remove from UI
    const filteredCourses = currentCourses.filter(c => c.id !== courseId);
    this.courses$.next(filteredCourses);
    
    // Show undo notification
    const undoNotification = this.notificationService.showWithUndo(
      'Course deleted',
      5000, // 5 second undo window
      () => {
        // Undo action
        this.courses$.next(currentCourses);
        return of(null); // Cancel the delete
      }
    );
    
    // Delay API call to allow undo
    return timer(5000).pipe(
      switchMap(() => {
        if (undoNotification.wasUndone) {
          return EMPTY;
        }
        
        return this.http.delete<void>(`/api/courses/${courseId}`);
      }),
      catchError(error => {
        // Rollback on server error
        this.courses$.next(currentCourses);
        this.notificationService.show('Delete failed', 'error');
        return throwError(() => error);
      })
    );
  }
}

// 2. Optimistic UI with Pending States
interface OptimisticItem<T> {
  data: T;
  status: 'synced' | 'pending' | 'error';
  tempId?: string;
}

@Injectable({ providedIn: 'root' })
export class OptimisticListService {
  private items$ = new BehaviorSubject<OptimisticItem<Task>[]>([]);
  
  addTaskOptimistically(task: Omit<Task, 'id'>): Observable<Task> {
    // Generate temporary ID
    const tempId = `temp_${Date.now()}`;
    const optimisticTask: OptimisticItem<Task> = {
      data: { ...task, id: tempId } as Task,
      status: 'pending',
      tempId
    };
    
    // Add to list immediately with pending status
    const currentItems = this.items$.value;
    this.items$.next([...currentItems, optimisticTask]);
    
    // Make API call
    return this.http.post<Task>('/api/tasks', task).pipe(
      tap(serverTask => {
        // Replace temp item with server response
        const updatedItems = this.items$.value.map(item =>
          item.tempId === tempId
            ? { data: serverTask, status: 'synced' as const }
            : item
        );
        this.items$.next(updatedItems);
      }),
      catchError(error => {
        // Mark as error but keep in list
        const updatedItems = this.items$.value.map(item =>
          item.tempId === tempId
            ? { ...item, status: 'error' as const }
            : item
        );
        this.items$.next(updatedItems);
        
        return throwError(() => error);
      })
    );
  }
  
  retryFailedItem(tempId: string) {
    const item = this.items$.value.find(i => i.tempId === tempId);
    if (!item || item.status !== 'error') return;
    
    // Reset to pending
    this.updateItemStatus(tempId, 'pending');
    
    // Retry API call
    return this.http.post<Task>('/api/tasks', item.data).pipe(
      tap(serverTask => {
        const updatedItems = this.items$.value.map(i =>
          i.tempId === tempId
            ? { data: serverTask, status: 'synced' as const }
            : i
        );
        this.items$.next(updatedItems);
      }),
      catchError(error => {
        this.updateItemStatus(tempId, 'error');
        return throwError(() => error);
      })
    );
  }
  
  private updateItemStatus(tempId: string, status: 'synced' | 'pending' | 'error') {
    const updatedItems = this.items$.value.map(item =>
      item.tempId === tempId ? { ...item, status } : item
    );
    this.items$.next(updatedItems);
  }
}

// 3. Component with Optimistic UI
@Component({
  selector: 'app-task-list',
  template: `
    <div *ngFor="let item of items$ | async" 
         [class.pending]="item.status === 'pending'"
         [class.error]="item.status === 'error'">
      
      <span>{{ item.data.title }}</span>
      
      <span *ngIf="item.status === 'pending'" class="status">
        <mat-spinner diameter="16"></mat-spinner>
        Saving...
      </span>
      
      <span *ngIf="item.status === 'error'" class="status error">
        Failed
        <button (click)="retry(item.tempId)">Retry</button>
      </span>
      
      <mat-icon *ngIf="item.status === 'synced'" class="status success">
        check_circle
      </mat-icon>
    </div>
  `,
  styles: [`
    .pending { opacity: 0.7; }
    .error { background: #fee; }
    .status { margin-left: auto; }
  `]
})
export class TaskListComponent {
  items$ = this.optimisticService.items$;
  
  constructor(private optimisticService: OptimisticListService) {}
  
  retry(tempId: string) {
    this.optimisticService.retryFailedItem(tempId).subscribe();
  }
}

// 4. Conflict Resolution Strategy
@Injectable({ providedIn: 'root' })
export class ConflictResolutionService {
  handleOptimisticUpdate<T extends { version: number }>(
    optimisticData: T,
    serverUpdate: () => Observable<T>
  ): Observable<T> {
    return serverUpdate().pipe(
      catchError(error => {
        if (error.status === 409) { // Conflict
          return this.resolveConflict(optimisticData, error.error.serverData);
        }
        return throwError(() => error);
      })
    );
  }
  
  private resolveConflict<T>(localData: T, serverData: T): Observable<T> {
    // Show conflict resolution dialog
    return this.dialog.open(ConflictDialogComponent, {
      data: { localData, serverData }
    }).afterClosed().pipe(
      switchMap(resolution => {
        if (resolution === 'keepLocal') {
          return this.forceUpdate(localData);
        } else if (resolution === 'keepServer') {
          return of(serverData);
        } else {
          // Merge strategy
          return this.mergeAndUpdate(localData, serverData);
        }
      })
    );
  }
}
```

## TypeScript Deep Dive

### 26. Explain TypeScript interfaces vs types. When do you use each?

**Answer:**

**Key Differences and Use Cases:**

```typescript
// INTERFACES - Preferred for object shapes and contracts

// 1. Object shapes and API contracts
interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'instructor';
  createdAt: Date;
}

// 2. Interfaces can be extended (inheritance)
interface Student extends User {
  enrolledCourses: string[];
  completedCourses: string[];
  gpa?: number;
}

// 3. Interfaces can be implemented by classes
class StudentImpl implements Student {
  id: string;
  name: string;
  email: string;
  role: 'user' = 'user';
  createdAt: Date;
  enrolledCourses: string[] = [];
  completedCourses: string[] = [];
  
  constructor(data: Partial<Student>) {
    Object.assign(this, data);
  }
  
  calculateProgress(): number {
    return this.completedCourses.length / this.enrolledCourses.length;
  }
}

// 4. Interface declaration merging (ambient declarations)
interface Course {
  id: string;
  title: string;
}

interface Course {
  instructor: string; // Merged with above
  duration: number;   // Merged with above
}

// Now Course has all four properties

// 5. Interface for function signatures
interface SearchFunction {
  (query: string, options?: SearchOptions): Observable<SearchResult[]>;
  cache?: Map<string, SearchResult[]>;
  lastQuery?: string;
}

const search: SearchFunction = (query, options) => {
  search.lastQuery = query;
  return of([]);
};
search.cache = new Map();

// TYPE ALIASES - For unions, primitives, and complex types

// 1. Union types
type Status = 'pending' | 'approved' | 'rejected' | 'cancelled';
type Result<T> = T | Error | null;

// 2. Primitive aliases
type UserId = string;
type Timestamp = number;
type Percentage = number; // 0-100

// 3. Tuple types
type Coordinate = [number, number];
type RGBColor = [red: number, green: number, blue: number]; // Named tuples

// 4. Complex type manipulation
type ReadonlyUser = Readonly<User>;
type PartialUser = Partial<User>;
type UserKeys = keyof User;
type UserValues = User[keyof User];

// 5. Conditional types
type IsArray<T> = T extends any[] ? true : false;
type ExtractArrayType<T> = T extends (infer U)[] ? U : never;

// 6. Mapped types
type Nullable<T> = {
  [P in keyof T]: T[P] | null;
};

type Getters<T> = {
  [P in keyof T as `get${Capitalize<string & P>}`]: () => T[P];
};

// 7. Type can alias primitives (interface cannot)
type Score = number;
type Name = string;
type IsActive = boolean;

// PRACTICAL EXAMPLES FROM COURSEWAGON

// Interface for API response structure
interface ApiResponse<T> {
  data: T;
  status: number;
  message: string;
  timestamp: Date;
}

// Type for specific response variations
type CourseResponse = ApiResponse<Course>;
type ErrorResponse = ApiResponse<null> & { errors: string[] };

// Interface for service contracts
interface CourseService {
  getCourses(): Observable<Course[]>;
  getCourse(id: string): Observable<Course>;
  createCourse(course: Partial<Course>): Observable<Course>;
  updateCourse(id: string, updates: Partial<Course>): Observable<Course>;
  deleteCourse(id: string): Observable<void>;
}

// Type for complex state management
type CourseState = {
  courses: Course[];
  selectedCourse: Course | null;
  loading: boolean;
  error: string | null;
  filters: {
    category?: string;
    level?: 'beginner' | 'intermediate' | 'advanced';
    search?: string;
  };
  sort: 'newest' | 'popular' | 'price';
};

// Type for action patterns
type CourseAction = 
  | { type: 'LOAD_COURSES'; payload: Course[] }
  | { type: 'SELECT_COURSE'; payload: string }
  | { type: 'UPDATE_COURSE'; payload: { id: string; updates: Partial<Course> } }
  | { type: 'SET_FILTER'; payload: Partial<CourseState['filters']> }
  | { type: 'SET_ERROR'; payload: string };

// Interface with optional and readonly properties
interface CourseConfig {
  readonly id: string;
  title: string;
  description?: string;
  readonly createdBy: string;
  lastModified?: Date;
  settings?: {
    isPublic: boolean;
    allowEnrollment: boolean;
    maxStudents?: number;
  };
}

// WHEN TO USE EACH:

// Use INTERFACE when:
// - Defining object shapes
// - Creating contracts for classes
// - Need declaration merging
// - Working with OOP patterns
// - Defining public API contracts

// Use TYPE when:
// - Creating union or intersection types
// - Working with primitives, tuples
// - Need type manipulation (mapped, conditional)
// - Creating utility types
// - Aliasing complex type expressions

// Example showing both working together:
interface BaseEntity {
  id: string;
  createdAt: Date;
  updatedAt: Date;
}

type EntityStatus = 'draft' | 'published' | 'archived';

interface PublishableEntity extends BaseEntity {
  status: EntityStatus;
  publishedAt?: Date;
  publishedBy?: string;
}

type EntityWithMeta<T extends BaseEntity> = T & {
  _meta: {
    version: number;
    lastAccessed: Date;
    accessCount: number;
  };
};

// Usage
type CourseWithMeta = EntityWithMeta<Course & PublishableEntity>;
```

---

### 27. What are generics in TypeScript? Show examples from your codebase.

**Answer:**

**Generics - Type Parameters for Reusable Code:**

```typescript
// 1. Basic Generic Function
function identity<T>(value: T): T {
  return value;
}

// Usage with type inference
const num = identity(42); // T is inferred as number
const str = identity("hello"); // T is inferred as string

// 2. Generic Service for API Calls
@Injectable({ providedIn: 'root' })
export class ApiService {
  constructor(private http: HttpClient) {}
  
  // Generic GET request
  get<T>(endpoint: string, params?: any): Observable<T> {
    return this.http.get<T>(`${environment.apiUrl}/${endpoint}`, { params });
  }
  
  // Generic POST with different request and response types
  post<TRequest, TResponse>(
    endpoint: string, 
    data: TRequest
  ): Observable<TResponse> {
    return this.http.post<TResponse>(
      `${environment.apiUrl}/${endpoint}`, 
      data
    );
  }
  
  // Generic paginated response
  getPaginated<T>(
    endpoint: string, 
    page: number, 
    limit: number
  ): Observable<PaginatedResponse<T>> {
    return this.get<PaginatedResponse<T>>(endpoint, { page, limit });
  }
}

// Generic pagination interface
interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  hasNext: boolean;
  hasPrev: boolean;
}

// 3. Generic Base Service Class
abstract class BaseEntityService<T extends BaseEntity> {
  protected abstract endpoint: string;
  
  constructor(protected http: HttpClient) {}
  
  getAll(): Observable<T[]> {
    return this.http.get<T[]>(this.endpoint);
  }
  
  getById(id: string): Observable<T> {
    return this.http.get<T>(`${this.endpoint}/${id}`);
  }
  
  create(entity: Omit<T, 'id' | 'createdAt' | 'updatedAt'>): Observable<T> {
    return this.http.post<T>(this.endpoint, entity);
  }
  
  update(id: string, updates: Partial<T>): Observable<T> {
    return this.http.patch<T>(`${this.endpoint}/${id}`, updates);
  }
  
  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.endpoint}/${id}`);
  }
}

// Concrete implementation
@Injectable({ providedIn: 'root' })
export class CourseService extends BaseEntityService<Course> {
  protected endpoint = '/api/courses';
  
  // Additional course-specific methods
  enrollStudent(courseId: string, studentId: string): Observable<Enrollment> {
    return this.http.post<Enrollment>(
      `${this.endpoint}/${courseId}/enroll`,
      { studentId }
    );
  }
}

// 4. Generic Form Controls
class FormControl<T> {
  private value: T;
  private validators: Array<Validator<T>> = [];
  private errors: ValidationError[] = [];
  
  constructor(initialValue: T, validators?: Array<Validator<T>>) {
    this.value = initialValue;
    this.validators = validators || [];
  }
  
  getValue(): T {
    return this.value;
  }
  
  setValue(value: T): void {
    this.value = value;
    this.validate();
  }
  
  private validate(): void {
    this.errors = [];
    for (const validator of this.validators) {
      const error = validator(this.value);
      if (error) {
        this.errors.push(error);
      }
    }
  }
  
  isValid(): boolean {
    return this.errors.length === 0;
  }
}

type Validator<T> = (value: T) => ValidationError | null;

// Usage
const emailControl = new FormControl<string>('', [
  (value) => !value ? { required: true } : null,
  (value) => !value.includes('@') ? { email: true } : null
]);

const ageControl = new FormControl<number>(0, [
  (value) => value < 0 ? { min: 0 } : null,
  (value) => value > 120 ? { max: 120 } : null
]);

// 5. Generic State Management
class Store<T> {
  private state$ = new BehaviorSubject<T>(this.initialState);
  
  constructor(private initialState: T) {}
  
  select<K extends keyof T>(key: K): Observable<T[K]> {
    return this.state$.pipe(
      map(state => state[key]),
      distinctUntilChanged()
    );
  }
  
  update(updates: Partial<T>): void {
    const currentState = this.state$.value;
    this.state$.next({ ...currentState, ...updates });
  }
  
  updateProperty<K extends keyof T>(key: K, value: T[K]): void {
    const currentState = this.state$.value;
    this.state$.next({ ...currentState, [key]: value });
  }
  
  getState(): T {
    return this.state$.value;
  }
  
  state(): Observable<T> {
    return this.state$.asObservable();
  }
}

// Usage
interface AppState {
  user: User | null;
  theme: 'light' | 'dark';
  language: string;
  notifications: Notification[];
}

const appStore = new Store<AppState>({
  user: null,
  theme: 'light',
  language: 'en',
  notifications: []
});

// Type-safe property selection
appStore.select('user').subscribe(user => console.log(user));
appStore.updateProperty('theme', 'dark'); // Type-safe

// 6. Generic Constraints
interface HasId {
  id: string | number;
}

function findById<T extends HasId>(items: T[], id: string | number): T | undefined {
  return items.find(item => item.id === id);
}

// More complex constraints
function merge<T extends object, U extends object>(obj1: T, obj2: U): T & U {
  return { ...obj1, ...obj2 };
}

// 7. Generic Utility Types from CourseWagon
type ApiResult<T> = 
  | { success: true; data: T }
  | { success: false; error: string };

async function apiCall<T>(
  fn: () => Promise<T>
): Promise<ApiResult<T>> {
  try {
    const data = await fn();
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

// 8. Generic React-style Component Props (Angular equivalent)
interface TableColumn<T> {
  key: keyof T;
  label: string;
  sortable?: boolean;
  render?: (value: T[keyof T], item: T) => string;
}

@Component({
  selector: 'app-data-table',
  template: `...`
})
export class DataTableComponent<T extends Record<string, any>> {
  @Input() data: T[] = [];
  @Input() columns: TableColumn<T>[] = [];
  @Input() trackBy?: (index: number, item: T) => any;
  
  getSortedData(): T[] {
    // Implementation
    return this.data;
  }
}

// 9. Generic Observable Operators
function withLoading<T>(): OperatorFunction<T, { data: T; loading: boolean }> {
  return (source: Observable<T>) =>
    source.pipe(
      map(data => ({ data, loading: false })),
      startWith({ data: null as any, loading: true }),
      catchError(error => of({ data: null as any, loading: false, error }))
    );
}

// Usage
this.courses$ = this.courseService.getCourses().pipe(
  withLoading(),
  shareReplay(1)
);

// 10. Multiple Type Parameters
class Cache<K, V> {
  private cache = new Map<K, V>();
  private timestamps = new Map<K, number>();
  
  set(key: K, value: V, ttl?: number): void {
    this.cache.set(key, value);
    this.timestamps.set(key, Date.now());
  }
  
  get(key: K): V | undefined {
    return this.cache.get(key);
  }
  
  isExpired(key: K, ttl: number): boolean {
    const timestamp = this.timestamps.get(key);
    if (!timestamp) return true;
    return Date.now() - timestamp > ttl;
  }
}

// Usage with different key/value types
const userCache = new Cache<string, User>();
const configCache = new Cache<Symbol, Configuration>();
const courseCache = new Cache<number, Course[]>();
```

---

### 28. How do you handle null/undefined safety? Do you use strict null checks?

**Answer:**

**Strict Null Checking Strategy:**

```typescript
// tsconfig.json configuration
{
  "compilerOptions": {
    "strict": true,              // Enables all strict checks
    "strictNullChecks": true,    // Explicit null/undefined checking
    "strictPropertyInitialization": true,
    "noImplicitAny": true,
    "strictFunctionTypes": true
  }
}

// 1. Proper Type Definitions with null/undefined
interface User {
  id: string;
  name: string;
  email: string;
  phone?: string;           // Optional property (can be undefined)
  avatar: string | null;    // Explicitly nullable
  metadata?: {
    lastLogin: Date;
    loginCount: number;
  } | null;                 // Optional and nullable
}

// 2. Null Guards and Type Narrowing
function processUser(user: User | null | undefined) {
  // Early return for null/undefined
  if (!user) {
    console.log('No user provided');
    return;
  }
  
  // TypeScript now knows user is User
  console.log(`Processing user: ${user.name}`);
  
  // Optional chaining for nested properties
  const lastLogin = user.metadata?.lastLogin;
  
  // Nullish coalescing for defaults
  const avatar = user.avatar ?? '/assets/default-avatar.png';
  const phone = user.phone ?? 'No phone provided';
  
  // Type guard for nested nullable
  if (user.metadata) {
    console.log(`Login count: ${user.metadata.loginCount}`);
  }
}

// 3. Non-null Assertion Operator (use sparingly!)
class UserComponent implements OnInit {
  @Input() userId!: string; // Definite assignment assertion
  
  user: User | null = null;
  
  ngOnInit() {
    // We know userId will be set by Angular before ngOnInit
    this.loadUser(this.userId);
  }
  
  loadUser(id: string) {
    this.userService.getUser(id).subscribe(user => {
      this.user = user;
      
      // Non-null assertion when we're certain
      this.processUserData(this.user!); // Only if we're 100% sure
    });
  }
  
  // Better approach with guard
  processUserSafely() {
    if (!this.user) {
      console.error('User not loaded');
      return;
    }
    
    // TypeScript knows user is not null here
    this.processUserData(this.user);
  }
}

// 4. Utility Functions for Null Safety
// Type guard functions
function isDefined<T>(value: T | undefined): value is T {
  return value !== undefined;
}

function isNotNull<T>(value: T | null): value is T {
  return value !== null;
}

function hasValue<T>(value: T | null | undefined): value is T {
  return value !== null && value !== undefined;
}

// Filter out null/undefined from arrays
const users: (User | null)[] = [user1, null, user2, undefined, user3];
const validUsers: User[] = users.filter(hasValue);

// 5. Safe Property Access Patterns
class CourseService {
  // Safe navigation in templates
  getCourseTitle(course: Course | null): string {
    return course?.title ?? 'Untitled Course';
  }
  
  // Defensive copying with null checks
  updateCourse(course: Course | null, updates: Partial<Course>): Course | null {
    if (!course) return null;
    
    return {
      ...course,
      ...updates,
      updatedAt: new Date()
    };
  }
  
  // Safe array operations
  getFirstChapter(course: Course | null): Chapter | undefined {
    return course?.chapters?.[0];
  }
  
  // Chained null checks
  getInstructorName(course: Course | null): string {
    return course?.instructor?.name ?? 'Unknown Instructor';
  }
}

// 6. Handling Form Values with Null Safety
interface CourseFormValue {
  title: string | null;
  description: string | null;
  price: number | null;
  tags: string[] | null;
}

class CourseFormComponent {
  form = this.fb.group({
    title: [null as string | null, Validators.required],
    description: [null as string | null],
    price: [null as number | null, [Validators.required, Validators.min(0)]],
    tags: [null as string[] | null]
  });
  
  submitForm() {
    const formValue = this.form.value as CourseFormValue;
    
    // Validate required fields
    if (!formValue.title || !formValue.price) {
      this.showError('Required fields missing');
      return;
    }
    
    // Transform with defaults
    const courseData: CreateCourseDto = {
      title: formValue.title,
      description: formValue.description ?? '',
      price: formValue.price,
      tags: formValue.tags ?? []
    };
    
    this.courseService.createCourse(courseData).subscribe();
  }
}

// 7. Observable Null Safety
class DataService {
  private userSubject = new BehaviorSubject<User | null>(null);
  
  user$ = this.userSubject.asObservable();
  
  // Filter out null values
  validUser$ = this.user$.pipe(
    filter((user): user is User => user !== null)
  );
  
  // Provide default value
  userWithDefault$ = this.user$.pipe(
    map(user => user ?? this.getGuestUser())
  );
  
  // Handle nullable in operators
  userName$ = this.user$.pipe(
    map(user => user?.name ?? 'Guest'),
    distinctUntilChanged()
  );
  
  // Safe switchMap
  userCourses$ = this.user$.pipe(
    switchMap(user => {
      if (!user) {
        return of([]);
      }
      return this.courseService.getUserCourses(user.id);
    })
  );
}

// 8. Template Null Safety
@Component({
  template: `
    <!-- Safe navigation operator -->
    <div *ngIf="user">
      <h2>{{ user.name }}</h2>
      <p>{{ user.email }}</p>
      
      <!-- Optional chaining in template -->
      <p>Phone: {{ user.phone ?? 'Not provided' }}</p>
      
      <!-- Nested null checks -->
      <div *ngIf="user.metadata as meta">
        <p>Last login: {{ meta.lastLogin | date }}</p>
        <p>Login count: {{ meta.loginCount }}</p>
      </div>
    </div>
    
    <!-- NgFor with null safety -->
    <ul>
      <li *ngFor="let course of courses ?? []">
        {{ course.title }}
      </li>
    </ul>
    
    <!-- Async pipe with default -->
    <div>
      Total: {{ (total$ | async) ?? 0 }}
    </div>
  `
})
export class UserProfileComponent {
  user: User | null = null;
  courses: Course[] | null = null;
  total$: Observable<number | null>;
}

// 9. Advanced Null Safety Patterns
// Result type for operations that might fail
type Result<T, E = Error> = 
  | { success: true; value: T }
  | { success: false; error: E };

function parseJson<T>(json: string): Result<T> {
  try {
    const value = JSON.parse(json) as T;
    return { success: true, value };
  } catch (error) {
    return { success: false, error: error as Error };
  }
}

// Usage
const result = parseJson<User>(jsonString);
if (result.success) {
  console.log(result.value.name); // Type-safe access
} else {
  console.error(result.error.message);
}

// 10. Null Safety Best Practices from CourseWagon
class SafeCourseService {
  // Always return Observable<T | null> for single items
  getCourse(id: string): Observable<Course | null> {
    return this.http.get<Course>(`/api/courses/${id}`).pipe(
      catchError(() => of(null))
    );
  }
  
  // Use empty arrays instead of null for collections
  getCourses(): Observable<Course[]> {
    return this.http.get<Course[]>('/api/courses').pipe(
      catchError(() => of([])) // Never null for arrays
    );
  }
  
  // Explicit about nullable returns
  findCourseBySlug(slug: string): Course | undefined {
    return this.coursesCache.find(c => c.slug === slug);
  }
  
  // Required vs optional parameters
  updateCourse(
    id: string,                    // Required
    updates: Partial<Course>,      // Required
    options?: UpdateOptions        // Optional
  ): Observable<Course> {
    const config = options ?? { silent: false };
    // ...
  }
}
```

---

### 29. Explain union types and intersection types with examples from your models.

**Answer:**

**Union Types (|) - "OR" relationship:**

```typescript
// 1. Basic Union Types
type Status = 'draft' | 'published' | 'archived' | 'deleted';
type Role = 'student' | 'instructor' | 'admin';
type Theme = 'light' | 'dark' | 'auto';

// 2. Union of Object Types
interface StudentUser {
  type: 'student';
  id: string;
  name: string;
  enrolledCourses: string[];
  gpa: number;
}

interface InstructorUser {
  type: 'instructor';
  id: string;
  name: string;
  coursesTaught: string[];
  rating: number;
  expertise: string[];
}

interface AdminUser {
  type: 'admin';
  id: string;
  name: string;
  permissions: string[];
  department: string;
}

// Discriminated Union
type User = StudentUser | InstructorUser | AdminUser;

// Type guards for discriminated unions
function processUser(user: User) {
  // Common properties available
  console.log(`User ${user.name} with ID ${user.id}`);
  
  // Type narrowing with discriminator
  switch (user.type) {
    case 'student':
      // TypeScript knows this is StudentUser
      console.log(`GPA: ${user.gpa}`);
      console.log(`Enrolled in ${user.enrolledCourses.length} courses`);
      break;
      
    case 'instructor':
      // TypeScript knows this is InstructorUser
      console.log(`Rating: ${user.rating}`);
      console.log(`Expertise: ${user.expertise.join(', ')}`);
      break;
      
    case 'admin':
      // TypeScript knows this is AdminUser
      console.log(`Department: ${user.department}`);
      console.log(`Has ${user.permissions.length} permissions`);
      break;
  }
}

// 3. API Response Unions
type ApiResponse<T> = 
  | { status: 'success'; data: T; timestamp: Date }
  | { status: 'error'; error: string; code: number }
  | { status: 'loading' };

function handleResponse<T>(response: ApiResponse<T>) {
  if (response.status === 'success') {
    // Access data property safely
    console.log(response.data);
  } else if (response.status === 'error') {
    // Access error properties safely
    console.error(`Error ${response.code}: ${response.error}`);
  } else {
    // Loading state
    console.log('Loading...');
  }
}

// 4. Complex Union Types from CourseWagon
type CourseContent = 
  | VideoContent
  | TextContent
  | QuizContent
  | AssignmentContent
  | LiveSessionContent;

interface VideoContent {
  type: 'video';
  url: string;
  duration: number;
  subtitles?: SubtitleTrack[];
  thumbnail: string;
}

interface TextContent {
  type: 'text';
  markdown: string;
  estimatedReadTime: number;
  attachments?: Attachment[];
}

interface QuizContent {
  type: 'quiz';
  questions: Question[];
  passingScore: number;
  timeLimit?: number;
  attempts: number;
}

interface AssignmentContent {
  type: 'assignment';
  description: string;
  dueDate: Date;
  rubric: Rubric;
  submissions: Submission[];
}

interface LiveSessionContent {
  type: 'live';
  scheduledAt: Date;
  meetingUrl: string;
  recordingUrl?: string;
  attendees: string[];
}

// Component handling union types
@Component({
  selector: 'app-content-renderer',
  template: `
    <div [ngSwitch]="content.type">
      <app-video-player *ngSwitchCase="'video'" 
        [video]="asVideo(content)">
      </app-video-player>
      
      <app-text-viewer *ngSwitchCase="'text'"
        [text]="asText(content)">
      </app-text-viewer>
      
      <app-quiz *ngSwitchCase="'quiz'"
        [quiz]="asQuiz(content)">
      </app-quiz>
      
      <app-assignment *ngSwitchCase="'assignment'"
        [assignment]="asAssignment(content)">
      </app-assignment>
      
      <app-live-session *ngSwitchCase="'live'"
        [session]="asLiveSession(content)">
      </app-live-session>
    </div>
  `
})
export class ContentRendererComponent {
  @Input() content!: CourseContent;
  
  // Type assertion helpers for template
  asVideo(content: CourseContent): VideoContent {
    return content as VideoContent;
  }
  
  asText(content: CourseContent): TextContent {
    return content as TextContent;
  }
  
  asQuiz(content: CourseContent): QuizContent {
    return content as QuizContent;
  }
  
  asAssignment(content: CourseContent): AssignmentContent {
    return content as AssignmentContent;
  }
  
  asLiveSession(content: CourseContent): LiveSessionContent {
    return content as LiveSessionContent;
  }
}

// **Intersection Types (&) - "AND" relationship:**

// 1. Basic Intersection Types
type Timestamped = {
  createdAt: Date;
  updatedAt: Date;
};

type Identifiable = {
  id: string;
};

type Versionable = {
  version: number;
  previousVersions?: string[];
};

// Combine multiple types
type Entity = Identifiable & Timestamped & Versionable;

// Now Entity has all properties from all three types
const entity: Entity = {
  id: 'abc123',
  createdAt: new Date(),
  updatedAt: new Date(),
  version: 1,
  previousVersions: []
};

// 2. Extending Interfaces with Intersection
interface Course {
  title: string;
  description: string;
  instructor: string;
  price: number;
}

interface OnlineCourse {
  platform: string;
  streamingUrl: string;
  chatEnabled: boolean;
}

interface CertifiedCourse {
  certificationBody: string;
  certificateTemplate: string;
  passingCriteria: PassingCriteria;
}

// Combine to create specialized course type
type OnlineCertifiedCourse = Course & OnlineCourse & CertifiedCourse;

const advancedCourse: OnlineCertifiedCourse = {
  // From Course
  title: 'Advanced TypeScript',
  description: 'Master TypeScript',
  instructor: 'John Doe',
  price: 99.99,
  
  // From OnlineCourse
  platform: 'CourseWagon',
  streamingUrl: 'https://stream.example.com',
  chatEnabled: true,
  
  // From CertifiedCourse
  certificationBody: 'Tech Cert Inc',
  certificateTemplate: 'template-001',
  passingCriteria: { minScore: 80, minAttendance: 90 }
};

// 3. Mixin Pattern with Intersections
type WithLoading = {
  loading: boolean;
  loadingMessage?: string;
};

type WithError = {
  error: Error | null;
  errorCode?: string;
};

type WithPagination = {
  page: number;
  pageSize: number;
  total: number;
  hasNext: boolean;
  hasPrev: boolean;
};

// Combine mixins for component state
type CourseListState = {
  courses: Course[];
} & WithLoading & WithError & WithPagination;

class CourseListComponent {
  state: CourseListState = {
    courses: [],
    loading: false,
    error: null,
    page: 1,
    pageSize: 10,
    total: 0,
    hasNext: false,
    hasPrev: false
  };
  
  loadCourses() {
    this.state.loading = true;
    this.state.error = null;
    
    this.courseService.getCourses(this.state.page, this.state.pageSize)
      .subscribe({
        next: (response) => {
          this.state.courses = response.data;
          this.state.total = response.total;
          this.state.hasNext = response.hasNext;
          this.state.hasPrev = response.hasPrev;
          this.state.loading = false;
        },
        error: (error) => {
          this.state.error = error;
          this.state.loading = false;
        }
      });
  }
}

// 4. Function Overloading with Intersections
type Logger = {
  log(message: string): void;
  log(level: LogLevel, message: string): void;
} & {
  error(message: string): void;
  warn(message: string): void;
  info(message: string): void;
};

// 5. Real-world Example from CourseWagon
// Base types
interface BaseContent {
  id: string;
  title: string;
  description: string;
  order: number;
}

interface Trackable {
  views: number;
  completions: number;
  averageTime: number;
  lastAccessed?: Date;
}

interface Commentable {
  comments: Comment[];
  commentsEnabled: boolean;
  commentsCount: number;
}

interface Rateable {
  rating: number;
  ratingCount: number;
  ratings: Rating[];
}

// Complex content type using intersections
type EnhancedContent = BaseContent & Trackable & Commentable & Rateable & {
  content: CourseContent; // Union type from earlier
  prerequisites?: string[];
  unlockConditions?: UnlockCondition[];
  metadata: ContentMetadata;
};

// Service using complex types
@Injectable({ providedIn: 'root' })
export class ContentService {
  // Method using union type parameter
  getContentDuration(content: CourseContent): number {
    switch (content.type) {
      case 'video':
        return content.duration;
      case 'text':
        return content.estimatedReadTime;
      case 'quiz':
        return content.timeLimit || content.questions.length * 60;
      case 'assignment':
        return 30 * 60; // Estimated 30 minutes
      case 'live':
        return 60 * 60; // Default 1 hour
      default:
        // Exhaustive check
        const _exhaustive: never = content;
        return 0;
    }
  }
  
  // Method returning intersection type
  enrichContent(
    basic: BaseContent,
    analytics: Trackable,
    social: Commentable & Rateable
  ): EnhancedContent {
    return {
      ...basic,
      ...analytics,
      ...social,
      content: this.loadContent(basic.id),
      metadata: this.loadMetadata(basic.id)
    };
  }
  
  // Type predicate for union types
  isVideoContent(content: CourseContent): content is VideoContent {
    return content.type === 'video';
  }
  
  // Generic with intersection constraint
  trackEvent<T extends Identifiable & Trackable>(
    item: T,
    event: 'view' | 'complete'
  ): void {
    console.log(`Tracking ${event} for item ${item.id}`);
    if (event === 'view') {
      item.views++;
    } else {
      item.completions++;
    }
    item.lastAccessed = new Date();
  }
}

// 6. Conditional Types with Unions and Intersections
type ExtractType<T, U> = T extends U ? T : never;
type ExcludeType<T, U> = T extends U ? never : T;

// Extract only content types that have duration
type TimedContent = ExtractType<CourseContent, { duration: number }>;

// Create a type that adds loading state to any type
type Loadable<T> = T & { isLoading: boolean; loadError?: Error };

// Usage
type LoadableCourse = Loadable<Course>;
const course: LoadableCourse = {
  title: 'TypeScript Advanced',
  description: 'Learn advanced TypeScript',
  instructor: 'Jane Doe',
  price: 149.99,
  isLoading: false
};
```

**Best Practices Summary:**
- Use **Union types** for "either/or" scenarios
- Use **Intersection types** for combining capabilities
- Prefer discriminated unions for complex object unions
- Use type guards to narrow union types
- Combine unions and intersections for flexible, type-safe APIs