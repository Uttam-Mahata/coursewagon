package routes

import (
	"go-server/middleware"
	"go-server/models"
	"go-server/repositories"
	"go-server/services"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
)

func SetupCourseRoutes(router *gin.RouterGroup, courseService services.CourseService, subjectRepo repositories.SubjectRepository, chapterRepo repositories.ChapterRepository, topicRepo repositories.TopicRepository) {
	router.POST("", handleCreateCourse(courseService))
	router.GET("", handleGetUserCourses(courseService))
	router.GET("/:id", handleGetCourse(courseService))
	router.PUT("/:id", handleUpdateCourse(courseService))
	router.DELETE("/:id", handleDeleteCourse(courseService))
	router.POST("/:id/subjects", handleGenerateSubjects(courseService))
	router.GET("/:id/subjects", handleGetCourseSubjects(subjectRepo))
	router.POST("/:id/subjects/bulk", handleCreateSubjects(subjectRepo, courseService))
	router.GET("/:id/hierarchy", handleGetCourseHierarchy(courseService, subjectRepo, chapterRepo, topicRepo))
}

func handleCreateCourse(courseService services.CourseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		userID, err := middleware.GetUserIDFromContext(c)
		if err != nil {
			c.JSON(http.StatusUnauthorized, models.APIResponse{
				Success: false,
				Error:   "unauthorized",
			})
			return
		}

		var req models.CourseCreateRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid request format",
			})
			return
		}

		course, err := courseService.CreateCourse(userID, &req)
		if err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   err.Error(),
			})
			return
		}

		c.JSON(http.StatusCreated, models.APIResponse{
			Success: true,
			Message: "course created successfully",
			Data:    course.ToDict(),
		})
	}
}

func handleGetUserCourses(courseService services.CourseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		userID, err := middleware.GetUserIDFromContext(c)
		if err != nil {
			c.JSON(http.StatusUnauthorized, models.APIResponse{
				Success: false,
				Error:   "unauthorized",
			})
			return
		}

		courses, err := courseService.GetUserCourses(userID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, models.APIResponse{
				Success: false,
				Error:   err.Error(),
			})
			return
		}

		// Convert to dict format
		var coursesData []map[string]interface{}
		for _, course := range courses {
			coursesData = append(coursesData, course.ToDict())
		}

		c.JSON(http.StatusOK, models.APIResponse{
			Success: true,
			Data:    coursesData,
		})
	}
}

func handleGetCourse(courseService services.CourseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		userID, err := middleware.GetUserIDFromContext(c)
		if err != nil {
			c.JSON(http.StatusUnauthorized, models.APIResponse{
				Success: false,
				Error:   "unauthorized",
			})
			return
		}

		courseID, err := middleware.ParseIDParam(c, "id")
		if err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid course ID",
			})
			return
		}

		course, err := courseService.GetCourseByID(courseID, userID)
		if err != nil {
			statusCode := http.StatusNotFound
			if err.Error() == "unauthorized access to course" {
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
			Data:    course.ToDict(),
		})
	}
}

func handleUpdateCourse(courseService services.CourseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		userID, err := middleware.GetUserIDFromContext(c)
		if err != nil {
			c.JSON(http.StatusUnauthorized, models.APIResponse{
				Success: false,
				Error:   "unauthorized",
			})
			return
		}

		courseID, err := middleware.ParseIDParam(c, "id")
		if err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid course ID",
			})
			return
		}

		var req models.CourseUpdateRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid request format",
			})
			return
		}

		course, err := courseService.UpdateCourse(courseID, userID, &req)
		if err != nil {
			statusCode := http.StatusBadRequest
			if err.Error() == "course not found" {
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

		c.JSON(http.StatusOK, models.APIResponse{
			Success: true,
			Message: "course updated successfully",
			Data:    course.ToDict(),
		})
	}
}

func handleDeleteCourse(courseService services.CourseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		userID, err := middleware.GetUserIDFromContext(c)
		if err != nil {
			c.JSON(http.StatusUnauthorized, models.APIResponse{
				Success: false,
				Error:   "unauthorized",
			})
			return
		}

		courseID, err := middleware.ParseIDParam(c, "id")
		if err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid course ID",
			})
			return
		}

		err = courseService.DeleteCourse(courseID, userID)
		if err != nil {
			statusCode := http.StatusBadRequest
			if err.Error() == "course not found" {
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

		c.JSON(http.StatusOK, models.APIResponse{
			Success: true,
			Message: "course deleted successfully",
		})
	}
}

func handleGenerateSubjects(courseService services.CourseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		userID, err := middleware.GetUserIDFromContext(c)
		if err != nil {
			c.JSON(http.StatusUnauthorized, models.APIResponse{
				Success: false,
				Error:   "unauthorized",
			})
			return
		}

		courseID, err := middleware.ParseIDParam(c, "id")
		if err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid course ID",
			})
			return
		}

		subjects, err := courseService.GenerateSubjects(courseID, userID)
		if err != nil {
			statusCode := http.StatusInternalServerError
			if err.Error() == "course not found" {
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

		// Convert to dict format
		var subjectsData []map[string]interface{}
		for _, subject := range subjects {
			subjectsData = append(subjectsData, subject.ToDict())
		}

		c.JSON(http.StatusOK, models.APIResponse{
			Success: true,
			Message: "subjects generated successfully",
			Data:    subjectsData,
		})
	}
}

