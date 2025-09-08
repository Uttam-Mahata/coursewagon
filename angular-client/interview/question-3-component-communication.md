# Question 3: Explain the component communication patterns you've implemented. How do parent-child components share data?

## Answer

### Component Communication Patterns in CourseWagon

We use multiple patterns for component communication, each suited for different scenarios:

### 1. Parent to Child: @Input Decorator

**Use Case:** Passing data down to child components

```typescript
// admin-testimonials.component.ts (Child)
export class AdminTestimonialsComponent {
  @Input() testimonials: any[] = [];
  @Input() loading: boolean = false;
  @Input() error: string = '';
}

// admin.component.html (Parent)
<app-admin-testimonials
  [testimonials]="testimonials"
  [loading]="loadingTestimonials"
  [error]="testimonialError">
</app-admin-testimonials>

// admin.component.ts (Parent)
export class AdminComponent {
  testimonials: any[] = [];
  loadingTestimonials = false;
  testimonialError = '';

  loadTestimonials() {
    this.loadingTestimonials = true;
    this.testimonialService.getAllTestimonials().subscribe({
      next: (data) => {
        this.testimonials = data;
        this.loadingTestimonials = false;
      },
      error: (error) => {
        this.testimonialError = 'Failed to load testimonials';
        this.loadingTestimonials = false;
      }
    });
  }
}
```

### 2. Child to Parent: @Output with EventEmitter

**Use Case:** Child components notifying parent of events

```typescript
// write-review.component.ts (Child)
export class WriteReviewComponent {
  @Input() userTestimonial: any = null;
  @Output() testimonialUpdated = new EventEmitter<any>();
  @Output() testimonialDeleted = new EventEmitter<void>();

  createTestimonial(): void {
    const testimonialData = {
      name: this.name,
      content: this.content,
      rating: this.rating
    };

    this.testimonialService.createTestimonial(testimonialData).subscribe({
      next: (response) => {
        // Emit event to parent with new testimonial data
        this.testimonialUpdated.emit(response);
        this.resetForm();
      }
    });
  }

  deleteTestimonial(): void {
    this.testimonialService.deleteTestimonial(this.testimonialId).subscribe({
      next: () => {
        // Notify parent that testimonial was deleted
        this.testimonialDeleted.emit();
      }
    });
  }
}

// profile.component.html (Parent)
<app-write-review
  [userTestimonial]="userTestimonial"
  (testimonialUpdated)="onTestimonialUpdated($event)"
  (testimonialDeleted)="onTestimonialDeleted()">
</app-write-review>

// profile.component.ts (Parent)
export class ProfileComponent {
  onTestimonialUpdated(testimonial: any): void {
    this.userTestimonial = testimonial;
    this.showSuccessMessage('Testimonial updated successfully!');
  }

  onTestimonialDeleted(): void {
    this.userTestimonial = null;
    this.showSuccessMessage('Testimonial deleted successfully!');
  }
}
```

### 3. Service-Based Communication (Most Common in Our App)

**Use Case:** Sharing data between unrelated components

```typescript
// auth.service.ts - Central state management
@Injectable({ providedIn: 'root' })
export class AuthService {
  // BehaviorSubject maintains current value
  private currentUserSource = new BehaviorSubject<any>(null);
  private isLoggedInSource = new BehaviorSubject<boolean>(false);
  
  // Expose as observables
  currentUser$ = this.currentUserSource.asObservable();
  isLoggedIn$ = this.isLoggedInSource.asObservable();

  login(email: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/login`, { email, password })
      .pipe(
        tap(response => {
          // Update shared state
          this.currentUserSource.next(response.user);
          this.isLoggedInSource.next(true);
          localStorage.setItem('token', response.token);
        })
      );
  }

  logout(): void {
    // Clear shared state
    this.currentUserSource.next(null);
    this.isLoggedInSource.next(false);
    localStorage.removeItem('token');
  }
}

// app.component.ts - Header subscribes to auth state
export class AppComponent implements OnInit {
  isAuthenticated = false;
  isAdmin = false;

