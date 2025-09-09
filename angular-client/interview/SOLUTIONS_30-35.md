# Solutions for Questions 30-35: TypeScript Advanced Topics

## TypeScript Deep Dive (Continued)

### 30. What are type guards and how have you implemented them?

**Answer:**

Type guards are expressions that perform runtime checks to narrow down types within conditional blocks. They help TypeScript's type system understand what type a variable is at a specific point in the code.

**Built-in Type Guards:**

```typescript
// 1. typeof type guard (for primitives)
function processValue(value: string | number | boolean) {
  if (typeof value === 'string') {
    // TypeScript knows value is string here
    console.log(value.toUpperCase());
    console.log(value.length);
  } else if (typeof value === 'number') {
    // TypeScript knows value is number here
    console.log(value.toFixed(2));
    console.log(value * 100);
  } else {
    // TypeScript knows value is boolean here
    console.log(value ? 'True' : 'False');
  }
}

// 2. instanceof type guard (for classes)
class Student {
  enrolledCourses: string[] = [];
  gpa: number = 0;
}

class Instructor {
  coursesTaught: string[] = [];
  rating: number = 0;
}

function processUser(user: Student | Instructor) {
  if (user instanceof Student) {
    // TypeScript knows user is Student
    console.log(`GPA: ${user.gpa}`);
    console.log(`Enrolled in ${user.enrolledCourses.length} courses`);
  } else {
    // TypeScript knows user is Instructor
    console.log(`Rating: ${user.rating}`);
    console.log(`Teaching ${user.coursesTaught.length} courses`);
  }
}

// 3. in operator type guard
interface Car {
  drive(): void;
  wheels: number;
}

interface Boat {
  sail(): void;
  propellers: number;
}

function operateVehicle(vehicle: Car | Boat) {
  if ('drive' in vehicle) {
    // TypeScript knows vehicle is Car
    vehicle.drive();
    console.log(`Has ${vehicle.wheels} wheels`);
  } else {
    // TypeScript knows vehicle is Boat
    vehicle.sail();
    console.log(`Has ${vehicle.propellers} propellers`);
  }
}
```

**Custom Type Guards:**

```typescript
// 1. User-defined type guard functions
interface Course {
  id: string;
  title: string;
  price: number;
  instructor: string;
}

interface FreeCourse extends Course {
  price: 0;
  sponsoredBy: string;
}

interface PaidCourse extends Course {
  price: number;
  refundPolicy: string;
}

// Type guard function with 'is' keyword
function isFreeCourse(course: Course): course is FreeCourse {
  return course.price === 0;
}

function isPaidCourse(course: Course): course is PaidCourse {
  return course.price > 0;
}

function processCourse(course: Course) {
  if (isFreeCourse(course)) {
    // TypeScript knows this is FreeCourse
    console.log(`Free course sponsored by ${course.sponsoredBy}`);
  } else if (isPaidCourse(course)) {
    // TypeScript knows this is PaidCourse
    console.log(`Paid course: $${course.price}`);
    console.log(`Refund policy: ${course.refundPolicy}`);
  }
}

// 2. Array type guards
function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && 
         value.every(item => typeof item === 'string');
}

function processData(data: unknown) {
  if (isStringArray(data)) {
    // TypeScript knows data is string[]
    data.forEach(str => console.log(str.toUpperCase()));
  }
}

// 3. Discriminated union type guards
type ApiResponse = 
  | { status: 'success'; data: any }
  | { status: 'error'; error: string; code: number }
  | { status: 'loading' };

function isSuccessResponse(response: ApiResponse): response is { status: 'success'; data: any } {
  return response.status === 'success';
}

function isErrorResponse(response: ApiResponse): response is { status: 'error'; error: string; code: number } {
  return response.status === 'error';
}

function handleApiResponse(response: ApiResponse) {
  if (isSuccessResponse(response)) {
    console.log('Data:', response.data);
  } else if (isErrorResponse(response)) {
    console.error(`Error ${response.code}: ${response.error}`);
  } else {
    console.log('Loading...');
  }
}
```

**Advanced Type Guards from CourseWagon:**

```typescript
// 1. Complex object validation
interface ValidCourse {
  id: string;
  title: string;
  description: string;
  chapters: Chapter[];
  instructor: Instructor;
  metadata: CourseMetadata;
}

function isValidCourse(obj: any): obj is ValidCourse {
  return obj != null &&
    typeof obj === 'object' &&
    typeof obj.id === 'string' &&
    typeof obj.title === 'string' &&
    typeof obj.description === 'string' &&
    Array.isArray(obj.chapters) &&
    obj.chapters.every(isValidChapter) &&
    isValidInstructor(obj.instructor) &&
    isValidMetadata(obj.metadata);
}

function isValidChapter(obj: any): obj is Chapter {
  return obj != null &&
    typeof obj === 'object' &&
    typeof obj.id === 'string' &&
    typeof obj.title === 'string' &&
    typeof obj.content === 'string';
}

// 2. Type guards with generics
function hasProperty<T extends object, K extends PropertyKey>(
  obj: T,
  key: K
): obj is T & Record<K, unknown> {
  return key in obj;
}

function processObject(obj: object) {
  if (hasProperty(obj, 'email')) {
    // TypeScript knows obj has an email property
    console.log(`Email: ${obj.email}`);
  }
  
  if (hasProperty(obj, 'id') && hasProperty(obj, 'name')) {
    // TypeScript knows obj has both id and name properties
    console.log(`${obj.id}: ${obj.name}`);
  }
}

// 3. Async type guards
async function isAuthenticated(token: string): Promise<boolean> {
  try {
    const response = await fetch('/api/verify', {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.ok;
  } catch {
    return false;
  }
}

// 4. Type guards in Angular services
@Injectable({ providedIn: 'root' })
export class ValidationService {
  isValidEmail(value: unknown): value is string {
    if (typeof value !== 'string') return false;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(value);
  }
  
  isValidPhoneNumber(value: unknown): value is string {
    if (typeof value !== 'string') return false;
    const phoneRegex = /^\+?[\d\s-()]+$/;
    return phoneRegex.test(value) && value.replace(/\D/g, '').length >= 10;
  }
  
  isValidCourseData(data: unknown): data is CreateCourseDto {
    if (!data || typeof data !== 'object') return false;
    
    const obj = data as any;
    return (
      typeof obj.title === 'string' && obj.title.length > 0 &&
      typeof obj.description === 'string' &&
      typeof obj.price === 'number' && obj.price >= 0 &&
      (!obj.tags || Array.isArray(obj.tags))
    );
  }
  
  isHttpErrorResponse(error: unknown): error is HttpErrorResponse {
    return error instanceof HttpErrorResponse;
  }
  
  isNetworkError(error: unknown): boolean {
    return this.isHttpErrorResponse(error) && error.status === 0;
  }
}

// 5. Type guards for form validation
export class FormValidators {
  static isRequiredFieldValid(value: unknown): value is NonNullable<unknown> {
    return value !== null && 
           value !== undefined && 
           (typeof value !== 'string' || value.trim().length > 0);
  }
  
  static isNumberInRange(value: unknown, min: number, max: number): value is number {
    return typeof value === 'number' && value >= min && value <= max;
  }
  
  static isValidDate(value: unknown): value is Date {
    return value instanceof Date && !isNaN(value.getTime());
  }
  
  static isFutureDate(value: unknown): value is Date {
    return this.isValidDate(value) && value > new Date();
  }
}

// 6. Combining multiple type guards
type Content = VideoContent | TextContent | QuizContent;

function isVideoContent(content: Content): content is VideoContent {
  return content.type === 'video';
}

function isTextContent(content: Content): content is TextContent {
  return content.type === 'text';
}

function isQuizContent(content: Content): content is QuizContent {
  return content.type === 'quiz';
}

function hasSubtitles(content: Content): content is VideoContent & { subtitles: NonNullable<VideoContent['subtitles']> } {
  return isVideoContent(content) && 
         content.subtitles !== undefined && 
         content.subtitles.length > 0;
}

// Usage in component
@Component({
  selector: 'app-content-player'
})
export class ContentPlayerComponent {
  @Input() content!: Content;
  
  getContentDuration(): number {
    if (isVideoContent(this.content)) {
      return this.content.duration;
    } else if (isTextContent(this.content)) {
      return this.content.estimatedReadTime * 60; // Convert to seconds
    } else if (isQuizContent(this.content)) {
      return (this.content.timeLimit || 30) * 60;
    }
    
    // Exhaustive check
    const _exhaustive: never = this.content;
    return 0;
  }
  
  canShowSubtitles(): boolean {
    return hasSubtitles(this.content);
  }
}
```

