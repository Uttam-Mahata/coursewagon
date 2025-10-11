# CourseWagon

[![Documentation](https://img.shields.io/badge/docs-online-blue?style=for-the-badge)](https://uttam-mahata.github.io/coursewagon/)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)
[![Live Demo](https://img.shields.io/badge/demo-live-success?style=for-the-badge)](https://www.coursewagon.live)

CourseWagon is an enterprise-grade educational platform that leverages generative AI to facilitate dynamic course content generation and comprehensive learning management. The platform integrates modern web technologies with advanced AI capabilities to deliver a scalable, secure, and user-centric educational experience.

## 📚 Documentation

**Complete documentation is available at: [https://uttam-mahata.github.io/coursewagon/](https://uttam-mahata.github.io/coursewagon/)**

- [Getting Started Guide](https://uttam-mahata.github.io/coursewagon/getting-started)
- [System Architecture](https://uttam-mahata.github.io/coursewagon/architecture)
- [API Reference](https://uttam-mahata.github.io/coursewagon/api-reference)
- [User Guide](https://uttam-mahata.github.io/coursewagon/user-guide)
- [Developer Guide](https://uttam-mahata.github.io/coursewagon/developer-guide)
- [Deployment Guide](https://uttam-mahata.github.io/coursewagon/deployment)
- [FAQ & Troubleshooting](https://uttam-mahata.github.io/coursewagon/faq)

##  Features

- **AI-Powered Content Generation**: Automatically generate course subjects, chapters, topics, and detailed content using Google Gemini AI
- **Comprehensive Course Management**: Create and organize courses with hierarchical structure (Courses  Subjects  Chapters  Topics  Content)
- **Real-time Authentication**: Secure user authentication with Firebase Auth and JWT tokens
- **Cloud Storage Integration**: Store images and media using Azure Blob Storage and Firebase Storage
- **Responsive UI**: Modern, responsive interface built with Angular 19 and Tailwind CSS
- **Admin Dashboard**: Comprehensive admin panel for managing users, courses, and testimonials
- **Mathematical Content Support**: Render mathematical equations using KaTeX and MathJax
- **Diagram Support**: Create and display diagrams using Mermaid.js
- **Email Notifications**: Automated email system for password resets and user notifications

##  Tech Stack

### Frontend
- **Framework**: Angular 19
- **Styling**: Tailwind CSS 4.1
- **Authentication**: Firebase Auth
- **Markdown**: ngx-markdown with Prism.js syntax highlighting
- **Math Rendering**: KaTeX, MathJax
- **Diagrams**: Mermaid.js
- **Icons**: Font Awesome

### Backend
- **Framework**: FastAPI (Python)
- **Database**: MySQL with SQLAlchemy ORM
- **AI Integration**: Google Gemini AI
- **Storage**: Azure Blob Storage, Firebase Storage
- **Authentication**: JWT tokens with Firebase Admin SDK
- **Email Service**: Mailgun
- **Deployment**: Google Cloud Run / Microsoft Azure

##  Project Structure

```
coursewagon/
 angular-client/          # Frontend Angular application
    src/
       app/            # Angular components and services
       environments/   # Environment configurations
       styles.css      # Global styles
    package.json        # Frontend dependencies
    angular.json        # Angular configuration

 python-server/          # Backend FastAPI application
    app.py             # Main FastAPI application
    models/            # Database models
    routes/            # API endpoints
    services/          # Business logic
    repositories/      # Data access layer
    utils/             # Helper utilities
    migrations/        # Database migrations
    requirements.txt   # Backend dependencies

 CLAUDE.md              # AI assistant instructions
 .env.example           # Environment variables template
```

##  Getting Started

### Prerequisites

- Node.js (v18 or higher)
- Python 3.10+
- MySQL database
- Firebase project (for authentication)
- Azure Storage account (optional)
- Google Gemini API key

### Frontend Setup

```bash
# Navigate to frontend directory
cd angular-client

# Install dependencies
npm install

# Configure environment variables
# Edit src/environments/environment.ts with your API endpoints

# Run development server
npm start
```

The application will be available at `http://localhost:4200`

### Backend Setup

```bash
# Navigate to backend directory
cd python-server

# Install uv package manager (recommended)
pip install uv

# Install dependencies
uv pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your configuration

# Run development server
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`

## =' Configuration

### Environment Variables

Copy `.env.example` to `.env` in the `python-server` directory and configure:

- **Database**: MySQL connection details
- **API Keys**: Gemini AI, Firebase, Azure Storage
- **JWT**: Secret keys and token expiration
- **Email**: Mailgun configuration
- **Storage**: Azure Blob Storage credentials

### Firebase Setup

1. Create a Firebase project
2. Enable Authentication
3. Download service account credentials
4. Place in `python-server/utils/`
5. Update Firebase configuration in Angular app

##  API Documentation

Once the backend is running, access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## > Testing

### Frontend Tests
```bash
cd angular-client
npm test
```

### Backend Tests
```bash
cd python-server
python -m pytest tests/
```

### Local Testing with Azure Storage
```bash
cd python-server/scripts
./test-local.sh
```

##  Deployment

### Frontend Deployment (Firebase Hosting)
```bash
cd angular-client
npm run build
firebase deploy
```

### Backend Deployment (Google Cloud Run)
```bash
cd python-server
gcloud run deploy coursewagon-api \
  --source . \
  --region asia-southeast1 \
  --allow-unauthenticated
```

##  Available Scripts

### Frontend
- `npm start` - Run development server
- `npm run build` - Build for production
- `npm test` - Run unit tests

### Backend
- `uvicorn app:app --reload` - Run development server
- `./scripts/test-local.sh` - Test with local Azure storage
- `./scripts/deploy-complete.sh` - Deploy to production

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

- Google Gemini AI for content generation
- Firebase for authentication and hosting
- Azure for cloud storage
- Angular and FastAPI communities

##  Support

For support, email contact@coursewagon.live or open an issue in the GitHub repository.

## Links

- **Live Application**: [https://www.coursewagon.live](https://www.coursewagon.live)

