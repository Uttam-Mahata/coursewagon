# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CourseWagon is an educational platform with AI-powered course content generation. It consists of:
- **Angular 19 Frontend** (`angular-client/`) - Modern responsive web app with Tailwind CSS
- **FastAPI Backend** (`python-server/`) - Python REST API with MySQL database
- **AI Integration** - Google Gemini AI for content generation and image processing

## Architecture

### Backend Structure (python-server/)

The backend follows a layered architecture:

```
app.py                    # FastAPI app entry point with lifespan management
├── routes/              # API endpoints (course, subject, chapter, topic, content, auth, admin, testimonial, image)
├── services/            # Business logic layer
├── repositories/        # Data access layer
├── models/              # SQLAlchemy models (User, Course, Subject, Chapter, Topic, Content, Testimonial, PasswordReset)
├── middleware/          # Auth middleware for JWT verification
├── utils/               # Helpers (JWT, Gemini AI, Azure/Firebase storage, encryption)
├── admin/               # Admin-specific routes, services, and repositories
├── migrations/          # Database migration scripts
└── extensions.py        # Database setup with connection pooling
```

**Key architectural patterns:**
- **Repository Pattern**: All database access goes through repository classes
- **Service Layer**: Business logic is separated from routes
- **Dependency Injection**: FastAPI dependencies for database sessions and auth
- **Lifespan Management**: Database migrations run on startup; background tasks are initialized and cleaned up properly

### Frontend Structure (angular-client/src/app/)

```
app/
├── services/           # API clients, auth, navigation, math rendering
├── admin/              # Admin dashboard components (users, testimonials)
├── auth/               # Authentication component
├── guards/             # Route guards (AuthGuard, NonAuthGuard, AdminGuard)
├── pipes/              # Custom pipes (filter-by-id)
├── directives/         # Custom directives (click-outside)
├── shared/             # Shared modules (markdown)
└── components/         # Feature components (courses, subjects, content, profile, etc.)
```

**Key frontend features:**
- **Firebase Auth**: Client-side authentication with JWT tokens sent to backend
- **Markdown Rendering**: ngx-markdown with KaTeX and MathJax for equations
- **Mermaid Diagrams**: Dynamic diagram rendering with mermaid.js
- **Route Guards**: Protect routes based on authentication and admin status

### Data Hierarchy

The content is organized hierarchically:
```
Course → Subject → Chapter → Topic → Content
```

**Note**: The architecture has evolved and there's ongoing migration from a chapter-based structure to a flatter subject-topic structure. Legacy routes still exist for backward compatibility.

## Development Commands

### Backend (python-server/)

```bash
# Install dependencies (using uv package manager)
uv pip install -r requirements.txt

# Run development server
uvicorn app:app --reload

# Run specific tests
python -m pytest tests/test_specific_file.py

# Database migrations
python migrations/add_welcome_email_sent_column.py
```

**Environment Setup**:
- Copy `.env.example` to `.env` and configure all required variables
- Place Firebase service account JSON at `coursewagon-firebase-adminsdk.json`
- Set `DATABASE_URL` environment variable for MySQL connection

### Frontend (angular-client/)

```bash
# Install dependencies
npm install

# Run development server (http://localhost:4200)
npm start

# Build for production
npm run build

# Run tests
npm test

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
4. Backend returns JWT access/refresh tokens
5. Frontend stores tokens and includes JWT in Authorization header for subsequent requests
6. Middleware (`auth_middleware.py`) validates JWT on protected routes

### AI Content Generation

- **Gemini AI**: Used for generating course subjects, chapters, topics, and detailed content
- **Image Generation**: Gemini can generate images; stored in Azure Blob Storage or Firebase Storage
- **Image Analysis**: `gemini_image_helper.py` handles image processing and analysis

### Storage Strategy

The app supports multiple storage backends:
- **Azure Blob Storage**: Primary cloud storage (configured via `AZURE_STORAGE_CONNECTION_STRING`)
- **Firebase Storage**: Alternative storage option
- **Unified Storage Helper**: `unified_storage_helper.py` abstracts storage operations

### Database Considerations

- **Connection Pooling**: Configured in `extensions.py` with pool_size=20, max_overflow=30
- **Session Management**: FastAPI dependency `get_db()` handles session lifecycle with proper rollback
- **Migrations**: Run manually via Python scripts in `migrations/`; executed on app startup in `app.py` lifespan

### Email Service

- **Gmail SMTP**: Primary email service configured via `MAIL_USERNAME` and `MAIL_PASSWORD` (Gmail App Password)
- **Mailgun**: Backup email service (can be configured via `MAILGUN_API_KEY`)
- **Templates**: HTML email templates in `python-server/templates/`
- **Background Tasks**: Email sending handled by `background_task_service.py` with APScheduler

## Common Patterns

### Adding a New API Endpoint

1. Define model in `models/` if needed
2. Create repository in `repositories/` for database operations
3. Implement business logic in `services/`
4. Create route in `routes/` using FastAPI router
5. Register router in `app.py` with `/api` prefix

### Adding a New Frontend Feature

1. Generate component: `ng generate component feature-name`
2. Create service for API calls if needed
3. Add route in `app-routing.module.ts` with appropriate guards
4. Implement component logic and template

### Working with Protected Routes

Backend:
```python
from middleware.auth_middleware import get_current_user
from fastapi import Depends

@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    # current_user contains decoded JWT payload
    pass
```

Frontend:
```typescript
// Add AuthGuard to route
{ path: 'feature', component: FeatureComponent, canActivate: [AuthGuard] }
```

## Testing

### Backend Tests
- Tests are in `python-server/tests/`
- Cover auth flows, email services, Firebase integration, image pipelines, storage
- Run with pytest: `python -m pytest tests/`

### Frontend Tests
- Unit tests use Jasmine and Karma
- Run with `npm test`
- Tests are colocated with components (`.spec.ts` files)

## Deployment

### Frontend
- Production build: `npm run build` (outputs to `dist/`)
- Deployed to Firebase Hosting: `firebase deploy`
- Live URL: https://www.coursewagon.live

### Backend
- Deployed to Google Cloud Run or Azure Container Apps
- Docker image built from `Dockerfile`
- Environment variables set via cloud platform
- API URL: Configured in frontend environment files

## Important Notes

- **Token Expiry**: JWT access tokens expire in 1 hour (configurable via `JWT_ACCESS_TOKEN_EXPIRES_HOURS`)
- **CORS**: Backend allows multiple origins including localhost:4200 and production domains
- **Admin Routes**: Protected by admin middleware; check `is_admin` flag in user model
- **Legacy Routes**: Some chapter-based routes exist for backward compatibility during migration
- **Math Rendering**: Content may contain LaTeX equations; use KaTeX or MathJax on frontend
- **Mermaid Diagrams**: Content may include Mermaid.js diagram definitions
