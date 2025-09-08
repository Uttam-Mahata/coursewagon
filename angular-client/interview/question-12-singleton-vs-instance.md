# Question 12: How do you manage singleton services vs instances per component?

## Answer

### Understanding Service Scope in Angular

Angular provides different strategies for managing service instances. CourseWagon primarily uses singleton services, but understanding when to use each pattern is crucial.

### 1. Singleton Services (Our Primary Pattern)

```typescript
// Most CourseWagon services are singletons
@Injectable({
  providedIn: 'root'  // Creates ONE instance for entire app
})
export class AuthService {
  private currentUserSource = new BehaviorSubject<any>(null);
  private isLoggedInSource = new BehaviorSubject<boolean>(false);
  
  // Shared state across entire application
  currentUser$ = this.currentUserSource.asObservable();
  isLoggedIn$ = this.isLoggedInSource.asObservable();
  
  constructor(private http: HttpClient) {
    console.log('AuthService created');  // Logs only ONCE
  }
}

// Used in multiple components - SAME instance
export class HeaderComponent {
  constructor(private auth: AuthService) {}  // Instance #1
}

export class ProfileComponent {
  constructor(private auth: AuthService) {}  // Same Instance #1
}

export class AdminComponent {
  constructor(private auth: AuthService) {}  // Still Instance #1
}
```

### 2. When Singleton Services Make Sense

```typescript
// ✅ Authentication State - Must be consistent
@Injectable({ providedIn: 'root' })
export class AuthService {
  private token: string | null = null;
  // All components need same auth state
}

// ✅ Shopping Cart - Shared across app
@Injectable({ providedIn: 'root' })
export class CartService {
  private items: CartItem[] = [];
  // Cart must be same everywhere
}

// ✅ User Preferences - Global settings
@Injectable({ providedIn: 'root' })
export class PreferencesService {
  private theme: 'light' | 'dark' = 'light';
  private language: string = 'en';
  // Settings apply app-wide
}

// ✅ WebSocket Connection - One connection for app
@Injectable({ providedIn: 'root' })
export class WebSocketService {
  private socket: WebSocket;
  // Don't want multiple connections
}
```

### 3. Instance Per Component Pattern

```typescript
// Service without providedIn
@Injectable()  // Note: No providedIn
export class FormStateService {
  private formData: any = {};
  private isDirty = false;
  
  constructor() {
    console.log('FormStateService created');  // Logs for EACH component
  }
  
  setFormData(data: any) {
    this.formData = data;
    this.isDirty = true;
  }
}

// Component 1 with its own instance
@Component({
  selector: 'app-course-create',
  providers: [FormStateService],  // New instance for this component
  template: '...'
})
export class CourseCreateComponent {
  constructor(private formState: FormStateService) {}  // Instance #1
  
  ngOnInit() {
    this.formState.setFormData({ title: 'Angular Course' });
  }
}

// Component 2 with different instance
@Component({
  selector: 'app-course-edit',
  providers: [FormStateService],  // Different instance
  template: '...'
})
export class CourseEditComponent {
  constructor(private formState: FormStateService) {}  // Instance #2
  
  ngOnInit() {
    this.formState.setFormData({ title: 'React Course' });
    // Doesn't affect CourseCreateComponent's data
  }
}
```

### 4. Component Tree Instances

```typescript
// Service instance shared with child components
@Injectable()
export class CourseEditorStateService {
  private editorState = {
    currentSection: '',
    unsavedChanges: false
  };
}

// Parent provides service
@Component({
  selector: 'app-course-editor',
  providers: [CourseEditorStateService],  // Provided here
  template: `
    <app-editor-toolbar></app-editor-toolbar>
    <app-editor-content></app-editor-content>
    <app-editor-preview></app-editor-preview>
  `
})
export class CourseEditorComponent {
  constructor(private editorState: CourseEditorStateService) {}
}

// Child components share parent's instance
@Component({
  selector: 'app-editor-toolbar',
  template: '...'
})
export class EditorToolbarComponent {
  constructor(private editorState: CourseEditorStateService) {}
  // Gets same instance as parent
}

@Component({
  selector: 'app-editor-content',
  template: '...'
})
export class EditorContentComponent {
  constructor(private editorState: CourseEditorStateService) {}
  // Also gets parent's instance
}
```

