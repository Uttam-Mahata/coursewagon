# Go Server - Course Wagon API

A comprehensive Go-based REST API server that integrates with Google's Gemini AI to generate educational content. This server provides course management, content generation, user authentication, and more.

## Features

### 🤖 AI-Powered Content Generation
- **Gemini Integration**: Uses Google's Gemini 2.5 Flash model for content generation
- **Structured Output**: Supports JSON schema-based responses for consistent data
- **Text Generation**: Generates detailed educational content for topics
- **Thinking Control**: Option to enable/disable thinking mode for different response times
- **System Instructions**: Custom system prompts for specialized content generation

### 🎓 Course Management
- **Hierarchical Structure**: Course → Subject → Chapter → Topic → Content
- **AI-Generated Subjects**: Automatically generate subjects for courses using Gemini
- **Content Generation**: Create detailed educational content for topics
- **Full CRUD Operations**: Complete management of educational content

### 🔐 Authentication & Security
- **JWT Authentication**: Secure access and refresh token system
- **Password Security**: bcrypt hashing with salts
- **Input Validation**: Comprehensive request validation and sanitization
- **Rate Limiting**: Basic rate limiting to prevent abuse
- **Security Headers**: Standard security headers implementation

### 🗄️ Database
- **GORM ORM**: Database abstraction with MySQL support
- **Repository Pattern**: Clean separation of data access logic
- **Migrations**: Database schema management
- **Soft Deletes**: Maintain data integrity with soft deletion

### 🌐 API Features
- **RESTful Design**: Clean and intuitive API endpoints
- **Error Handling**: Comprehensive error responses with proper HTTP codes
- **CORS Support**: Cross-origin resource sharing configuration
- **Pagination**: Support for paginated responses
- **Search**: Course search functionality

## Technology Stack

- **Language**: Go 1.21+
- **Web Framework**: Gin
- **Database**: MySQL with GORM ORM
- **AI Integration**: Google Gemini API
- **Authentication**: JWT with bcrypt
- **Validation**: go-playground/validator
- **Logging**: Logrus
- **Containerization**: Docker & Docker Compose

## Quick Start

### Prerequisites
- Go 1.21 or higher
- MySQL 8.0+
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd go-server
   ```

2. **Install dependencies**
   ```bash
   go mod download
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set up database**
   ```bash
   # Create MySQL database
   mysql -u root -p
   CREATE DATABASE coursewagon;
   ```

5. **Run the application**
   ```bash
   go run cmd/main.go
   ```

### Docker Setup

1. **Using Docker Compose (Recommended)**
   ```bash
   # Set your Gemini API key
   export API_KEY=your-gemini-api-key
   
   # Start services
   docker-compose up -d
   ```

2. **Using Docker only**
   ```bash
   # Build image
   docker build -t go-server .
   
   # Run container
   docker run -p 8000:8000 \
     -e DB_HOST=your-db-host \
     -e API_KEY=your-gemini-api-key \
     go-server
   ```

## API Documentation

### Base URL
```
http://localhost:8000/api
```

### Authentication Endpoints
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh tokens
- `POST /auth/password-reset/request` - Request password reset
- `POST /auth/password-reset/confirm` - Confirm password reset

### Course Management
- `GET /courses` - Get user courses
- `POST /courses` - Create course
- `GET /courses/:id` - Get specific course
- `PUT /courses/:id` - Update course
- `DELETE /courses/:id` - Delete course
- `POST /courses/:id/subjects` - Generate subjects using AI
- `GET /courses/:id/hierarchy` - Get complete course hierarchy

### Content Generation
- `POST /content/generate` - Generate AI content for a topic
- `GET /content/topic/:topic_id` - Get content by topic
- `PUT /content/:id` - Update content
- `DELETE /content/:id` - Delete content

### Public Endpoints
- `GET /public/courses/search` - Search courses
- `GET /public/testimonials` - Get approved testimonials

### User Management
- `GET /users/profile` - Get user profile

