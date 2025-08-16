package routes

import (
	"go-server/middleware"
	"go-server/models"
	"go-server/services"
	"net/http"

	"github.com/gin-gonic/gin"
)

func SetupSubjectRoutes(router *gin.RouterGroup, subjectService services.SubjectService, chapterService services.ChapterService) {
	router.GET("/:id", handleGetSubject(subjectService))
	router.PUT("/:id", handleUpdateSubject(subjectService))
	router.DELETE("/:id", handleDeleteSubject(subjectService))
	router.GET("/:id/chapters", handleGetSubjectChapters(chapterService))
	router.POST("/:id/chapters", handleGenerateChapters(chapterService))
}

func handleGetSubject(subjectService services.SubjectService) gin.HandlerFunc {
	return func(c *gin.Context) {
		subjectID, err := middleware.ParseIDParam(c, "id")
		if err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid subject ID",
			})
			return
		}

		subject, err := subjectService.GetSubjectByID(subjectID)
		if err != nil {
			statusCode := http.StatusInternalServerError
			if err.Error() == "subject not found" {
				statusCode = http.StatusNotFound
			}

			c.JSON(statusCode, models.APIResponse{
				Success: false,
				Error:   err.Error(),
			})
			return
		}

		c.JSON(http.StatusOK, models.APIResponse{
			Success: true,
			Data:    subject.ToDict(),
		})
	}
}

func handleUpdateSubject(subjectService services.SubjectService) gin.HandlerFunc {
	return func(c *gin.Context) {
		subjectID, err := middleware.ParseIDParam(c, "id")
		if err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid subject ID",
			})
			return
		}

		var req struct {
			Name string `json:"name" binding:"required"`
		}

		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid request format",
			})
			return
		}

		subject, err := subjectService.UpdateSubject(subjectID, req.Name)
		if err != nil {
			statusCode := http.StatusInternalServerError
			if err.Error() == "subject not found" {
				statusCode = http.StatusNotFound
			}

			c.JSON(statusCode, models.APIResponse{
				Success: false,
				Error:   err.Error(),
			})
			return
		}

		c.JSON(http.StatusOK, models.APIResponse{
			Success: true,
			Message: "subject updated successfully",
			Data:    subject.ToDict(),
		})
	}
}

func handleDeleteSubject(subjectService services.SubjectService) gin.HandlerFunc {
	return func(c *gin.Context) {
		subjectID, err := middleware.ParseIDParam(c, "id")
		if err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid subject ID",
			})
			return
		}

		if err := subjectService.DeleteSubject(subjectID); err != nil {
			statusCode := http.StatusInternalServerError
			if err.Error() == "subject not found" {
				statusCode = http.StatusNotFound
			}

			c.JSON(statusCode, models.APIResponse{
				Success: false,
				Error:   err.Error(),
			})
			return
		}

		c.JSON(http.StatusOK, models.APIResponse{
			Success: true,
			Message: "subject deleted successfully",
		})
	}
}

func handleGetSubjectChapters(chapterService services.ChapterService) gin.HandlerFunc {
	return func(c *gin.Context) {
		subjectID, err := middleware.ParseIDParam(c, "id")
		if err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid subject ID",
			})
			return
		}

		chapters, err := chapterService.GetChaptersBySubjectID(subjectID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, models.APIResponse{
				Success: false,
				Error:   err.Error(),
			})
			return
		}

		var chapterDicts []map[string]interface{}
		for _, chapter := range chapters {
			chapterDicts = append(chapterDicts, chapter.ToDict())
		}

		c.JSON(http.StatusOK, models.APIResponse{
			Success: true,
			Data:    chapterDicts,
		})
	}
}

func handleGenerateChapters(chapterService services.ChapterService) gin.HandlerFunc {
	return func(c *gin.Context) {
		subjectID, err := middleware.ParseIDParam(c, "id")
		if err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid subject ID",
			})
			return
		}

		var req struct {
			CourseID uint `json:"course_id" binding:"required"`
		}

		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid request format",
			})
			return
		}

		chapters, err := chapterService.GenerateChapters(req.CourseID, subjectID)
		if err != nil {
			statusCode := http.StatusInternalServerError
			if err.Error() == "subject not found" || err.Error() == "course not found" {
				statusCode = http.StatusNotFound
			}

			c.JSON(statusCode, models.APIResponse{
				Success: false,
				Error:   err.Error(),
			})
			return
		}

		var chapterDicts []map[string]interface{}
		for _, chapter := range chapters {
			chapterDicts = append(chapterDicts, chapter.ToDict())
		}

		c.JSON(http.StatusOK, models.APIResponse{
			Success: true,
			Message: "chapters generated successfully",
			Data:    chapterDicts,
		})
	}
}