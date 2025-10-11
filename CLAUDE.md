# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CourseWagon is an educational platform with AI-powered course content generation. It consists of:
- **Angular 19 Frontend** (`angular-client/`) - Modern responsive web app with Tailwind CSS
- **FastAPI Backend** (`python-server/`) - Python REST API with MySQL database
- **AI Integration** - Google Gemini AI for content generation and image processing
- **Caching Layer** - Redis (primary) with in-memory fallback for performance optimization

## Architecture

### Backend Structure (python-server/)

The backend follows a layered architecture:

```
app.py                    # FastAPI app entry point with lifespan management
├── routes/              # API endpoints (course, subject, chapter, topic, content, auth, admin, testimonial, image, enrollment, learning, utility)
├── services/            # Business logic layer
├── repositories/        # Data access layer
├── models/              # SQLAlchemy models (User, Course, Subject, Chapter, Topic, Content, Testimonial, PasswordReset)
├── middleware/          # Auth middleware for JWT verification
├── utils/               # Helpers (JWT, Gemini AI, Azure/Firebase storage, encryption, caching)
├── admin/               # Admin-specific routes, services, and repositories
├── migrations/          # Database migration scripts
└── extensions.py        # Database setup with connection pooling
```

**Key architectural patterns:**
- **Repository Pattern**: All database access goes through repository classes
- **Service Layer**: Business logic is separated from routes
- **Dependency Injection**: FastAPI dependencies for database sessions and auth
- **Lifespan Management**: Database migrations run on startup; background tasks are initialized and cleaned up properly
- **Caching Strategy**: Two-tier caching with Redis (primary) and in-memory (fallback)

### Frontend Structure (angular-client/src/app/)

```
app/
├── services/           # API clients, auth, navigation, math rendering, cache service
├── admin/              # Admin dashboard components (users, testimonials)
├── auth/               # Authentication component
├── guards/             # Route guards (AuthGuard, NonAuthGuard, AdminGuard)
├── interceptors/       # HTTP interceptors (cache, auth)
├── pipes/              # Custom pipes (filter-by-id)
├── directives/         # Custom directives (click-outside)
├── shared/             # Shared modules (markdown)
└── components/         # Feature components (courses, subjects, content, profile, etc.)
```

**Key frontend features:**
- **Standalone Components**: Angular 19 standalone architecture (no NgModules)
- **Firebase Auth**: Client-side authentication with JWT tokens sent to backend
- **Markdown Rendering**: ngx-markdown with KaTeX and MathJax for equations
- **Mermaid Diagrams**: Dynamic diagram rendering with mermaid.js
- **Route Guards**: Protect routes based on authentication and admin status
- **HTTP Cache Interceptor**: Automatic GET request caching (3 min TTL)
- **Multi-layer Caching**: Memory cache, LocalStorage, and Observable caching with shareReplay

### Data Hierarchy

The content is organized hierarchically:
```
Course → Subject → Chapter → Topic → Content
```

**Note**: The architecture has evolved and there's ongoing migration from a chapter-based structure to a flatter subject-topic structure. Legacy routes still exist for backward compatibility.

### Caching Architecture

**Backend Caching** (`utils/cache_helper.py`):
- Redis-based primary cache with in-memory fallback
- Decorator support: `@cached(ttl=600, key_prefix="course")`
- Pattern-based invalidation: `invalidate_cache("courses:*")`
- TTL ranges: 3-5 minutes for most resources

**Frontend Caching**:
- HTTP interceptor cache (3 min TTL for GET requests)
- Memory cache service with TTL support
- LocalStorage for persistent caching
- Observable caching with `shareReplay` for request deduplication

**Cache Key Conventions**:
- Courses: `course:{id}`, `courses:all`, `courses:user:{user_id}`
- Subjects: `subject:{id}`, `subjects:course:{course_id}`
- Topics: `topic:{id}`, `topics:subject:{subject_id}`
- Content: `content:{id}`, `content:topic:{topic_id}`

## Development Commands

### Backend (python-server/)

```bash
# Install dependencies (using uv package manager)
uv pip install -r requirements.txt

# Run development server
uvicorn app:app --reload

# Run all tests
python -m pytest tests/ -v

# Run specific tests
python -m pytest tests/test_cache.py -v

# Run tests with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Database migrations (run manually)
python migrations/add_welcome_email_sent_column.py
python migrations/add_database_indexes.py
```

