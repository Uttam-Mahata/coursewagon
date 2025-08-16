package middleware

import (
	"go-server/config"
	"go-server/utils"
	"net/http"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
)

// AuthMiddleware validates JWT tokens
func AuthMiddleware(cfg *config.Config) gin.HandlerFunc {
	jwtUtil := utils.NewJWTUtil(
		cfg.JWTSecretKey,
		cfg.JWTAccessTokenExpires,
		cfg.JWTRefreshTokenExpires,
	)

	return gin.HandlerFunc(func(c *gin.Context) {
		// Get token from Authorization header
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.JSON(http.StatusUnauthorized, gin.H{
				"success": false,
				"error":   "authorization header required",
			})
			c.Abort()
			return
		}

		// Extract token
		token := utils.ExtractTokenFromHeader(authHeader)
		if token == "" {
			c.JSON(http.StatusUnauthorized, gin.H{
				"success": false,
				"error":   "invalid authorization header format",
			})
			c.Abort()
			return
		}

		// Validate token
		claims, err := jwtUtil.ValidateToken(token)
		if err != nil {
			var statusCode int
			var message string

			switch err {
			case utils.ErrTokenExpired:
				statusCode = http.StatusUnauthorized
				message = "token has expired"
			case utils.ErrTokenInvalid:
				statusCode = http.StatusUnauthorized
				message = "invalid token"
			default:
				statusCode = http.StatusUnauthorized
				message = "authentication failed"
			}

			c.JSON(statusCode, gin.H{
				"success": false,
				"error":   message,
			})
			c.Abort()
			return
		}

		// Check if it's an access token
		if claims.Subject != "access_token" {
			c.JSON(http.StatusUnauthorized, gin.H{
				"success": false,
				"error":   "invalid token type",
			})
			c.Abort()
			return
		}

		// Store user information in context
		c.Set("user_id", claims.UserID)
		c.Set("user_email", claims.Email)

		c.Next()
	})
}

// OptionalAuthMiddleware validates JWT tokens but doesn't require them
func OptionalAuthMiddleware(cfg *config.Config) gin.HandlerFunc {
	jwtUtil := utils.NewJWTUtil(
		cfg.JWTSecretKey,
		cfg.JWTAccessTokenExpires,
		cfg.JWTRefreshTokenExpires,
	)

	return gin.HandlerFunc(func(c *gin.Context) {
		// Get token from Authorization header
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.Next()
			return
		}

		// Extract token
		token := utils.ExtractTokenFromHeader(authHeader)
		if token == "" {
			c.Next()
			return
		}

		// Validate token
		claims, err := jwtUtil.ValidateToken(token)
		if err != nil {
			// Log the error but don't block the request
			logrus.Debugf("Optional auth failed: %v", err)
			c.Next()
			return
		}

		// Check if it's an access token
		if claims.Subject == "access_token" {
			// Store user information in context
			c.Set("user_id", claims.UserID)
			c.Set("user_email", claims.Email)
		}

		c.Next()
	})
}

// GetUserIDFromContext extracts user ID from gin context
func GetUserIDFromContext(c *gin.Context) (uint, error) {
	userID, exists := c.Get("user_id")
	if !exists {
		return 0, gin.Error{Err: http.ErrNotFound, Type: gin.ErrorTypePublic}
	}

	id, ok := userID.(uint)
	if !ok {
		return 0, gin.Error{Err: http.ErrNotFound, Type: gin.ErrorTypePublic}
	}

	return id, nil
}

// GetUserEmailFromContext extracts user email from gin context
func GetUserEmailFromContext(c *gin.Context) (string, error) {
	userEmail, exists := c.Get("user_email")
	if !exists {
		return "", gin.Error{Err: http.ErrNotFound, Type: gin.ErrorTypePublic}
	}

	email, ok := userEmail.(string)
	if !ok {
		return "", gin.Error{Err: http.ErrNotFound, Type: gin.ErrorTypePublic}
	}

	return email, nil
}

// AdminMiddleware ensures user has admin privileges
func AdminMiddleware() gin.HandlerFunc {
	return gin.HandlerFunc(func(c *gin.Context) {
		// This would require checking user admin status in database
		// For now, we'll just pass through
		// TODO: Implement admin check
		c.Next()
	})
}

// ParseIDParam parses ID parameter from URL
func ParseIDParam(c *gin.Context, paramName string) (uint, error) {
	idStr := c.Param(paramName)
	if idStr == "" {
		return 0, gin.Error{Err: http.ErrNotFound, Type: gin.ErrorTypePublic}
	}

	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		return 0, gin.Error{Err: http.ErrNotFound, Type: gin.ErrorTypePublic}
	}

	return uint(id), nil
}