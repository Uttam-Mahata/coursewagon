# Question 10: Explain the purpose of NonAuthGuard and AdminGuard. How do they work together with AuthGuard?

## Answer

### Overview of Three-Guard System

CourseWagon implements three complementary guards that work together to create a complete authorization system:

1. **AuthGuard**: Ensures user is logged in
2. **NonAuthGuard**: Ensures user is NOT logged in  
3. **AdminGuard**: Ensures user is admin

### 1. NonAuthGuard Implementation

**Purpose:** Prevents authenticated users from accessing auth pages (login/signup)

```typescript
// auth.guard.ts
@Injectable({
  providedIn: 'root'
})
export class NonAuthGuard implements CanActivate {
  
  constructor(
    private authService: AuthService, 
    private router: Router
  ) {}
  
  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    
    // Check if we have a token
    const token = this.authService.getToken();
    
    if (!token) {
      return true;  // No token = not authenticated = allow access
    }
    
    // If token exists, user is logged in, redirect to courses
    this.router.navigate(['/courses']);
    return false;  // Block access to auth pages
  }
}
```

**Use Cases:**
```typescript
// Prevents logged-in users from seeing login page
{ path: 'auth', component: AuthComponent, canActivate: [NonAuthGuard] }
{ path: 'forgot-password', component: ForgotPasswordComponent, canActivate: [NonAuthGuard] }
```

### 2. AdminGuard Implementation

**Purpose:** Restricts access to admin-only features

```typescript
// auth.guard.ts
@Injectable({
  providedIn: 'root'
})
export class AdminGuard implements CanActivate {
  
  constructor(
    private authService: AuthService, 
    private router: Router
  ) {}
  
  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    
    const user = this.authService.getCurrentUser();
    
    // Check two conditions:
    // 1. User exists (is authenticated)
    // 2. User has admin flag
    if (user && user.is_admin) {
      return true;  // Allow access to admin routes
    }
    
    // Not admin or not authenticated, redirect to home
    this.router.navigate(['/home']);
    return false;
  }
}
```

**Use Case:**
```typescript
// Admin panel protection
{ path: 'admin', component: AdminComponent, canActivate: [AdminGuard] }
```

### 3. How They Work Together

#### Scenario Analysis:

```typescript
// Route configurations showing guard cooperation
const routes: Routes = [
  // 1. Public routes - No guards
  { path: 'home', component: HomeComponent },
  { path: 'terms', component: TermsComponent },
  
  // 2. Auth pages - NonAuthGuard prevents logged-in access
  { path: 'auth', component: AuthComponent, canActivate: [NonAuthGuard] },
  { path: 'forgot-password', component: ForgotPasswordComponent, canActivate: [NonAuthGuard] },
  
  // 3. User routes - AuthGuard ensures authentication
  { path: 'profile', component: ProfileComponent, canActivate: [AuthGuard] },
  { path: 'courses', component: CoursesComponent, canActivate: [AuthGuard] },
  
  // 4. Admin routes - AdminGuard ensures admin role
  { path: 'admin', component: AdminComponent, canActivate: [AdminGuard] },
  
  // 5. Could combine guards for extra security
  { 
    path: 'admin/sensitive', 
    component: SensitiveComponent, 
    canActivate: [AuthGuard, AdminGuard]  // Both must pass
  }
];
```

### 4. User Flow Examples

#### Flow 1: Non-authenticated User
```typescript
/*
User (not logged in) tries to access:

/home          → ✅ Allowed (no guard)
/auth          → ✅ Allowed (NonAuthGuard passes - no token)
/profile       → ❌ Blocked (AuthGuard fails) → Redirect to /auth
/admin         → ❌ Blocked (AdminGuard fails) → Redirect to /home
*/
```

#### Flow 2: Regular Authenticated User
```typescript
/*
User (logged in, not admin) tries to access:

/home          → ✅ Allowed (no guard)
/auth          → ❌ Blocked (NonAuthGuard fails) → Redirect to /courses
/profile       → ✅ Allowed (AuthGuard passes)
/admin         → ❌ Blocked (AdminGuard fails - not admin) → Redirect to /home
*/
```

