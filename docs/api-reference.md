---
layout: default
title: API Reference
nav_order: 4
description: "Complete API documentation for CourseWagon backend services"
---

# API Reference
{: .no_toc }

Complete reference for all CourseWagon API endpoints.
{: .fs-6 .fw-300 }

## Table of Contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Base URL

**Development**: `http://localhost:8000/api`  
**Production**: `https://coursewagon-api-[hash].run.app/api` or `https://api.coursewagon.live/api`

---

## Authentication

Most endpoints require authentication using JWT tokens.

### Headers

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Token Endpoints

#### Verify Firebase Token

```http
POST /api/auth/verify-token
```

Verify Firebase ID token and receive JWT tokens.

**Request Body:**
```json
{
  "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "is_admin": false
  }
}
```

#### Refresh Access Token

```http
POST /api/auth/refresh
```

Get a new access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Check Email Availability

```http
POST /api/auth/check-email
```

Check if an email is already registered.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "available": true
}
```

---

## Course Management

### Get All Courses

```http
GET /api/courses
```

**Authentication**: Required

**Response:**
```json
[
  {
    "id": 1,
    "title": "Web Development Fundamentals",
    "description": "Learn HTML, CSS, and JavaScript",
    "user_id": 1,
    "created_at": "2024-01-01T00:00:00Z",
    "subject_count": 5
  }
]
```

### Get Course by ID

```http
GET /api/courses/{course_id}
```

**Authentication**: Required

**Response:**
```json
{
  "id": 1,
  "title": "Web Development Fundamentals",
  "description": "Learn HTML, CSS, and JavaScript",
  "user_id": 1,
  "created_at": "2024-01-01T00:00:00Z",
  "subjects": [
    {
      "id": 1,
      "name": "HTML Basics",
      "order": 1,
      "topic_count": 5
    }
  ]
}
```

### Create Course

```http
POST /api/courses
```

**Authentication**: Required

**Request Body:**
```json
{
  "title": "Web Development Fundamentals",
  "description": "Learn HTML, CSS, and JavaScript"
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Web Development Fundamentals",
  "description": "Learn HTML, CSS, and JavaScript",
  "user_id": 1,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Update Course

```http
PUT /api/courses/{course_id}
```

**Authentication**: Required (Owner only)

**Request Body:**
```json
{
  "title": "Updated Course Title",
  "description": "Updated description"
}
```

### Delete Course

```http
DELETE /api/courses/{course_id}
```

**Authentication**: Required (Owner only)

**Response:**
```json
{
  "message": "Course deleted successfully"
}
```

---

## Subject Management

### Generate Subjects

```http
POST /api/subjects/{course_id}/generate
```

**Authentication**: Required

Generate AI-powered subjects for a course.

**Request Body:**
```json
{
  "count": 5
}
```

**Response:**
```json
{
  "subjects": [
    {
      "id": 1,
      "name": "HTML Basics",
      "course_id": 1,
      "order": 1
    },
    {
      "id": 2,
      "name": "CSS Styling",
      "course_id": 1,
      "order": 2
    }
  ]
}
```

### Get Course Subjects

```http
GET /api/subjects/course/{course_id}
```

**Authentication**: Required

**Response:**
```json
[
  {
    "id": 1,
    "name": "HTML Basics",
    "course_id": 1,
    "order": 1,
    "topic_count": 5
  }
]
```

### Update Subject

```http
PUT /api/subjects/{subject_id}
```

**Authentication**: Required

**Request Body:**
```json
{
  "name": "Updated Subject Name",
  "order": 1
}
```

### Delete Subject

```http
DELETE /api/subjects/{subject_id}
```

**Authentication**: Required

---

## Topic Management

### Generate Topics

```http
POST /api/topics/subject/{subject_id}/generate
```

**Authentication**: Required

Generate AI-powered topics for a subject.

**Request Body:**
```json
{
  "count": 10
}
```

**Response:**
```json
{
  "topics": [
    {
      "id": 1,
      "name": "Introduction to HTML",
      "subject_id": 1,
      "order": 1,
      "has_content": false
    }
  ]
}
```

### Get Subject Topics

```http
GET /api/topics/subject/{subject_id}
```

**Authentication**: Required

**Response:**
```json
[
  {
    "id": 1,
    "name": "Introduction to HTML",
    "subject_id": 1,
    "order": 1,
    "has_content": true
  }
]
```

### Update Topic

```http
PUT /api/topics/{topic_id}
```

**Authentication**: Required

**Request Body:**
```json
{
  "name": "Updated Topic Name",
  "order": 1
}
```

### Delete Topic

```http
DELETE /api/topics/{topic_id}
```

**Authentication**: Required

---

## Content Management

### Generate Content

```http
POST /api/content/courses/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/topics/{topic_id}/generate
```

**Authentication**: Required

Generate AI-powered detailed content for a topic.

**Response:**
```json
{
  "content": {
    "id": 1,
    "topic_id": 1,
    "content": "# Introduction to HTML\n\nHTML (HyperText Markup Language)...",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### Get Topic Content

```http
GET /api/content/courses/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/topics/{topic_id}
```

**Authentication**: Required

**Response:**
```json
{
  "id": 1,
  "topic_id": 1,
  "content": "# Introduction to HTML\n\nHTML (HyperText Markup Language)...",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Update Content

```http
PUT /api/content/{content_id}
```

**Authentication**: Required

**Request Body:**
```json
{
  "content": "# Updated Content\n\nUpdated markdown content..."
}
```

---

## Image Management

### Upload Image

```http
POST /api/images/upload
```

**Authentication**: Required

**Request:** Multipart form data
```
image: <file>
```

**Response:**
```json
{
  "url": "https://storage.googleapis.com/coursewagon-storage-bucket/images/abc123.jpg"
}
```

### Generate AI Image

```http
POST /api/images/generate
```

**Authentication**: Required

**Request Body:**
```json
{
  "prompt": "A visual representation of HTML tags and structure"
}
```

**Response:**
```json
{
  "url": "https://storage.googleapis.com/coursewagon-storage-bucket/images/generated-abc123.jpg"
}
```

---

## User Management

### Get Current User

```http
GET /api/users/me
```

**Authentication**: Required

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "is_admin": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Update User Profile

```http
PUT /api/users/me
```

**Authentication**: Required

**Request Body:**
```json
{
  "name": "Updated Name",
  "email": "newemail@example.com"
}
```

---

## Admin Endpoints

All admin endpoints require admin privileges.

### Get All Users

```http
GET /api/admin/users
```

**Authentication**: Required (Admin only)

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Results per page (default: 20)

**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe",
      "is_admin": false,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 20
}
```

### Update User Admin Status

```http
PUT /api/admin/users/{user_id}/admin
```

**Authentication**: Required (Admin only)

**Request Body:**
```json
{
  "is_admin": true
}
```

### Delete User

```http
DELETE /api/admin/users/{user_id}
```

**Authentication**: Required (Admin only)

---

## Testimonials

### Get All Testimonials

```http
GET /api/testimonials
```

**Authentication**: Not required

**Response:**
```json
[
  {
    "id": 1,
    "user_name": "John Doe",
    "user_email": "john@example.com",
    "content": "Great platform for learning!",
    "rating": 5,
    "is_approved": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### Create Testimonial

```http
POST /api/testimonials
```

**Authentication**: Required

**Request Body:**
```json
{
  "content": "Great platform for learning!",
  "rating": 5
}
```

### Update Testimonial Approval (Admin)

```http
PUT /api/admin/testimonials/{testimonial_id}/approve
```

**Authentication**: Required (Admin only)

**Request Body:**
```json
{
  "is_approved": true
}
```

---

## Health Check

### Check API Health

```http
GET /api/health
```

**Authentication**: Not required

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-10-10T15:30:00.000Z",
  "version": "1.0.0"
}
```

---

## Error Responses

### Standard Error Format

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized (missing or invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `409` - Conflict (e.g., duplicate email)
- `422` - Unprocessable Entity (validation error)
- `500` - Internal Server Error

### Common Error Examples

**Unauthorized:**
```json
{
  "detail": "Not authenticated"
}
```

**Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Invalid email format",
      "type": "value_error.email"
    }
  ]
}
```

**Not Found:**
```json
{
  "detail": "Course not found"
}
```

---

## Rate Limiting

**Recommended limits:**
- Authentication endpoints: 10 requests/minute
- Content generation: 20 requests/minute
- General endpoints: 100 requests/minute

---

## Interactive API Documentation

For interactive API testing and more details:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## SDK Examples

### JavaScript/TypeScript

```typescript
// Authentication
const response = await fetch('http://localhost:8000/api/auth/verify-token', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    id_token: firebaseIdToken
  })
});

const { access_token, refresh_token, user } = await response.json();

// Authenticated Request
const courses = await fetch('http://localhost:8000/api/courses', {
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  }
});
```

### Python

```python
import requests

# Authentication
response = requests.post(
    'http://localhost:8000/api/auth/verify-token',
    json={'id_token': firebase_id_token}
)
tokens = response.json()

# Authenticated Request
headers = {
    'Authorization': f"Bearer {tokens['access_token']}",
    'Content-Type': 'application/json'
}
courses = requests.get('http://localhost:8000/api/courses', headers=headers)
```

### cURL

```bash
# Authentication
curl -X POST http://localhost:8000/api/auth/verify-token \
  -H "Content-Type: application/json" \
  -d '{"id_token": "your-firebase-token"}'

# Authenticated Request
curl -X GET http://localhost:8000/api/courses \
  -H "Authorization: Bearer your-access-token" \
  -H "Content-Type: application/json"
```

---

## Need Help?

- 📖 [Getting Started](getting-started) - Setup guide
- 🏗️ [System Architecture](architecture) - Understand the system
- 💻 [Developer Guide](developer-guide) - Contribute to the project
- 🐛 [GitHub Issues](https://github.com/Uttam-Mahata/coursewagon/issues) - Report bugs