---

### 31. How do you type HTTP responses from your backend API?

**Answer:**

**Comprehensive HTTP Response Typing Strategy:**

```typescript
// 1. Base Response Interfaces
interface BaseApiResponse {
  timestamp: string;
  path: string;
  version: string;
}

interface SuccessResponse<T> extends BaseApiResponse {
  success: true;
  data: T;
  message?: string;
}

interface ErrorResponse extends BaseApiResponse {
  success: false;
  error: string;
  code: string;
  details?: Record<string, any>;
  stackTrace?: string;
}

interface PaginatedResponse<T> extends SuccessResponse<T[]> {
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

type ApiResponse<T> = SuccessResponse<T> | ErrorResponse;

// 2. Domain-specific Response Types
interface CourseResponse {
  id: string;
  title: string;
  description: string;
  instructor: InstructorResponse;
  chapters: ChapterResponse[];
  price: number;
  currency: string;
  thumbnail: string;
  rating: number;
  enrollmentCount: number;
  createdAt: string;
  updatedAt: string;
}

interface InstructorResponse {
  id: string;
  name: string;
  bio: string;
  avatar: string;
  rating: number;
  courseCount: number;
}

interface ChapterResponse {
  id: string;
  title: string;
  description: string;
  duration: number;
  order: number;
  content: ContentResponse;
  isPreview: boolean;
}

interface EnrollmentResponse {
  id: string;
  courseId: string;
  userId: string;
  enrolledAt: string;
  progress: number;
  completedChapters: string[];
  lastAccessedAt: string;
  certificateUrl?: string;
}

// 3. Authentication Response Types
interface LoginResponse {
  user: UserResponse;
  tokens: {
    accessToken: string;
    refreshToken: string;
    expiresIn: number;
  };
  permissions: string[];
}

interface UserResponse {
  id: string;
  email: string;
  name: string;
  role: 'student' | 'instructor' | 'admin';
  avatar?: string;
  emailVerified: boolean;
  profile: UserProfileResponse;
}

interface UserProfileResponse {
  bio?: string;
  location?: string;
  website?: string;
  social?: {
    twitter?: string;
    linkedin?: string;
    github?: string;
  };
  preferences: {
    theme: 'light' | 'dark' | 'auto';
    language: string;
    notifications: NotificationPreferences;
  };
}
```

**Service Implementation with Typed Responses:**

```typescript
@Injectable({ providedIn: 'root' })
export class ApiService {
  private baseUrl = environment.apiUrl;
  
  constructor(
    private http: HttpClient,
    private errorHandler: ErrorHandlerService
  ) {}
  
  // 1. Generic typed request methods
  get<T>(endpoint: string, options?: HttpOptions): Observable<T> {
    return this.http.get<ApiResponse<T>>(
      `${this.baseUrl}${endpoint}`,
      options
    ).pipe(
      map(response => this.extractData(response)),
      catchError(error => this.handleError(error))
    );
  }
  
  post<TRequest, TResponse>(
    endpoint: string,
    data: TRequest,
    options?: HttpOptions
  ): Observable<TResponse> {
    return this.http.post<ApiResponse<TResponse>>(
      `${this.baseUrl}${endpoint}`,
      data,
      options
    ).pipe(
      map(response => this.extractData(response)),
      catchError(error => this.handleError(error))
    );
  }
  
  getPaginated<T>(
    endpoint: string,
    params: PaginationParams
  ): Observable<PaginatedData<T>> {
    return this.http.get<PaginatedResponse<T>>(
      `${this.baseUrl}${endpoint}`,
      { params: this.buildParams(params) }
    ).pipe(
      map(response => ({
        items: response.data,
        ...response.pagination
      })),
      catchError(error => this.handleError(error))
    );
  }
  
  private extractData<T>(response: ApiResponse<T>): T {
    if (response.success) {
      return response.data;
    }
    throw new ApiError(response as ErrorResponse);
  }
  
  private handleError(error: HttpErrorResponse): Observable<never> {
    return throwError(() => this.errorHandler.handle(error));
  }
}

// 2. Specific Service with Typed Responses
@Injectable({ providedIn: 'root' })
export class CourseApiService {
  constructor(private api: ApiService) {}
  
  // Typed response methods
  getCourses(filters?: CourseFilters): Observable<CourseResponse[]> {
    return this.api.get<CourseResponse[]>('/courses', { params: filters });
  }
  
  getCourse(id: string): Observable<CourseResponse> {
    return this.api.get<CourseResponse>(`/courses/${id}`);
  }
  
  createCourse(data: CreateCourseDto): Observable<CourseResponse> {
    return this.api.post<CreateCourseDto, CourseResponse>('/courses', data);
  }
  
  updateCourse(id: string, updates: UpdateCourseDto): Observable<CourseResponse> {
    return this.api.patch<UpdateCourseDto, CourseResponse>(
      `/courses/${id}`,
      updates
    );
  }
  
  // Paginated response
  getCoursesPage(page: number, pageSize: number): Observable<PaginatedData<CourseResponse>> {
    return this.api.getPaginated<CourseResponse>('/courses', { page, pageSize });
  }
  
  // Complex nested response
  getCourseWithEnrollment(courseId: string): Observable<CourseWithEnrollment> {
    return forkJoin({
      course: this.getCourse(courseId),
      enrollment: this.getEnrollment(courseId)
    }).pipe(
      map(({ course, enrollment }) => ({
        ...course,
        enrollment: enrollment || null,
        isEnrolled: !!enrollment
      }))
    );
  }
  
  // File upload with typed response
  uploadCourseThumbnail(courseId: string, file: File): Observable<ImageUploadResponse> {
    const formData = new FormData();
    formData.append('thumbnail', file);
    
    return this.api.post<FormData, ImageUploadResponse>(
      `/courses/${courseId}/thumbnail`,
      formData
    );
  }
}

// 3. Response Transformation and Mapping
interface RawDateResponse {
  createdAt: string;
  updatedAt: string;
}

interface ParsedDateResponse {
  createdAt: Date;
  updatedAt: Date;
}

@Injectable({ providedIn: 'root' })
export class DataTransformService {
  // Transform string dates to Date objects
  parseDates<T extends RawDateResponse>(response: T): T & ParsedDateResponse {
    return {
      ...response,
      createdAt: new Date(response.createdAt),
      updatedAt: new Date(response.updatedAt)
    };
  }
  
  // Transform nested responses
  transformCourseResponse(raw: CourseResponse): Course {
    return {
      ...raw,
      createdAt: new Date(raw.createdAt),
      updatedAt: new Date(raw.updatedAt),
      instructor: this.transformInstructorResponse(raw.instructor),
      chapters: raw.chapters.map(ch => this.transformChapterResponse(ch)),
      thumbnailUrl: this.buildMediaUrl(raw.thumbnail)
    };
  }
  
  private transformInstructorResponse(raw: InstructorResponse): Instructor {
    return {
      ...raw,
      avatarUrl: this.buildMediaUrl(raw.avatar)
    };
  }
  
  private transformChapterResponse(raw: ChapterResponse): Chapter {
    return {
      ...raw,
      content: this.transformContentResponse(raw.content)
    };
  }
  
  private buildMediaUrl(path: string): string {
    if (path.startsWith('http')) return path;
    return `${environment.cdnUrl}/${path}`;
  }
}

// 4. Error Response Handling
class ApiError extends Error {
  constructor(public response: ErrorResponse) {
    super(response.error);
    this.name = 'ApiError';
  }
  
  get code(): string {
    return this.response.code;
  }
  
  get details(): Record<string, any> | undefined {
    return this.response.details;
  }
  
  isValidationError(): boolean {
    return this.code === 'VALIDATION_ERROR';
  }
  
  isAuthError(): boolean {
    return this.code === 'AUTH_ERROR' || this.code === 'UNAUTHORIZED';
  }
  
  isNotFoundError(): boolean {
    return this.code === 'NOT_FOUND';
  }
}

// 5. Response Interceptor for Type Safety
@Injectable()
export class ResponseInterceptor implements HttpInterceptor {
  intercept(
    req: HttpRequest<any>,
    next: HttpHandler
  ): Observable<HttpEvent<any>> {
    return next.handle(req).pipe(
      map(event => {
        if (event instanceof HttpResponse) {
          // Validate response structure
          if (this.isApiResponse(event.body)) {
            return event;
          }
          
          // Wrap non-standard responses
          const wrappedBody: SuccessResponse<any> = {
            success: true,
            data: event.body,
            timestamp: new Date().toISOString(),
            path: req.url,
            version: '1.0'
          };
          
          return event.clone({ body: wrappedBody });
        }
        return event;
      })
    );
  }
  
  private isApiResponse(body: any): body is ApiResponse<any> {
    return body && 
           typeof body === 'object' && 
           'success' in body &&
           typeof body.success === 'boolean';
  }
}

// 6. Type-safe HTTP Client Wrapper
@Injectable({ providedIn: 'root' })
export class TypedHttpClient {
  constructor(private http: HttpClient) {}
  
  request<TResponse>(
    method: string,
    url: string,
    options?: {
      body?: any;
      headers?: HttpHeaders;
      params?: HttpParams;
      responseType?: 'json';
    }
  ): Observable<TResponse> {
    return this.http.request<TResponse>(method, url, options);
  }
  
  // Strongly typed batch requests
  batch<T extends Record<string, Observable<any>>>(
    requests: T
  ): Observable<{ [K in keyof T]: ObservedValueOf<T[K]> }> {
    return forkJoin(requests);
  }
  
  // Example usage
  loadDashboardData() {
    return this.batch({
      user: this.getUserProfile(),
      courses: this.getCourses(),
      stats: this.getStats(),
      notifications: this.getNotifications()
    });
  }
}
```

