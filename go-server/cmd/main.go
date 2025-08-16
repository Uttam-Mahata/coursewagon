package main

import (
	"go-server/config"
	"go-server/middleware"
	"go-server/routes"
	"log"
	"net/http"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
)

func main() {
	// Load configuration
	cfg, err := config.LoadConfig()
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	// Setup logging
	setupLogging(cfg)

	// Setup database
	db, err := config.SetupDatabase(cfg)
	if err != nil {
		logrus.Fatalf("Failed to setup database: %v", err)
	}

	// Set Gin mode
	if cfg.Environment == "production" {
		gin.SetMode(gin.ReleaseMode)
	}

	// Create Gin router
	router := gin.New()

	// Setup CORS middleware
	router.Use(cors.New(cors.Config{
		AllowOrigins: []string{
			"*",
			"http://localhost:4200",
			"http://127.0.0.1:4200",
			"https://coursewagon-backend.victoriousforest-3a334815.southeastasia.azurecontainerapps.io",
			"https://www.coursewagon.live",
			"https://coursewagon.web.app",
		},
		AllowMethods: []string{
			"GET", "POST", "PUT", "DELETE", "OPTIONS",
		},
		AllowHeaders: []string{
			"Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin",
		},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
	}))

	// Global middleware
	router.Use(middleware.LoggerMiddleware())
	router.Use(middleware.ErrorHandlerMiddleware())
	router.Use(middleware.DatabaseErrorMiddleware())

	// Health check endpoint
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "healthy"})
	})

	// Setup routes
	api := router.Group("/api")
	routes.SetupRoutes(api, db, cfg)

	// Start server
	port := cfg.Port
	if port == "" {
		port = "8000"
	}

	logrus.Infof("Starting server on port %s", port)
	if err := router.Run(":" + port); err != nil {
		logrus.Fatalf("Failed to start server: %v", err)
	}
}

func setupLogging(cfg *config.Config) {
	// Set log level
	if cfg.Debug {
		logrus.SetLevel(logrus.DebugLevel)
	} else {
		logrus.SetLevel(logrus.InfoLevel)
	}

	// Set log format
	logrus.SetFormatter(&logrus.TextFormatter{
		FullTimestamp: true,
		TimestampFormat: "2006-01-02 15:04:05",
	})
}