package models

// Request/Response DTOs for API endpoints

// Course DTOs
type CourseCreateRequest struct {
	Name        string `json:"name" validate:"required"`
	Description string `json:"description" validate:"required"`
}

type CourseUpdateRequest struct {
	Name        *string `json:"name"`
	Description *string `json:"description"`
	ImageURL    *string `json:"image_url"`
}

// Subject DTOs
type SubjectCreateRequest struct {
	CourseID uint     `json:"course_id" validate:"required"`
	Subjects []string `json:"subjects" validate:"required,min=1"`
}

// Chapter DTOs
type ChapterCreateRequest struct {
	SubjectID uint     `json:"subject_id" validate:"required"`
	Chapters  []string `json:"chapters" validate:"required,min=1"`
}

// Topic DTOs
type TopicCreateRequest struct {
	ChapterID uint     `json:"chapter_id" validate:"required"`
	Topics    []string `json:"topics" validate:"required,min=1"`
}

// Content DTOs
type ContentGenerateRequest struct {
	CourseID  uint `json:"course_id" validate:"required"`
	SubjectID uint `json:"subject_id" validate:"required"`
	ChapterID uint `json:"chapter_id" validate:"required"`
	TopicID   uint `json:"topic_id" validate:"required"`
}

// User DTOs
type UserRegisterRequest struct {
	Email     string  `json:"email" validate:"required,email"`
	Password  string  `json:"password" validate:"required,min=6"`
	FirstName *string `json:"first_name"`
	LastName  *string `json:"last_name"`
}

type UserLoginRequest struct {
	Email    string `json:"email" validate:"required,email"`
	Password string `json:"password" validate:"required"`
}

type UserLoginResponse struct {
	User         map[string]interface{} `json:"user"`
	AccessToken  string                 `json:"access_token"`
	RefreshToken string                 `json:"refresh_token"`
}

type PasswordResetRequest struct {
	Email string `json:"email" validate:"required,email"`
}

type PasswordResetConfirmRequest struct {
	Token    string `json:"token" validate:"required"`
	Password string `json:"password" validate:"required,min=6"`
}

// Testimonial DTOs
type TestimonialCreateRequest struct {
	Quote  string `json:"quote" validate:"required"`
	Rating int    `json:"rating" validate:"required,min=1,max=5"`
}

type TestimonialUpdateRequest struct {
	Quote      *string `json:"quote"`
	Rating     *int    `json:"rating" validate:"omitempty,min=1,max=5"`
	IsApproved *bool   `json:"is_approved"`
}

// Generic response types
type APIResponse struct {
	Success bool        `json:"success"`
	Message string      `json:"message,omitempty"`
	Data    interface{} `json:"data,omitempty"`
	Error   string      `json:"error,omitempty"`
}

type PaginatedResponse struct {
	Items      interface{} `json:"items"`
	Page       int         `json:"page"`
	PerPage    int         `json:"per_page"`
	Total      int64       `json:"total"`
	TotalPages int         `json:"total_pages"`
}

// Gemini API schemas for structured output (based on the provided documentation)
type GeminiSchema struct {
	Type              string                   `json:"type"`
	Format            string                   `json:"format,omitempty"`
	Description       string                   `json:"description,omitempty"`
	Nullable          bool                     `json:"nullable,omitempty"`
	Enum              []string                 `json:"enum,omitempty"`
	MaxItems          *int                     `json:"maxItems,omitempty"`
	MinItems          *int                     `json:"minItems,omitempty"`
	Properties        map[string]*GeminiSchema `json:"properties,omitempty"`
	Required          []string                 `json:"required,omitempty"`
	PropertyOrdering  []string                 `json:"propertyOrdering,omitempty"`
	Items             *GeminiSchema            `json:"items,omitempty"`
}

// Gemini Content Generation Schemas
type GeminiSubjectSchema struct {
	Subjects []string `json:"subjects"`
}

type GeminiChapterSchema struct {
	Chapters []string `json:"chapters"`
}

type GeminiTopicSchema struct {
	Topics []string `json:"topics"`
}