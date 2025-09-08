# Question 14: How do you handle HTTP interceptors for adding authentication headers to API requests?

## Answer

### HTTP Interceptor Overview

HTTP Interceptors in Angular allow you to intercept and modify HTTP requests and responses globally. CourseWagon uses an AuthInterceptor to automatically add JWT tokens to API requests.

### 1. Current AuthInterceptor Implementation

```typescript
// auth.interceptor.ts
@Injectable()
export class AuthInterceptor implements HttpInterceptor {

  constructor(
    private authService: AuthService, 
    private router: Router
  ) {}

  intercept(
    request: HttpRequest<unknown>, 
    next: HttpHandler
  ): Observable<HttpEvent<unknown>> {
    
    // 1. Get token from AuthService
    const token = this.authService.getToken();
    
    if (token) {
      // 2. Clone request and add Authorization header
      const clonedRequest = request.clone({
        headers: request.headers.set('Authorization', `Bearer ${token}`)
      });
      
      console.log(`Adding token to ${request.url}`);
      
      // 3. Handle request with error catching
      return next.handle(clonedRequest).pipe(
        catchError((error: HttpErrorResponse) => {
          console.error('HTTP Error:', error);
          
          // 4. Handle 401 Unauthorized
          if (error.status === 401) {
            console.log('Authentication error detected, logging out...');
            this.authService.logout();
            this.router.navigate(['/auth']);
          }
          
          return throwError(() => error);
        })
      );
    }
    
    // 5. Pass through original request if no token
    return next.handle(request).pipe(
      catchError((error: HttpErrorResponse) => {
        console.error('HTTP Error:', error);
        if (error.status === 401) {
          this.router.navigate(['/auth']);
        }
        return throwError(() => error);
      })
    );
  }
}
```

### 2. Interceptor Registration

```typescript
// app.module.ts - How interceptor is registered
import { HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http';

@NgModule({
  imports: [
    HttpClientModule,
    // ... other imports
  ],
  providers: [
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true  // Allows multiple interceptors
    }
  ]
})
export class AppModule { }
```

### 3. How Interceptors Work - Step by Step

```typescript
// When a component makes an HTTP request:

// 1. Component initiates request
this.http.get('/api/courses')

// 2. Request flows through interceptor chain
AuthInterceptor.intercept() {
  // Check for token
  token = authService.getToken() // "eyJhbGci..."
  
  // Clone and modify request
  newRequest = request.clone({
    headers: { Authorization: "Bearer eyJhbGci..." }
  })
  
  // Pass to next handler
  return next.handle(newRequest)
}

// 3. Request sent to server with headers:
GET /api/courses
Authorization: Bearer eyJhbGci...

// 4. Response flows back through interceptor
// 5. Error handling if needed
// 6. Component receives response/error
```

### 4. Advanced Interceptor Patterns

#### Multiple Interceptors:
```typescript
// logging.interceptor.ts
@Injectable()
export class LoggingInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const started = Date.now();
    
    return next.handle(req).pipe(
      tap(event => {
        if (event instanceof HttpResponse) {
          const elapsed = Date.now() - started;
          console.log(`Request for ${req.urlWithParams} took ${elapsed} ms`);
        }
      })
    );
  }
}

// retry.interceptor.ts
@Injectable()
export class RetryInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(req).pipe(
      retry(3),  // Retry failed requests 3 times
      catchError(error => {
        if (error.status === 503) {
          console.log('Service unavailable, retrying...');
          return timer(1000).pipe(
            switchMap(() => next.handle(req))
          );
        }
        return throwError(error);
      })
    );
  }
}

// Register multiple interceptors (order matters!)
providers: [
  { provide: HTTP_INTERCEPTORS, useClass: LoggingInterceptor, multi: true },
  { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true },
  { provide: HTTP_INTERCEPTORS, useClass: RetryInterceptor, multi: true }
]
// Execution order: Logging → Auth → Retry → Server
```

### 5. Conditional Header Addition

