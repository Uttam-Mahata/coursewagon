---
layout: default
title: System Architecture
nav_order: 3
description: "Comprehensive overview of CourseWagon's system architecture and design patterns"
---

# System Architecture
{: .no_toc }

Comprehensive overview of CourseWagon's system architecture, design patterns, and technology stack.
{: .fs-6 .fw-300 }

## Table of Contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## High-Level Architecture

CourseWagon follows a modern client-server architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    Client Layer                         │
│  Angular 19 SPA with Tailwind CSS, Firebase Auth       │
│  ngx-markdown, KaTeX/MathJax, Mermaid.js              │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS/REST API (JWT Auth)
┌────────────────────▼────────────────────────────────────┐
│                 API Gateway Layer                        │
│  FastAPI with CORS, Auth Middleware, Error Handling    │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Application Layer                           │
│  Routes → Services → Repositories                       │
│  Background Tasks (Email, Notifications)                │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Infrastructure Layer                        │
│  MySQL Database, Cloud Storage (GCS/Azure/Firebase)    │
│  Google Gemini AI, Email Services (Gmail/Mailgun)      │
└─────────────────────────────────────────────────────────┘
```

---

## Frontend Architecture (Angular 19)

### Component Hierarchy

```
App Component
├── Header/Footer (Always visible)
├── Router Outlet
    ├── Public Routes
    │   ├── Home
    │   ├── Auth/Login
    │   ├── How It Works
    │   ├── Help Center
    │   └── Terms/Privacy
    ├── Protected Routes (AuthGuard)
    │   ├── Courses List
    │   ├── Course Creation
    │   ├── Subjects
    │   ├── Course Content
    │   ├── Learning View
    │   ├── Profile
    │   └── Write Review
    └── Admin Routes (AdminGuard)
        ├── Admin Dashboard
        ├── User Management
        └── Testimonial Management
```

### Key Frontend Technologies

**Core Framework:**
- Angular 19 (Standalone Components)
- TypeScript
- RxJS for reactive programming

**UI & Styling:**
- Tailwind CSS 4.1
- Font Awesome icons
- Responsive design (mobile-first)

**Content Rendering:**
- **ngx-markdown**: Markdown rendering with Prism.js syntax highlighting
- **KaTeX**: Fast math rendering for inline equations
- **MathJax**: Complex math rendering for display equations
- **Mermaid.js**: Diagram rendering (flowcharts, sequence diagrams, etc.)

**Authentication:**
- Firebase Auth (client-side)
- JWT tokens for API communication
- AuthGuard, NonAuthGuard, AdminGuard for route protection

### Service Architecture

```typescript
// API Communication Layer
├── auth.service.ts          // Authentication & user management
├── course.service.ts         // Course CRUD operations
├── subject.service.ts        // Subject management
├── content.service.ts        // Content generation & retrieval
├── admin.service.ts          // Admin operations
├── testimonial.service.ts    // Testimonial management
└── image.service.ts          // Image upload & processing

// Utility Services
├── navigation.service.ts     // Navigation state management
└── math-rendering.service.ts // Math & diagram rendering helpers
```

---

## Backend Architecture (FastAPI + Python)

### Layered Architecture Pattern

```
Routes Layer (API Endpoints)
    ↓
Services Layer (Business Logic)
    ↓
Repositories Layer (Data Access)
    ↓
Models Layer (Database Schema)
    ↓
