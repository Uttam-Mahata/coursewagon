package routes

import (
	"go-server/middleware"
	"go-server/models"
	"go-server/services"
	"net/http"

	"github.com/gin-gonic/gin"
)

func SetupImageRoutes(router *gin.RouterGroup, imageService services.ImageService) {
	router.POST("/courses/:id/generate", handleGenerateCourseImage(imageService))
	router.POST("/subjects/:id/generate", handleGenerateSubjectImage(imageService))
	router.POST("/custom", handleGenerateCustomImage(imageService))
	router.GET("/list/:prefix", handleListImages(imageService))
	router.DELETE("/:path", handleDeleteImage(imageService))
}

func handleGenerateCourseImage(imageService services.ImageService) gin.HandlerFunc {
	return func(c *gin.Context) {
		courseID, err := middleware.ParseIDParam(c, "id")
		if err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid course ID",
			})
			return
		}

		imageURL, err := imageService.GenerateCourseImage(courseID)
		if err != nil {
			statusCode := http.StatusInternalServerError
			if err.Error() == "course not found" {
				statusCode = http.StatusNotFound
			}

			c.JSON(statusCode, models.APIResponse{
				Success: false,
				Message: "Failed to generate course image",
				Error:   err.Error(),
			})
			return
		}

		c.JSON(http.StatusOK, models.APIResponse{
			Success: true,
			Message: "Course image generated successfully",
			Data: map[string]interface{}{
				"image_url": imageURL,
				"course_id": courseID,
			},
		})
	}
}

func handleGenerateSubjectImage(imageService services.ImageService) gin.HandlerFunc {
	return func(c *gin.Context) {
		subjectID, err := middleware.ParseIDParam(c, "id")
		if err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid subject ID",
			})
			return
		}

		imageURL, err := imageService.GenerateSubjectImage(subjectID)
		if err != nil {
			statusCode := http.StatusInternalServerError
			if err.Error() == "subject not found" {
				statusCode = http.StatusNotFound
			}

			c.JSON(statusCode, models.APIResponse{
				Success: false,
				Message: "Failed to generate subject image",
				Error:   err.Error(),
			})
			return
		}

		c.JSON(http.StatusOK, models.APIResponse{
			Success: true,
			Message: "Subject image generated successfully",
			Data: map[string]interface{}{
				"image_url":  imageURL,
				"subject_id": subjectID,
			},
		})
	}
}

func handleGenerateCustomImage(imageService services.ImageService) gin.HandlerFunc {
	return func(c *gin.Context) {
		var req struct {
			Prompt string `json:"prompt" binding:"required"`
		}

		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid request format",
			})
			return
		}

		imageURL, err := imageService.GenerateCustomImage(req.Prompt)
		if err != nil {
			c.JSON(http.StatusInternalServerError, models.APIResponse{
				Success: false,
				Message: "Failed to generate custom image",
				Error:   err.Error(),
			})
			return
		}

		c.JSON(http.StatusOK, models.APIResponse{
			Success: true,
			Message: "Custom image generated successfully",
			Data: map[string]interface{}{
				"image_url": imageURL,
				"prompt":    req.Prompt,
			},
		})
	}
}

func handleListImages(imageService services.ImageService) gin.HandlerFunc {
	return func(c *gin.Context) {
		prefix := c.Param("prefix")

		images, err := imageService.ListImages(prefix)
		if err != nil {
			c.JSON(http.StatusInternalServerError, models.APIResponse{
				Success: false,
				Message: "Failed to list images",
				Error:   err.Error(),
			})
			return
		}

		c.JSON(http.StatusOK, models.APIResponse{
			Success: true,
			Message: "Images retrieved successfully",
			Data: map[string]interface{}{
				"images": images,
				"count":  len(images),
				"prefix": prefix,
			},
		})
	}
}

func handleDeleteImage(imageService services.ImageService) gin.HandlerFunc {
	return func(c *gin.Context) {
		imagePath := c.Param("path")

		if err := imageService.DeleteImage(imagePath); err != nil {
			c.JSON(http.StatusInternalServerError, models.APIResponse{
				Success: false,
				Message: "Failed to delete image",
				Error:   err.Error(),
			})
			return
		}

		c.JSON(http.StatusOK, models.APIResponse{
			Success: true,
			Message: "Image deleted successfully",
		})
	}
}