```typescript
// Enhanced interceptor with conditional logic
export class SmartAuthInterceptor implements HttpInterceptor {
  
  private skipUrls = [
    '/assets/',
    '/public/',
    'https://external-api.com'
  ];
  
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Skip authentication for certain URLs
    if (this.shouldSkipAuth(req.url)) {
      return next.handle(req);
    }
    
    const token = this.authService.getToken();
    
    // Different handling for different request types
    let modifiedReq = req;
    
    if (token) {
      // Add auth header
      modifiedReq = req.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      });
    }
    
    // Add other headers based on request type
    if (req.method === 'POST' || req.method === 'PUT') {
      modifiedReq = modifiedReq.clone({
        setHeaders: {
          'Content-Type': 'application/json'
        }
      });
    }
    
    // Add custom headers for our API
    if (req.url.includes(environment.apiUrl)) {
      modifiedReq = modifiedReq.clone({
        setHeaders: {
          'X-App-Version': environment.appVersion,
          'X-Client-Type': 'web'
        }
      });
    }
    
    return next.handle(modifiedReq);
  }
  
  private shouldSkipAuth(url: string): boolean {
    return this.skipUrls.some(skipUrl => url.includes(skipUrl));
  }
}
```

### 6. Error Handling Strategies

```typescript
// Comprehensive error handling interceptor
export class ErrorInterceptor implements HttpInterceptor {
  
  constructor(
    private authService: AuthService,
    private router: Router,
    private notificationService: NotificationService
  ) {}
  
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(req).pipe(
      catchError((error: HttpErrorResponse) => {
        // Handle different error statuses
        switch (error.status) {
          case 401:
            this.handle401Error(error);
            break;
          case 403:
            this.handle403Error();
            break;
          case 404:
            this.handle404Error(error);
            break;
          case 500:
            this.handle500Error(error);
            break;
          case 0:
            this.handleNetworkError();
            break;
          default:
            this.handleGenericError(error);
        }
        
        return throwError(() => error);
      })
    );
  }
  
  private handle401Error(error: HttpErrorResponse): void {
    // Token expired or invalid
    if (this.authService.getToken()) {
      this.notificationService.error('Session expired. Please login again.');
      this.authService.logout();
    }
    this.router.navigate(['/auth'], {
      queryParams: { returnUrl: this.router.url }
    });
  }
  
  private handle403Error(): void {
    // Forbidden - user doesn't have permission
    this.notificationService.error('You do not have permission to access this resource.');
    this.router.navigate(['/']);
  }
  
  private handle404Error(error: HttpErrorResponse): void {
    // Resource not found
    if (error.url?.includes('/api/courses')) {
      this.notificationService.error('Course not found.');
      this.router.navigate(['/courses']);
    }
  }
  
  private handle500Error(error: HttpErrorResponse): void {
    // Server error
    this.notificationService.error('Server error. Please try again later.');
    console.error('Server error:', error);
  }
  
  private handleNetworkError(): void {
    // No internet connection
    this.notificationService.error('Network error. Please check your connection.');
  }
  
  private handleGenericError(error: HttpErrorResponse): void {
    const message = error.error?.message || 'An unexpected error occurred.';
    this.notificationService.error(message);
  }
}
```

### 7. Request/Response Transformation

```typescript
// Transform requests and responses
export class TransformInterceptor implements HttpInterceptor {
  
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Transform request body
    let modifiedReq = req;
    
    if (req.body && req.method === 'POST') {
      // Convert snake_case to camelCase for backend
      const transformedBody = this.convertKeysToSnakeCase(req.body);
      modifiedReq = req.clone({ body: transformedBody });
    }
    
    return next.handle(modifiedReq).pipe(
      map(event => {
        // Transform response
        if (event instanceof HttpResponse && event.body) {
          // Convert camelCase to snake_case from backend
          const transformedBody = this.convertKeysToCamelCase(event.body);
          return event.clone({ body: transformedBody });
        }
        return event;
      })
    );
  }
  
  private convertKeysToSnakeCase(obj: any): any {
    // Implementation for key transformation
    // user_name → userName
  }
  
  private convertKeysToCamelCase(obj: any): any {
    // Implementation for key transformation
    // userName → user_name
  }
}
```

### 8. Caching Interceptor

