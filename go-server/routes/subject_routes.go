package routes

import (
	"go-server/repositories"

	"github.com/gin-gonic/gin"
)

func SetupSubjectRoutes(router *gin.RouterGroup, subjectRepo repositories.SubjectRepository, chapterRepo repositories.ChapterRepository, courseRepo repositories.CourseRepository) {
	// Subject routes can be added here as needed
	// For now, most subject operations are handled through course routes
}