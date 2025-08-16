package repositories

import (
	"go-server/models"

	"github.com/sirupsen/logrus"
	"gorm.io/gorm"
)

type TopicRepository interface {
	BaseRepository
	GetTopicsByChapterID(chapterID uint) ([]models.Topic, error)
	GetTopicWithContents(topicID uint) (*models.Topic, error)
	CreateTopics(topics []models.Topic) error
	DeleteTopicsByChapterID(chapterID uint) error
}

type TopicRepositoryImpl struct {
	*BaseRepositoryImpl
}

func NewTopicRepository(db *gorm.DB) TopicRepository {
	return &TopicRepositoryImpl{
		BaseRepositoryImpl: NewBaseRepository(db),
	}
}

// GetTopicsByChapterID gets all topics for a specific chapter
func (r *TopicRepositoryImpl) GetTopicsByChapterID(chapterID uint) ([]models.Topic, error) {
	var topics []models.Topic
	err := r.DB.Where("chapter_id = ?", chapterID).Find(&topics).Error
	if err != nil {
		logrus.Errorf("Error getting topics by chapter ID: %v", err)
		return nil, err
	}
	return topics, nil
}

// GetTopicWithContents gets a topic with its contents
func (r *TopicRepositoryImpl) GetTopicWithContents(topicID uint) (*models.Topic, error) {
	var topic models.Topic
	err := r.DB.Preload("Contents").First(&topic, topicID).Error
	if err != nil {
		logrus.Errorf("Error getting topic with contents: %v", err)
		return nil, err
	}
	return &topic, nil
}

// CreateTopics creates multiple topics
func (r *TopicRepositoryImpl) CreateTopics(topics []models.Topic) error {
	err := r.DB.CreateInBatches(&topics, 100).Error
	if err != nil {
		logrus.Errorf("Error creating topics: %v", err)
	}
	return err
}

// DeleteTopicsByChapterID deletes all topics for a chapter
func (r *TopicRepositoryImpl) DeleteTopicsByChapterID(chapterID uint) error {
	err := r.DB.Where("chapter_id = ?", chapterID).Delete(&models.Topic{}).Error
	if err != nil {
		logrus.Errorf("Error deleting topics by chapter ID: %v", err)
	}
	return err
}