### 5. Real-World Example: Modal Service Pattern

```typescript
// Sometimes you want BOTH patterns

// Global modal manager (Singleton)
@Injectable({ providedIn: 'root' })
export class ModalService {
  private openModals: ComponentRef<any>[] = [];
  
  open(component: Type<any>, config?: any): ComponentRef<any> {
    // Create and track modal
    const modalRef = this.createModal(component, config);
    this.openModals.push(modalRef);
    return modalRef;
  }
  
  closeAll() {
    this.openModals.forEach(modal => modal.destroy());
    this.openModals = [];
  }
}

// Modal-specific state (Instance per modal)
@Injectable()
export class ModalStateService {
  private data: any;
  private result: Subject<any> = new Subject();
  
  setData(data: any) {
    this.data = data;
  }
  
  close(result?: any) {
    this.result.next(result);
    this.result.complete();
  }
}

// Each modal gets its own state
@Component({
  selector: 'app-confirm-modal',
  providers: [ModalStateService],  // New instance per modal
  template: `
    <div class="modal">
      <h2>{{ title }}</h2>
      <button (click)="confirm()">Confirm</button>
      <button (click)="cancel()">Cancel</button>
    </div>
  `
})
export class ConfirmModalComponent {
  constructor(
    private modalService: ModalService,      // Singleton
    private modalState: ModalStateService    // Instance
  ) {}
}
```

### 6. Lazy Loaded Module Services

```typescript
// Service scoped to lazy module
@Injectable({
  providedIn: 'any'  // New instance per lazy module
})
export class LazyModuleService {
  constructor() {
    console.log('LazyModuleService created');
  }
}

// Admin module (lazy loaded)
@NgModule({
  declarations: [AdminComponent],
  imports: [CommonModule],
  providers: []  // Don't need to provide, 'any' handles it
})
export class AdminModule {}

// Feature module (lazy loaded)
@NgModule({
  declarations: [FeatureComponent],
  imports: [CommonModule],
  providers: []  // Gets different instance of LazyModuleService
})
export class FeatureModule {}
```

### 7. Decision Matrix: Singleton vs Instance

| Use Case | Pattern | Example in CourseWagon |
|----------|---------|------------------------|
| **Authentication** | Singleton | AuthService - One user state |
| **HTTP Client** | Singleton | HttpClient - Connection pooling |
| **Form State** | Instance | Each form has own state |
| **Modal Data** | Instance | Each modal independent |
| **Navigation** | Singleton | Router - One route state |
| **Temp Storage** | Instance | Component-specific cache |
| **WebSocket** | Singleton | One connection per app |
| **Validation** | Instance | Form-specific rules |
| **User Preferences** | Singleton | Theme, language settings |
| **Component State** | Instance | Local component data |

### 8. Memory Management Considerations

```typescript
// Singleton - Lives forever
@Injectable({ providedIn: 'root' })
export class CacheService {
  private cache = new Map<string, any>();  // Accumulates data
  
  constructor() {
    // Need to manage memory manually
    setInterval(() => this.cleanOldEntries(), 60000);
  }
  
  private cleanOldEntries() {
    // Prevent memory leaks in long-lived service
  }
}

// Instance - Cleaned up with component
@Injectable()
export class ComponentCacheService {
  private cache = new Map<string, any>();  // Auto-cleaned
  
  // No need for cleanup - destroyed with component
}

// Component using instance service
@Component({
  providers: [ComponentCacheService]
})
export class DataViewComponent implements OnDestroy {
  constructor(private cache: ComponentCacheService) {}
  
  ngOnDestroy() {
    // Service instance is also destroyed
    // Memory automatically freed
  }
}
```

