# Question 7: Walk through your authentication guard implementation. How does AuthGuard determine if a user can access a route?

## Answer

### AuthGuard Implementation Overview

AuthGuard is a route guard that protects authenticated routes by checking if the user has a valid JWT token before allowing access.

### 1. Current AuthGuard Implementation

```typescript
// auth.guard.ts
@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  
  constructor(
    private authService: AuthService, 
    private router: Router
  ) {}
  
  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    
    // Step 1: Check if we have a token in localStorage
    const token = this.authService.getToken();
    
    // Step 2: If token exists, allow access
    if (token) {
      return true;
    }
    
    // Step 3: If no token, redirect to login with return URL
    this.router.navigate(['/auth'], { 
      queryParams: { returnUrl: state.url } 
    });
    return false;
  }
}
```

### 2. How AuthGuard Works - Step by Step

```typescript
// When user navigates to /profile

// 1. Router checks route configuration
{ path: 'profile', component: ProfileComponent, canActivate: [AuthGuard] }

// 2. Router calls AuthGuard.canActivate()
canActivate(route, state) {
  // route = ActivatedRouteSnapshot for '/profile'
  // state = RouterStateSnapshot with url: '/profile'
}

// 3. AuthGuard checks authentication
const token = this.authService.getToken();
// getToken() returns: localStorage.getItem('token')

// 4. Decision logic
if (token) {
  // Token exists: "eyJhbGciOiJIUzI1NiIs..."
  return true;  // Allow navigation to /profile
} else {
  // No token found
  this.router.navigate(['/auth'], { 
    queryParams: { returnUrl: '/profile' }  // Save intended destination
  });
  return false;  // Block navigation
}
```

### 3. Integration with AuthService

```typescript
// auth.service.ts - Methods used by AuthGuard
export class AuthService {
  private tokenKey = 'token';
  private userKey = 'user';
  
  getToken(): string | null {
    // Simply retrieves token from localStorage
    return localStorage.getItem(this.tokenKey);
  }
  
  getCurrentUser(): any {
    const userStr = localStorage.getItem(this.userKey);
    return userStr ? JSON.parse(userStr) : null;
  }
  
  // Called after successful login
  storeAuthData(token: string, user: any): void {
    localStorage.setItem(this.tokenKey, token);
    localStorage.setItem(this.userKey, JSON.stringify(user));
    
    // Update observables for reactive components
    this.currentUserSource.next(user);
    this.isLoggedInSource.next(true);
  }
}
```

### 4. Return URL Pattern Implementation

```typescript
// auth.component.ts - Login component handles return URL
export class AuthComponent implements OnInit {
  returnUrl: string;
  
  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService
  ) {}
  
  ngOnInit() {
    // Capture return URL from query params
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/courses';
  }
  
  login() {
    this.authService.login(this.email, this.password).subscribe({
      next: (response) => {
        // After successful login, navigate to return URL
        this.router.navigateByUrl(this.returnUrl);
      },
      error: (error) => {
        this.showError('Invalid credentials');
      }
    });
  }
}
```

### 5. Current Limitations & Improvements

#### Current Limitations:
```typescript
// 1. No token validation - just checks existence
if (token) {
  return true;  // Token might be expired!
}

// 2. Synchronous check only
// Can't make async API call to validate

// 3. No role-based checks in base AuthGuard
// Admin check is in separate AdminGuard
```

#### Improved Implementation:

```typescript
// Enhanced AuthGuard with token validation
export class EnhancedAuthGuard implements CanActivate {
  
  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean | UrlTree> {
    
    return this.authService.isAuthenticated$.pipe(
      take(1),
      map(isAuthenticated => {
        if (isAuthenticated) {
          // Additional check: Token expiration
          if (this.isTokenExpired()) {
            return this.router.createUrlTree(['/auth'], {
              queryParams: { returnUrl: state.url, reason: 'expired' }
            });
          }
          
          // Check role requirements if specified
          const requiredRole = route.data['role'];
          if (requiredRole && !this.hasRole(requiredRole)) {
            return this.router.createUrlTree(['/unauthorized']);
          }
          
          return true;
        }
        
        // Not authenticated
        return this.router.createUrlTree(['/auth'], {
          queryParams: { returnUrl: state.url }
        });
      })
    );
  }
  
  private isTokenExpired(): boolean {
    const token = this.authService.getToken();
    if (!token) return true;
    
    try {
      // Decode JWT to check expiration
      const payload = JSON.parse(atob(token.split('.')[1]));
      const expirationTime = payload.exp * 1000; // Convert to milliseconds
      return Date.now() > expirationTime;
    } catch {
      return true;
    }
  }
  
  private hasRole(requiredRole: string): boolean {
    const user = this.authService.getCurrentUser();
    return user && user.role === requiredRole;
  }
}
```

