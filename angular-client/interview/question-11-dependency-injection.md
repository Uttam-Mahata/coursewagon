# Question 11: Explain Angular's dependency injection system. What's the difference between `providedIn: 'root'` vs providing in a module?

## Answer

### Understanding Angular's Dependency Injection (DI)

Angular's DI is a design pattern where classes receive dependencies from external sources rather than creating them. It's the backbone of Angular's architecture.

### 1. How Dependency Injection Works

```typescript
// Without DI (Bad - tight coupling)
export class BadCourseComponent {
  private courseService: CourseService;
  private http: HttpClient;
  
  constructor() {
    this.http = new HttpClient();  // Creating dependencies manually
    this.courseService = new CourseService(this.http);  // Have to know implementation
  }
}

// With DI (Good - loose coupling)
export class GoodCourseComponent {
  constructor(
    private courseService: CourseService  // Angular provides this
  ) {
    // courseService is automatically injected
    // Component doesn't know how CourseService is created
  }
}
```

### 2. ProvidedIn: 'root' Pattern (Our Current Approach)

```typescript
// auth.service.ts - Most common pattern in CourseWagon
@Injectable({
  providedIn: 'root'  // Service available application-wide
})
export class AuthService {
  constructor(
    private http: HttpClient,
    private router: Router,
    private firebaseAuthService: FirebaseAuthService
  ) {}
}

// How Angular handles this:
// 1. Service registered in root injector
// 2. Single instance (singleton) for entire app
// 3. Tree-shakeable - removed if not used
// 4. No need to add to providers array
```

### 3. Module-Level Providers (Traditional Approach)

```typescript
// Alternative: Providing in module
@Injectable()  // Note: No providedIn
export class ModuleLevelService {
  constructor(private http: HttpClient) {}
}

// app.module.ts
@NgModule({
  providers: [
    ModuleLevelService,  // Provided here
    {
      provide: API_URL,
      useValue: 'https://api.coursewagon.com'
    }
  ]
})
export class AppModule {}

// Problems with this approach:
// 1. Not tree-shakeable
// 2. Service included even if not used
// 3. Have to remember to add to providers
```

### 4. Different Provider Strategies

#### Strategy 1: Root Level (Singleton)
```typescript
// Most services in CourseWagon use this
@Injectable({ providedIn: 'root' })
export class CourseService {
  private courses: Course[] = [];  // Shared state
  
  constructor(private http: HttpClient) {}
  
  getCourses(): Observable<Course[]> {
    // Same instance used everywhere
    return this.http.get<Course[]>('/api/courses');
  }
}

// Usage: Same instance in all components
export class Component1 {
  constructor(private courseService: CourseService) {}
}
export class Component2 {
  constructor(private courseService: CourseService) {}  // Same instance
}
```

#### Strategy 2: Component Level (New Instance)
```typescript
// Service without providedIn
@Injectable()
export class ComponentScopedService {
  private data: any[] = [];  // Each component gets own data
}

// Provided at component level
@Component({
  selector: 'app-course-editor',
  providers: [ComponentScopedService],  // New instance for this component
  template: '...'
})
export class CourseEditorComponent {
  constructor(private scopedService: ComponentScopedService) {}
}

// Another component
@Component({
  selector: 'app-course-viewer',
  providers: [ComponentScopedService],  // Different instance
  template: '...'
})
export class CourseViewerComponent {
  constructor(private scopedService: ComponentScopedService) {}
}
```

#### Strategy 3: Lazy Module Level
```typescript
// Service for lazy-loaded module only
@Injectable({
  providedIn: 'any'  // New instance per lazy module
})
export class LazyModuleService {}

// Or provide in specific module
@Injectable({
  providedIn: AdminModule  // Only available in AdminModule
})
export class AdminOnlyService {}
```

### 5. Injection Token Pattern

```typescript
// For non-class dependencies (values, interfaces, functions)

// Define token
export const API_BASE_URL = new InjectionToken<string>('api.base.url');
export const IS_PRODUCTION = new InjectionToken<boolean>('is.production');

// Provide value
@NgModule({
  providers: [
    { provide: API_BASE_URL, useValue: 'https://api.coursewagon.com' },
    { provide: IS_PRODUCTION, useValue: environment.production }
  ]
})
export class AppModule {}

// Inject token
export class ApiService {
  constructor(
    @Inject(API_BASE_URL) private apiUrl: string,
    @Inject(IS_PRODUCTION) private isProd: boolean
  ) {
    console.log(`API URL: ${this.apiUrl}, Production: ${this.isProd}`);
  }
}
```

### 6. Provider Configuration Options

```typescript
// Different ways to configure providers

// 1. useClass - Provide a different class
{
  provide: AuthService,
  useClass: MockAuthService  // For testing
}

// 2. useValue - Provide a value
{
  provide: API_CONFIG,
  useValue: {
    url: 'https://api.coursewagon.com',
    timeout: 5000
  }
}

// 3. useFactory - Dynamic creation
{
  provide: LoggerService,
  useFactory: (isProd: boolean) => {
    return isProd ? new ProdLogger() : new DevLogger();
  },
  deps: [IS_PRODUCTION]  // Dependencies for factory
}

// 4. useExisting - Alias to existing service
{
  provide: OldAuthService,
  useExisting: AuthService  // Use AuthService when OldAuthService requested
}
```