## Project Structure

```
go-server/
├── cmd/
│   └── main.go              # Application entry point
├── config/
│   └── config.go            # Configuration management
├── middleware/
│   ├── auth_middleware.go   # JWT authentication
│   └── middleware.go        # General middleware
├── models/
│   ├── user.go             # User model
│   ├── course.go           # Course model
│   ├── subject.go          # Subject model
│   ├── chapter.go          # Chapter model
│   ├── topic.go            # Topic model
│   ├── content.go          # Content model
│   ├── testimonial.go      # Testimonial model
│   ├── password_reset.go   # Password reset model
│   └── schemas.go          # Request/Response DTOs
├── repositories/
│   ├── base_repository.go  # Base repository interface
│   ├── user_repository.go  # User data access
│   ├── course_repository.go # Course data access
│   └── ...                 # Other repositories
├── services/
│   ├── auth_service.go     # Authentication logic
│   ├── course_service.go   # Course business logic
│   ├── content_service.go  # Content generation logic
│   └── email_service.go    # Email service
├── routes/
│   ├── routes.go           # Route setup
│   ├── auth_routes.go      # Auth endpoints
│   ├── course_routes.go    # Course endpoints
│   ├── content_routes.go   # Content endpoints
│   └── public_routes.go    # Public endpoints
├── utils/
│   ├── gemini_helper.go    # Gemini AI integration
│   ├── jwt_utils.go        # JWT utilities
│   └── validation.go       # Validation utilities
├── Dockerfile
├── docker-compose.yml
├── go.mod
├── go.sum
└── README.md
```

## Gemini AI Integration

### Text Generation
The server integrates with Google's Gemini 2.5 Flash model to generate educational content:

```go
// Basic text generation
content, err := geminiHelper.GenerateContent(ctx, prompt)

// With thinking disabled for faster responses
content, err := geminiHelper.GenerateContentWithThinking(ctx, prompt, true)

// With system instructions
content, err := geminiHelper.GenerateContentWithSystemInstruction(ctx, prompt, systemInstruction)
```

### Structured Output
Generate structured JSON responses using schemas:

```go
// Generate subjects as JSON array
subjects, err := geminiHelper.GenerateSubjects(ctx, courseName, courseDescription)

// Generate chapters for a subject
chapters, err := geminiHelper.GenerateChapters(ctx, subjectName, courseName)

// Generate topics for a chapter
topics, err := geminiHelper.GenerateTopics(ctx, chapterName, subjectName, courseName)
```

### Content Generation Features
- **Markdown Processing**: Handles mermaid diagrams and markdown formatting
- **Content Extraction**: Extracts and processes different content formats
- **Error Handling**: Comprehensive error handling for API failures
- **Context Management**: Proper context handling for cancellation and timeouts

## Configuration

### Environment Variables
All configuration is handled through environment variables. See `.env.example` for all available options.

### Key Configurations
- **Database**: MySQL connection settings
- **JWT**: Token secrets and expiration times
- **Gemini API**: Your Google AI Studio API key
- **Email**: SMTP settings for notifications
- **Security**: Various security-related settings

## Development

### Running Tests
```bash
go test ./...
```

### Code Formatting
```bash
go fmt ./...
```

### Linting
```bash
golangci-lint run
```

### Building
```bash
go build -o bin/server cmd/main.go
```

## Deployment

### Production Build
```bash
docker build -t go-server:prod -f Dockerfile.prod .
```

### Environment Setup
1. Set up production database
2. Configure environment variables
3. Set up reverse proxy (nginx)
4. Configure SSL certificates
5. Set up monitoring and logging

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## Roadmap

- [ ] Add more AI models support
- [ ] Implement real-time features with WebSocket
- [ ] Add comprehensive testing suite
- [ ] Implement caching layer
- [ ] Add API rate limiting per user
- [ ] Implement file upload for course materials
- [ ] Add email notification system
- [ ] Implement admin dashboard features