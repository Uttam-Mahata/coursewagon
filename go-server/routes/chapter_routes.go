package routes

import (
	"go-server/repositories"

	"github.com/gin-gonic/gin"
)

func SetupChapterRoutes(router *gin.RouterGroup, chapterRepo repositories.ChapterRepository, topicRepo repositories.TopicRepository, subjectRepo repositories.SubjectRepository) {
	// Chapter routes can be added here as needed
	// For now, most chapter operations are handled through course hierarchy
}