Database (MySQL with SQLAlchemy ORM)
```

### Backend Structure

```
python-server/
├── app.py                    # FastAPI application entry point
├── extensions.py             # Database setup & connection pooling
├── routes/                   # API endpoint definitions
│   ├── auth_routes.py        # Authentication endpoints
│   ├── course_routes.py      # Course management
│   ├── subject_routes.py     # Subject management
│   ├── chapter_routes.py     # Chapter management (legacy)
│   ├── topic_routes.py       # Topic management
│   ├── content_routes.py     # Content generation & retrieval
│   ├── admin_routes.py       # Admin operations
│   ├── testimonial_routes.py # Testimonial management
│   └── image_routes.py       # Image upload & processing
├── services/                 # Business logic layer
│   ├── auth_service.py       # Authentication logic
│   ├── course_service.py     # Course business logic
│   ├── content_service.py    # Content generation with Gemini AI
│   ├── image_service.py      # Image processing
│   ├── email_service.py      # Email sending
│   └── background_task_service.py  # Background job scheduler
├── repositories/             # Data access layer
│   ├── user_repository.py
│   ├── course_repository.py
│   ├── content_repository.py
│   └── ...
├── models/                   # SQLAlchemy models
│   ├── user.py
│   ├── course.py
│   ├── subject.py
│   ├── chapter.py
│   ├── topic.py
│   ├── content.py
│   ├── testimonial.py
│   └── password_reset.py
├── middleware/               # Request/response processing
│   └── auth_middleware.py    # JWT verification
├── utils/                    # Helper utilities
│   ├── jwt_helper.py         # JWT token management
│   ├── gemini_helper.py      # Gemini AI integration
│   ├── gemini_image_helper.py  # Image generation with AI
│   ├── gcs_storage_helper.py   # Google Cloud Storage
│   ├── azure_storage_helper.py # Azure Blob Storage
│   ├── firebase_storage_helper.py  # Firebase Storage
│   ├── unified_storage_helper.py   # Storage abstraction with fallback
│   └── encryption_helper.py  # Data encryption
└── migrations/               # Database migration scripts
```

### Key Backend Technologies

**Core Framework:**
- FastAPI (high-performance async API framework)
- Python 3.10+
- Uvicorn (ASGI server)

**Database:**
- MySQL 8.0
- SQLAlchemy ORM
- PyMySQL driver
- Connection pooling (pool_size=20, max_overflow=30)

**AI Integration:**
- Google Gemini AI (gemini-2.0-flash model)
- Content generation
- Image generation and analysis

**Storage:**
- Google Cloud Storage (primary)
- Azure Blob Storage (fallback)
- Firebase Storage (fallback)
- Unified storage abstraction layer

**Authentication:**
- Firebase Admin SDK for token verification
- JWT tokens for API authentication
- Password hashing with bcrypt

**Email Services:**
- Gmail SMTP (primary)
- Mailgun (backup)
- HTML email templates
- Background task scheduler (APScheduler)

---

## Database Architecture

### Entity Relationship Diagram

```
┌─────────────┐
│    User     │
├─────────────┤
│ id          │◄─────┐
│ email       │      │
│ name        │      │
│ is_admin    │      │
│ created_at  │      │
└─────────────┘      │
                     │ user_id
┌─────────────┐      │
│   Course    │      │
├─────────────┤      │
│ id          │      │
│ title       │      │
│ description │      │
│ user_id     ├──────┘
│ created_at  │
└──────┬──────┘
       │ course_id
       │
┌──────▼──────┐
│   Subject   │
├─────────────┤
│ id          │
│ name        │
│ course_id   │
│ order       │
└──────┬──────┘
       │ subject_id
       │
┌──────▼──────┐
│    Topic    │
├─────────────┤
│ id          │
│ name        │
│ subject_id  │
│ has_content │
│ order       │
└──────┬──────┘
       │ topic_id
       │
┌──────▼──────┐
│   Content   │
├─────────────┤
│ id          │
│ topic_id    │
│ content     │ (TEXT/LONGTEXT)
│ created_at  │
│ updated_at  │
└─────────────┘
```

### Data Hierarchy

CourseWagon organizes educational content in a hierarchical structure:

```
Course (Web Development)
├── Subject (HTML Basics)
│   ├── Topic (Introduction to HTML)
│   │   └── Content (Detailed lesson content)
│   ├── Topic (HTML Tags)
│   │   └── Content (Detailed lesson content)
│   └── Topic (Semantic HTML)
│       └── Content (Detailed lesson content)
├── Subject (CSS Styling)
│   ├── Topic (CSS Selectors)
│   │   └── Content (Detailed lesson content)
│   └── Topic (Flexbox Layout)
│       └── Content (Detailed lesson content)
└── Subject (JavaScript Fundamentals)
    └── ...
