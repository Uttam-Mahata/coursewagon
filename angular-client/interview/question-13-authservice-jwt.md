# Question 13: Walk through your AuthService implementation. How do you handle JWT token management?

## Answer

### AuthService Overview

The AuthService is the core authentication system in CourseWagon, managing JWT tokens, user state, and authentication flow.

### 1. Service Architecture

```typescript
// auth.service.ts
@Injectable({
  providedIn: 'root'  // Singleton service
})
export class AuthService {
  private authUrl = environment.authApiUrl;
  private tokenKey = 'auth_token';      // localStorage key for JWT
  private userKey = 'current_user';     // localStorage key for user data
  
  // Observable sources for reactive state
  private currentUserSource = new BehaviorSubject<any>(null);
  private isLoggedInSource = new BehaviorSubject<boolean>(false);
  
  // Public observables for components to subscribe
  currentUser$ = this.currentUserSource.asObservable();
  isLoggedIn$ = this.isLoggedInSource.asObservable();

  constructor(
    private http: HttpClient, 
    private router: Router,
    private firebaseAuthService: FirebaseAuthService
  ) {
    this.checkAuthState();  // Initialize auth state on service creation
  }
}
```

### 2. JWT Token Flow

#### Login Process:
```typescript
login(email: string, password: string, rememberMe: boolean = false): Observable<any> {
  console.log(`Attempting to login with ${email}, remember me: ${rememberMe}`);
  
  // 1. Send credentials to backend
  return this.http.post(`${this.authUrl}/login`, { 
    email, 
    password,
    remember_me: rememberMe 
  }).pipe(
    tap((response: any) => {
      // 2. Backend returns JWT token and user data
      // Response structure: { access_token: "eyJhb...", user: {...} }
      
      console.log('Login successful, storing auth data', response);
      
      // 3. Store token and user data
      this.storeAuthData(response.access_token, response.user);
    }),
    catchError(error => {
      console.error('Login failed:', error);
      return throwError(error);
    })
  );
}

storeAuthData(token: string, user: any): void {
  // Store JWT in localStorage
  localStorage.setItem(this.tokenKey, token);
  
  // Store user data
  this.storeUser(user);
}

private storeUser(user: any): void {
  // Store user object in localStorage
  localStorage.setItem(this.userKey, JSON.stringify(user));
  
  // Update observables for reactive components
  this.currentUserSource.next(user);
  this.isLoggedInSource.next(true);
}
```

### 3. Token Persistence & Initialization

```typescript
checkAuthState(): void {
  // Called in constructor to restore auth state
  const token = this.getToken();
  const user = this.getCurrentUser();
  
  if (token && user) {
    // Valid session found
    this.currentUserSource.next(user);
    this.isLoggedInSource.next(true);
    
    // Optional: Validate token with backend
    // this.validateToken(token).subscribe(...);
    
    console.log('Auth state restored', {
      token: token.substring(0, 10) + '...', 
      user
    });
  } else {
    // No valid session
    this.clearAuthData();
    console.log('No valid auth session found');
  }
}

getToken(): string | null {
  return localStorage.getItem(this.tokenKey);
}

getCurrentUser(): any {
  const userStr = localStorage.getItem(this.userKey);
  return userStr ? JSON.parse(userStr) : null;
}
```

### 4. Token Usage in HTTP Requests

```typescript
// auth.interceptor.ts - Automatically adds JWT to requests
export class AuthInterceptor implements HttpInterceptor {
  constructor(private authService: AuthService) {}
  
  intercept(
    req: HttpRequest<any>, 
    next: HttpHandler
  ): Observable<HttpEvent<any>> {
    // Get token from AuthService
    const token = this.authService.getToken();
    
    if (token) {
      // Clone request and add Authorization header
      req = req.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      });
    }
    
    return next.handle(req).pipe(
      catchError(error => {
        if (error.status === 401) {
          // Token expired or invalid
          this.authService.logout();
          console.error('Unauthorized - logging out');
        }
        return throwError(error);
      })
    );
  }
}
```

### 5. Logout & Token Cleanup

```typescript
logout(): void {
  // 1. Clear observables first (update UI immediately)
  this.currentUserSource.next(null);
  this.isLoggedInSource.next(false);
  
  // 2. Clear stored data
  this.clearAuthData();
  
  // 3. Navigate to login
  this.router.navigate(['/auth']);
}

private clearAuthData(): void {
  // Remove JWT token
  localStorage.removeItem(this.tokenKey);
  
  // Remove user data
  localStorage.removeItem(this.userKey);
  
  // Update observables
  this.currentUserSource.next(null);
  this.isLoggedInSource.next(false);
}
```

### 6. JWT Structure & Decoding

```typescript
// JWT token structure (not implemented but important to understand)
interface JWTPayload {
  sub: string;        // Subject (user ID)
  email: string;      // User email
  exp: number;        // Expiration timestamp
  iat: number;        // Issued at timestamp
  role: string;       // User role
  permissions: string[];
}

// How to decode JWT (if needed)
decodeToken(token: string): JWTPayload | null {
  try {
    // JWT structure: header.payload.signature
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64).split('').map(c => {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      }).join('')
    );
    
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Failed to decode token:', error);
    return null;
  }
}

// Check if token is expired
isTokenExpired(token: string): boolean {
  const decoded = this.decodeToken(token);
  if (!decoded || !decoded.exp) return true;
  
  const expirationDate = new Date(decoded.exp * 1000);
  return expirationDate < new Date();
}
```

### 7. Token Refresh Strategy (Not Implemented Yet)