### 7. Real Examples from CourseWagon

```typescript
// app.module.ts - How we configure providers
@NgModule({
  providers: [
    // HTTP Interceptor registration
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true  // Multiple interceptors allowed
    },
    
    // Guards are provided at root via @Injectable
    AuthGuard,
    AdminGuard,
    NonAuthGuard,
    
    // Services use providedIn: 'root' so not listed here
  ]
})

// auth.interceptor.ts
@Injectable()  // No providedIn because provided in module
export class AuthInterceptor implements HttpInterceptor {
  constructor(private authService: AuthService) {}
  
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const token = this.authService.getToken();
    if (token) {
      req = req.clone({
        setHeaders: { Authorization: `Bearer ${token}` }
      });
    }
    return next.handle(req);
  }
}
```

### 8. Hierarchical Injection

```typescript
// Angular creates a hierarchy of injectors

/*
                Root Injector
                     |
            Platform Injector
                     |
              App Module Injector
                /          \
        Lazy Module      Component Injector
          Injector           /        \
              |        Child Comp   Child Comp
         Component      Injector    Injector
          Injector
*/

// Service lookup goes up the tree until found

// Example: Component-level override
@Component({
  selector: 'app-test-mode',
  providers: [
    { provide: CourseService, useClass: MockCourseService }
  ]
})
export class TestModeComponent {
  constructor(private courseService: CourseService) {
    // Gets MockCourseService, not the root CourseService
  }
}
```

### 9. Tree-Shaking Benefits

```typescript
// providedIn: 'root' enables tree-shaking

// This service will be removed if never imported
@Injectable({ providedIn: 'root' })
export class UnusedService {
  // If no component imports this, it's removed from bundle
}

// Module providers are NOT tree-shakeable
@NgModule({
  providers: [AlwaysIncludedService]  // Always in bundle
})

// Bundle size comparison:
// With providedIn: 'root' - Only used services: ~150KB
// With module providers - All services: ~250KB
```

### 10. Testing with DI

```typescript
// Easy to test with DI
describe('CourseComponent', () => {
  let component: CourseComponent;
  let courseService: jasmine.SpyObj<CourseService>;
  
  beforeEach(() => {
    const spy = jasmine.createSpyObj('CourseService', ['getCourses']);
    
    TestBed.configureTestingModule({
      declarations: [CourseComponent],
      providers: [
        { provide: CourseService, useValue: spy }  // Inject mock
      ]
    });
    
    component = TestBed.createComponent(CourseComponent).componentInstance;
    courseService = TestBed.inject(CourseService) as jasmine.SpyObj<CourseService>;
  });
  
  it('should load courses on init', () => {
    const mockCourses = [{ id: 1, name: 'Angular' }];
    courseService.getCourses.and.returnValue(of(mockCourses));
    
    component.ngOnInit();
    
    expect(courseService.getCourses).toHaveBeenCalled();
    expect(component.courses).toEqual(mockCourses);
  });
});
```

### 11. Common Patterns and Best Practices

```typescript
// ✅ DO: Use providedIn: 'root' for services
@Injectable({ providedIn: 'root' })
export class DataService {}

// ✅ DO: Use constructor injection
constructor(private service: DataService) {}

// ❌ DON'T: Use providers array unless necessary
@NgModule({
  providers: [DataService]  // Avoid unless specific reason
})

// ✅ DO: Use InjectionToken for config
export const CONFIG = new InjectionToken<Config>('app.config');

// ❌ DON'T: Use string tokens
providers: [{ provide: 'config', useValue: {} }]  // Type-unsafe

// ✅ DO: Inject in constructor
constructor(@Inject(CONFIG) private config: Config) {}

// ❌ DON'T: Use inject() outside constructor (unless in v14+ inject function)
ngOnInit() {
  const service = inject(DataService);  // Only in constructor or field initializer
}
```

### 12. Comparison Table

| Aspect | providedIn: 'root' | Module Providers | Component Providers |
|--------|-------------------|------------------|---------------------|
| **Scope** | Application-wide | Module scope | Component tree |
| **Instance** | Singleton | Singleton in module | New per component |
| **Tree-shakeable** | Yes ✅ | No ❌ | No ❌ |
| **Bundle size** | Optimized | Always included | Component bundle |
| **Use case** | Shared services | Module-specific | Component state |
| **Testing** | Easy to mock | Easy to mock | Isolated testing |

### Interview Talking Points

1. **Default to providedIn: 'root'**: Modern best practice for services
2. **Understand hierarchy**: Injectors form a tree, lookup goes upward
3. **Tree-shaking benefits**: Only used services included in bundle
4. **Testing advantages**: DI makes mocking dependencies trivial
5. **Know when to use each**: Root for shared, component for isolated state
6. **Performance impact**: Singleton services share memory, reduce overhead