---

### 32. What are decorators in TypeScript/Angular? Explain @Component, @Injectable, @Input, @Output

**Answer:**

Decorators are special declarations that can be attached to classes, methods, properties, or parameters to modify their behavior. They use the `@` symbol and are essentially functions that are executed at runtime.

**Core Angular Decorators:**

```typescript
// 1. @Component Decorator
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-course-card',           // HTML tag name
  templateUrl: './course-card.component.html',
  styleUrls: ['./course-card.component.scss'],
  
  // Additional metadata
  providers: [CourseService],             // Component-level services
  changeDetection: ChangeDetectionStrategy.OnPush,
  encapsulation: ViewEncapsulation.Emulated,
  animations: [
    trigger('slideIn', [
      transition(':enter', [
        style({ transform: 'translateX(-100%)' }),
        animate('300ms ease-in', style({ transform: 'translateX(0%)' }))
      ])
    ])
  ],
  host: {
    '[class.selected]': 'isSelected',
    '(click)': 'onClick($event)'
  },
  standalone: true,                       // Angular 14+ standalone component
  imports: [CommonModule, RouterModule]   // Dependencies for standalone
})
export class CourseCardComponent implements OnInit {
  isSelected = false;
  
  ngOnInit() {
    console.log('Component initialized');
  }
  
  onClick(event: Event) {
    this.isSelected = !this.isSelected;
  }
}

// 2. @Injectable Decorator
@Injectable({
  providedIn: 'root'  // Singleton service at root level
})
export class CourseService {
  constructor(private http: HttpClient) {}
  
  getCourses(): Observable<Course[]> {
    return this.http.get<Course[]>('/api/courses');
  }
}

// Module-level injection
@Injectable({
  providedIn: CourseModule  // Only available in CourseModule
})
export class CourseStateService {
  private state = new BehaviorSubject<CourseState>(initialState);
}

// No providedIn - must be provided manually
@Injectable()
export class CourseValidator {
  validate(course: Course): ValidationResult {
    // Validation logic
  }
}

// Using in component providers
@Component({
  selector: 'app-course-form',
  providers: [CourseValidator]  // New instance per component
})
export class CourseFormComponent {}
```

**Input/Output Decorators:**

```typescript
// 3. @Input and @Output Decorators
@Component({
  selector: 'app-course-detail',
  template: `
    <div class="course-detail">
      <h2>{{ course.title }}</h2>
      <p>{{ course.description }}</p>
      <button (click)="enrollUser()">Enroll</button>
      <button (click)="favoriteToggle()">
        {{ isFavorite ? 'Unfavorite' : 'Favorite' }}
      </button>
    </div>
  `
})
export class CourseDetailComponent implements OnInit, OnChanges {
  // Basic @Input
  @Input() course!: Course;
  
  // @Input with alias
  @Input('courseId') id!: string;
  
  // @Input with setter for validation/transformation
  private _rating: number = 0;
  @Input()
  set rating(value: number) {
    this._rating = Math.max(0, Math.min(5, value)); // Clamp between 0-5
  }
  get rating(): number {
    return this._rating;
  }
  
  // @Input with transform (Angular 16+)
  @Input({ transform: booleanAttribute }) disabled = false;
  @Input({ transform: numberAttribute }) maxStudents = 100;
  
  // Required @Input (Angular 16+)
  @Input({ required: true }) userId!: string;
  
  // Basic @Output
  @Output() enrolled = new EventEmitter<EnrollmentEvent>();
  
  // @Output with alias
  @Output('onFavorite') favoriteChanged = new EventEmitter<boolean>();
  
  // Two-way binding support
  @Input() isFavorite = false;
  @Output() isFavoriteChange = new EventEmitter<boolean>();
  
  ngOnInit() {
    console.log('Course ID:', this.id);
  }
  
  ngOnChanges(changes: SimpleChanges) {
    if (changes['course']) {
      console.log('Course changed:', changes['course'].currentValue);
    }
  }
  
  enrollUser() {
    const event: EnrollmentEvent = {
      courseId: this.course.id,
      userId: this.userId,
      timestamp: new Date()
    };
    this.enrolled.emit(event);
  }
  
  favoriteToggle() {
    this.isFavorite = !this.isFavorite;
    this.isFavoriteChange.emit(this.isFavorite); // Enables [(isFavorite)]
    this.favoriteChanged.emit(this.isFavorite);
  }
}

// Parent component usage
@Component({
  selector: 'app-course-page',
  template: `
    <app-course-detail
      [course]="selectedCourse"
      [courseId]="courseId"
      [rating]="userRating"
      [userId]="currentUserId"
      [(isFavorite)]="isCourseFavorite"
      (enrolled)="handleEnrollment($event)"
      (onFavorite)="updateFavoriteStatus($event)"
    ></app-course-detail>
  `
})
export class CoursePageComponent {
  selectedCourse: Course;
  courseId = 'course-123';
  userRating = 4.5;
  currentUserId = 'user-456';
  isCourseFavorite = false;
  
  handleEnrollment(event: EnrollmentEvent) {
    console.log('User enrolled:', event);
  }
  
  updateFavoriteStatus(isFavorite: boolean) {
    console.log('Favorite status:', isFavorite);
  }
}
```