### 6. Guard Execution Flow Diagram

```typescript
/*
User navigates to /profile
         |
         v
Router checks route config
         |
         v
    Has guards?
    /         \
   No          Yes
   |            |
   v            v
Navigate    Call AuthGuard.canActivate()
directly            |
                   v
              Check token
              /         \
         Exists      No token
            |            |
            v            v
       Return true   Store return URL
       (Allow)       Navigate to /auth
                     Return false (Block)
*/
```

### 7. Multiple Guards Execution

```typescript
// When route has multiple guards
{ 
  path: 'admin/users', 
  component: AdminUsersComponent,
  canActivate: [AuthGuard, AdminGuard, PermissionGuard]
}

// Execution order:
// 1. AuthGuard - Check if logged in
// 2. AdminGuard - Check if admin (only if AuthGuard passes)
// 3. PermissionGuard - Check specific permission (only if AdminGuard passes)
// ALL must return true for navigation to proceed
```

### 8. Testing AuthGuard

```typescript
// auth.guard.spec.ts
describe('AuthGuard', () => {
  let guard: AuthGuard;
  let authService: jasmine.SpyObj<AuthService>;
  let router: jasmine.SpyObj<Router>;
  
  beforeEach(() => {
    const authSpy = jasmine.createSpyObj('AuthService', ['getToken']);
    const routerSpy = jasmine.createSpyObj('Router', ['navigate']);
    
    TestBed.configureTestingModule({
      providers: [
        AuthGuard,
        { provide: AuthService, useValue: authSpy },
        { provide: Router, useValue: routerSpy }
      ]
    });
    
    guard = TestBed.inject(AuthGuard);
    authService = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    router = TestBed.inject(Router) as jasmine.SpyObj<Router>;
  });
  
  it('should allow access when token exists', () => {
    authService.getToken.and.returnValue('valid-token');
    
    const result = guard.canActivate(
      {} as ActivatedRouteSnapshot,
      { url: '/profile' } as RouterStateSnapshot
    );
    
    expect(result).toBe(true);
    expect(router.navigate).not.toHaveBeenCalled();
  });
  
  it('should redirect to auth when no token', () => {
    authService.getToken.and.returnValue(null);
    
    const result = guard.canActivate(
      {} as ActivatedRouteSnapshot,
      { url: '/profile' } as RouterStateSnapshot
    );
    
    expect(result).toBe(false);
    expect(router.navigate).toHaveBeenCalledWith(
      ['/auth'], 
      { queryParams: { returnUrl: '/profile' } }
    );
  });
});
```

### 9. Common Use Cases

```typescript
// 1. Protecting user profile
{ path: 'profile', component: ProfileComponent, canActivate: [AuthGuard] }

// 2. Protecting course creation
{ path: 'create-course', component: CourseComponent, canActivate: [AuthGuard] }

// 3. Nested route protection
{ 
  path: 'courses/:id/content', 
  component: ContentComponent, 
  canActivate: [AuthGuard, EnrollmentGuard] 
}

// 4. Lazy loaded module protection
{
  path: 'premium',
  loadChildren: () => import('./premium/premium.module'),
  canLoad: [AuthGuard, PremiumGuard]  // Prevents download if not authorized
}
```

### 10. Security Considerations

```typescript
// Current: Client-side only
// Token validation happens on client
// Can be bypassed by modifying localStorage

// Best Practice: Server validation
// Every API call validates token server-side
// Guards are first line of defense, not only defense

// HTTP Interceptor adds token to requests
export class AuthInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const token = this.authService.getToken();
    
    if (token) {
      req = req.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      });
    }
    
    return next.handle(req);
  }
}
```

### Interview Talking Points

1. **Simple but Effective**: Current implementation is straightforward and works
2. **Return URL Pattern**: Good UX - users go where they intended after login
3. **Room for Enhancement**: Token validation, async checks, role-based access
4. **Security Awareness**: Client-side guards are UX feature, not security feature
5. **Testing**: Guards should be unit tested for all scenarios