```typescript
// Cache GET requests
@Injectable()
export class CacheInterceptor implements HttpInterceptor {
  private cache = new Map<string, HttpResponse<any>>();
  
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Only cache GET requests
    if (req.method !== 'GET') {
      return next.handle(req);
    }
    
    // Check if request is cached
    const cached = this.cache.get(req.urlWithParams);
    if (cached) {
      console.log(`Returning cached response for ${req.urlWithParams}`);
      return of(cached);
    }
    
    // Make request and cache response
    return next.handle(req).pipe(
      tap(event => {
        if (event instanceof HttpResponse) {
          console.log(`Caching response for ${req.urlWithParams}`);
          this.cache.set(req.urlWithParams, event);
          
          // Clear cache after 5 minutes
          setTimeout(() => {
            this.cache.delete(req.urlWithParams);
          }, 300000);
        }
      })
    );
  }
  
  // Method to clear cache
  clearCache(): void {
    this.cache.clear();
  }
}
```

### 9. Testing Interceptors

```typescript
describe('AuthInterceptor', () => {
  let interceptor: AuthInterceptor;
  let authService: jasmine.SpyObj<AuthService>;
  let httpMock: HttpTestingController;
  let httpClient: HttpClient;
  
  beforeEach(() => {
    const authSpy = jasmine.createSpyObj('AuthService', ['getToken', 'logout']);
    
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        AuthInterceptor,
        { provide: AuthService, useValue: authSpy },
        { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true }
      ]
    });
    
    interceptor = TestBed.inject(AuthInterceptor);
    authService = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    httpMock = TestBed.inject(HttpTestingController);
    httpClient = TestBed.inject(HttpClient);
  });
  
  it('should add auth header when token exists', () => {
    authService.getToken.and.returnValue('test-token');
    
    httpClient.get('/api/test').subscribe();
    
    const req = httpMock.expectOne('/api/test');
    expect(req.request.headers.get('Authorization')).toBe('Bearer test-token');
  });
  
  it('should not add header when no token', () => {
    authService.getToken.and.returnValue(null);
    
    httpClient.get('/api/test').subscribe();
    
    const req = httpMock.expectOne('/api/test');
    expect(req.request.headers.has('Authorization')).toBeFalse();
  });
  
  it('should logout on 401 error', () => {
    authService.getToken.and.returnValue('test-token');
    
    httpClient.get('/api/test').subscribe({
      error: (error) => {
        expect(error.status).toBe(401);
        expect(authService.logout).toHaveBeenCalled();
      }
    });
    
    const req = httpMock.expectOne('/api/test');
    req.flush('Unauthorized', { status: 401, statusText: 'Unauthorized' });
  });
});
```

### 10. Production Considerations

```typescript
// Production-ready interceptor
export class ProductionInterceptor implements HttpInterceptor {
  
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Add request ID for tracking
    const requestId = this.generateRequestId();
    
    let modifiedReq = req.clone({
      setHeaders: {
        'X-Request-ID': requestId
      }
    });
    
    // Add timeout
    const timeout = req.context.get(TIMEOUT) || 30000;
    
    return next.handle(modifiedReq).pipe(
      timeout(timeout),
      tap({
        next: (event) => {
          if (event instanceof HttpResponse) {
            // Log successful requests in production
            this.logRequest(requestId, req, event);
          }
        },
        error: (error) => {
          // Log errors for monitoring
          this.logError(requestId, req, error);
        }
      }),
      catchError(error => {
        // Report to error tracking service
        this.errorReporter.report(error, {
          requestId,
          url: req.urlWithParams,
          method: req.method
        });
        
        return throwError(() => error);
      })
    );
  }
  
  private generateRequestId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
  
  private logRequest(id: string, req: HttpRequest<any>, res: HttpResponse<any>): void {
    // Send to logging service
  }
  
  private logError(id: string, req: HttpRequest<any>, error: any): void {
    // Send to error tracking
  }
}
```

### Interview Talking Points

1. **Interceptor Chain**: Understand order of execution matters
2. **Request Cloning**: Requests are immutable, must clone to modify
3. **Error Handling**: Centralized error handling for consistency
4. **Token Management**: Automatic token injection reduces boilerplate
5. **Testing Strategy**: Mock interceptors for unit tests
6. **Performance**: Consider caching and retry strategies
7. **Security**: Never log sensitive data in interceptors