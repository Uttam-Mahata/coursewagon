# Question 8: What's the difference between CanActivate, CanDeactivate, and CanLoad guards?

## Answer

### Overview of Angular Route Guards

Angular provides different types of guards for different scenarios in the navigation lifecycle. Each guard serves a specific purpose and executes at different times.

### 1. CanActivate Guard

**Purpose:** Determines if a route can be activated (navigated to)

**When it runs:** Before navigating TO a route

**Use cases:** Authentication, authorization, feature flags

#### Implementation Example:

```typescript
// Our AuthGuard implementation
@Injectable({ providedIn: 'root' })
export class AuthGuard implements CanActivate {
  
  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    
    const token = this.authService.getToken();
    
    if (token) {
      return true;  // Allow navigation
    }
    
    // Redirect to login
    return this.router.createUrlTree(['/auth'], {
      queryParams: { returnUrl: state.url }
    });
  }
}

// Usage in routes
{ 
  path: 'profile', 
  component: ProfileComponent, 
  canActivate: [AuthGuard]  // Checks before entering
}
```

#### Real-world Examples in CourseWagon:

```typescript
// 1. Protecting authenticated routes
{ path: 'courses', component: CoursesComponent, canActivate: [AuthGuard] }

// 2. Admin-only routes
{ path: 'admin', component: AdminComponent, canActivate: [AdminGuard] }

// 3. Preventing authenticated users from auth page
{ path: 'auth', component: AuthComponent, canActivate: [NonAuthGuard] }
```

### 2. CanDeactivate Guard

**Purpose:** Determines if a user can leave a route

**When it runs:** Before navigating AWAY from a route

**Use cases:** Unsaved changes warning, form validation, cleanup

#### Implementation Example (Not Currently Used, But Should Be):

```typescript
// Interface for components that can be deactivated
export interface CanComponentDeactivate {
  canDeactivate: () => Observable<boolean> | Promise<boolean> | boolean;
}

// Generic CanDeactivate guard
@Injectable({ providedIn: 'root' })
export class CanDeactivateGuard implements CanDeactivate<CanComponentDeactivate> {
  
  canDeactivate(
    component: CanComponentDeactivate,
    currentRoute: ActivatedRouteSnapshot,
    currentState: RouterStateSnapshot,
    nextState?: RouterStateSnapshot
  ): Observable<boolean> | Promise<boolean> | boolean {
    
    return component.canDeactivate ? component.canDeactivate() : true;
  }
}

// Component implementation - Perfect for CourseComponent
export class CourseComponent implements CanComponentDeactivate {
  hasUnsavedChanges = false;
  courseForm: FormGroup;
  
  ngOnInit() {
    this.courseForm.valueChanges.subscribe(() => {
      this.hasUnsavedChanges = true;
    });
  }
  
  canDeactivate(): Observable<boolean> | Promise<boolean> | boolean {
    if (!this.hasUnsavedChanges) {
      return true;  // No changes, can leave
    }
    
    // Confirm dialog
    return confirm('You have unsaved changes. Do you really want to leave?');
  }
  
  saveCourse() {
    this.courseService.saveCourse(this.courseForm.value).subscribe(() => {
      this.hasUnsavedChanges = false;  // Reset flag after save
    });
  }
}

// Route configuration
{ 
  path: 'create-course', 
  component: CourseComponent,
  canActivate: [AuthGuard],
  canDeactivate: [CanDeactivateGuard]  // Prevents accidental navigation
}
```

#### Where We Should Use CanDeactivate:

```typescript
// 1. Course creation form
// User spending time creating course content
{ 
  path: 'create-course', 
  component: CourseComponent,
  canDeactivate: [UnsavedChangesGuard]
}

// 2. Profile editing
// Prevent losing profile changes
{ 
  path: 'profile/edit', 
  component: ProfileEditComponent,
  canDeactivate: [UnsavedChangesGuard]
}

// 3. Write review component
// Don't lose review text
{ 
  path: 'write-review', 
  component: WriteReviewComponent,
  canDeactivate: [UnsavedChangesGuard]
}
```

### 3. CanLoad Guard

**Purpose:** Determines if a lazy-loaded module can be loaded

**When it runs:** Before downloading the lazy-loaded module code

**Use cases:** Prevent unauthorized users from downloading admin code

#### Implementation Example:

```typescript
// CanLoad guard for lazy modules
@Injectable({ providedIn: 'root' })
export class AdminCanLoadGuard implements CanLoad {
  
  canLoad(
    route: Route,
    segments: UrlSegment[]
  ): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    
    const user = this.authService.getCurrentUser();
    
    // Check if user is admin BEFORE downloading admin module
    if (user && user.is_admin) {
      return true;  // Download and load module
    }
    
    // Don't download module, redirect
    return this.router.createUrlTree(['/unauthorized']);
  }
}

// Lazy loading with CanLoad
const routes: Routes = [
  {
    path: 'admin',
    loadChildren: () => import('./admin/admin.module').then(m => m.AdminModule),
    canLoad: [AdminCanLoadGuard]  // Prevents module download
  }
];
```

