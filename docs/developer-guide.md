---
layout: default
title: Developer Guide
nav_order: 6
description: "Guide for developers contributing to CourseWagon"
---

# Developer Guide
{: .no_toc }

Everything you need to know to contribute to CourseWagon.
{: .fs-6 .fw-300 }

## Table of Contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Welcome Contributors!

We're excited that you're interested in contributing to CourseWagon! This guide will help you get started with development, understand our codebase, and make your first contribution.

---

## Development Environment Setup

### Prerequisites

Ensure you have these tools installed:

- **Node.js** v18+ and npm
- **Python** 3.10+
- **MySQL** 8.0+
- **Git**
- **Code Editor** (VS Code recommended)

### Recommended VS Code Extensions

**For Frontend (Angular):**
- Angular Language Service
- ESLint
- Prettier
- Angular Snippets
- TypeScript Hero

**For Backend (Python):**
- Python
- Pylance
- Python Docstring Generator
- autoDocstring

**General:**
- GitLens
- REST Client
- MySQL (for database management)

### Fork and Clone

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/coursewagon.git
   cd coursewagon
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/Uttam-Mahata/coursewagon.git
   ```

### Setup Development Environment

Follow the [Getting Started Guide](getting-started) to set up both frontend and backend.

---

## Project Structure

### Repository Layout

```
coursewagon/
├── angular-client/           # Frontend Angular application
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/   # Feature components
│   │   │   ├── services/     # API clients & utilities
│   │   │   ├── guards/       # Route guards
│   │   │   ├── pipes/        # Custom pipes
│   │   │   └── directives/   # Custom directives
│   │   ├── environments/     # Environment configs
│   │   └── styles.css        # Global styles
│   ├── package.json
│   └── angular.json
│
├── python-server/            # Backend FastAPI application
│   ├── app.py                # Application entry point
│   ├── routes/               # API endpoints
│   ├── services/             # Business logic
│   ├── repositories/         # Data access layer
│   ├── models/               # Database models
│   ├── middleware/           # Request/response processing
│   ├── utils/                # Helper utilities
│   ├── migrations/           # Database migrations
│   ├── tests/                # Test files
│   └── requirements.txt
│
├── docs/                     # Documentation
├── .github/                  # GitHub Actions workflows
├── README.md
├── CLAUDE.md                 # AI assistant instructions
└── LICENSE
```

---

## Development Workflow

### Creating a Feature Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name
```

### Making Changes

1. **Make your changes** in your feature branch
2. **Follow coding standards** (see below)
3. **Test your changes** thoroughly
4. **Commit with clear messages**:
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(content): add math equation rendering support
fix(auth): resolve token refresh issue
docs(api): update API reference for new endpoints
refactor(services): improve error handling in course service
test(api): add tests for authentication endpoints
```

### Submitting a Pull Request

1. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request** on GitHub:
   - Go to your fork on GitHub
   - Click "Compare & pull request"
   - Fill in the PR template
   - Link related issues

3. **PR Description Should Include**:
   - What changes were made
   - Why the changes were necessary
   - How to test the changes
   - Screenshots (for UI changes)
   - Related issue numbers

4. **Wait for Review**:
   - Address reviewer feedback
   - Make requested changes
   - Keep the PR up to date with main branch

---

## Coding Standards

### Frontend (TypeScript/Angular)

**Style Guide:**
- Follow [Angular Style Guide](https://angular.io/guide/styleguide)
- Use TypeScript strict mode
- Prefer standalone components
- Use RxJS for async operations

**Naming Conventions:**
```typescript
// Components
export class CourseListComponent { }

// Services
export class CourseService { }

// Interfaces
export interface Course { }

// Constants
export const API_BASE_URL = '';

// Variables - camelCase
const courseTitle = 'Web Development';

// Private properties with underscore
private _courses: Course[] = [];
```

**Component Structure:**
```typescript
@Component({
  selector: 'app-feature',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './feature.component.html',
  styleUrls: ['./feature.component.css']
})
export class FeatureComponent implements OnInit, OnDestroy {
  // Public properties
  public courses: Course[] = [];
  
  // Private properties
  private subscription: Subscription;
  
  constructor(private courseService: CourseService) {}
  
  ngOnInit(): void {
    // Initialize
  }
  
  ngOnDestroy(): void {
    // Cleanup subscriptions
    this.subscription?.unsubscribe();
  }
  
  // Public methods
  public loadCourses(): void { }
  
  // Private methods
  private processCourses(): void { }
}
```

**RxJS Best Practices:**
```typescript
// Always unsubscribe
this.subscription = this.courseService.getCourses()
  .subscribe(courses => this.courses = courses);

// Use async pipe when possible
courses$ = this.courseService.getCourses();

// Error handling
this.courseService.getCourses()
  .pipe(
    catchError(error => {
      console.error('Error loading courses:', error);
      return of([]);
    })
  )
  .subscribe(courses => this.courses = courses);