```

**Note**: There's ongoing migration from a chapter-based structure to a flatter subject-topic structure. Legacy chapter routes still exist for backward compatibility.

---

## Authentication & Authorization Flow

### 1. User Registration/Login

```
User → Firebase Auth (Client) → Firebase ID Token
                                      ↓
Backend receives token → Firebase Admin SDK verifies
                                      ↓
Create/Update user in MySQL → Generate JWT tokens
                                      ↓
Return JWT access & refresh tokens → Store in frontend
```

### 2. Authenticated API Requests

```
Frontend → API Request with JWT in Authorization header
              ↓
Auth Middleware → Verify JWT signature
              ↓
Extract user info → Attach to request context
              ↓
Route Handler → Access current_user data
```

### 3. Token Refresh Flow

```
Access token expires (1 hour)
    ↓
Frontend detects 401 Unauthorized
    ↓
Send refresh token to /api/auth/refresh
    ↓
Backend verifies refresh token (30 days validity)
    ↓
Generate new access token
    ↓
Return new access token → Update frontend storage
```

### Security Features

- **Password Hashing**: bcrypt with salt
- **JWT Tokens**: Signed with secret keys
- **Token Expiration**: Access (1 hour), Refresh (30 days)
- **CORS Protection**: Restricted to allowed origins
- **Rate Limiting**: Recommended at API gateway level
- **Input Validation**: Pydantic models for request validation

---

## AI Content Generation Pipeline

### Content Generation Flow

```
User Request → Course Service → Gemini AI
                                    ↓
                            Generate prompt with context
                                    ↓
                            Gemini processes (gemini-2.0-flash)
                                    ↓
                            Returns Markdown content
                                    ↓
                            Parse & validate content
                                    ↓
                            Store in database
                                    ↓
                            Return to frontend
                                    ↓
                            Render with ngx-markdown
                                    ↓
                            Process math (KaTeX/MathJax)
                                    ↓
                            Render diagrams (Mermaid.js)
```

### Gemini AI Integration

**Content Types Generated:**
1. **Course Subjects**: Generate relevant subjects for a course
2. **Topics**: Generate topics within a subject
3. **Detailed Content**: Generate comprehensive lesson content with:
   - Core concepts and definitions
   - Real-world examples
   - Mathematical equations (LaTeX format)
   - Code snippets with syntax highlighting
   - Mermaid.js diagrams (flowcharts, sequence diagrams, etc.)
   - Practice questions and exercises

**Prompt Engineering:**
- Contextual prompts with course and subject information
- Structured output requirements (Markdown format)
- Math formatting requirements ($$ for display, $ for inline)
- Diagram syntax requirements (Mermaid.js)
- Code block formatting with language tags

---

## Multi-Cloud Storage Architecture

### Storage Strategy

CourseWagon implements a resilient multi-cloud storage architecture with automatic failover:

```
Upload Request
    ↓
Unified Storage Helper
    ↓
Try: Google Cloud Storage (Primary)
    ↓ (if fails)
Try: Azure Blob Storage (Fallback 1)
    ↓ (if fails)
Try: Firebase Storage (Fallback 2)
    ↓
Return: Public URL
```

### Storage Configuration

**Google Cloud Storage (Primary):**
- Bucket: `coursewagon-storage-bucket`
- Public read access
- Service account authentication
- Fast access for deployed apps

**Azure Blob Storage (Fallback):**
- Connection string authentication
- Blob container with public access
- High availability

**Firebase Storage (Final Fallback):**
- Firebase Admin SDK
- Integrated with Firebase Auth
- Easy to configure

### Use Cases

- **Course Images**: Subject/topic thumbnails
- **User Uploads**: Profile pictures, custom content
- **AI-Generated Images**: Gemini AI-generated illustrations
- **Static Assets**: Documents, PDFs, resources

---

## Email Notification System

### Email Architecture

```
Trigger Event (User signup, Password reset)
    ↓
Background Task Service (APScheduler)
    ↓
Email Service
    ↓
Try: Gmail SMTP (Primary)
    ↓ (if fails)
Try: Mailgun API (Backup)
    ↓
