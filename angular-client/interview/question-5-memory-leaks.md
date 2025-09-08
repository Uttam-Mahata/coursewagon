# Question 5: How do you handle memory leaks with subscriptions? Show examples from your services.

## Answer

### Understanding Memory Leaks in Angular

Memory leaks occur when subscriptions aren't properly cleaned up, causing components to remain in memory even after being destroyed. This is critical in SPAs where users navigate between routes frequently.

### 1. The Problem: Subscriptions Without Cleanup

```typescript
// ❌ BAD: Memory leak example from early version
export class BadComponent implements OnInit {
  userData: any;
  
  ngOnInit() {
    // This subscription lives forever!
    this.userService.userData$.subscribe(data => {
      this.userData = data;
    });
    
    // Even after component is destroyed, subscription continues
    interval(1000).subscribe(count => {
      console.log(count); // Keeps logging even after navigation
    });
  }
  // No cleanup! Memory leak!
}
```

### 2. Our Current Implementation Patterns

#### Pattern 1: Subscription Array (Most Common in Our Code)

```typescript
// courses.component.ts
export class CoursesComponent implements OnInit, OnDestroy {
  private subscriptions: Subscription[] = [];
  courses: any[] = [];
  
  ngOnInit() {
    // Store all subscriptions
    this.subscriptions.push(
      this.authService.currentUser$.subscribe(user => {
        if (user) {
          this.loadCourses(true);
        } else {
          this.courses = [];
          this.loading = false;
        }
      })
    );

    this.subscriptions.push(
      this.route.queryParams.subscribe(params => {
        if (params['search']) {
          this.searchQuery = params['search'];
          this.searchCourses();
        }
      })
    );

    this.subscriptions.push(
      this.courseService.courseUpdated$.subscribe(() => {
        this.loadCourses(false);
      })
    );
  }

  ngOnDestroy() {
    // Clean up all subscriptions at once
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }
}
```

#### Pattern 2: Individual Subscription Variables

```typescript
// profile.component.ts
export class ProfileComponent implements OnInit, OnDestroy {
  private userSub?: Subscription;
  private courseSub?: Subscription;
  
  ngOnInit() {
    this.userSub = this.authService.currentUser$.subscribe(user => {
      if (user) {
        this.user = user;
        this.loadUserCourses();
      }
    });
  }
  
  loadUserCourses() {
    this.courseSub = this.courseService.getUserCourses().subscribe(courses => {
      this.enrolledCourses = courses;
    });
  }
  
  ngOnDestroy() {
    // Clean up with null checks
    if (this.userSub) this.userSub.unsubscribe();
    if (this.courseSub) this.courseSub.unsubscribe();
  }
}
```

#### Pattern 3: takeUntil with Subject (Advanced Pattern)

```typescript
// admin.component.ts - Better pattern for multiple subscriptions
export class AdminComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();
  
  ngOnInit() {
    // All subscriptions auto-complete when destroy$ emits
    this.authService.currentUser$
      .pipe(takeUntil(this.destroy$))
      .subscribe(user => {
        this.currentUser = user;
      });
    
    this.adminService.getStatistics()
      .pipe(
        takeUntil(this.destroy$),
        retry(3),
        catchError(error => {
          console.error('Failed to load statistics:', error);
          return of(null);
        })
      )
      .subscribe(stats => {
        if (stats) this.statistics = stats;
      });
    
    // Auto-cleanup for interval
    interval(30000)
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.refreshDashboard();
      });
  }
  
  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
```

### 3. Services: No Cleanup Needed (Usually)

```typescript
// auth.service.ts - Services are singletons, live for app lifetime
@Injectable({ providedIn: 'root' })
export class AuthService {
  private currentUserSource = new BehaviorSubject<any>(null);
  currentUser$ = this.currentUserSource.asObservable();
  
  constructor(private http: HttpClient) {
    // No need to unsubscribe - service lives forever
    this.checkStoredAuth();
  }
  
  // HTTP observables complete automatically
  login(email: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/login`, { email, password })
      .pipe(
        tap(response => {
          this.currentUserSource.next(response.user);
        })
      );
    // HTTP request completes after response - no leak
  }
}
```

### 4. Async Pipe: Automatic Cleanup

```typescript
// course-list.component.ts
@Component({
  template: `
    <!-- Async pipe handles subscription and cleanup automatically -->
    <div *ngFor="let course of courses$ | async">
      {{ course.title }}
    </div>
  `
})
export class CourseListComponent {
  // No manual subscription needed!
  courses$ = this.courseService.getCourses();
  
