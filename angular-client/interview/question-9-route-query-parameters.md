# Question 9: How do you handle route parameters and query parameters in your course detail pages?

## Answer

### Understanding Route vs Query Parameters

CourseWagon uses both route parameters and query parameters for different purposes:
- **Route Parameters**: Required values that are part of the URL path (e.g., `/courses/:id`)
- **Query Parameters**: Optional values after `?` (e.g., `/courses?search=angular`)

### 1. Route Parameters in Course Navigation

#### Current Implementation:

```typescript
// course-content.component.ts - Handles nested route parameters
export class CourseContentComponent implements OnInit {
  courseId: number;
  subjectId: number;
  topicId?: number;  // Optional parameter
  
  ngOnInit() {
    // Subscribe to route parameter changes
    this.subscriptions.add(
      this.route.paramMap.subscribe(params => {
        // Extract multiple parameters
        const newCourseId = +params.get('course_id')!;  // + converts to number
        const newSubjectId = +params.get('subject_id')!;
        const topicId = params.get('topic_id');  // Optional, might be null
        
        // Check if course or subject has changed
        if (newCourseId !== this.courseId || newSubjectId !== this.subjectId) {
          this.courseId = newCourseId;
          this.subjectId = newSubjectId;
          this.loadInitialData();
        }
        
        // Handle optional topic parameter
        if (topicId) {
          this.selectedTopicId = +topicId;
          this.scrollToTopic(this.selectedTopicId);
        }
      })
    );
  }
}
```

#### Route Configuration:

```typescript
// app-routing.module.ts
const routes: Routes = [
  // Single parameter
  { 
    path: 'courses/:course_id/subjects', 
    component: SubjectsComponent 
  },
  
  // Multiple parameters
  { 
    path: 'courses/:course_id/subjects/:subject_id/content', 
    component: CourseContentComponent
  },
  
  // Optional parameter
  { 
    path: 'courses/:course_id/subjects/:subject_id/content/:topic_id', 
    component: CourseContentComponent
  }
];
```

### 2. Query Parameters Usage

#### Authentication Return URL:

```typescript
// auth.component.ts - Handles return URL after login
export class AuthComponent implements OnInit {
  returnUrl: string = '/courses';  // Default redirect
  
  ngOnInit() {
    // Get return URL from query parameters
    this.route.queryParams.subscribe(params => {
      // Check for return URL
      this.returnUrl = params['returnUrl'] || '/courses';
      
      // Check for auth mode (login vs signup)
      const mode = params['mode'];
      if (mode === 'signup') {
        this.isLoginMode = false;
      } else if (mode === 'login') {
        this.isLoginMode = true;
      }
    });
  }
  
  onSubmit() {
    if (this.isLoginMode) {
      this.authService.login(this.email, this.password).subscribe({
        next: (response) => {
          // Navigate to return URL after successful login
          this.router.navigateByUrl(this.returnUrl);
        }
      });
    }
  }
}
```

#### Password Reset Token:

```typescript
// reset-password.component.ts
export class ResetPasswordComponent implements OnInit {
  token: string = '';
  
  ngOnInit(): void {
    // Get token from URL query parameters
    this.route.queryParams.subscribe(params => {
      this.token = params['token'] || '';
      
      if (!this.token) {
        this.errorMessage = 'Missing password reset token.';
        return;
      }
      
      // Verify token validity
      this.verifyResetToken(this.token);
    });
  }
}
```

### 3. Different Ways to Access Parameters

#### Method 1: ParamMap Observable (Recommended)

```typescript
// Best for parameters that might change during component lifetime
ngOnInit() {
  // Using paramMap (recommended)
  this.route.paramMap.subscribe(params => {
    this.courseId = +params.get('course_id')!;
    // Reactive to parameter changes
    this.loadCourseDetails(this.courseId);
  });
}
```

#### Method 2: Snapshot (One-time Read)

```typescript
// Good for parameters that won't change
ngOnInit() {
  // Using snapshot - doesn't update if params change
  this.courseId = +this.route.snapshot.params['course_id'];
  this.subjectId = +this.route.snapshot.params['subject_id'];
  
  // Query parameters snapshot
  const searchTerm = this.route.snapshot.queryParams['search'];
}
```

#### Method 3: Direct Params Observable

```typescript
// Legacy approach (still works)
ngOnInit() {
  this.route.params.subscribe(params => {
    this.courseId = +params['course_id'];
  });
  
  this.route.queryParams.subscribe(queryParams => {
    this.searchQuery = queryParams['search'];
  });
}
```

### 4. Navigation with Parameters

#### Programmatic Navigation:

```typescript
// course.service.ts - Navigation examples
export class CourseNavigationService {
  
  // Navigate with route parameters
  navigateToCourseContent(courseId: number, subjectId: number) {
    this.router.navigate([
      '/courses', courseId, 'subjects', subjectId, 'content'
    ]);
  }
  
  // Navigate with query parameters
  navigateToCoursesWithSearch(searchTerm: string) {
    this.router.navigate(['/courses'], {
      queryParams: { search: searchTerm, category: 'programming' }
    });
  }
  
  // Navigate with both route and query parameters
  navigateToTopicWithHighlight(courseId: number, topicId: number) {
    this.router.navigate(
      ['/courses', courseId, 'content', topicId],
      { 
        queryParams: { highlight: 'true', section: 'intro' },
        queryParamsHandling: 'merge'  // Preserve existing query params
      }
    );
  }
  
  // Navigate with fragment (anchor)
  navigateToSection(courseId: number, section: string) {
    this.router.navigate(
      ['/courses', courseId],
      { fragment: section }  // Creates URL: /courses/123#section
    );
  }
}
```

