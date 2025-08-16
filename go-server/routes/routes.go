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
	subjectService := services.NewSubjectService(subjectRepo, courseRepo)
	chapterService := services.NewChapterService(chapterRepo, subjectRepo, courseRepo)
	topicService := services.NewTopicService(topicRepo, chapterRepo, subjectRepo, courseRepo)
	contentService := services.NewContentService(contentRepo, topicRepo, chapterRepo, subjectRepo, courseRepo)
	testimonialService := services.NewTestimonialService(testimonialRepo, userRepo)
	imageService := services.NewImageService(courseRepo, subjectRepo)

	// Auth routes (no auth required)
	authGroup := router.Group("/auth")
	SetupAuthRoutes(authGroup, authService)

	// Protected routes (auth required)
	protected := router.Group("/")
	protected.Use(middleware.AuthMiddleware(cfg))
	{
		// Course routes
		SetupCourseRoutes(protected.Group("/courses"), courseService, subjectService, chapterService, topicService)

		// Content routes  
		SetupContentRoutes(protected.Group("/content"), contentService)

		// Subject routes
		SetupSubjectRoutes(protected.Group("/subjects"), subjectService, chapterService)

		// Chapter routes
		SetupChapterRoutes(protected.Group("/chapters"), chapterService, topicService)

		// Topic routes
		SetupTopicRoutes(protected.Group("/topics"), topicService)

		// User profile routes
		SetupUserRoutes(protected.Group("/users"), authService)

		// Testimonial routes
		SetupTestimonialRoutes(protected.Group("/testimonials"), testimonialService)

		// Image routes
		SetupImageRoutes(protected.Group("/images"), imageService)
	}

	// Public routes (optional auth)
	public := router.Group("/public")
	public.Use(middleware.OptionalAuthMiddleware(cfg))
	{
		// Public course search
		SetupPublicRoutes(public, courseService, testimonialRepo)
	}
}