# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CourseWagon is a full-stack educational platform that uses AI to generate course content. It consists of:
- **Frontend**: Angular 19 application with Tailwind CSS, Firebase authentication, and Material Design
- **Backend**: FastAPI (Python) server with MySQL database, Azure Storage, and Google Gemini AI integration

## Development Commands

### Angular Frontend (angular-client/)
```bash
# Install dependencies
npm install

# Run development server (http://localhost:4200)
npm start

# Build for production
npm run build

# Run tests
npm test
```

### Python Backend (python-server/)
```bash
# Install dependencies (using uv)
uv pip install -r requirements.txt

# Run development server (http://localhost:8000)
uvicorn app:app --reload

# Run local tests with Azure Storage
./scripts/test-local.sh
```

## Architecture Overview

### Frontend Structure
- **Routing**: App uses Angular Router with auth guards (AuthGuard, AdminGuard, NonAuthGuard)
- **Services**: Organized by feature (auth, course, content, chapter, etc.) in `src/app/services/`
- **Components**: Feature-based components (home, courses, admin, profile, etc.)
- **State Management**: Services handle state with RxJS observables
- **Authentication**: Firebase Auth integration with JWT tokens for API calls

### Backend Structure
- **API Framework**: FastAPI with async support
- **Database**: SQLAlchemy ORM with MySQL
- **File Storage**: Azure Blob Storage for images, Firebase for user uploads
- **AI Integration**: Google Gemini for content generation
- **Authentication**: JWT-based auth with Firebase integration
- **Email Service**: SendGrid integration for password reset and notifications

### Key API Patterns
- RESTful endpoints under `/api/`
- Authentication required for most endpoints (JWT in Authorization header)
- Content generation endpoints use Gemini AI
- Image upload endpoints support both Azure and Firebase storage

### Environment Configuration
- Frontend environments in `angular-client/src/environments/`
- Backend uses `.env` file with keys for:
  - Database connection (MySQL)
  - Azure Storage credentials
  - Firebase Admin SDK
  - SendGrid API
  - Google Gemini API
  - JWT secrets

### Deployment
- Frontend: Firebase Hosting
- Backend: Google Cloud Run (asia-southeast1) || Microsoft Azure 
- Database: Cloud SQL (MySQL)
- Storage: Azure Blob Storage + Firebase Storage