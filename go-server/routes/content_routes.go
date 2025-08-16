package routes

import (
	"go-server/middleware"
	"go-server/models"
	"go-server/services"
	"net/http"

	"github.com/gin-gonic/gin"
)

func SetupContentRoutes(router *gin.RouterGroup, contentService services.ContentService) {
	router.POST("/generate", handleGenerateContent(contentService))
	router.GET("/topic/:topic_id", handleGetContentByTopic(contentService))
	router.PUT("/:id", handleUpdateContent(contentService))
	router.DELETE("/:id", handleDeleteContent(contentService))
}

func handleGenerateContent(contentService services.ContentService) gin.HandlerFunc {
	return func(c *gin.Context) {
		userID, err := middleware.GetUserIDFromContext(c)
		if err != nil {
			c.JSON(http.StatusUnauthorized, models.APIResponse{
				Success: false,
				Error:   "unauthorized",
			})
			return
		}

		var req models.ContentGenerateRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid request format",
			})
			return
		}

		content, err := contentService.GenerateContent(userID, &req)
		if err != nil {
			statusCode := http.StatusInternalServerError
			if err.Error() == "course not found" || err.Error() == "topic not found" ||
				err.Error() == "chapter not found" || err.Error() == "subject not found" {
				statusCode = http.StatusNotFound
			} else if err.Error() == "unauthorized access to course" {
				statusCode = http.StatusForbidden
			}

			c.JSON(statusCode, models.APIResponse{
				Success: false,
				Error:   err.Error(),
			})
			return
		}

		c.JSON(http.StatusCreated, models.APIResponse{
			Success: true,
			Message: "content generated successfully",
			Data:    content.ToDict(),
		})
	}
}

func handleGetContentByTopic(contentService services.ContentService) gin.HandlerFunc {
	return func(c *gin.Context) {
		userID, err := middleware.GetUserIDFromContext(c)
		if err != nil {
			c.JSON(http.StatusUnauthorized, models.APIResponse{
				Success: false,
				Error:   "unauthorized",
			})
			return
		}

		topicID, err := middleware.ParseIDParam(c, "topic_id")
		if err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid topic ID",
			})
			return
		}

		content, err := contentService.GetContentByTopicID(topicID, userID)
		if err != nil {
			statusCode := http.StatusNotFound
			if err.Error() == "unauthorized access to content" {
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
			Data:    content.ToDict(),
		})
	}
}

func handleUpdateContent(contentService services.ContentService) gin.HandlerFunc {
	return func(c *gin.Context) {
		userID, err := middleware.GetUserIDFromContext(c)
		if err != nil {
			c.JSON(http.StatusUnauthorized, models.APIResponse{
				Success: false,
				Error:   "unauthorized",
			})
			return
		}

		contentID, err := middleware.ParseIDParam(c, "id")
		if err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid content ID",
			})
			return
		}

		var req struct {
			Content string `json:"content" binding:"required"`
		}

		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "content is required",
			})
			return
		}

		content, err := contentService.UpdateContent(contentID, userID, req.Content)
		if err != nil {
			statusCode := http.StatusBadRequest
			if err.Error() == "content not found" {
				statusCode = http.StatusNotFound
			} else if err.Error() == "unauthorized access to content" {
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
			Message: "content updated successfully",
			Data:    content.ToDict(),
		})
	}
}

func handleDeleteContent(contentService services.ContentService) gin.HandlerFunc {
	return func(c *gin.Context) {
		userID, err := middleware.GetUserIDFromContext(c)
		if err != nil {
			c.JSON(http.StatusUnauthorized, models.APIResponse{
				Success: false,
				Error:   "unauthorized",
			})
			return
		}

		contentID, err := middleware.ParseIDParam(c, "id")
		if err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid content ID",
			})
			return
		}

		err = contentService.DeleteContent(contentID, userID)
		if err != nil {
			statusCode := http.StatusBadRequest
			if err.Error() == "content not found" {
				statusCode = http.StatusNotFound
			} else if err.Error() == "unauthorized access to content" {
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
			Message: "content deleted successfully",
		})
	}
}