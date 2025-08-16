package middleware

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
	"gorm.io/gorm"
)

// LoggerMiddleware logs HTTP requests
func LoggerMiddleware() gin.HandlerFunc {
	return gin.LoggerWithConfig(gin.LoggerConfig{
		Formatter: func(param gin.LogFormatterParams) string {
			logrus.WithFields(logrus.Fields{
				"status_code":  param.StatusCode,
				"latency":      param.Latency,
				"client_ip":    param.ClientIP,
				"method":       param.Method,
				"path":         param.Path,
				"user_agent":   param.Request.UserAgent(),
				"error":        param.ErrorMessage,
				"body_size":    param.BodySize,
			}).Info("HTTP Request")
			return ""
		},
		Output: logrus.StandardLogger().Out,
	})
}

// ErrorHandlerMiddleware handles panics and errors
func ErrorHandlerMiddleware() gin.HandlerFunc {
	return gin.RecoveryWithWriter(logrus.StandardLogger().Out, func(c *gin.Context, recovered interface{}) {
		if err, ok := recovered.(string); ok {
			logrus.Errorf("Panic recovered: %s", err)
		} else {
			logrus.Errorf("Panic recovered: %v", recovered)
		}

		c.JSON(http.StatusInternalServerError, gin.H{
			"success": false,
			"error":   "internal server error",
		})
	})
}

// DatabaseErrorMiddleware handles database-specific errors
func DatabaseErrorMiddleware() gin.HandlerFunc {
	return gin.HandlerFunc(func(c *gin.Context) {
		c.Next()

		// Check for database errors in the response
		if len(c.Errors) > 0 {
			for _, err := range c.Errors {
				switch err.Err {
				case gorm.ErrRecordNotFound:
					if !c.Writer.Written() {
						c.JSON(http.StatusNotFound, gin.H{
							"success": false,
							"error":   "resource not found",
						})
					}
					return
				case gorm.ErrInvalidTransaction:
					logrus.Errorf("Database transaction error: %v", err.Err)
					if !c.Writer.Written() {
						c.JSON(http.StatusInternalServerError, gin.H{
							"success": false,
							"error":   "database transaction error",
						})
					}
					return
				default:
					if isDBConnectionError(err.Err) {
						logrus.Errorf("Database connection error: %v", err.Err)
						if !c.Writer.Written() {
							c.JSON(http.StatusServiceUnavailable, gin.H{
								"success": false,
								"error":   "database connection error",
							})
						}
						return
					}
				}
			}
		}
	})
}

// RateLimitMiddleware implements basic rate limiting
func RateLimitMiddleware() gin.HandlerFunc {
	// Simple in-memory rate limiting (not suitable for production)
	clients := make(map[string][]time.Time)
	maxRequests := 100
	timeWindow := time.Minute

	return gin.HandlerFunc(func(c *gin.Context) {
		clientIP := c.ClientIP()
		now := time.Now()

		// Clean old requests
		if requests, exists := clients[clientIP]; exists {
			var validRequests []time.Time
			for _, reqTime := range requests {
				if now.Sub(reqTime) < timeWindow {
					validRequests = append(validRequests, reqTime)
				}
			}
			clients[clientIP] = validRequests
		}

		// Check rate limit
		if len(clients[clientIP]) >= maxRequests {
			c.JSON(http.StatusTooManyRequests, gin.H{
				"success": false,
				"error":   "rate limit exceeded",
			})
			c.Abort()
			return
		}

		// Add current request
		clients[clientIP] = append(clients[clientIP], now)

		c.Next()
	})
}

// SecurityHeadersMiddleware adds security headers
func SecurityHeadersMiddleware() gin.HandlerFunc {
	return gin.HandlerFunc(func(c *gin.Context) {
		c.Header("X-Frame-Options", "SAMEORIGIN")
		c.Header("X-XSS-Protection", "1; mode=block")
		c.Header("X-Content-Type-Options", "nosniff")
		c.Header("Referrer-Policy", "strict-origin-when-cross-origin")
		c.Header("Content-Security-Policy", "default-src 'self'")
		c.Next()
	})
}

// ValidationErrorMiddleware handles validation errors consistently
func ValidationErrorMiddleware() gin.HandlerFunc {
	return gin.HandlerFunc(func(c *gin.Context) {
		c.Next()

		// Handle validation errors
		if len(c.Errors) > 0 {
			for _, err := range c.Errors {
				if err.Type == gin.ErrorTypeBind {
					if !c.Writer.Written() {
						c.JSON(http.StatusBadRequest, gin.H{
							"success": false,
							"error":   "validation error",
							"details": err.Error(),
						})
					}
					return
				}
			}
		}
	})
}

// Helper function to check if error is a database connection error
func isDBConnectionError(err error) bool {
	if err == nil {
		return false
	}
	
	errorStr := err.Error()
	connectionErrors := []string{
		"connection refused",
		"connection reset",
		"connection timeout",
		"database is closed",
		"invalid connection",
	}

	for _, connErr := range connectionErrors {
		if len(errorStr) >= len(connErr) && errorStr[:len(connErr)] == connErr {
			return true
		}
	}

	return false
}