**Environment Setup**:
- Copy `.env.example` to `.env` and configure all required variables
- Place Firebase service account JSON at `coursewagon-firebase-adminsdk.json`
- Set `DATABASE_URL` environment variable for MySQL connection
- Optional: Configure Redis via `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD` (falls back to in-memory cache if not set)

### Frontend (angular-client/)

```bash
# Install dependencies
npm install

# Run development server (http://localhost:4200)
npm start

# Build for production
npm run build

# Run all tests
npm test

# Run specific test file
npm test -- --include='**/cache.service.spec.ts'

# Watch mode for development
npm run watch
```

**Environment Setup**:
- Configure Firebase credentials in `src/app/config/firebase.config.ts`
- Set API endpoints in `src/environments/environment.ts` (dev) and `environment.prod.ts` (prod)

## Key Implementation Details

### Authentication Flow

1. User authenticates via Firebase Auth on frontend
2. Frontend sends Firebase ID token to backend `/api/auth/verify-token`
3. Backend verifies token with Firebase Admin SDK, creates/updates user in MySQL
4. Backend returns JWT access/refresh tokens stored in HttpOnly cookies
5. Frontend includes cookies automatically in subsequent requests
6. Middleware (`auth_middleware.py`) validates JWT on protected routes

**CORS Configuration**:
- Production: Only allows `https://www.coursewagon.live` and `https://coursewagon.web.app`
- Development: Also allows `localhost:4200` for local testing
- Cookie-based auth requires exact origin matching (no wildcards)

### AI Content Generation

- **Gemini AI**: Used for generating course subjects, chapters, topics, and detailed content
- **Image Generation**: Gemini can generate images; stored in Azure Blob Storage or Firebase Storage
- **Image Analysis**: `gemini_image_helper.py` handles image processing and analysis

### Storage Strategy

The app supports multiple storage backends:
- **Azure Blob Storage**: Primary cloud storage (configured via `AZURE_STORAGE_CONNECTION_STRING`)
- **Firebase Storage**: Alternative storage option
- **Google Cloud Storage**: Available via GCS service account
- **Unified Storage Helper**: `unified_storage_helper.py` abstracts storage operations

### Database Considerations

- **Connection Pooling**: Configured in `extensions.py` with pool_size=20, max_overflow=30, pool_recycle=3600
- **Session Management**: FastAPI dependency `get_db()` handles session lifecycle with proper rollback
- **Migrations**: Run manually via Python scripts in `migrations/`; executed on app startup in `app.py` lifespan
- **Indexes**: Performance indexes added via `migrations/add_database_indexes.py` for courses, subjects, topics, users

**Optimization Patterns**:
- Use `joinedload` for eager loading to prevent N+1 queries
- Query only needed columns for large datasets
- Implement pagination with `offset().limit()`

### Email Service

- **Gmail SMTP**: Primary email service configured via `MAIL_USERNAME` and `MAIL_PASSWORD` (Gmail App Password)
- **Mailgun**: Backup email service (can be configured via `MAILGUN_API_KEY`)
- **Templates**: HTML email templates in `python-server/templates/`
- **Background Tasks**: Email sending handled by `background_task_service.py` with APScheduler

### Performance Optimization

**Backend**:
- Cache expensive database queries using `@cached` decorator
- Invalidate caches on data mutations
- Use connection pooling for database connections

**Frontend**:
- Cache HTTP GET requests via interceptor
- Use `shareReplay` operator to deduplicate concurrent requests
- Store user preferences in LocalStorage

## Common Patterns

### Adding a New API Endpoint

1. Define model in `models/` if needed
2. Create repository in `repositories/` for database operations
3. Implement business logic in `services/` with caching if appropriate
4. Create route in `routes/` using FastAPI router
5. Register router in `app.py` with `/api` prefix
6. Consider adding cache invalidation for mutations

Example with caching:
```python
from utils.cache_helper import cached, invalidate_cache

@cached(ttl=300, key_prefix="courses")
def get_all_courses(db: Session):
    return db.query(Course).all()

def create_course(db: Session, course_data: dict):
    course = Course(**course_data)
    db.add(course)
    db.commit()
    invalidate_cache("courses:*")  # Invalidate list cache
    return course
```