#### Flow 3: Admin User
```typescript
/*
Admin user (logged in, is_admin: true) tries to access:

/home          → ✅ Allowed (no guard)
/auth          → ❌ Blocked (NonAuthGuard fails) → Redirect to /courses
/profile       → ✅ Allowed (AuthGuard passes)
/admin         → ✅ Allowed (AdminGuard passes)
*/
```

### 5. Guard Interaction Matrix

| Route Type | No Auth | Regular User | Admin User | Guards Used |
|------------|---------|--------------|------------|-------------|
| Public Pages | ✅ | ✅ | ✅ | None |
| Auth Pages | ✅ | ❌ → /courses | ❌ → /courses | NonAuthGuard |
| User Pages | ❌ → /auth | ✅ | ✅ | AuthGuard |
| Admin Pages | ❌ → /home | ❌ → /home | ✅ | AdminGuard |

### 6. Why This Three-Guard Pattern?

#### Benefits:

```typescript
// 1. Separation of Concerns
// Each guard has single responsibility
class AuthGuard {     // Only checks: "Is user logged in?"
class NonAuthGuard {   // Only checks: "Is user NOT logged in?"
class AdminGuard {     // Only checks: "Is user admin?"

// 2. Better UX
// NonAuthGuard prevents confusion
// Without NonAuthGuard: Logged-in user sees login page
// With NonAuthGuard: Automatically redirected to courses

// 3. Flexible Combinations
{ 
  path: 'super-admin',
  canActivate: [AuthGuard, AdminGuard, SuperAdminGuard]
  // Can layer multiple guards for complex requirements
}

// 4. Clear Intent in Routes
{ path: 'auth', canActivate: [NonAuthGuard] }  // Clear: only for non-authenticated
{ path: 'admin', canActivate: [AdminGuard] }    // Clear: only for admins
```

### 7. Enhanced Implementation Pattern

```typescript
// Better implementation with role-based system
export enum UserRole {
  GUEST = 'guest',
  USER = 'user',
  INSTRUCTOR = 'instructor',
  ADMIN = 'admin',
  SUPER_ADMIN = 'super_admin'
}

// Generic role guard
@Injectable({ providedIn: 'root' })
export class RoleGuard implements CanActivate {
  
  canActivate(route: ActivatedRouteSnapshot): boolean | UrlTree {
    const requiredRoles = route.data['roles'] as UserRole[];
    const user = this.authService.getCurrentUser();
    
    if (!user) {
      return this.router.createUrlTree(['/auth']);
    }
    
    if (requiredRoles.includes(user.role)) {
      return true;
    }
    
    // Redirect based on role
    switch(user.role) {
      case UserRole.ADMIN:
        return this.router.createUrlTree(['/admin']);
      case UserRole.INSTRUCTOR:
        return this.router.createUrlTree(['/instructor']);
      default:
        return this.router.createUrlTree(['/courses']);
    }
  }
}

// Usage with role-based guard
const routes: Routes = [
  { 
    path: 'instructor',
    component: InstructorComponent,
    canActivate: [RoleGuard],
    data: { roles: [UserRole.INSTRUCTOR, UserRole.ADMIN] }
  },
  { 
    path: 'admin',
    component: AdminComponent,
    canActivate: [RoleGuard],
    data: { roles: [UserRole.ADMIN, UserRole.SUPER_ADMIN] }
  }
];
```

### 8. Common Patterns & Anti-Patterns

#### Good Patterns:
```typescript
// ✅ Clear single responsibility
export class PremiumGuard {
  canActivate(): boolean {
    return this.authService.getCurrentUser()?.isPremium || false;
  }
}

// ✅ Meaningful redirects
export class NonAuthGuard {
  canActivate(): boolean | UrlTree {
    if (!this.authService.getToken()) {
      return true;
    }
    // Redirect to user's default page, not generic home
    const user = this.authService.getCurrentUser();
    const defaultRoute = user?.is_admin ? '/admin' : '/courses';
    return this.router.createUrlTree([defaultRoute]);
  }
}
```