**Other Important Decorators:**

```typescript
// 4. @ViewChild and @ViewChildren
@Component({
  selector: 'app-course-list',
  template: `
    <input #searchInput type="text" />
    <app-course-card 
      *ngFor="let course of courses" 
      [course]="course">
    </app-course-card>
    <div #scrollContainer class="scroll-container">
      <!-- content -->
    </div>
  `
})
export class CourseListComponent implements AfterViewInit {
  // Access single element/component
  @ViewChild('searchInput') searchInput!: ElementRef<HTMLInputElement>;
  @ViewChild('scrollContainer', { static: false }) scrollContainer!: ElementRef;
  
  // Access multiple elements/components
  @ViewChildren(CourseCardComponent) courseCards!: QueryList<CourseCardComponent>;
  
  // With read option
  @ViewChild('searchInput', { read: ViewContainerRef }) 
  searchInputContainer!: ViewContainerRef;
  
  ngAfterViewInit() {
    // Elements are available here
    this.searchInput.nativeElement.focus();
    
    this.courseCards.changes.subscribe(cards => {
      console.log(`Number of cards: ${cards.length}`);
    });
  }
}

// 5. @ContentChild and @ContentChildren
@Component({
  selector: 'app-tab-container',
  template: `
    <div class="tabs">
      <ng-content select="[tab-header]"></ng-content>
    </div>
    <div class="tab-content">
      <ng-content select="[tab-content]"></ng-content>
    </div>
  `
})
export class TabContainerComponent implements AfterContentInit {
  @ContentChild('tabHeader') header!: ElementRef;
  @ContentChildren(TabItemComponent) tabs!: QueryList<TabItemComponent>;
  
  ngAfterContentInit() {
    console.log(`Found ${this.tabs.length} tabs`);
  }
}

// 6. @HostBinding and @HostListener
@Directive({
  selector: '[appHighlight]'
})
export class HighlightDirective {
  @HostBinding('class.highlighted') isHighlighted = false;
  @HostBinding('style.backgroundColor') backgroundColor = 'transparent';
  @HostBinding('attr.role') role = 'button';
  
  @HostListener('mouseenter', ['$event'])
  onMouseEnter(event: MouseEvent) {
    this.isHighlighted = true;
    this.backgroundColor = 'yellow';
  }
  
  @HostListener('mouseleave')
  onMouseLeave() {
    this.isHighlighted = false;
    this.backgroundColor = 'transparent';
  }
  
  @HostListener('window:resize', ['$event'])
  onWindowResize(event: Event) {
    console.log('Window resized');
  }
}

// 7. Custom Property Decorators
function LogProperty(target: any, propertyKey: string) {
  let value: any;
  
  const getter = () => {
    console.log(`Getting ${propertyKey}: ${value}`);
    return value;
  };
  
  const setter = (newValue: any) => {
    console.log(`Setting ${propertyKey}: ${newValue}`);
    value = newValue;
  };
  
  Object.defineProperty(target, propertyKey, {
    get: getter,
    set: setter,
    enumerable: true,
    configurable: true
  });
}

// Custom method decorator
function Debounce(delay: number = 300) {
  return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    let timeout: any;
    const original = descriptor.value;
    
    descriptor.value = function(...args: any[]) {
      clearTimeout(timeout);
      timeout = setTimeout(() => original.apply(this, args), delay);
    };
    
    return descriptor;
  };
}

// Custom class decorator
function Singleton<T extends { new(...args: any[]): {} }>(constructor: T) {
  let instance: T;
  
  return class extends constructor {
    constructor(...args: any[]) {
      if (instance) {
        return instance;
      }
      super(...args);
      instance = this as any;
    }
  };
}

// Usage of custom decorators
@Singleton
class ConfigService {
  @LogProperty
  apiUrl = 'https://api.example.com';
  
  @Debounce(500)
  search(query: string) {
    console.log('Searching:', query);
  }
}

// 8. Parameter Decorators
@Injectable()
export class AdvancedService {
  constructor(
    @Inject(API_URL) private apiUrl: string,
    @Optional() private logger?: LoggerService,
    @SkipSelf() private parentService?: ParentService,
    @Self() private localService: LocalService
  ) {}
}
```

---

### 33. Explain the difference between `public`, `private`, and `protected` access modifiers.

**Answer:**

Access modifiers control the visibility and accessibility of class members (properties and methods) in TypeScript.

**Access Modifier Overview:**

```typescript
// 1. PUBLIC (default) - Accessible everywhere
class Course {
  public title: string;           // Explicit public
  description: string;             // Implicit public (default)
  public readonly id: string;      // Public and readonly
  
  public constructor(title: string, description: string) {
    this.id = this.generateId();
    this.title = title;
    this.description = description;
  }
  
  public enroll(student: Student): void {
    console.log(`${student.name} enrolled in ${this.title}`);
  }
  
  getInfo(): string {              // Implicit public method
    return `${this.title}: ${this.description}`;
  }
  
  private generateId(): string {
    return `course_${Date.now()}`;
  }
}

// Usage
const course = new Course('Angular', 'Learn Angular');
console.log(course.title);        // ✅ Accessible
console.log(course.description);  // ✅ Accessible
course.enroll(student);           // ✅ Accessible
// course.generateId();            // ❌ Error: private method

// 2. PRIVATE - Only accessible within the class
class BankAccount {
  private balance: number;
  private readonly accountNumber: string;
  private transactions: Transaction[] = [];
  
  constructor(initialBalance: number) {
    this.balance = initialBalance;
    this.accountNumber = this.generateAccountNumber();
  }
  
  // Private method - internal use only
  private generateAccountNumber(): string {
    return `ACC${Math.random().toString(36).substring(2, 15)}`;
  }
  
  private validateAmount(amount: number): void {
    if (amount <= 0) {
      throw new Error('Amount must be positive');
    }
  }
  
  private addTransaction(type: 'deposit' | 'withdrawal', amount: number): void {
    this.transactions.push({
      type,
      amount,
      timestamp: new Date(),
      balance: this.balance
    });
  }
  
  // Public methods that use private members
  public deposit(amount: number): void {
    this.validateAmount(amount);      // ✅ Can access private method
    this.balance += amount;            // ✅ Can access private property
    this.addTransaction('deposit', amount);
  }
  
  public withdraw(amount: number): boolean {
    this.validateAmount(amount);
    if (amount > this.balance) {      // ✅ Can access private property
      return false;
    }
    this.balance -= amount;
    this.addTransaction('withdrawal', amount);
    return true;
  }
  
  public getBalance(): number {
    return this.balance;               // ✅ Controlled access to private data
  }
}

const account = new BankAccount(1000);
account.deposit(500);                 // ✅ Public method
console.log(account.getBalance());    // ✅ 1500
// console.log(account.balance);      // ❌ Error: private property
// account.validateAmount(100);       // ❌ Error: private method

// 3. PROTECTED - Accessible within class and subclasses
class User {
  protected id: string;
  protected email: string;
  protected createdAt: Date;
  public name: string;
  
  constructor(name: string, email: string) {
    this.id = this.generateId();
    this.name = name;
    this.email = email;
    this.createdAt = new Date();
  }
  
  protected generateId(): string {
    return `user_${Date.now()}`;
  }
  
  protected validateEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
  
  public getEmail(): string {
    return this.email;
  }
}

class AdminUser extends User {
  private permissions: string[];
  
  constructor(name: string, email: string, permissions: string[]) {
    super(name, email);
    this.permissions = permissions;
    this.id = `admin_${this.id}`;     // ✅ Can access protected property
  }
  
  public changeUserEmail(newEmail: string): void {
    if (this.validateEmail(newEmail)) { // ✅ Can access protected method
      this.email = newEmail;            // ✅ Can access protected property
      console.log(`Email updated at ${this.createdAt}`); // ✅ Protected
    }
  }
  
  public getAdminInfo(): string {
    return `Admin ${this.name} (${this.id})`; // ✅ Protected id accessible
  }
}

const admin = new AdminUser('John', 'john@example.com', ['read', 'write']);
console.log(admin.name);              // ✅ Public property
console.log(admin.getEmail());        // ✅ Public method
// console.log(admin.id);              // ❌ Error: protected property
// admin.validateEmail('test@test.com'); // ❌ Error: protected method
```