```typescript
// Future enhancement: Auto-refresh tokens
refreshToken(): Observable<any> {
  const currentToken = this.getToken();
  
  if (!currentToken) {
    return throwError('No token to refresh');
  }
  
  return this.http.post(`${this.authUrl}/refresh`, {
    token: currentToken
  }).pipe(
    tap((response: any) => {
      // Store new token
      localStorage.setItem(this.tokenKey, response.access_token);
    }),
    catchError(error => {
      // Refresh failed, logout
      this.logout();
      return throwError(error);
    })
  );
}

// Auto-refresh before expiration
setupTokenRefresh(): void {
  interval(60000).pipe(  // Check every minute
    filter(() => {
      const token = this.getToken();
      if (!token) return false;
      
      const decoded = this.decodeToken(token);
      const expiresIn = decoded.exp * 1000 - Date.now();
      
      // Refresh if expires in less than 5 minutes
      return expiresIn < 300000 && expiresIn > 0;
    }),
    switchMap(() => this.refreshToken())
  ).subscribe();
}
```

### 8. Social Authentication Integration

```typescript
// Google Sign-In with Firebase
async signInWithGoogle(): Promise<any> {
  try {
    // 1. Sign in with Firebase
    const firebaseResult = await this.firebaseAuthService.signInWithGoogle();
    const { user, accessToken } = firebaseResult;
    
    // 2. Exchange Firebase token for backend JWT
    const backendResponse = await this.http.post(
      `${this.authUrl}/google-auth`,
      {
        firebase_token: accessToken,
        user_data: {
          uid: user.uid,
          email: user.email,
          display_name: user.displayName,
          photo_url: user.photoURL,
          email_verified: user.emailVerified
        }
      }
    ).toPromise();
    
    // 3. Store backend JWT
    if (backendResponse && backendResponse.access_token) {
      this.storeAuthData(
        backendResponse.access_token, 
        backendResponse.user
      );
      return backendResponse;
    }
    
    throw new Error('Invalid response from backend');
  } catch (error) {
    console.error('Google sign-in error:', error);
    throw error;
  }
}
```

### 9. Security Considerations

```typescript
// Current Implementation Strengths:
// ✅ Token stored in localStorage (persists across sessions)
// ✅ Token automatically added to all HTTP requests
// ✅ 401 responses trigger logout
// ✅ Observables for reactive UI updates

// Security Improvements Needed:
// ⚠️ No token expiration checking on frontend
// ⚠️ No token refresh mechanism
// ⚠️ localStorage vulnerable to XSS
// ⚠️ No token rotation on sensitive operations

// Better Security Implementation:
class SecureAuthService {
  // Use httpOnly cookies instead of localStorage
  private storeTokenSecurely(token: string): void {
    // Backend sets httpOnly cookie
    // Frontend can't access token directly
  }
  
  // Implement token rotation
  async performSensitiveOperation(operation: () => Promise<any>) {
    await this.rotateToken();  // Get fresh token
    return operation();
  }
  
  // Add CSRF protection
  private getCsrfToken(): string {
    return document.querySelector('meta[name="csrf-token"]')
      ?.getAttribute('content') || '';
  }
}
```

### 10. Testing JWT Management

```typescript
describe('AuthService JWT Management', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;
  
  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [AuthService]
    });
    
    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
    localStorage.clear();
  });
  
  it('should store JWT on successful login', fakeAsync(() => {
    const mockResponse = {
      access_token: 'eyJhbGciOiJIUzI1NiIs...',
      user: { id: 1, email: 'test@example.com' }
    };
    
    service.login('test@example.com', 'password').subscribe();
    
    const req = httpMock.expectOne(`${environment.authApiUrl}/login`);
    req.flush(mockResponse);
    
    tick();
    
    expect(localStorage.getItem('auth_token')).toBe(mockResponse.access_token);
    expect(service.getToken()).toBe(mockResponse.access_token);
  }));
  
  it('should clear token on logout', () => {
    localStorage.setItem('auth_token', 'test-token');
    
    service.logout();
    
    expect(localStorage.getItem('auth_token')).toBeNull();
    expect(service.getToken()).toBeNull();
  });
  
  it('should restore auth state on initialization', () => {
    const mockUser = { id: 1, email: 'test@example.com' };
    localStorage.setItem('auth_token', 'test-token');
    localStorage.setItem('current_user', JSON.stringify(mockUser));
    
    service.checkAuthState();
    
    service.currentUser$.subscribe(user => {
      expect(user).toEqual(mockUser);
    });
    
    service.isLoggedIn$.subscribe(isLoggedIn => {
      expect(isLoggedIn).toBe(true);
    });
  });
});
```

### 11. Common JWT Patterns

```typescript
// Pattern 1: Role-based access from JWT
hasRole(requiredRole: string): boolean {
  const token = this.getToken();
  if (!token) return false;
  
  const decoded = this.decodeToken(token);
  return decoded?.role === requiredRole;
}

// Pattern 2: Permission checking
hasPermission(permission: string): boolean {
  const token = this.getToken();
  if (!token) return false;
  
  const decoded = this.decodeToken(token);
  return decoded?.permissions?.includes(permission) || false;
}

// Pattern 3: User ID extraction
getUserId(): string | null {
  const token = this.getToken();
  if (!token) return null;
  
  const decoded = this.decodeToken(token);
  return decoded?.sub || null;
}
```

### Interview Talking Points

1. **JWT Storage Strategy**: Using localStorage for persistence, aware of XSS risks
2. **Token Lifecycle**: Login → Store → Use in requests → Logout/Clear
3. **Reactive State**: BehaviorSubjects for real-time auth state updates
4. **Security Awareness**: Know the vulnerabilities and improvements needed
5. **Interceptor Pattern**: Automatic token injection in HTTP requests
6. **Error Handling**: 401 responses trigger logout
7. **Future Enhancements**: Token refresh, secure storage, CSRF protection