#### Anti-Patterns:
```typescript
// ❌ Guard doing too much
export class SuperGuard {
  canActivate(): boolean {
    // Checking everything in one guard
    if (!this.authService.getToken()) {
      this.router.navigate(['/auth']);
      return false;
    }
    if (this.authService.getCurrentUser()?.is_admin) {
      return true;
    }
    if (this.route.data['requiresPremium']) {
      // Too many responsibilities!
    }
  }
}

// ❌ Inconsistent redirects
export class BadGuard {
  canActivate(): boolean {
    if (!authorized) {
      // Sometimes redirects, sometimes doesn't
      if (Math.random() > 0.5) {
        this.router.navigate(['/home']);
      }
      return false;
    }
  }
}
```

### 9. Testing the Guards Together

```typescript
describe('Guard Integration', () => {
  let authGuard: AuthGuard;
  let nonAuthGuard: NonAuthGuard;
  let adminGuard: AdminGuard;
  let authService: jasmine.SpyObj<AuthService>;
  
  beforeEach(() => {
    // Setup test environment
  });
  
  it('should handle unauthenticated user flow', () => {
    authService.getToken.and.returnValue(null);
    authService.getCurrentUser.and.returnValue(null);
    
    // NonAuthGuard allows access to auth page
    expect(nonAuthGuard.canActivate()).toBe(true);
    
    // AuthGuard blocks access to protected pages
    expect(authGuard.canActivate()).toBe(false);
    
    // AdminGuard blocks access to admin pages
    expect(adminGuard.canActivate()).toBe(false);
  });
  
  it('should handle regular user flow', () => {
    authService.getToken.and.returnValue('valid-token');
    authService.getCurrentUser.and.returnValue({ 
      id: 1, 
      is_admin: false 
    });
    
    // NonAuthGuard blocks auth pages for logged-in users
    expect(nonAuthGuard.canActivate()).toBe(false);
    
    // AuthGuard allows access to protected pages
    expect(authGuard.canActivate()).toBe(true);
    
    // AdminGuard blocks non-admin users
    expect(adminGuard.canActivate()).toBe(false);
  });
  
  it('should handle admin user flow', () => {
    authService.getToken.and.returnValue('admin-token');
    authService.getCurrentUser.and.returnValue({ 
      id: 1, 
      is_admin: true 
    });
    
    // Admin can't access auth pages (already logged in)
    expect(nonAuthGuard.canActivate()).toBe(false);
    
    // Admin can access protected pages
    expect(authGuard.canActivate()).toBe(true);
    
    // Admin can access admin pages
    expect(adminGuard.canActivate()).toBe(true);
  });
});
```

### 10. Future Enhancements

```typescript
// 1. Add instructor guard
export class InstructorGuard implements CanActivate {
  canActivate(): boolean {
    const user = this.authService.getCurrentUser();
    return user?.role === 'instructor' || user?.is_admin;
  }
}

// 2. Add enrollment guard for course content
export class EnrollmentGuard implements CanActivate {
  canActivate(route: ActivatedRouteSnapshot): Observable<boolean> {
    const courseId = +route.params['course_id'];
    return this.courseService.isUserEnrolled(courseId);
  }
}

// 3. Add time-based guard
export class BusinessHoursGuard implements CanActivate {
  canActivate(): boolean {
    const hour = new Date().getHours();
    return hour >= 9 && hour < 17;  // 9 AM to 5 PM only
  }
}
```

### Interview Talking Points

1. **Separation of Concerns**: Each guard has one clear responsibility
2. **User Experience**: NonAuthGuard prevents confusion for logged-in users
3. **Security Layers**: Multiple guards can combine for complex requirements
4. **Redirect Logic**: Each guard redirects to appropriate location
5. **Scalability**: Easy to add new guards for new roles/requirements
6. **Testing**: Each guard can be tested independently and together