package routes

import (
	"go-server/repositories"

	"github.com/gin-gonic/gin"
)

func SetupTopicRoutes(router *gin.RouterGroup, topicRepo repositories.TopicRepository, chapterRepo repositories.ChapterRepository) {
	// Topic routes can be added here as needed
	// For now, most topic operations are handled through course hierarchy
}