**Practical Examples from CourseWagon:**

```typescript
// 1. Service with mixed access modifiers
@Injectable({ providedIn: 'root' })
export class AuthService {
  // Private state management
  private currentUserSubject: BehaviorSubject<User | null>;
  private refreshTokenTimeout?: number;
  private readonly TOKEN_KEY = 'auth_token';
  
  // Protected for extension
  protected apiUrl = environment.apiUrl;
  protected httpOptions = {
    headers: new HttpHeaders({ 'Content-Type': 'application/json' })
  };
  
  // Public observables
  public currentUser$: Observable<User | null>;
  public isAuthenticated$: Observable<boolean>;
  
  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    const storedUser = this.loadStoredUser();
    this.currentUserSubject = new BehaviorSubject<User | null>(storedUser);
    this.currentUser$ = this.currentUserSubject.asObservable();
    this.isAuthenticated$ = this.currentUser$.pipe(
      map(user => !!user)
    );
  }
  
  // Private helper methods
  private loadStoredUser(): User | null {
    const token = localStorage.getItem(this.TOKEN_KEY);
    if (token) {
      try {
        return this.decodeToken(token);
      } catch {
        this.clearStorage();
      }
    }
    return null;
  }
  
  private decodeToken(token: string): User {
    // Token decoding logic
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.user;
  }
  
  private clearStorage(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem('refresh_token');
  }
  
  private scheduleTokenRefresh(expiresIn: number): void {
    this.clearTokenRefreshTimer();
    const timeout = (expiresIn - 60) * 1000; // Refresh 1 min before expiry
    this.refreshTokenTimeout = window.setTimeout(
      () => this.refreshToken().subscribe(),
      timeout
    );
  }
  
  private clearTokenRefreshTimer(): void {
    if (this.refreshTokenTimeout) {
      clearTimeout(this.refreshTokenTimeout);
    }
  }
  
  // Protected methods for subclasses
  protected handleAuthResponse(response: AuthResponse): void {
    localStorage.setItem(this.TOKEN_KEY, response.accessToken);
    localStorage.setItem('refresh_token', response.refreshToken);
    this.currentUserSubject.next(response.user);
    this.scheduleTokenRefresh(response.expiresIn);
  }
  
  // Public API
  public login(credentials: LoginCredentials): Observable<User> {
    return this.http.post<AuthResponse>(
      `${this.apiUrl}/auth/login`,
      credentials,
      this.httpOptions
    ).pipe(
      tap(response => this.handleAuthResponse(response)),
      map(response => response.user)
    );
  }
  
  public logout(): void {
    this.clearStorage();
    this.clearTokenRefreshTimer();
    this.currentUserSubject.next(null);
    this.router.navigate(['/login']);
  }
  
  public get currentUserValue(): User | null {
    return this.currentUserSubject.value;
  }
  
  public refreshToken(): Observable<AuthResponse> {
    const refreshToken = localStorage.getItem('refresh_token');
    return this.http.post<AuthResponse>(
      `${this.apiUrl}/auth/refresh`,
      { refreshToken },
      this.httpOptions
    ).pipe(
      tap(response => this.handleAuthResponse(response))
    );
  }
}

// 2. Component with proper encapsulation
@Component({
  selector: 'app-course-form',
  templateUrl: './course-form.component.html'
})
export class CourseFormComponent implements OnInit {
  // Private form state
  private destroyed$ = new Subject<void>();
  private autoSaveSubscription?: Subscription;
  
  // Protected for testing
  protected form: FormGroup;
  protected submitted = false;
  
  // Public for template binding
  public loading = false;
  public errors: ValidationErrors | null = null;
  public categories = ['Programming', 'Design', 'Business'];
  
  constructor(
    private fb: FormBuilder,
    private courseService: CourseService,
    private router: Router
  ) {
    this.form = this.createForm();
  }
  
  // Private form creation
  private createForm(): FormGroup {
    return this.fb.group({
      title: ['', [Validators.required, Validators.minLength(3)]],
      description: ['', [Validators.required, Validators.minLength(10)]],
      price: [0, [Validators.required, Validators.min(0)]],
      category: ['', Validators.required]
    });
  }
  
  private setupAutoSave(): void {
    this.autoSaveSubscription = this.form.valueChanges.pipe(
      debounceTime(3000),
      distinctUntilChanged(),
      takeUntil(this.destroyed$)
    ).subscribe(values => {
      this.saveDraft(values);
    });
  }
  
  private saveDraft(values: any): void {
    localStorage.setItem('course_draft', JSON.stringify(values));
  }
  
  private loadDraft(): void {
    const draft = localStorage.getItem('course_draft');
    if (draft) {
      try {
        this.form.patchValue(JSON.parse(draft));
      } catch (e) {
        console.error('Failed to load draft', e);
      }
    }
  }
  
  // Protected validation methods
  protected validateField(fieldName: string): void {
    const field = this.form.get(fieldName);
    if (field && field.invalid && (field.dirty || field.touched)) {
      this.errors = field.errors;
    }
  }
  
  // Public methods for template
  public ngOnInit(): void {
    this.loadDraft();
    this.setupAutoSave();
  }
  
  public onSubmit(): void {
    this.submitted = true;
    
    if (this.form.invalid) {
      this.markFormGroupTouched(this.form);
      return;
    }
    
    this.loading = true;
    this.courseService.createCourse(this.form.value).pipe(
      takeUntil(this.destroyed$)
    ).subscribe({
      next: (course) => {
        localStorage.removeItem('course_draft');
        this.router.navigate(['/courses', course.id]);
      },
      error: (error) => {
        this.loading = false;
        this.errors = error.errors;
      }
    });
  }
  
  public hasError(fieldName: string, errorType: string): boolean {
    const field = this.form.get(fieldName);
    return !!(field && field.hasError(errorType) && (field.dirty || field.touched));
  }
  
  public ngOnDestroy(): void {
    this.destroyed$.next();
    this.destroyed$.complete();
    this.autoSaveSubscription?.unsubscribe();
  }
  
  private markFormGroupTouched(formGroup: FormGroup): void {
    Object.keys(formGroup.controls).forEach(key => {
      const control = formGroup.get(key);
      control?.markAsTouched();
      
      if (control instanceof FormGroup) {
        this.markFormGroupTouched(control);
      }
    });
  }
}

// 3. Class inheritance with access modifiers
abstract class BaseEntityService<T extends { id: string }> {
  protected abstract endpoint: string;
  protected cache = new Map<string, T>();
  
  constructor(protected http: HttpClient) {}
  
  // Protected utility methods
  protected buildUrl(path: string): string {
    return `${environment.apiUrl}${this.endpoint}${path}`;
  }
  
  protected handleError(operation: string): (error: HttpErrorResponse) => Observable<never> {
    return (error: HttpErrorResponse) => {
      console.error(`${operation} failed:`, error);
      return throwError(() => error);
    };
  }
  
  // Public CRUD operations
  public getAll(): Observable<T[]> {
    return this.http.get<T[]>(this.buildUrl('')).pipe(
      tap(items => items.forEach(item => this.cache.set(item.id, item))),
      catchError(this.handleError('getAll'))
    );
  }
  
  public getById(id: string): Observable<T> {
    const cached = this.cache.get(id);
    if (cached) {
      return of(cached);
    }
    
    return this.http.get<T>(this.buildUrl(`/${id}`)).pipe(
      tap(item => this.cache.set(id, item)),
      catchError(this.handleError('getById'))
    );
  }
  
  public create(item: Omit<T, 'id'>): Observable<T> {
    return this.http.post<T>(this.buildUrl(''), item).pipe(
      tap(created => this.cache.set(created.id, created)),
      catchError(this.handleError('create'))
    );
  }
  
  // Private cache management
  private clearCache(): void {
    this.cache.clear();
  }
}

// Concrete implementation
@Injectable({ providedIn: 'root' })
export class CourseEntityService extends BaseEntityService<Course> {
  protected endpoint = '/api/courses';
  
  // Additional public methods
  public searchCourses(query: string): Observable<Course[]> {
    return this.http.get<Course[]>(
      this.buildUrl(`/search?q=${query}`)  // Uses protected method
    ).pipe(
      catchError(this.handleError('searchCourses')) // Uses protected method
    );
  }
}
```

