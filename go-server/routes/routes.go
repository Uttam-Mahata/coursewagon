package routes

import (
	"go-server/config"
	"go-server/middleware"
	"go-server/repositories"
	"go-server/services"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

// SetupRoutes initializes all routes
func SetupRoutes(router *gin.RouterGroup, db *gorm.DB, cfg *config.Config) {
	// Initialize repositories
	userRepo := repositories.NewUserRepository(db)
	courseRepo := repositories.NewCourseRepository(db)
	subjectRepo := repositories.NewSubjectRepository(db)
	chapterRepo := repositories.NewChapterRepository(db)
	topicRepo := repositories.NewTopicRepository(db)
	contentRepo := repositories.NewContentRepository(db)
	testimonialRepo := repositories.NewTestimonialRepository(db)

	// Initialize services
	emailService := services.NewEmailService()
	authService := services.NewAuthService(userRepo, cfg, emailService)
	courseService := services.NewCourseService(courseRepo, subjectRepo)
	contentService := services.NewContentService(contentRepo, topicRepo, chapterRepo, subjectRepo, courseRepo)

	// Auth routes (no auth required)
	authGroup := router.Group("/auth")
	SetupAuthRoutes(authGroup, authService)

	// Protected routes (auth required)
	protected := router.Group("/")
	protected.Use(middleware.AuthMiddleware(cfg))
	{
		// Course routes
		SetupCourseRoutes(protected.Group("/courses"), courseService, subjectRepo, chapterRepo, topicRepo)

		// Content routes  
		SetupContentRoutes(protected.Group("/content"), contentService)

		// Subject routes
		SetupSubjectRoutes(protected.Group("/subjects"), subjectRepo, chapterRepo, courseRepo)

		// Chapter routes
		SetupChapterRoutes(protected.Group("/chapters"), chapterRepo, topicRepo, subjectRepo)

		// Topic routes
		SetupTopicRoutes(protected.Group("/topics"), topicRepo, chapterRepo)

		// User profile routes
		SetupUserRoutes(protected.Group("/users"), authService)

		// Testimonial routes
		SetupTestimonialRoutes(protected.Group("/testimonials"), testimonialRepo)
	}

	// Public routes (optional auth)
	public := router.Group("/public")
	public.Use(middleware.OptionalAuthMiddleware(cfg))
	{
		// Public course search
		SetupPublicRoutes(public, courseService, testimonialRepo)
	}
}