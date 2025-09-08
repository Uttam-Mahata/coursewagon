# Question 6: Explain your routing architecture. How do you implement lazy loading for feature modules?

## Answer

### Current Routing Architecture

CourseWagon currently uses a **traditional eager-loading routing architecture** defined in `app-routing.module.ts`. All components are loaded upfront when the application starts.

### 1. Current Route Structure

```typescript
// app-routing.module.ts
const routes: Routes = [
  // Public routes
  { path: 'home', component: HomeComponent },
  { path: 'terms', component: TermsComponent },
  { path: 'privacy-policy', component: PrivacyPolicyComponent },
  
  // Authentication routes with guards
  { path: 'auth', component: AuthComponent, canActivate: [NonAuthGuard] },
  { path: 'forgot-password', component: ForgotPasswordComponent },
  { path: 'reset-password', component: ResetPasswordComponent },
  
  // Protected routes
  { path: 'profile', component: ProfileComponent, canActivate: [AuthGuard] },
  { path: 'courses', component: CoursesComponent, canActivate: [AuthGuard] },
  { path: 'create-course', component: CourseComponent, canActivate: [AuthGuard] },
  
  // Admin routes
  { path: 'admin', component: AdminComponent, canActivate: [AdminGuard] },
  
  // Nested course routes with parameters
  { 
    path: 'courses/:course_id/subjects', 
    component: SubjectsComponent, 
    canActivate: [AuthGuard] 
  },
  { 
    path: 'courses/:course_id/subjects/:subject_id/content', 
    component: CourseContentComponent,
    canActivate: [AuthGuard]
  },
  
  // Default and wildcard routes
  { path: '', redirectTo: '/home', pathMatch: 'full' },
  { path: '**', redirectTo: '/home' }
];
```

### 2. Route Configuration Options

```typescript
@NgModule({
  imports: [RouterModule.forRoot(routes, { 
    useHash: false,                      // Clean URLs without #
    scrollPositionRestoration: 'enabled', // Restore scroll on navigation
    anchorScrolling: 'enabled',          // Enable anchor scrolling
    scrollOffset: [0, 0]                 // Scroll offset configuration
  })],
  exports: [RouterModule]
})
export class AppRoutingModule { }
```

### 3. Route Guards Architecture

```typescript
// Three types of guards protecting different route groups
export class AuthGuard implements CanActivate {
  // Protects authenticated routes
  canActivate(): boolean {
    if (this.authService.getToken()) {
      return true;
    }
    this.router.navigate(['/auth']);
    return false;
  }
}

export class NonAuthGuard implements CanActivate {
  // Prevents authenticated users from accessing auth pages
  canActivate(): boolean {
    if (!this.authService.getToken()) {
      return true;
    }
    this.router.navigate(['/home']);
    return false;
  }
}

export class AdminGuard implements CanActivate {
  // Protects admin-only routes
  canActivate(): boolean {
    const user = this.authService.getCurrentUser();
    if (user && user.is_admin) {
      return true;
    }
    this.router.navigate(['/home']);
    return false;
  }
}
```

### 4. Why We Don't Use Lazy Loading (Yet)

**Current State:**
- All 19 components loaded in main bundle
- Initial bundle size: ~2.5MB (could be optimized)
- Works fine for current user base

**Reasons for not implementing:**
1. **Moderate app size**: 19 components is manageable
2. **Simple deployment**: Single bundle easier to cache
3. **No performance complaints**: Load time acceptable
4. **Development simplicity**: Easier debugging and testing

### 5. How to Implement Lazy Loading (Future Enhancement)

If we were to implement lazy loading, here's the approach:

#### Step 1: Create Feature Modules

```typescript
// admin/admin.module.ts
@NgModule({
  declarations: [
    AdminComponent,
    AdminDashboardComponent,
    AdminUsersComponent,
    AdminCoursesComponent,
    AdminTestimonialsComponent
  ],
  imports: [
    CommonModule,
    AdminRoutingModule,
    SharedModule
  ]
})
export class AdminModule { }

// admin/admin-routing.module.ts
const routes: Routes = [
  {
    path: '',
    component: AdminComponent,
    children: [
      { path: 'dashboard', component: AdminDashboardComponent },
      { path: 'users', component: AdminUsersComponent },
      { path: 'courses', component: AdminCoursesComponent },
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' }
    ]
  }
];
```

#### Step 2: Update Main Routes for Lazy Loading

