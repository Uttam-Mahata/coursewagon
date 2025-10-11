---
layout: default
title: Quick Reference
nav_order: 11
description: "Quick reference guide for common tasks"
---

# Quick Reference
{: .no_toc }

Quick access to common commands and workflows.
{: .fs-6 .fw-300 }

## Table of Contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Frontend Commands

### Development

```bash
# Navigate to frontend
cd angular-client

# Install dependencies
npm install

# Start development server
npm start
# Access at http://localhost:4200

# Build for production
npm run build

# Run tests
npm test

# Run tests in watch mode
npm run watch

# Generate component
ng generate component feature-name

# Generate service
ng generate service services/feature
```

### Common Issues

```bash
# Port already in use
ng serve --port 4201

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Fix permissions
sudo chown -R $USER:$GROUP ~/.npm
```

---

## Backend Commands

### Development

```bash
# Navigate to backend
cd python-server

# Install dependencies
pip install -r requirements.txt
# Or with uv (recommended)
uv pip install -r requirements.txt

# Start development server
uvicorn app:app --reload
# Access at http://localhost:8000

# Run tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_specific.py

# Run with coverage
pytest --cov=. tests/
```

### Database

```bash
# Create database
mysql -u root -p
CREATE DATABASE coursewagon;

# Run migrations
python migrations/migration_file.py

# Check database connection
python -c "from extensions import engine; print(engine.connect())"
```

---

## Git Workflow

### Basic Workflow

```bash
# Clone repository
git clone https://github.com/Uttam-Mahata/coursewagon.git
cd coursewagon

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push to your fork
git push origin feature/your-feature-name

# Update from upstream
git fetch upstream
git merge upstream/main
```

### Commit Message Format

```bash
# Feature
git commit -m "feat(scope): add new feature"

# Bug fix
git commit -m "fix(scope): resolve issue"

# Documentation
git commit -m "docs: update API documentation"

# Refactoring
git commit -m "refactor(scope): improve code structure"

# Tests
git commit -m "test: add unit tests for feature"
```

---

## Environment Setup

### Frontend Environment

```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api',
  firebase: {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_PROJECT.firebaseapp.com",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_PROJECT.appspot.com",
    messagingSenderId: "YOUR_SENDER_ID",
    appId: "YOUR_APP_ID"
  }
};
```

### Backend Environment

```bash
# .env file
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/coursewagon
JWT_SECRET_KEY=your-secret-key
JWT_REFRESH_SECRET_KEY=your-refresh-key
GEMINI_API_KEY=your-gemini-key
FIREBASE_CREDENTIALS_PATH=./firebase-adminsdk.json
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

---

## Docker Commands

### Build and Run

```bash
# Build Docker image
docker build -t coursewagon-api .

# Run container
docker run -p 8000:8000 --env-file .env coursewagon-api

# Stop container
docker stop <container-id>

# Remove container
docker rm <container-id>

# Remove image
docker rmi coursewagon-api
```

---

## API Endpoints

### Authentication

```bash
# Verify Firebase token
curl -X POST http://localhost:8000/api/auth/verify-token \
  -H "Content-Type: application/json" \
  -d '{"id_token": "YOUR_FIREBASE_TOKEN"}'

# Refresh access token
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

### Courses

```bash
# Get all courses
curl -X GET http://localhost:8000/api/courses \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Create course
curl -X POST http://localhost:8000/api/courses \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Course Title", "description": "Description"}'

# Get course by ID
curl -X GET http://localhost:8000/api/courses/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Content Generation

```bash
# Generate subjects
curl -X POST http://localhost:8000/api/subjects/1/generate \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"count": 5}'

# Generate topics
curl -X POST http://localhost:8000/api/topics/subject/1/generate \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"count": 10}'

# Generate content
curl -X POST http://localhost:8000/api/content/courses/1/subjects/1/chapters/1/topics/1/generate \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Database Queries

### MySQL Common Queries