Send HTML Email (Template-based)
```

### Email Features

- **Welcome Emails**: Sent on user registration
- **Password Reset**: Secure token-based reset links
- **Notifications**: Course updates, system announcements
- **HTML Templates**: Professional email designs
- **Background Processing**: Non-blocking email sending
- **Retry Logic**: Automatic retry on failure
- **Dual Providers**: Gmail SMTP + Mailgun backup

---

## Deployment Architecture

### Google Cloud Run Deployment

```
GitHub Push → GitHub Actions CI/CD
                    ↓
              Cloud Build
                    ↓
        Build Docker Image
                    ↓
        Push to Artifact Registry
                    ↓
        Deploy to Cloud Run
                    ↓
        Load secrets from Secret Manager
                    ↓
        Health check verification
                    ↓
        Live on production URL
```

### Infrastructure Components

**Frontend:**
- Firebase Hosting
- CDN distribution
- SSL/TLS certificates
- Custom domain support

**Backend:**
- Google Cloud Run (serverless containers)
- Auto-scaling (0 to N instances)
- Secrets in Google Cloud Secret Manager
- Cloud Build for CI/CD
- Artifact Registry for Docker images

**Database:**
- MySQL (Cloud SQL or external)
- Connection pooling
- Automated backups

---

## Performance Optimizations

### Frontend Optimizations

- **Lazy Loading**: Routes and modules loaded on demand
- **AOT Compilation**: Ahead-of-time compilation for production
- **Tree Shaking**: Remove unused code
- **Code Splitting**: Split bundles for faster initial load
- **CDN Delivery**: Static assets via Firebase CDN
- **Image Optimization**: Responsive images with proper formats
- **Caching**: Service worker caching (future enhancement)

### Backend Optimizations

- **Connection Pooling**: Database connections reused (pool_size=20)
- **Async Operations**: FastAPI async endpoints for I/O operations
- **Caching**: Response caching for frequently accessed data (future)
- **Query Optimization**: Indexed database columns
- **Background Tasks**: Email sending in background threads
- **Auto-scaling**: Cloud Run scales based on traffic

---

## Security Architecture

### Security Layers

**1. Network Security:**
- HTTPS/TLS encryption
- CORS restrictions
- Rate limiting (recommended)

**2. Authentication:**
- Firebase Auth (multi-factor ready)
- JWT token-based API auth
- Password hashing (bcrypt)
- Token expiration

**3. Authorization:**
- Role-based access control (admin/user)
- Route guards (AuthGuard, AdminGuard)
- Middleware verification

**4. Data Security:**
- SQL injection protection (SQLAlchemy ORM)
- XSS protection (Angular sanitization)
- CSRF protection
- Input validation (Pydantic)

**5. Secret Management:**
- Google Cloud Secret Manager
- Environment variables
- No secrets in code

---

## Design Patterns Used

### Backend Patterns

1. **Repository Pattern**: Data access abstraction
2. **Service Layer Pattern**: Business logic separation
3. **Dependency Injection**: FastAPI dependencies
4. **Factory Pattern**: Storage helper creation
5. **Strategy Pattern**: Multiple storage providers

### Frontend Patterns

1. **Component-Based Architecture**: Reusable Angular components
2. **Observer Pattern**: RxJS observables for async operations
3. **Guard Pattern**: Route protection
4. **Service Pattern**: Centralized business logic
5. **Singleton Pattern**: Shared services

---

## Future Enhancements

### Planned Features

- **Caching Layer**: Redis for API response caching
- **Search Engine**: Elasticsearch for content search
- **Real-time Features**: WebSocket for live updates
- **Progressive Web App**: Service workers for offline support
- **Analytics**: User behavior tracking
- **Recommendations**: AI-powered course recommendations
- **Collaboration**: Multi-user course editing
- **Video Content**: Video upload and streaming
- **Gamification**: Badges, points, leaderboards

---

## Need More Details?

- [API Reference](api-reference) - Detailed API documentation
- [Developer Guide](developer-guide) - Contributing guidelines
- [Deployment Guide](deployment) - Production deployment steps