  // No ngOnDestroy needed - async pipe handles it!
}
```

### 5. When You Don't Need to Unsubscribe

```typescript
export class ChapterContentComponent implements OnInit {
  ngOnInit() {
    // ✅ HTTP requests complete automatically
    this.http.get('/api/chapter/1').subscribe(chapter => {
      this.chapter = chapter;
    });
    // No unsubscribe needed - completes after response
    
    // ✅ Router events in services (singleton)
    // Only in services, not components!
    
    // ✅ Async pipe in template
    // <div>{{ observable$ | async }}</div>
  }
}
```

### 6. When You MUST Unsubscribe

```typescript
export class DangerousComponent implements OnInit {
  ngOnInit() {
    // ❌ MUST unsubscribe: Infinite observables
    interval(1000).subscribe();
    
    // ❌ MUST unsubscribe: Subject/BehaviorSubject
    this.authService.currentUser$.subscribe();
    
    // ❌ MUST unsubscribe: EventEmitter
    this.someService.events.subscribe();
    
    // ❌ MUST unsubscribe: Form value changes
    this.form.valueChanges.subscribe();
    
    // ❌ MUST unsubscribe: Route params in components
    this.route.params.subscribe();
  }
}
```

### 7. Advanced Pattern: Custom Destroy Service

```typescript
// destroy.service.ts - Reusable cleanup service
@Injectable()
export class DestroyService extends Subject<void> implements OnDestroy {
  ngOnDestroy() {
    this.next();
    this.complete();
  }
}

// component using destroy service
@Component({
  providers: [DestroyService]  // Provided per component
})
export class SmartComponent implements OnInit {
  constructor(
    private destroy$: DestroyService,
    private dataService: DataService
  ) {}
  
  ngOnInit() {
    // Super clean syntax
    this.dataService.data$
      .pipe(takeUntil(this.destroy$))
      .subscribe(data => this.handleData(data));
  }
  // No ngOnDestroy needed!
}
```

### 8. Memory Leak Detection Tools

```typescript
// Helper to detect leaks in development
export class LeakDetectorComponent implements OnDestroy {
  private subscriptionCount = 0;
  
  trackSubscription<T>(obs: Observable<T>): Observable<T> {
    this.subscriptionCount++;
    console.log(`Active subscriptions: ${this.subscriptionCount}`);
    
    return obs.pipe(
      finalize(() => {
        this.subscriptionCount--;
        console.log(`Active subscriptions: ${this.subscriptionCount}`);
      })
    );
  }
  
  ngOnDestroy() {
    if (this.subscriptionCount > 0) {
      console.error(`MEMORY LEAK: ${this.subscriptionCount} subscriptions not cleaned!`);
    }
  }
}
```

### 9. Real Issues We've Fixed

```typescript
// Before: Memory leak in course player
export class VideoPlayerComponent implements OnInit {
  ngOnInit() {
    // Leaked! Kept playing even after navigation
    interval(100).subscribe(() => {
      this.updateProgress();
    });
  }
}

// After: Proper cleanup
export class VideoPlayerComponent implements OnInit, OnDestroy {
  private progressTimer?: Subscription;
  
  ngOnInit() {
    this.progressTimer = interval(100).subscribe(() => {
      this.updateProgress();
    });
  }
  
  ngOnDestroy() {
    if (this.progressTimer) {
      this.progressTimer.unsubscribe();
    }
  }
}
```

### 10. Best Practices Checklist

✅ **Always unsubscribe from:**
- Component subscriptions to services
- Interval/Timer observables  
- Subject/BehaviorSubject subscriptions
- Form value changes
- Custom event emitters

✅ **Preferred patterns:**
1. Async pipe when possible (automatic cleanup)
2. takeUntil pattern for multiple subscriptions
3. Subscription arrays for simple cases
4. First/Take operators for single values

✅ **Code review checklist:**
- Every `subscribe()` has corresponding cleanup
- No subscriptions in constructors
- Services don't subscribe to their own observables
- HTTP requests don't need manual unsubscribe

### Interview Tips

1. **Show awareness**: Memory leaks are serious in SPAs
2. **Know patterns**: Multiple ways to handle cleanup
3. **Understand when**: Not all subscriptions need cleanup
4. **Production experience**: Share real bugs you've fixed
5. **Tools**: Chrome DevTools Memory Profiler experience