  ngOnInit(): void {
    // React to authentication changes anywhere in app
    this.authService.isLoggedIn$.subscribe((isAuth: boolean) => {
      this.isAuthenticated = isAuth;
      if (isAuth) {
        const user = this.authService.getCurrentUser();
        this.isAdmin = user && user.is_admin;
      }
    });
  }
}

// courses.component.ts - Another component using same service
export class CoursesComponent implements OnInit {
  ngOnInit() {
    // React to same authentication state
    this.authService.currentUser$.subscribe(user => {
      if (user) {
        this.loadEnrolledCourses();
      } else {
        this.enrolledCourses = [];
      }
    });
  }
}
```

### 4. ViewChild/ViewChildren Pattern

**Use Case:** Parent directly accessing child component methods

```typescript
// admin.component.ts
export class AdminComponent implements AfterViewInit {
  @ViewChild(AdminDashboardComponent) dashboardComponent!: AdminDashboardComponent;
  @ViewChild('courseSection') courseSection!: ElementRef;

  ngAfterViewInit() {
    // Direct access to child component
    if (this.dashboardComponent) {
      // Set up navigation callbacks
      this.dashboardComponent.viewAllUsers = () => {
        this.setActiveTab('users');
        this.scrollToSection(this.courseSection);
      };
    }
  }

  refreshDashboard() {
    // Directly call child component method
    if (this.dashboardComponent) {
      this.dashboardComponent.loadStatistics();
    }
  }
}
```

### 5. Route Parameters for Component Communication

**Use Case:** Passing data through routing

```typescript
// Navigation with data
this.router.navigate(['/course', courseId], {
  queryParams: { enrolled: true }
});

// course-detail.component.ts - Receiving route data
export class CourseDetailComponent implements OnInit {
  ngOnInit() {
    // Get path parameters
    this.route.params.subscribe(params => {
      this.courseId = params['id'];
      this.loadCourseDetails(this.courseId);
    });

    // Get query parameters
    this.route.queryParams.subscribe(queryParams => {
      if (queryParams['enrolled']) {
        this.showEnrollmentSuccess = true;
      }
    });
  }
}
```

### 6. Subject/BehaviorSubject Pattern for Event Bus

```typescript
// notification.service.ts - Event bus pattern
@Injectable({ providedIn: 'root' })
export class NotificationService {
  private notificationSubject = new Subject<Notification>();
  notification$ = this.notificationSubject.asObservable();

  showSuccess(message: string) {
    this.notificationSubject.next({
      type: 'success',
      message: message
    });
  }

  showError(message: string) {
    this.notificationSubject.next({
      type: 'error',
      message: message
    });
  }
}

// Any component can publish
this.notificationService.showSuccess('Course enrolled successfully!');

// Any component can subscribe
this.notificationService.notification$.subscribe(notification => {
  this.displayNotification(notification);
});
```

### 7. Communication Pattern Decision Matrix

| Scenario | Pattern | Example in Our App |
|----------|---------|-------------------|
| Parent → Child data | @Input | Admin → AdminDashboard stats |
| Child → Parent events | @Output | WriteReview → Profile updates |
| Sibling components | Service | Header ↔ Courses (auth state) |
| Global state | BehaviorSubject | Authentication across app |
| Direct child access | ViewChild | Admin accessing Dashboard |
| Navigation data | Route params | Course list → Course detail |

### 8. Best Practices We Follow

1. **Unidirectional Data Flow**: Data flows down, events bubble up
2. **Service for Shared State**: Auth, user data, cart items
3. **Smart vs Dumb Components**: Container components handle logic, presentational components just display
4. **Avoid Tight Coupling**: Prefer services over direct ViewChild access
5. **Type Safety**: Always type @Input/@Output properties

### Interview Tips

1. **Know when to use each pattern** - There's no one-size-fits-all
2. **Explain trade-offs** - Services add complexity but provide flexibility
3. **Show understanding of data flow** - Unidirectional is easier to debug
4. **Mention memory management** - Unsubscribe from services
5. **Real examples** - Use actual code from your project