### 4. Key Differences Table

| Guard Type | When It Runs | Purpose | Return Value | Use Case |
|------------|--------------|---------|--------------|----------|
| **CanActivate** | Before entering route | Check access permission | boolean/UrlTree | Auth check, role check |
| **CanDeactivate** | Before leaving route | Prevent data loss | boolean | Unsaved changes warning |
| **CanLoad** | Before downloading module | Prevent code download | boolean/UrlTree | Lazy module auth |

### 5. Other Guard Types (Bonus Knowledge)

#### CanActivateChild
```typescript
// Protects all child routes
@Injectable({ providedIn: 'root' })
export class AuthChildGuard implements CanActivateChild {
  canActivateChild(
    childRoute: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean | UrlTree> | boolean | UrlTree {
    // Same as CanActivate but for child routes
    return this.authService.isAuthenticated();
  }
}

// Usage
{
  path: 'courses',
  canActivateChild: [AuthChildGuard],  // Applies to all children
  children: [
    { path: 'list', component: CourseListComponent },
    { path: 'detail/:id', component: CourseDetailComponent },
    { path: 'create', component: CreateCourseComponent }
  ]
}
```

#### Resolve (Deprecated in favor of Resolvers)
```typescript
// Pre-fetch data before route activation
@Injectable({ providedIn: 'root' })
export class CourseResolver implements Resolve<Course> {
  resolve(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<Course> {
    const courseId = route.params['id'];
    return this.courseService.getCourse(courseId);
  }
}

// Usage
{ 
  path: 'course/:id', 
  component: CourseDetailComponent,
  resolve: { course: CourseResolver }  // Data available in component
}
```

### 6. Guard Execution Order

```typescript
// When navigating FROM RouteA TO RouteB:
/*
1. CanDeactivate (RouteA) - Can we leave?
2. CanLoad (RouteB) - Can we download? (if lazy)
3. CanActivate (RouteB) - Can we enter?
4. CanActivateChild (RouteB) - Can we enter children?
5. Resolve (RouteB) - Fetch required data

If ANY guard returns false, navigation is cancelled
*/

// Example flow
{
  path: 'admin',
  loadChildren: () => import('./admin/admin.module'),
  canLoad: [AdminCanLoadGuard],        // Step 1: Check before download
  canActivate: [AdminActivateGuard],   // Step 2: Check before activation
  canDeactivate: [SaveChangesGuard],   // Checks when leaving
  resolve: { data: AdminDataResolver } // Step 3: Fetch data
}
```

### 7. Practical Implementation Strategy

```typescript
// How we could improve CourseWagon with all guard types

// 1. CanActivate - Already using for auth
{ path: 'profile', canActivate: [AuthGuard] }

// 2. CanDeactivate - Should add for forms
{ 
  path: 'create-course', 
  canActivate: [AuthGuard],
  canDeactivate: [UnsavedChangesGuard]
}

// 3. CanLoad - When we implement lazy loading
{
  path: 'admin',
  loadChildren: () => import('./admin/admin.module'),
  canLoad: [AdminGuard],  // Don't let non-admins download admin code
  canActivate: [AuthGuard] // Double-check on activation
}

// 4. CanActivateChild - For nested course routes
{
  path: 'courses/:id',
  canActivateChild: [EnrollmentGuard],  // Must be enrolled
  children: [
    { path: 'content', component: ContentComponent },
    { path: 'quiz', component: QuizComponent },
    { path: 'certificate', component: CertificateComponent }
  ]
}
```

### 8. Testing Different Guard Types

```typescript
// Testing CanDeactivate
it('should prevent navigation with unsaved changes', () => {
  component.hasUnsavedChanges = true;
  spyOn(window, 'confirm').and.returnValue(false);
  
  const canDeactivate = component.canDeactivate();
  
  expect(canDeactivate).toBe(false);
  expect(window.confirm).toHaveBeenCalledWith(
    'You have unsaved changes. Do you really want to leave?'
  );
});

// Testing CanLoad
it('should prevent module load for non-admin', () => {
  authService.getCurrentUser.and.returnValue({ is_admin: false });
  
  const canLoad = guard.canLoad(route, segments);
  
  expect(canLoad).toEqual(router.createUrlTree(['/unauthorized']));
});
```

### Interview Talking Points

1. **Know all guard types**: Shows comprehensive Angular knowledge
2. **Understand lifecycle**: When each guard executes in navigation
3. **Real examples**: Where you'd use each in CourseWagon
4. **Security vs UX**: CanLoad for security, CanDeactivate for UX
5. **Future improvements**: How you'd enhance current implementation