**Best Practices:**
- Use `private` for internal implementation details
- Use `protected` for members that subclasses might need
- Use `public` explicitly for API surface
- Keep public interface minimal
- Prefer composition over inheritance when possible

---

### 34. What are async/await patterns? How do they compare to Promises and Observables?

**Answer:**

**Comparison of Asynchronous Patterns:**

```typescript
// 1. CALLBACKS (Old pattern - avoid)
function loadDataCallback(
  callback: (error: Error | null, data?: any) => void
): void {
  setTimeout(() => {
    try {
      const data = { id: 1, name: 'Course' };
      callback(null, data);
    } catch (error) {
      callback(error as Error);
    }
  }, 1000);
}

// Usage - Callback Hell
loadDataCallback((error, data) => {
  if (error) {
    console.error(error);
    return;
  }
  
  loadDataCallback((error2, data2) => {
    if (error2) {
      console.error(error2);
      return;
    }
    
    loadDataCallback((error3, data3) => {
      // Nested callbacks - hard to read and maintain
    });
  });
});

// 2. PROMISES
function loadDataPromise(): Promise<any> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      try {
        const data = { id: 1, name: 'Course' };
        resolve(data);
      } catch (error) {
        reject(error);
      }
    }, 1000);
  });
}

// Promise chaining
loadDataPromise()
  .then(data => {
    console.log('Data:', data);
    return loadDataPromise(); // Return another promise
  })
  .then(data2 => {
    console.log('Data2:', data2);
    return loadDataPromise();
  })
  .then(data3 => {
    console.log('Data3:', data3);
  })
  .catch(error => {
    console.error('Error:', error);
  })
  .finally(() => {
    console.log('Cleanup');
  });

// 3. ASYNC/AWAIT (Syntactic sugar over Promises)
async function loadDataAsync(): Promise<any> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ id: 1, name: 'Course' });
    }, 1000);
  });
}

// Sequential execution
async function processSequentially() {
  try {
    const data1 = await loadDataAsync();
    console.log('Data1:', data1);
    
    const data2 = await loadDataAsync();
    console.log('Data2:', data2);
    
    const data3 = await loadDataAsync();
    console.log('Data3:', data3);
  } catch (error) {
    console.error('Error:', error);
  } finally {
    console.log('Cleanup');
  }
}

// Parallel execution
async function processInParallel() {
  try {
    // Start all promises at once
    const [data1, data2, data3] = await Promise.all([
      loadDataAsync(),
      loadDataAsync(),
      loadDataAsync()
    ]);
    
    console.log('All data:', data1, data2, data3);
  } catch (error) {
    console.error('One failed:', error);
  }
}

// 4. OBSERVABLES (RxJS)
function loadDataObservable(): Observable<any> {
  return new Observable(observer => {
    const timeout = setTimeout(() => {
      observer.next({ id: 1, name: 'Course' });
      observer.complete();
    }, 1000);
    
    // Cleanup function
    return () => clearTimeout(timeout);
  });
}

// Observable usage
const subscription = loadDataObservable()
  .pipe(
    switchMap(data1 => {
      console.log('Data1:', data1);
      return loadDataObservable();
    }),
    switchMap(data2 => {
      console.log('Data2:', data2);
      return loadDataObservable();
    })
  )
  .subscribe({
    next: data3 => console.log('Data3:', data3),
    error: error => console.error('Error:', error),
    complete: () => console.log('Complete')
  });

// Can cancel
subscription.unsubscribe();
```

**Real-world CourseWagon Examples:**

```typescript
// 1. Service with mixed async patterns
@Injectable({ providedIn: 'root' })
export class CourseService {
  constructor(
    private http: HttpClient,
    private auth: AuthService
  ) {}
  
  // Returns Observable (Angular standard)
  getCourses(): Observable<Course[]> {
    return this.http.get<Course[]>('/api/courses');
  }
  
  // Convert Observable to Promise for async/await
  async getCoursesAsync(): Promise<Course[]> {
    return firstValueFrom(this.getCourses());
  }
  
  // Using async/await with try-catch
  async loadCourseData(courseId: string): Promise<CourseData> {
    try {
      // Parallel requests
      const [course, chapters, enrollment] = await Promise.all([
        firstValueFrom(this.http.get<Course>(`/api/courses/${courseId}`)),
        firstValueFrom(this.http.get<Chapter[]>(`/api/courses/${courseId}/chapters`)),
        firstValueFrom(this.http.get<Enrollment>(`/api/enrollments/${courseId}`))
      ]);
      
      return {
        course,
        chapters,
        enrollment,
        isEnrolled: !!enrollment
      };
    } catch (error) {
      console.error('Failed to load course data:', error);
      throw new Error('Course not found');
    }
  }
  
  // Sequential operations with async/await
  async enrollInCourse(courseId: string): Promise<Enrollment> {
    // Check authentication first
    const user = await firstValueFrom(this.auth.currentUser$);
    if (!user) {
      throw new Error('User not authenticated');
    }
    
    // Check if already enrolled
    const existingEnrollment = await this.checkEnrollment(courseId, user.id);
    if (existingEnrollment) {
      return existingEnrollment;
    }
    
    // Process payment
    const payment = await this.processPayment(courseId, user.id);
    
    // Create enrollment
    const enrollment = await firstValueFrom(
      this.http.post<Enrollment>('/api/enrollments', {
        courseId,
        userId: user.id,
        paymentId: payment.id
      })
    );
    
    // Send confirmation email
    await this.sendConfirmationEmail(enrollment);
    
    return enrollment;
  }
  
  // Error handling with async/await
  async updateCourse(
    courseId: string, 
    updates: Partial<Course>
  ): Promise<Course> {
    try {
      // Validate permissions
      const hasPermission = await this.checkPermissions(courseId);
      if (!hasPermission) {
        throw new Error('Insufficient permissions');
      }
      
      // Update course
      const updated = await firstValueFrom(
        this.http.patch<Course>(`/api/courses/${courseId}`, updates)
      );
      
      // Clear cache
      await this.clearCourseCache(courseId);
      
      return updated;
    } catch (error) {
      if (error instanceof HttpErrorResponse) {
        if (error.status === 404) {
          throw new Error('Course not found');
        } else if (error.status === 403) {
          throw new Error('Access denied');
        }
      }
      throw error;
    }
  }
  
  // Observable with async operations
  searchCoursesAdvanced(query: string): Observable<Course[]> {
    return from(this.validateSearchQuery(query)).pipe(
      switchMap(async (validQuery) => {
        // Async operation inside Observable
        const filters = await this.getUserPreferences();
        return { query: validQuery, filters };
      }),
      switchMap(({ query, filters }) => 
        this.http.post<Course[]>('/api/courses/search', { query, filters })
      ),
      catchError(async (error) => {
        // Async error handling
        await this.logError(error);
        return [];
      })
    );
  }
  
  private async validateSearchQuery(query: string): Promise<string> {
    // Async validation
    if (!query || query.length < 3) {
      throw new Error('Query too short');
    }
    return query.trim();
  }
  
  private async getUserPreferences(): Promise<any> {
    const user = await firstValueFrom(this.auth.currentUser$);
    return user?.preferences || {};
  }
  
  private async logError(error: any): Promise<void> {
    // Async logging
    await fetch('/api/logs', {
      method: 'POST',
      body: JSON.stringify({ error: error.message })
    });
  }
}

// 2. Component mixing async patterns
@Component({
  selector: 'app-course-detail'
})
export class CourseDetailComponent implements OnInit {
  course$: Observable<Course>;
  loading = true;
  error: string | null = null;
  
  constructor(
    private courseService: CourseService,
    private route: ActivatedRoute
  ) {}
  
  ngOnInit() {
    // Observable pattern for reactive updates
    this.course$ = this.route.params.pipe(
      switchMap(params => this.courseService.getCourse(params['id'])),
      tap(() => this.loading = false),
      catchError(error => {
        this.error = error.message;
        this.loading = false;
        return EMPTY;
      })
    );
    
    // Also load additional data with async/await
    this.loadAdditionalData();
  }
  
  async loadAdditionalData() {
    const courseId = this.route.snapshot.params['id'];
    
    try {
      // Sequential loading
      const recommendations = await this.loadRecommendations(courseId);
      const reviews = await this.loadReviews(courseId);
      
      // Process data
      this.processRecommendations(recommendations);
      this.processReviews(reviews);
    } catch (error) {
      console.error('Failed to load additional data:', error);
    }
  }
  
  async onEnroll() {
    this.loading = true;
    
    try {
      const courseId = this.route.snapshot.params['id'];
      const enrollment = await this.courseService.enrollInCourse(courseId);
      
      // Show success message
      this.showNotification('Successfully enrolled!');
      
      // Navigate to course player
      await this.router.navigate(['/courses', courseId, 'play']);
    } catch (error) {
      this.showError(error.message);
    } finally {
      this.loading = false;
    }
  }
  
  // Mixing Observable and Promise
  async refreshCourse() {
    const courseId = this.route.snapshot.params['id'];
    
    // Convert Observable to Promise
    const course = await firstValueFrom(
      this.courseService.getCourse(courseId)
    );
    
    // Update local state
    this.updateLocalState(course);
    
    // Return Observable for template
    return of(course);
  }
}

// 3. Testing with different async patterns
describe('CourseService', () => {
  let service: CourseService;
  
  // Testing Observables
  it('should load courses (Observable)', (done) => {
    service.getCourses().subscribe(courses => {
      expect(courses.length).toBeGreaterThan(0);
      done();
    });
  });
  
  // Testing with async/await
  it('should load courses (async/await)', async () => {
    const courses = await service.getCoursesAsync();
    expect(courses.length).toBeGreaterThan(0);
  });
  
  // Testing with fakeAsync
  it('should load courses (fakeAsync)', fakeAsync(() => {
    let courses: Course[];
    service.getCourses().subscribe(c => courses = c);
    tick();
    expect(courses!.length).toBeGreaterThan(0);
  }));
  
  // Testing error handling
  it('should handle errors', async () => {
    try {
      await service.enrollInCourse('invalid-id');
      fail('Should have thrown');
    } catch (error) {
      expect(error.message).toContain('not found');
    }
  });
});
```