func handleGetCourseSubjects(subjectRepo repositories.SubjectRepository) gin.HandlerFunc {
	return func(c *gin.Context) {
		courseID, err := middleware.ParseIDParam(c, "id")
		if err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid course ID",
			})
			return
		}

		subjects, err := subjectRepo.GetSubjectsByCourseID(courseID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, models.APIResponse{
				Success: false,
				Error:   "failed to get subjects",
			})
			return
		}

		// Convert to dict format
		var subjectsData []map[string]interface{}
		for _, subject := range subjects {
			subjectsData = append(subjectsData, subject.ToDict())
		}

		c.JSON(http.StatusOK, models.APIResponse{
			Success: true,
			Data:    subjectsData,
		})
	}
}

func handleCreateSubjects(subjectRepo repositories.SubjectRepository, courseService services.CourseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		userID, err := middleware.GetUserIDFromContext(c)
		if err != nil {
			c.JSON(http.StatusUnauthorized, models.APIResponse{
				Success: false,
				Error:   "unauthorized",
			})
			return
		}

		courseID, err := middleware.ParseIDParam(c, "id")
		if err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid course ID",
			})
			return
		}

		var req models.SubjectCreateRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid request format",
			})
			return
		}

		// Verify course ownership
		_, err = courseService.GetCourseByID(courseID, userID)
		if err != nil {
			statusCode := http.StatusNotFound
			if err.Error() == "unauthorized access to course" {
				statusCode = http.StatusForbidden
			}

			c.JSON(statusCode, models.APIResponse{
				Success: false,
				Error:   err.Error(),
			})
			return
		}

		// Create subjects
		var subjects []models.Subject
		for _, name := range req.Subjects {
			subjects = append(subjects, models.Subject{
				Name:     name,
				CourseID: courseID,
			})
		}

		err = subjectRepo.CreateSubjects(subjects)
		if err != nil {
			c.JSON(http.StatusInternalServerError, models.APIResponse{
				Success: false,
				Error:   "failed to create subjects",
			})
			return
		}

		// Convert to dict format
		var subjectsData []map[string]interface{}
		for _, subject := range subjects {
			subjectsData = append(subjectsData, subject.ToDict())
		}

		c.JSON(http.StatusCreated, models.APIResponse{
			Success: true,
			Message: "subjects created successfully",
			Data:    subjectsData,
		})
	}
}

func handleGetCourseHierarchy(courseService services.CourseService, subjectRepo repositories.SubjectRepository, chapterRepo repositories.ChapterRepository, topicRepo repositories.TopicRepository) gin.HandlerFunc {
	return func(c *gin.Context) {
		userID, err := middleware.GetUserIDFromContext(c)
		if err != nil {
			c.JSON(http.StatusUnauthorized, models.APIResponse{
				Success: false,
				Error:   "unauthorized",
			})
			return
		}

		courseID, err := middleware.ParseIDParam(c, "id")
		if err != nil {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "invalid course ID",
			})
			return
		}

		// Verify course ownership
		course, err := courseService.GetCourseByID(courseID, userID)
		if err != nil {
			statusCode := http.StatusNotFound
			if err.Error() == "unauthorized access to course" {
				statusCode = http.StatusForbidden
			}

			c.JSON(statusCode, models.APIResponse{
				Success: false,
				Error:   err.Error(),
			})
			return
		}

		// Get subjects
		subjects, err := subjectRepo.GetSubjectsByCourseID(courseID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, models.APIResponse{
				Success: false,
				Error:   "failed to get subjects",
			})
			return
		}

		// Build hierarchy
		hierarchy := make(map[string]interface{})
		hierarchy["course"] = course.ToDict()
		hierarchy["subjects"] = make([]map[string]interface{}, 0)

		for _, subject := range subjects {
			subjectData := subject.ToDict()

			// Get chapters for this subject
			chapters, err := chapterRepo.GetChaptersBySubjectID(subject.ID)
			if err != nil {
				continue
			}

			subjectData["chapters"] = make([]map[string]interface{}, 0)
			for _, chapter := range chapters {
				chapterData := chapter.ToDict()

				// Get topics for this chapter
				topics, err := topicRepo.GetTopicsByChapterID(chapter.ID)
				if err != nil {
					continue
				}

				var topicsData []map[string]interface{}
				for _, topic := range topics {
					topicsData = append(topicsData, topic.ToDict())
				}
				chapterData["topics"] = topicsData

				subjectData["chapters"] = append(subjectData["chapters"].([]map[string]interface{}), chapterData)
			}

			hierarchy["subjects"] = append(hierarchy["subjects"].([]map[string]interface{}), subjectData)
		}

		c.JSON(http.StatusOK, models.APIResponse{
			Success: true,
			Data:    hierarchy,
		})
	}
}