package routes

import (
	"go-server/models"
	"go-server/repositories"
	"go-server/services"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
)

func SetupPublicRoutes(router *gin.RouterGroup, courseService services.CourseService, testimonialRepo repositories.TestimonialRepository) {
	router.GET("/courses/search", handleSearchCourses(courseService))
	router.GET("/testimonials", handleGetApprovedTestimonials(testimonialRepo))
}

func handleSearchCourses(courseService services.CourseService) gin.HandlerFunc {
	return func(c *gin.Context) {
		query := c.Query("q")
		if query == "" {
			c.JSON(http.StatusBadRequest, models.APIResponse{
				Success: false,
				Error:   "search query is required",
			})
			return
		}

		limitStr := c.DefaultQuery("limit", "10")
		limit, err := strconv.Atoi(limitStr)
		if err != nil || limit <= 0 || limit > 50 {
			limit = 10
		}

		courses, err := courseService.SearchCourses(query, limit)
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

func handleGetApprovedTestimonials(testimonialRepo repositories.TestimonialRepository) gin.HandlerFunc {
	return func(c *gin.Context) {
		testimonials, err := testimonialRepo.GetApprovedTestimonials()
		if err != nil {
			c.JSON(http.StatusInternalServerError, models.APIResponse{
				Success: false,
				Error:   "failed to get testimonials",
			})
			return
		}

		// Convert to dict format
		var testimonialsData []map[string]interface{}
		for _, testimonial := range testimonials {
			testimonialsData = append(testimonialsData, testimonial.ToDict())
		}

		c.JSON(http.StatusOK, models.APIResponse{
			Success: true,
			Data:    testimonialsData,
		})
	}
}