package repositories

import (
	"go-server/models"

	"github.com/sirupsen/logrus"
	"gorm.io/gorm"
)

type ContentRepository interface {
	BaseRepository
	GetContentByTopicID(topicID uint) (*models.Content, error)
	CreateContent(content *models.Content) error
	UpdateContent(content *models.Content) error
	DeleteContentByTopicID(topicID uint) error
	GetContentWithTopic(contentID uint) (*models.Content, error)
}

type ContentRepositoryImpl struct {
	*BaseRepositoryImpl
}

func NewContentRepository(db *gorm.DB) ContentRepository {
	return &ContentRepositoryImpl{
		BaseRepositoryImpl: NewBaseRepository(db),
	}
}

// GetContentByTopicID gets content for a specific topic
func (r *ContentRepositoryImpl) GetContentByTopicID(topicID uint) (*models.Content, error) {
	var content models.Content
	err := r.DB.Where("topic_id = ?", topicID).First(&content).Error
	if err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, nil
		}
		logrus.Errorf("Error getting content by topic ID: %v", err)
		return nil, err
	}
	return &content, nil
}

// CreateContent creates new content
func (r *ContentRepositoryImpl) CreateContent(content *models.Content) error {
	err := r.DB.Create(content).Error
	if err != nil {
		logrus.Errorf("Error creating content: %v", err)
	}
	return err
}

// UpdateContent updates existing content
func (r *ContentRepositoryImpl) UpdateContent(content *models.Content) error {
	err := r.DB.Save(content).Error
	if err != nil {
		logrus.Errorf("Error updating content: %v", err)
	}
	return err
}

// DeleteContentByTopicID deletes content for a topic
func (r *ContentRepositoryImpl) DeleteContentByTopicID(topicID uint) error {
	err := r.DB.Where("topic_id = ?", topicID).Delete(&models.Content{}).Error
	if err != nil {
		logrus.Errorf("Error deleting content by topic ID: %v", err)
	}
	return err
}

// GetContentWithTopic gets content with its topic information
func (r *ContentRepositoryImpl) GetContentWithTopic(contentID uint) (*models.Content, error) {
	var content models.Content
	err := r.DB.Preload("Topic").First(&content, contentID).Error
	if err != nil {
		logrus.Errorf("Error getting content with topic: %v", err)
		return nil, err
	}
	return &content, nil
}