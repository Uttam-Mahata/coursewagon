# CourseWagon 🚂

A modern, full-stack course management system built with Angular and Python Flask.

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)

## 🎯 Overview

CourseWagon is a comprehensive learning management system that allows educational institutions to manage and deliver courses, modules, and content efficiently. The platform supports hierarchical content organization with subjects, modules, chapters, topics, subtopics, and content management.

## 🏗 Architecture

```mermaid
graph TB
    subgraph Frontend [Angular Frontend]
        UI[User Interface]
        AG[Auth Guard]
        IS[Interceptor Service]
        CS[Component Services]
    end
    
    subgraph Backend [Python Flask Backend]
        API[API Routes]
        AUTH[Auth Service]
        SVC[Services Layer]
        REPO[Repositories]
        DB[(Database)]
        GM[Gemini Helper]
    end
    
    UI --> AG
    AG --> IS
    IS --> CS
    CS --> API
    API --> AUTH
    API --> SVC
    SVC --> REPO
    REPO --> DB
    SVC --> GM
```

## ✨ Features

- User Authentication and Authorization
- Course Management
- Subject and Module Organization
- Chapter and Topic Management
- Content Delivery
- Mermaid Diagram Support
- AI Integration with Google Gemini

## 🛠 Tech Stack

### Frontend
- Angular
- Angular Material
- TypeScript
- Firebase Integration
- Mermaid.js

### Backend
- Python Flask
- SQLAlchemy ORM
- JWT Authentication
- Google Gemini AI Integration

## 📁 Project Structure

```mermaid
graph LR
    subgraph Client [client-app]
        ANG[Angular App]
        COMP[Components]
        SRV[Services]
        AUTH[Auth]
        RT[Routing]
    end
    
    subgraph Server [server-app]
        PY[Python App]
        MDW[Middleware]
        MDL[Models]
        REP[Repositories]
        SVC[Services]
        UTL[Utils]
    end
    
    ANG --> COMP
    COMP --> SRV
    COMP --> AUTH
    COMP --> RT
    
    PY --> MDW
    PY --> MDL
    MDL --> REP
    REP --> SVC
    SVC --> UTL
```

## 🚀 Installation

### Frontend Setup
```bash
cd client-app
npm install
```

### Backend Setup
```bash
cd server-app
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 🏃‍♂️ Running the Application

### Frontend
```bash
cd client-app
ng serve
```
The application will be available at `http://localhost:4200`

### Backend
```bash
cd server-app
python app.py
```
The API server will start at `http://localhost:5000`

## 📚 API Documentation

### Authentication Endpoints
- POST /api/auth/register - User registration 
- POST /api/auth/login - User login
- GET /api/auth/profile - Get user profile

### Course Management
- GET /api/courses - List all courses
- POST /api/courses - Create new course
- GET /api/courses/{id} - Get course details
- PUT /api/courses/{id} - Update course
- DELETE /api/courses/{id} - Delete course

### Content Hierarchy
```mermaid
erDiagram
    COURSE ||--o{ SUBJECT : contains
    SUBJECT ||--o{ MODULE : has
    MODULE ||--o{ CHAPTER : includes
    CHAPTER ||--o{ TOPIC : contains
    TOPIC ||--o{ SUBTOPIC : has
    SUBTOPIC ||--o{ CONTENT : contains
    
    COURSE {
        string id
        string name
        string description
    }
    SUBJECT {
        string id
        string name
        string course_id
    }
    MODULE {
        string id
        string name
        string subject_id
    }
    CHAPTER {
        string id
        string title
        string module_id
    }
    TOPIC {
        string id
        string title
        string chapter_id
    }
    SUBTOPIC {
        string id
        string title
        string topic_id
    }
    CONTENT {
        string id
        string content
        string subtopic_id
    }
```

## 🤝 Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Make changes
4. Commit (`git commit -am 'Add new feature'`)
5. Push (`git push origin feature/improvement`)
6. Create Pull Request
---

Built with ❤️ using Angular and Flask