```sql
-- View all courses
SELECT * FROM courses;

-- View course with subjects
SELECT c.*, COUNT(s.id) as subject_count
FROM courses c
LEFT JOIN subjects s ON c.id = s.course_id
GROUP BY c.id;

-- View topics with content status
SELECT t.*, c.id IS NOT NULL as has_content
FROM topics t
LEFT JOIN contents c ON t.id = c.topic_id
WHERE t.subject_id = 1;

-- Get user course count
SELECT u.email, COUNT(c.id) as course_count
FROM users u
LEFT JOIN courses c ON u.id = c.user_id
GROUP BY u.id;
```

---

## Deployment

### Google Cloud Run

```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT_ID/coursewagon-api

# Deploy to Cloud Run
gcloud run deploy coursewagon-api \
  --image gcr.io/PROJECT_ID/coursewagon-api \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated

# View logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# Update service
gcloud run services update coursewagon-api \
  --region us-central1 \
  --set-env-vars KEY=VALUE
```

### Firebase Hosting

```bash
# Login to Firebase
firebase login

# Initialize project
firebase init

# Build frontend
cd angular-client
npm run build

# Deploy to Firebase
firebase deploy --only hosting

# View hosting URL
firebase hosting:channel:list
```

---

## Testing

### Frontend Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test -- feature.component.spec.ts
```

### Backend Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_auth.py

# Run with coverage
pytest --cov=. --cov-report=html tests/

# Run tests matching pattern
pytest -k "test_course"
```

---

## Debugging

### Frontend Debugging

```typescript
// Add breakpoint in code
debugger;

// Console logging
console.log('Debug:', variable);
console.table(arrayOfObjects);
console.error('Error:', error);

// Chrome DevTools
// Press F12 or Cmd+Option+I (Mac) / Ctrl+Shift+I (Windows)
```

### Backend Debugging

```python
# Python debugger
import pdb; pdb.set_trace()

# Logging
import logging
logger = logging.getLogger(__name__)
logger.info("Info message")
logger.error("Error message")

# Print debugging
print(f"Debug: {variable}")
```

---

## VS Code Shortcuts

### General

- `Cmd/Ctrl + P` - Quick file open
- `Cmd/Ctrl + Shift + P` - Command palette
- `Cmd/Ctrl + B` - Toggle sidebar
- `Cmd/Ctrl + J` - Toggle terminal

### Editing

- `Cmd/Ctrl + D` - Select next occurrence
- `Cmd/Ctrl + Shift + L` - Select all occurrences
- `Alt + Up/Down` - Move line up/down
- `Shift + Alt + Up/Down` - Copy line up/down
- `Cmd/Ctrl + /` - Toggle comment

### Navigation

- `Cmd/Ctrl + G` - Go to line
- `Cmd/Ctrl + Shift + O` - Go to symbol
- `F12` - Go to definition
- `Alt + Left/Right` - Go back/forward

---

## Common Markdown Syntax

### Text Formatting

```markdown
**Bold text**
*Italic text*
***Bold and italic***
~~Strikethrough~~
`Inline code`
```

### Code Blocks

````markdown
```python
def hello():
    print("Hello, World!")
```
````

### Math Equations

```markdown
Inline: $E = mc^2$

Display:
$$
\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
$$
```

### Mermaid Diagrams

````markdown
```mermaid
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[End]
    B -->|No| D[End]
```
````

---

## Useful Links

### Documentation
- [Getting Started](getting-started)
- [Architecture](architecture)
- [API Reference](api-reference)
- [User Guide](user-guide)
- [Developer Guide](developer-guide)

### External Resources
- [Angular Docs](https://angular.io/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Firebase Docs](https://firebase.google.com/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Mermaid.js](https://mermaid.js.org/)

### Repository
- [GitHub Repository](https://github.com/Uttam-Mahata/coursewagon)
- [Issues](https://github.com/Uttam-Mahata/coursewagon/issues)
- [Discussions](https://github.com/Uttam-Mahata/coursewagon/discussions)

---

## Support

Need help? Contact us:
- 📧 Email: [contact@coursewagon.live](mailto:contact@coursewagon.live)
- 🐛 Issues: [GitHub Issues](https://github.com/Uttam-Mahata/coursewagon/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/Uttam-Mahata/coursewagon/discussions)