### Adding a New Frontend Feature

1. Generate component: `ng generate component feature-name` (creates standalone component)
2. Create service for API calls if needed
3. Add route in `app.routes.ts` with appropriate guards
4. Implement component logic and template
5. Consider adding caching for read-heavy operations

### Working with Protected Routes

Backend:
```python
from middleware.auth_middleware import get_current_user
from fastapi import Depends

@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    # current_user contains decoded JWT payload with user_id, email, is_admin
    pass
```

Frontend:
```typescript
// Add AuthGuard to route in app.routes.ts
{ path: 'feature', component: FeatureComponent, canActivate: [AuthGuard] }

// For admin-only routes
{ path: 'admin', component: AdminComponent, canActivate: [AuthGuard, AdminGuard] }
```

### Implementing Caching

Backend:
```python
from utils.cache_helper import cached, invalidate_cache

# Cache function results
@cached(ttl=600, key_prefix="user")
def get_user_by_id(user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# Invalidate on updates
def update_user(user_id: int, data: dict):
    # ... update logic
    invalidate_cache(f"user:{user_id}:*")
```

Frontend:
```typescript
// Use cache service
this.cacheService.set('user:profile', userData, 5 * 60 * 1000);
const cached = this.cacheService.get('user:profile');

// Skip HTTP cache for specific requests
const headers = new HttpHeaders({ 'X-Skip-Cache': 'true' });
this.http.get(url, { headers });
```

## Testing

### Backend Tests
- Tests are in `python-server/tests/`
- Cover auth flows, email services, Firebase integration, image pipelines, storage, caching
- Run with pytest: `python -m pytest tests/` or `python -m pytest tests/test_cache.py -v`

### Frontend Tests
- Unit tests use Jasmine and Karma
- Run with `npm test`
- Tests are colocated with components (`.spec.ts` files)
- Run specific tests: `npm test -- --include='**/component.spec.ts'`

## Deployment

### Frontend
- Production build: `npm run build` (outputs to `dist/`)
- Deployed to Firebase Hosting: `firebase deploy`
- Live URL: https://www.coursewagon.live

### Backend
- Deployed to Google Cloud Run (primary) or Azure Container Apps
- Docker image built from `Dockerfile` in `python-server/`
- CI/CD via GitHub Actions (`.github/workflows/deploy.yml`)
- Environment variables set via cloud platform secrets
- API URL: Configured in frontend environment files

**Cloud Run Deployment**:
```bash
# Automated via GitHub Actions on push to main
# Manual deployment:
cd python-server
docker build -t gcr.io/PROJECT_ID/coursewagon-api .
docker push gcr.io/PROJECT_ID/coursewagon-api
gcloud run deploy coursewagon-api --image gcr.io/PROJECT_ID/coursewagon-api
```

**Azure Deployment** (alternative):
```bash
cd python-server
chmod +x deploy-to-azure.sh
./deploy-to-azure.sh

# Update deployment
./update-azure-deployment.sh
```

### Redis Setup (Production)

For production caching, deploy Redis:
- **Google Cloud Memorystore**: Managed Redis on GCP
- **Azure Cache for Redis**: Managed Redis on Azure
- **Self-hosted**: Docker container or dedicated instance

Set environment variables:
```bash
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
```

## Important Notes

- **Token Expiry**: JWT access tokens expire in 1 hour (configurable via `JWT_ACCESS_TOKEN_EXPIRES_HOURS`)
- **CORS**: Backend allows specific origins based on environment (production restricts to prod domains only)
- **Admin Routes**: Protected by admin middleware; check `is_admin` flag in user model
- **Legacy Routes**: Some chapter-based routes exist for backward compatibility during migration
- **Math Rendering**: Content may contain LaTeX equations; use KaTeX or MathJax on frontend
- **Mermaid Diagrams**: Content may include Mermaid.js diagram definitions
- **Cache Fallback**: System automatically falls back to in-memory cache if Redis is unavailable
- **Database Migrations**: Migrations run automatically on app startup; check logs for errors
- **Background Tasks**: APScheduler handles async email sending; cleaned up on shutdown
- **Connection Pooling**: Database pool configured for 20 base connections + 30 overflow