#### Template Navigation:

```html
<!-- Route parameters in template -->
<a [routerLink]="['/courses', course.id, 'subjects']">
  View Subjects
</a>

<!-- With query parameters -->
<a [routerLink]="['/courses']" 
   [queryParams]="{ category: 'web-development', level: 'beginner' }">
  Browse Courses
</a>

<!-- Preserve query parameters -->
<a [routerLink]="['/courses', course.id]" 
   queryParamsHandling="preserve">
  View Course
</a>

<!-- Multiple parameters -->
<a [routerLink]="['/courses', course.id, 'subjects', subject.id, 'content']"
   [queryParams]="{ expanded: 'true' }">
  View Content
</a>
```

### 5. Complex Parameter Handling Pattern

```typescript
// subjects-chapters.component.ts - Complex parameter management
export class SubjectsChaptersComponent implements OnInit, OnDestroy {
  private paramSubscription?: Subscription;
  
  // Track all parameters
  routeParams = {
    courseId: 0,
    subjectId: 0,
    chapterId: 0
  };
  
  queryParams = {
    view: 'grid',
    sort: 'name',
    filter: ''
  };
  
  ngOnInit() {
    // Combine route and query parameters
    this.paramSubscription = combineLatest([
      this.route.paramMap,
      this.route.queryParamMap
    ]).subscribe(([params, queryParams]) => {
      // Handle route parameters
      const courseId = +params.get('course_id')!;
      const subjectId = params.get('subject_id');
      
      // Handle query parameters
      this.queryParams.view = queryParams.get('view') || 'grid';
      this.queryParams.sort = queryParams.get('sort') || 'name';
      this.queryParams.filter = queryParams.get('filter') || '';
      
      // Only reload if significant parameters changed
      if (courseId !== this.routeParams.courseId) {
        this.routeParams.courseId = courseId;
        this.loadCourseData();
      }
      
      // Apply view settings
      this.applyViewSettings();
    });
  }
  
  ngOnDestroy() {
    this.paramSubscription?.unsubscribe();
  }
}
```

### 6. Parameter Validation and Error Handling

```typescript
export class CourseDetailComponent implements OnInit {
  
  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      const courseIdStr = params.get('course_id');
      
      // Validate parameter exists
      if (!courseIdStr) {
        this.router.navigate(['/courses']);
        return;
      }
      
      // Validate parameter is valid number
      const courseId = +courseIdStr;
      if (isNaN(courseId) || courseId <= 0) {
        this.showError('Invalid course ID');
        this.router.navigate(['/courses']);
        return;
      }
      
      // Load course with error handling
      this.courseService.getCourse(courseId).subscribe({
        next: (course) => {
          this.course = course;
        },
        error: (error) => {
          if (error.status === 404) {
            this.showError('Course not found');
            this.router.navigate(['/courses']);
          }
        }
      });
    });
  }
}
```

### 7. Query Parameters Persistence

```typescript
// Preserving query parameters across navigation
export class NavigationService {
  
  // Method 1: Preserve all query params
  navigatePreservingQueryParams(path: string[]) {
    this.router.navigate(path, {
      queryParamsHandling: 'preserve'
    });
  }
  
  // Method 2: Merge new with existing
  navigateWithMergedParams(path: string[], newParams: any) {
    this.router.navigate(path, {
      queryParams: newParams,
      queryParamsHandling: 'merge'
    });
  }
  
  // Method 3: Selective preservation
  navigateWithSelectedParams(path: string[]) {
    const currentParams = this.route.snapshot.queryParams;
    const preservedParams = {
      search: currentParams['search'],
      category: currentParams['category']
      // Don't preserve other params
    };
    
    this.router.navigate(path, {
      queryParams: preservedParams
    });
  }
}
```

### 8. URL Structure Best Practices

```typescript
// Good URL structures in CourseWagon

// ✅ Clear hierarchy with route params
'/courses/123/subjects/456/content'

// ✅ Optional parameters at the end
'/courses/123/subjects/456/content/789'  // 789 is optional topic

// ✅ Query params for filters/options
'/courses?category=programming&level=beginner&sort=popular'

// ❌ Avoid deep nesting
'/courses/123/subjects/456/chapters/789/topics/012/content/345'

// ✅ Better: Flatten where possible
'/content/345?course=123&subject=456'
```

### 9. Testing Parameter Handling

```typescript
// Testing route parameters
it('should load course based on route params', fakeAsync(() => {
  // Set up test route
  const activatedRoute = TestBed.inject(ActivatedRoute);
  (activatedRoute.paramMap as any) = of(
    convertToParamMap({ course_id: '123', subject_id: '456' })
  );
  
  component.ngOnInit();
  tick();
  
  expect(component.courseId).toBe(123);
  expect(component.subjectId).toBe(456);
  expect(courseService.getCourse).toHaveBeenCalledWith(123);
}));

// Testing query parameters
it('should handle return URL from query params', () => {
  const activatedRoute = TestBed.inject(ActivatedRoute);
  (activatedRoute.queryParams as any) = of({ 
    returnUrl: '/profile',
    mode: 'signup' 
  });
  
  component.ngOnInit();
  
  expect(component.returnUrl).toBe('/profile');
  expect(component.isLoginMode).toBe(false);
});
```

### Interview Talking Points

1. **Know the difference**: Route params are required, query params are optional
2. **Observable vs Snapshot**: Use observables when params might change
3. **Type conversion**: Always convert string params to proper types (+param for numbers)
4. **Error handling**: Validate parameters and handle invalid values
5. **Navigation patterns**: Show various ways to navigate with parameters
6. **Performance**: Unsubscribe from parameter observables in OnDestroy