### 9. Testing Implications

```typescript
// Testing Singleton Service
describe('AuthService (Singleton)', () => {
  let service: AuthService;
  
  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AuthService);
  });
  
  afterEach(() => {
    // Must clean singleton state between tests
    service.logout();  
    localStorage.clear();
  });
  
  it('should maintain state across components', () => {
    service.login('user', 'pass');
    
    // Create multiple components
    const comp1 = TestBed.createComponent(Component1);
    const comp2 = TestBed.createComponent(Component2);
    
    // Both get same service state
    expect(comp1.componentInstance.authService).toBe(
      comp2.componentInstance.authService
    );
  });
});

// Testing Instance Service
describe('FormStateService (Instance)', () => {
  it('should have isolated state per component', () => {
    @Component({
      template: '',
      providers: [FormStateService]
    })
    class TestComponent1 {
      constructor(public formState: FormStateService) {}
    }
    
    @Component({
      template: '',
      providers: [FormStateService]
    })
    class TestComponent2 {
      constructor(public formState: FormStateService) {}
    }
    
    const fix1 = TestBed.createComponent(TestComponent1);
    const fix2 = TestBed.createComponent(TestComponent2);
    
    // Different instances
    expect(fix1.componentInstance.formState).not.toBe(
      fix2.componentInstance.formState
    );
  });
});
```

### 10. Advanced Pattern: Service Factories

```typescript
// When you need configured instances
export function createLoggerService(name: string): LoggerService {
  return new LoggerService(name);
}

@Component({
  selector: 'app-admin',
  providers: [
    {
      provide: LoggerService,
      useFactory: () => createLoggerService('AdminComponent')
    }
  ]
})
export class AdminComponent {
  constructor(private logger: LoggerService) {
    this.logger.log('Admin initialized');  // Logs: [AdminComponent] Admin initialized
  }
}

@Component({
  selector: 'app-user',
  providers: [
    {
      provide: LoggerService,
      useFactory: () => createLoggerService('UserComponent')
    }
  ]
})
export class UserComponent {
  constructor(private logger: LoggerService) {
    this.logger.log('User initialized');  // Logs: [UserComponent] User initialized
  }
}
```

### 11. Common Mistakes to Avoid

```typescript
// ❌ BAD: Storing component-specific data in singleton
@Injectable({ providedIn: 'root' })
export class BadService {
  currentFormData: any;  // Shared between all forms!
}

// ✅ GOOD: Use instance service for component data
@Injectable()
export class GoodFormService {
  currentFormData: any;  // Isolated per form
}

// ❌ BAD: Creating multiple auth services
@Component({
  providers: [AuthService]  // DON'T: Creates new auth instance!
})
export class BadComponent {}

// ✅ GOOD: Use root singleton for auth
@Component({
  // No providers - uses root singleton
})
export class GoodComponent {
  constructor(private auth: AuthService) {}  // Gets singleton
}
```

### 12. Our Service Architecture in CourseWagon

```typescript
// Singleton Services (Shared State)
- AuthService          // User authentication state
- CourseService        // Course data cache
- AdminService         // Admin operations
- NavigationService    // Navigation helpers
- FirebaseAuthService  // Firebase integration

// Could be Instance Services (If needed)
- FormBuilderService   // Per-form validation
- EditorStateService   // Per-editor state
- WizardStateService   // Per-wizard progress
- UploadService        // Per-upload progress

// Current Reality: Everything is singleton
// This works because:
// 1. Simpler to manage
// 2. App is not complex enough to need instances
// 3. No conflicting state requirements yet
```

### Interview Talking Points

1. **Default to Singleton**: Simpler, less memory overhead
2. **Use Instances for Isolation**: When components need independent state
3. **Memory Management**: Singletons live forever, instances cleaned up
4. **Testing Considerations**: Singletons need state cleanup between tests
5. **Know the Trade-offs**: Singletons share state (good and bad)
6. **Future Planning**: As app grows, may need more instance services