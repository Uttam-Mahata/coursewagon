# Question 2: What are the differences between OnInit, AfterViewInit, and OnDestroy lifecycle hooks? Where have you used them in CourseWagon?

## Answer

### Lifecycle Hooks Overview

Angular components go through a lifecycle from creation to destruction. Here are the key hooks we use:

### 1. OnInit

**When it runs:** After Angular initializes all data-bound properties (after first ngOnChanges)

**Purpose:** 
- Initialize component
- Fetch initial data
- Set up subscriptions
- Perfect for API calls

**Our Implementation Examples:**

```typescript
// app.component.ts - Setting up global authentication state
export class AppComponent implements OnInit {
  isAuthenticated = false;
  isAdmin = false;

  ngOnInit(): void {
    // Subscribe to authentication state changes
    this.authService.isLoggedIn$.subscribe((isAuth: boolean) => {
      this.isAuthenticated = isAuth;
      if (isAuth) {
        const user = this.authService.getCurrentUser();
        this.isAdmin = user && user.is_admin;
      } else {
        this.isAdmin = false;
      }
    });
    
    // Check initial auth state
    this.authService.checkAuthState();
  }
}
```

```typescript
// course-detail.component.ts - Loading data based on route params
export class CourseDetailComponent implements OnInit {
  ngOnInit() {
    // Get course ID from route and load course data
    this.route.params.subscribe(params => {
      const courseId = params['id'];
      if (courseId) {
        this.loadCourseDetails(courseId);
        this.loadCourseChapters(courseId);
      }
    });

    // Check authentication for enrollment status
    this.authService.currentUser$.subscribe(user => {
      if (user) {
        this.checkEnrollmentStatus();
      }
    });
  }
}
```

### 2. AfterViewInit

**When it runs:** After Angular initializes component's views and child views

**Purpose:**
- Access @ViewChild elements
- Perform DOM manipulations
- Initialize third-party libraries that need DOM

**Our Implementation Example:**

```typescript
// admin.component.ts - Setting up child component callbacks
export class AdminComponent implements OnInit, AfterViewInit {
  @ViewChild(AdminDashboardComponent) dashboardComponent!: AdminDashboardComponent;
  
  ngAfterViewInit() {
    // Can only access ViewChild after view initializes
    if (this.dashboardComponent) {
      // Set up callbacks for dashboard navigation
      this.dashboardComponent.viewAllUsers = () => this.setActiveTab('users');
      this.dashboardComponent.reviewTestimonials = () => this.setActiveTab('testimonials');
      this.dashboardComponent.manageCourses = () => this.setActiveTab('courses');
    }
  }
}
```

### 3. OnDestroy

**When it runs:** Just before Angular destroys the component

**Purpose:**
- Clean up subscriptions (prevent memory leaks)
- Clear timers
- Release resources

**Our Implementation Examples:**

```typescript
// courses.component.ts - Proper subscription cleanup
export class CoursesComponent implements OnInit, OnDestroy {
  private subscriptions: Subscription[] = [];

  ngOnInit() {
    // Store subscriptions for cleanup
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
  }

  ngOnDestroy() {
    // Clean up all subscriptions to prevent memory leaks
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }
}
```

### 4. Execution Order & Timing

```
Constructor → ngOnChanges → ngOnInit → ngAfterContentInit → 
ngAfterContentChecked → ngAfterViewInit → ngAfterViewChecked → 
... (component lifetime) ... → ngOnDestroy
```

### 5. Common Patterns in Our Codebase

#### Pattern 1: Authentication Check in OnInit
```typescript
ngOnInit(): void {
  this.authService.isLoggedIn$.subscribe(isLoggedIn => {
    this.isLoggedIn = isLoggedIn;
    if (isLoggedIn) {
      this.loadUserData();
    }
  });
}
```

#### Pattern 2: Route Parameter Handling in OnInit
```typescript
ngOnInit(): void {
  this.route.params.subscribe(params => {
    const id = params['id'];
    this.loadData(id);
  });
}
```

#### Pattern 3: Cleanup in OnDestroy
```typescript
private destroy$ = new Subject<void>();

ngOnInit() {
  this.someObservable$
    .pipe(takeUntil(this.destroy$))
    .subscribe(data => this.handleData(data));
}

ngOnDestroy() {
  this.destroy$.next();
  this.destroy$.complete();
}
```

### 6. Best Practices We Follow

1. **OnInit for Data**: Always fetch data in OnInit, not constructor
2. **ViewChild in AfterViewInit**: Only access @ViewChild after view initializes
3. **Always Unsubscribe**: Every subscription needs cleanup in OnDestroy
4. **Avoid Heavy Operations**: Don't block UI thread in lifecycle hooks

### 7. Common Mistakes to Avoid

```typescript
// ❌ Wrong: Accessing ViewChild in OnInit
ngOnInit() {
  this.childComponent.doSomething(); // May be undefined!
}

// ✅ Correct: Access ViewChild in AfterViewInit
ngAfterViewInit() {
  if (this.childComponent) {
    this.childComponent.doSomething();
  }
}

// ❌ Wrong: Not unsubscribing
ngOnInit() {
  this.service.data$.subscribe(data => this.data = data);
  // Memory leak!
}

// ✅ Correct: Proper cleanup
private sub: Subscription;
ngOnInit() {
  this.sub = this.service.data$.subscribe(data => this.data = data);
}
ngOnDestroy() {
  if (this.sub) this.sub.unsubscribe();
}
```

### Interview Tip

When discussing lifecycle hooks:
1. Explain the timing and purpose clearly
2. Give real examples from your code
3. Emphasize memory leak prevention with OnDestroy
4. Show you understand the component lifecycle flow