```

### Backend (Python/FastAPI)

**Style Guide:**
- Follow [PEP 8](https://pep8.org/)
- Use type hints
- Write docstrings for functions and classes
- Use snake_case for functions and variables

**Naming Conventions:**
```python
# Classes - PascalCase
class CourseService:
    pass

# Functions - snake_case
def get_course_by_id(course_id: int) -> Course:
    pass

# Constants - UPPER_SNAKE_CASE
API_BASE_URL = "https://api.coursewagon.live"

# Variables - snake_case
course_title = "Web Development"

# Private methods - leading underscore
def _validate_course(self, course: Course) -> bool:
    pass
```

**Function Documentation:**
```python
def generate_content(
    course_id: int,
    subject_id: int,
    topic_id: int
) -> Content:
    """
    Generate AI-powered content for a topic.
    
    Args:
        course_id: The ID of the course
        subject_id: The ID of the subject
        topic_id: The ID of the topic
    
    Returns:
        Content: The generated content object
    
    Raises:
        ValueError: If any ID is invalid
        APIError: If Gemini API fails
    """
    pass
```

**Error Handling:**
```python
# Use HTTPException for API errors
from fastapi import HTTPException

if not course:
    raise HTTPException(
        status_code=404,
        detail="Course not found"
    )

# Use try-except for external services
try:
    content = gemini_helper.generate_content(prompt)
except Exception as e:
    logger.error(f"Gemini API error: {e}")
    raise HTTPException(
        status_code=500,
        detail="Failed to generate content"
    )
```

**Database Operations:**
```python
# Always use dependency injection for db
@router.get("/courses/{course_id}")
async def get_course(
    course_id: int,
    db: Session = Depends(get_db)
):
    course = course_repository.get_course_by_id(db, course_id)
    return course

# Use repositories for data access
class CourseRepository:
    def get_course_by_id(
        self,
        db: Session,
        course_id: int
    ) -> Optional[Course]:
        return db.query(Course).filter(
            Course.id == course_id
        ).first()
```

---

## Testing

### Frontend Testing

**Run Tests:**
```bash
cd angular-client
npm test
```

**Write Unit Tests:**
```typescript
describe('CourseService', () => {
  let service: CourseService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [CourseService]
    });
    service = TestBed.inject(CourseService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  it('should fetch courses', () => {
    const mockCourses = [{ id: 1, title: 'Test' }];
    
    service.getCourses().subscribe(courses => {
      expect(courses).toEqual(mockCourses);
    });

    const req = httpMock.expectOne('/api/courses');
    expect(req.request.method).toBe('GET');
    req.flush(mockCourses);
  });

  afterEach(() => {
    httpMock.verify();
  });
});
```

### Backend Testing

**Run Tests:**
```bash
cd python-server
python -m pytest tests/
```

**Write Unit Tests:**
```python
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_get_courses():
    response = client.get("/api/courses")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_course():
    course_data = {
        "title": "Test Course",
        "description": "Test description"
    }
    response = client.post("/api/courses", json=course_data)
    assert response.status_code == 201
    assert response.json()["title"] == "Test Course"
```

**Test Coverage:**
```bash
# Run with coverage
pytest --cov=. tests/