**When to Use Each Pattern:**

```typescript
// Use OBSERVABLES when:
// - Multiple values over time (streams)
// - Need cancellation
// - Complex transformations with operators
// - Angular's HTTP client
// - Reactive forms

class WebSocketService {
  messages$: Observable<Message> = new Observable(observer => {
    const ws = new WebSocket('ws://localhost:8080');
    
    ws.onmessage = (event) => observer.next(JSON.parse(event.data));
    ws.onerror = (error) => observer.error(error);
    ws.onclose = () => observer.complete();
    
    return () => ws.close(); // Cleanup
  });
}

// Use PROMISES/ASYNC-AWAIT when:
// - Single value resolution
// - Sequential operations
// - Simple error handling
// - Working with Promise-based APIs

async function uploadFile(file: File): Promise<string> {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('/api/upload', {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) {
    throw new Error('Upload failed');
  }
  
  const { url } = await response.json();
  return url;
}

// Converting between patterns
class ConversionService {
  // Observable to Promise
  async observableToPromise() {
    const value = await firstValueFrom(this.getObservable());
    const values = await lastValueFrom(this.getObservable());
    return value;
  }
  
  // Promise to Observable
  promiseToObservable() {
    return from(this.getPromise());
  }
  
  // Async function to Observable
  asyncToObservable() {
    return defer(() => this.asyncFunction());
  }
  
  // Multiple Promises to Observable stream
  promisesToStream() {
    return from([
      this.promise1(),
      this.promise2(),
      this.promise3()
    ]).pipe(
      concatMap(promise => from(promise))
    );
  }
}
```

**Best Practices:**
- Use Observables for Angular HTTP and reactive patterns
- Use async/await for sequential operations and better readability
- Convert between patterns when needed using RxJS operators
- Handle errors appropriately in each pattern
- Consider cancellation requirements when choosing

---

### 35. How do you handle type inference vs explicit typing? What's your coding style?

**Answer:**

**Type Inference vs Explicit Typing Strategy:**

```typescript
// 1. WHEN TO USE TYPE INFERENCE

// Simple primitive assignments - inference is clear
const courseId = 'course-123';           // Inferred: string
const price = 99.99;                     // Inferred: number
const isPublished = true;                // Inferred: boolean
const tags = ['angular', 'typescript'];  // Inferred: string[]

// Object literals with obvious structure
const course = {
  title: 'Angular Advanced',
  price: 149.99,
  duration: 480
};  // Type is inferred from values

// Function return types when obvious
function calculateDiscount(price: number, percentage: number) {
  return price * (1 - percentage / 100);  // Return type inferred as number
}

// Array methods with type inference
const courseIds = courses
  .filter(c => c.isPublished)  // c is inferred from courses array
  .map(c => c.id)              // Return type inferred from c.id
  .slice(0, 10);                // Final type inferred as string[]

// Destructuring with inference
const { title, instructor } = course;  // Types inferred from course object

// 2. WHEN TO USE EXPLICIT TYPING

// Function parameters - always explicit
function enrollStudent(
  courseId: string,
  studentId: string,
  options?: EnrollmentOptions
): Observable<Enrollment> {
  // Implementation
}

// Class properties
class CourseService {
  private cache: Map<string, Course>;  // Explicit typing
  private baseUrl: string;             // Explicit typing
  public courses$: Observable<Course[]>; // Explicit typing
  
  constructor(private http: HttpClient) {
    this.cache = new Map();  // Inference works but explicit is clearer
    this.baseUrl = environment.apiUrl;
    this.courses$ = this.loadCourses();
  }
}

// Complex return types
function processApiResponse(
  response: unknown
): ApiResponse<Course> | ErrorResponse {  // Explicit return type
  if (isValidResponse(response)) {
    return response as ApiResponse<Course>;
  }
  return { error: 'Invalid response' };
}

// Type assertions when needed
const inputElement = document.getElementById('search') as HTMLInputElement;
const courseData = JSON.parse(jsonString) as Course;

// Generic constraints
function updateEntity<T extends BaseEntity>(
  entity: T,
  updates: Partial<T>
): T {
  return { ...entity, ...updates, updatedAt: new Date() };
}
```

**My Coding Style Guidelines:**