```typescript
// app-routing.module.ts with lazy loading
const routes: Routes = [
  // Eager loaded (critical path)
  { path: 'home', component: HomeComponent },
  { path: 'auth', component: AuthComponent, canActivate: [NonAuthGuard] },
  
  // Lazy loaded feature modules
  {
    path: 'admin',
    loadChildren: () => import('./admin/admin.module').then(m => m.AdminModule),
    canLoad: [AdminGuard] // Note: canLoad prevents download if unauthorized
  },
  {
    path: 'courses',
    loadChildren: () => import('./courses/courses.module').then(m => m.CoursesModule),
    canLoad: [AuthGuard]
  },
  {
    path: 'profile',
    loadChildren: () => import('./profile/profile.module').then(m => m.ProfileModule),
    canLoad: [AuthGuard]
  }
];
```

#### Step 3: Preloading Strategy

```typescript
// Custom preloading strategy
export class SelectivePreloadingStrategy implements PreloadingStrategy {
  preload(route: Route, load: () => Observable<any>): Observable<any> {
    // Preload if route has preload flag
    if (route.data && route.data['preload']) {
      return load();
    }
    return of(null);
  }
}

// app-routing.module.ts
RouterModule.forRoot(routes, {
  preloadingStrategy: SelectivePreloadingStrategy,
  // or use built-in: PreloadAllModules
})

// Route with preload flag
{
  path: 'courses',
  loadChildren: () => import('./courses/courses.module').then(m => m.CoursesModule),
  data: { preload: true } // Preload this module
}
```

### 6. Route Parameter Handling

```typescript
// Nested route parameters
// URL: /courses/123/subjects/456/content

export class CourseContentComponent implements OnInit {
  courseId: string;
  subjectId: string;

  constructor(private route: ActivatedRoute) {}

  ngOnInit() {
    // Access nested route parameters
    this.route.params.subscribe(params => {
      this.courseId = params['course_id'];
      this.subjectId = params['subject_id'];
      this.loadContent();
    });

    // Or use snapshot for one-time read
    this.courseId = this.route.snapshot.params['course_id'];
  }
}
```

### 7. Route Resolver Pattern (Used for Redirects)

```typescript
// route-redirect.resolver.ts
@Injectable({ providedIn: 'root' })
export class RouteRedirectResolver implements Resolve<boolean> {
  resolve(route: ActivatedRouteSnapshot): Observable<boolean> {
    // Handle legacy URL redirects
    const courseId = route.params['course_id'];
    const subjectId = route.params['subject_id'];
    
    // Redirect to new URL structure
    this.router.navigate(['/courses', courseId, 'subjects', subjectId, 'content']);
    return of(false);
  }
}
```

### 8. Benefits of Lazy Loading (When We Implement)

```typescript
// Bundle size comparison
// Current (Eager Loading):
// main.js: 2.5MB - Contains everything

// With Lazy Loading:
// main.js: 800KB - Core + Home + Auth
// admin.js: 400KB - Admin module (loaded on demand)
// courses.js: 600KB - Courses module (loaded on demand)
// profile.js: 300KB - Profile module (loaded on demand)

// Result: 68% reduction in initial load
```

### 9. Route Performance Monitoring

```typescript
export class RoutePerformanceService {
  constructor(private router: Router) {
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: NavigationEnd) => {
      // Track route changes
      performance.mark('route-change-end');
      performance.measure('route-change', 'route-change-start', 'route-change-end');
      
      const measure = performance.getEntriesByName('route-change')[0];
      console.log(`Route change took: ${measure.duration}ms`);
    });
  }
}
```

### 10. Migration Plan for Lazy Loading

**Phase 1: Identify Candidates**
- Admin module (5 components, admin-only)
- Profile module (3 components, auth required)
- Legal pages module (terms, privacy, rarely accessed)

**Phase 2: Create Feature Modules**
- Move components to feature folders
- Create routing modules
- Share common imports via SharedModule

**Phase 3: Update Routes**
- Convert to loadChildren syntax
- Add canLoad guards
- Implement preloading strategy

**Phase 4: Optimize**
- Analyze bundle sizes
- Add route-level code splitting
- Implement progressive loading

### Interview Talking Points

1. **Current Architecture**: Explain why eager loading works for current scale
2. **Future Planning**: Show you understand when lazy loading becomes necessary
3. **Implementation Knowledge**: Demonstrate you know HOW to implement it
4. **Performance Awareness**: Discuss bundle sizes and load times
5. **Trade-offs**: Lazy loading adds complexity but improves performance