# Generate HTML report
pytest --cov=. --cov-report=html tests/
```

---

## Adding New Features

### Adding a New API Endpoint

1. **Define Model** (if needed):
   ```python
   # models/feature.py
   class Feature(Base):
       __tablename__ = "features"
       id = Column(Integer, primary_key=True)
       name = Column(String(255))
   ```

2. **Create Repository**:
   ```python
   # repositories/feature_repository.py
   class FeatureRepository:
       def get_all(self, db: Session):
           return db.query(Feature).all()
   ```

3. **Create Service**:
   ```python
   # services/feature_service.py
   class FeatureService:
       def __init__(self):
           self.repository = FeatureRepository()
       
       def get_features(self, db: Session):
           return self.repository.get_all(db)
   ```

4. **Create Route**:
   ```python
   # routes/feature_routes.py
   from fastapi import APIRouter, Depends
   
   router = APIRouter(prefix="/api/features")
   
   @router.get("/")
   async def get_features(db: Session = Depends(get_db)):
       service = FeatureService()
       return service.get_features(db)
   ```

5. **Register Route** in `app.py`:
   ```python
   from routes import feature_routes
   app.include_router(feature_routes.router)
   ```

### Adding a New Frontend Component

1. **Generate Component**:
   ```bash
   ng generate component feature-name
   ```

2. **Create Service** (if needed):
   ```bash
   ng generate service services/feature
   ```

3. **Implement Component**:
   ```typescript
   export class FeatureComponent implements OnInit {
     features: Feature[] = [];
     
     constructor(private featureService: FeatureService) {}
     
     ngOnInit(): void {
       this.loadFeatures();
     }
     
     loadFeatures(): void {
       this.featureService.getFeatures()
         .subscribe(features => this.features = features);
     }
   }
   ```

4. **Add Route** in routing module:
   ```typescript
   {
     path: 'feature',
     component: FeatureComponent,
     canActivate: [AuthGuard]
   }
   ```

---

## Database Migrations

### Creating a Migration

1. **Create migration file** in `python-server/migrations/`:
   ```python
   # migrations/add_new_column.py
   import sys
   import os
   sys.path.append(os.path.dirname(os.path.dirname(__file__)))
   
   from extensions import engine
   from sqlalchemy import text
   
   def upgrade():
       with engine.connect() as conn:
           conn.execute(text("""
               ALTER TABLE courses
               ADD COLUMN new_field VARCHAR(255)
           """))
           conn.commit()
   
   if __name__ == "__main__":
       upgrade()
       print("Migration completed!")
   ```

2. **Run migration**:
   ```bash
   python migrations/add_new_column.py
   ```

3. **Update model** to reflect changes

---

## Debugging

### Frontend Debugging

**Browser DevTools:**
- Open Chrome DevTools (F12)
- Use Console for logs
- Use Network tab for API calls
- Use Angular DevTools extension

**VS Code Debugging:**
```json
// .vscode/launch.json
{
  "type": "chrome",
  "request": "launch",
  "name": "Angular Debug",
  "url": "http://localhost:4200",
  "webRoot": "${workspaceFolder}/angular-client"
}
```

### Backend Debugging

**Python Debugger:**
```python
import pdb; pdb.set_trace()  # Set breakpoint
```

**VS Code Debugging:**
```json
// .vscode/launch.json
{
  "type": "python",
  "request": "launch",
  "name": "FastAPI Debug",
  "program": "${workspaceFolder}/python-server/app.py",
  "console": "integratedTerminal"
}
```

**Logging:**
```python
import logging

logger = logging.getLogger(__name__)
logger.info("Info message")
logger.error("Error message")
```

---

## Performance Optimization

### Frontend Optimization

**Lazy Loading:**
```typescript
// Lazy load feature modules
{
  path: 'feature',
  loadChildren: () => import('./feature/feature.module')
    .then(m => m.FeatureModule)
}
```

**Change Detection:**
```typescript
// Use OnPush for better performance
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush
})
```

**TrackBy Functions:**
```typescript
trackByCourseId(index: number, course: Course): number {
  return course.id;
}
```

### Backend Optimization

**Database Queries:**
```python
# Use eager loading to avoid N+1 queries
courses = db.query(Course).options(
    joinedload(Course.subjects)
).all()

# Use pagination
def get_courses_paginated(
    db: Session,
    skip: int = 0,
    limit: int = 20
):
    return db.query(Course).offset(skip).limit(limit).all()
```

**Caching** (future enhancement):
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_course_cached(course_id: int):
    # This will be cached
    pass
```

---

## Security Best Practices

### Frontend Security

1. **Never store sensitive data** in localStorage
2. **Sanitize user input** (Angular does this automatically)
3. **Use HTTPS** in production
4. **Validate on both client and server**

### Backend Security

1. **Validate all inputs** with Pydantic
2. **Use parameterized queries** (SQLAlchemy handles this)
3. **Hash passwords** with bcrypt
4. **Implement rate limiting**
5. **Keep dependencies updated**

---

## Documentation

### Code Comments

**When to comment:**
- Complex algorithms
- Non-obvious business logic
- Workarounds or hacks
- Public API functions

**When NOT to comment:**
- Self-explanatory code
- Obvious operations
- Already documented in docstrings

### Updating Documentation

When adding new features:

1. Update relevant `.md` files in `docs/`
2. Update API reference if adding endpoints
3. Update user guide if adding user-facing features
4. Update README if changing setup process

---

## Common Issues

### Port Already in Use

```bash
# Find process using port
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows
```

### Database Connection Issues

```bash
# Check MySQL is running
sudo systemctl status mysql  # Linux
brew services list  # Mac

# Reset database
mysql -u root -p
DROP DATABASE coursewagon;
CREATE DATABASE coursewagon;
```

### Node Module Issues

```bash
# Clear and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## Getting Help

**Stuck on something?**

1. 📖 Check this documentation
2. 🔍 Search existing [GitHub Issues](https://github.com/Uttam-Mahata/coursewagon/issues)
3. 💬 Ask in [GitHub Discussions](https://github.com/Uttam-Mahata/coursewagon/discussions)
4. 📧 Email: [contact@coursewagon.live](mailto:contact@coursewagon.live)

---

## What's Next?

- [API Reference](api-reference) - Detailed API documentation
- [System Architecture](architecture) - Understand the system design
- [Deployment Guide](deployment) - Deploy to production

---

Thank you for contributing to CourseWagon! 🎉