```typescript
// 1. SERVICE LAYER STYLE
@Injectable({ providedIn: 'root' })
export class CourseManagementService {
  // Explicit typing for class members
  private readonly courses$ = new BehaviorSubject<Course[]>([]);
  private readonly loading$ = new BehaviorSubject<boolean>(false);
  private readonly errors$ = new Subject<ApiError>();
  
  // Explicit return types for public methods
  public getCourses(): Observable<Course[]> {
    return this.courses$.asObservable();
  }
  
  public getCourse(id: string): Observable<Course | undefined> {
    return this.courses$.pipe(
      map(courses => courses.find(c => c.id === id))
    );
  }
  
  // Explicit parameter types, inferred internal variables
  public async createCourse(
    courseData: CreateCourseDto,
    options?: CourseOptions
  ): Promise<Course> {
    // Inferred for simple assignments
    const url = `${this.apiUrl}/courses`;
    const headers = this.buildHeaders(options);
    
    try {
      // Explicit typing when type isn't obvious
      const response: ApiResponse<Course> = await this.http
        .post<ApiResponse<Course>>(url, courseData, { headers })
        .toPromise();
      
      // Inferred from response
      const newCourse = response.data;
      
      // Update state
      const currentCourses = this.courses$.value;
      this.courses$.next([...currentCourses, newCourse]);
      
      return newCourse;
    } catch (error) {
      // Explicit when handling unknown types
      const apiError = this.handleError(error as HttpErrorResponse);
      this.errors$.next(apiError);
      throw apiError;
    }
  }
  
  // Private methods can use more inference
  private buildHeaders(options?: CourseOptions) {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });
    
    if (options?.includeAuth) {
      return headers.set('Authorization', `Bearer ${this.getToken()}`);
    }
    
    return headers;
  }
}

// 2. COMPONENT STYLE
@Component({
  selector: 'app-course-list',
  templateUrl: './course-list.component.html'
})
export class CourseListComponent implements OnInit, OnDestroy {
  // Explicit typing for template bindings
  courses$: Observable<Course[]>;
  loading$: Observable<boolean>;
  selectedCourse: Course | null = null;
  filters: CourseFilters = {
    category: '',
    level: 'all',
    sortBy: 'date'
  };
  
  // Explicit for subscriptions
  private destroy$ = new Subject<void>();
  
  constructor(
    private courseService: CourseService,
    private router: Router,
    private route: ActivatedRoute
  ) {
    // Initialize observables with explicit types
    this.courses$ = this.initializeCourses();
    this.loading$ = this.courseService.loading$;
  }
  
  ngOnInit(): void {
    // Inferred for route params
    this.route.queryParams
      .pipe(takeUntil(this.destroy$))
      .subscribe(params => {
        // Explicit when transforming
        const filters: CourseFilters = {
          category: params['category'] || '',
          level: params['level'] || 'all',
          sortBy: params['sort'] || 'date'
        };
        this.applyFilters(filters);
      });
  }
  
  // Explicit return types for public methods
  onCourseSelect(course: Course): void {
    this.selectedCourse = course;
    this.router.navigate(['/courses', course.id]);
  }
  
  onFilterChange(filterType: keyof CourseFilters, value: string): void {
    // Inferred for simple updates
    const newFilters = {
      ...this.filters,
      [filterType]: value
    };
    this.applyFilters(newFilters);
  }
  
  // Private methods can use inference
  private initializeCourses() {
    return this.courseService.getCourses().pipe(
      map(courses => this.sortCourses(courses, this.filters.sortBy)),
      shareReplay(1)
    );
  }
  
  private sortCourses(courses: Course[], sortBy: string) {
    // Inference for internal logic
    const sorted = [...courses];
    
    switch (sortBy) {
      case 'date':
        return sorted.sort((a, b) => 
          b.createdAt.getTime() - a.createdAt.getTime()
        );
      case 'title':
        return sorted.sort((a, b) => 
          a.title.localeCompare(b.title)
        );
      case 'price':
        return sorted.sort((a, b) => a.price - b.price);
      default:
        return sorted;
    }
  }
  
  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}

// 3. UTILITY FUNCTIONS STYLE
// Explicit generics and constraints
export function groupBy<T, K extends keyof T>(
  items: T[],
  key: K
): Map<T[K], T[]> {
  // Inferred for implementation
  const grouped = new Map<T[K], T[]>();
  
  for (const item of items) {
    const groupKey = item[key];
    const group = grouped.get(groupKey) || [];
    group.push(item);
    grouped.set(groupKey, group);
  }
  
  return grouped;
}

// Explicit for complex types
export function createPaginatedResponse<T>(
  items: T[],
  page: number,
  pageSize: number,
  total: number
): PaginatedResponse<T> {
  return {
    data: items,
    pagination: {
      page,
      pageSize,
      total,
      totalPages: Math.ceil(total / pageSize),
      hasNext: page * pageSize < total,
      hasPrev: page > 1
    }
  };
}

// 4. TYPE DEFINITIONS STYLE
// Always explicit for interfaces and types
interface Course {
  id: string;
  title: string;
  description: string;
  instructor: Instructor;
  chapters: Chapter[];
  price: number;
  currency: Currency;
  tags: string[];
  level: CourseLevel;
  duration: number;
  rating: Rating;
  createdAt: Date;
  updatedAt: Date;
}

type CourseLevel = 'beginner' | 'intermediate' | 'advanced';
type Currency = 'USD' | 'EUR' | 'GBP';

interface Rating {
  average: number;
  count: number;
  distribution: Record<1 | 2 | 3 | 4 | 5, number>;
}

// 5. CONFIGURATION AND CONSTANTS
// Explicit for exported constants
export const COURSE_CATEGORIES: ReadonlyArray<Category> = [
  { id: 'dev', name: 'Development', icon: 'code' },
  { id: 'design', name: 'Design', icon: 'palette' },
  { id: 'business', name: 'Business', icon: 'briefcase' }
] as const;

export const DEFAULT_PAGINATION: Readonly<PaginationConfig> = {
  pageSize: 20,
  maxPageSize: 100,
  defaultSort: 'createdAt:desc'
};

// 6. ERROR HANDLING STYLE
class CourseError extends Error {
  // Explicit for public properties
  public readonly code: string;
  public readonly statusCode: number;
  public readonly details?: Record<string, any>;
  
  constructor(
    message: string,
    code: string = 'COURSE_ERROR',
    statusCode: number = 500,
    details?: Record<string, any>
  ) {
    super(message);
    this.name = 'CourseError';
    this.code = code;
    this.statusCode = statusCode;
    this.details = details;
  }
  
  // Explicit return types for methods
  public toJSON(): ErrorResponse {
    return {
      error: this.message,
      code: this.code,
      statusCode: this.statusCode,
      details: this.details
    };
  }
}
```

**My Type Safety Principles:**

```typescript
// 1. Strict Configuration
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}

// 2. Type Guards for Runtime Safety
function isCourse(obj: unknown): obj is Course {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'title' in obj &&
    'price' in obj
  );
}

// 3. Branded Types for Domain Modeling
type UserId = string & { readonly brand: unique symbol };
type CourseId = string & { readonly brand: unique symbol };

function createUserId(id: string): UserId {
  return id as UserId;
}

function createCourseId(id: string): CourseId {
  return id as CourseId;
}

// Prevents mixing IDs
function enrollUser(userId: UserId, courseId: CourseId): void {
  // Type safe - can't accidentally swap parameters
}

// 4. Const Assertions for Literals
const ROLES = ['student', 'instructor', 'admin'] as const;
type Role = typeof ROLES[number]; // 'student' | 'instructor' | 'admin'

const config = {
  apiUrl: 'https://api.example.com',
  timeout: 5000,
  retries: 3
} as const;

// 5. Template Literal Types
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';
type ApiEndpoint = `/api/${string}`;
type RoutePattern = `/${string}/:${string}`;

function apiCall(
  method: HttpMethod,
  endpoint: ApiEndpoint
): Observable<unknown> {
  // Type-safe API calls
}
```

**Best Practices Summary:**
- **Explicit** for: public APIs, function parameters, return types, class properties
- **Inference** for: local variables, simple assignments, array operations
- **Always explicit** for: exported functions, public methods, type definitions
- **Use inference** when: type is obvious, reduces noise, improves readability
- **Be consistent** within a codebase and team