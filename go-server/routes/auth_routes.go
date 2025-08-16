package routes

import (
	"go-server/middleware"
	"go-server/models"
	"go-server/services"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
)

func SetupAuthRoutes(router *gin.RouterGroup, authService services.AuthService) {
	router.POST("/register", handleRegister(authService))
	router.POST("/login", handleLogin(authService))
	router.POST("/refresh", handleRefreshToken(authService))
	router.POST("/password-reset/request", handlePasswordResetRequest(authService))
	router.POST("/password-reset/confirm", handlePasswordResetConfirm(authService))
}

func handleRegister(authService services.AuthService) gin.HandlerFunc {
	return func(c *gin.Context) {
		var req models.UserRegisterRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid request format",
			})
			return
		}

		user, err := authService.Register(&req)
		if err != nil {
			statusCode := http.StatusBadRequest
			if err.Error() == "user with this email already exists" {
				statusCode = http.StatusConflict
			}

			c.JSON(statusCode, models.APIResponse{
				Success: false,
				Error:   err.Error(),
			})
			return
		}

		c.JSON(http.StatusCreated, models.APIResponse{
			Success: true,
			Message: "user registered successfully",
			Data:    user.ToDict(),
		})
	}
}

func handleLogin(authService services.AuthService) gin.HandlerFunc {
	return func(c *gin.Context) {
		var req models.UserLoginRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid request format",
			})
			return
		}

		response, err := authService.Login(&req)
		if err != nil {
			statusCode := http.StatusUnauthorized
			if err.Error() == "account is deactivated" {
				statusCode = http.StatusForbidden
			}

			c.JSON(statusCode, models.APIResponse{
				Success: false,
				Error:   err.Error(),
			})
			return
		}

		c.JSON(http.StatusOK, models.APIResponse{
			Success: true,
			Message: "login successful",
			Data:    response,
		})
	}
}

func handleRefreshToken(authService services.AuthService) gin.HandlerFunc {
	return func(c *gin.Context) {
		var req struct {
			RefreshToken string `json:"refresh_token" binding:"required"`
		}

		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "refresh token is required",
			})
			return
		}

		response, err := authService.RefreshToken(req.RefreshToken)
		if err != nil {
			c.JSON(http.StatusUnauthorized, models.APIResponse{
				Success: false,
				Error:   err.Error(),
			})
			return
		}

		c.JSON(http.StatusOK, models.APIResponse{
			Success: true,
			Message: "tokens refreshed successfully",
			Data:    response,
		})
	}
}

func handlePasswordResetRequest(authService services.AuthService) gin.HandlerFunc {
	return func(c *gin.Context) {
		var req models.PasswordResetRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid request format",
			})
			return
		}

		err := authService.RequestPasswordReset(req.Email)
		if err != nil {
			logrus.Errorf("Password reset request error: %v", err)
			// Always return success to prevent email enumeration
		}

		c.JSON(http.StatusOK, models.APIResponse{
			Success: true,
			Message: "if the email exists, a password reset link has been sent",
		})
	}
}

func handlePasswordResetConfirm(authService services.AuthService) gin.HandlerFunc {
	return func(c *gin.Context) {
		var req models.PasswordResetConfirmRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid request format",
			})
			return
		}

		err := authService.ResetPassword(req.Token, req.Password)
		if err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   err.Error(),
			})
			return
		}

		c.JSON(http.StatusOK, models.APIResponse{
			Success: true,
			Message: "password reset successfully",
		})
	}
}

func SetupUserRoutes(router *gin.RouterGroup, authService services.AuthService) {
	router.GET("/profile", handleGetProfile(authService))
}

func handleGetProfile(authService services.AuthService) gin.HandlerFunc {
	return func(c *gin.Context) {
		userID, err := middleware.GetUserIDFromContext(c)
		if err != nil {
			c.JSON(http.StatusUnauthorized, models.APIResponse{
				Success: false,
				Error:   "unauthorized",
			})
			return
		}

		user, err := authService.GetUserProfile(userID)
		if err != nil {
			c.JSON(http.StatusNotFound, models.APIResponse{
				Success: false,
				Error:   err.Error(),
			})
			return
		}

		c.JSON(http.StatusOK, models.APIResponse{
			Success: true,
			Data:    user.ToDict(),
		})
	}
}