package services

import (
	"context"
	"errors"
	"fmt"
	"go-server/models"
	"go-server/repositories"
	"go-server/utils"

	"github.com/sirupsen/logrus"
	"gorm.io/gorm"
)

type ContentService interface {
	GenerateContent(userID uint, req *models.ContentGenerateRequest) (*models.Content, error)
	GetContentByTopicID(topicID, userID uint) (*models.Content, error)
	UpdateContent(contentID, userID uint, content string) (*models.Content, error)
	DeleteContent(contentID, userID uint) error
}

type ContentServiceImpl struct {
	contentRepo repositories.ContentRepository
	topicRepo   repositories.TopicRepository
	chapterRepo repositories.ChapterRepository
	subjectRepo repositories.SubjectRepository
	courseRepo  repositories.CourseRepository
	geminiHelper *utils.GeminiHelper
}

func NewContentService(
	contentRepo repositories.ContentRepository,
	topicRepo repositories.TopicRepository,
	chapterRepo repositories.ChapterRepository,
	subjectRepo repositories.SubjectRepository,
	courseRepo repositories.CourseRepository,
) ContentService {
	return &ContentServiceImpl{
		contentRepo:  contentRepo,
		topicRepo:    topicRepo,
		chapterRepo:  chapterRepo,
		subjectRepo:  subjectRepo,
		courseRepo:   courseRepo,
		geminiHelper: utils.NewGeminiHelper(),
	}
}

// GenerateContent generates detailed content for a topic using Gemini AI
func (s *ContentServiceImpl) GenerateContent(userID uint, req *models.ContentGenerateRequest) (*models.Content, error) {
	// Validate request
	if err := utils.ValidateStruct(req); err != nil {
		return nil, fmt.Errorf("validation error: %s", utils.FormatValidationErrors(err))
	}

	// Verify ownership and get entities
	course := &models.Course{}
	if err := s.courseRepo.GetByID(req.CourseID, course); err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, errors.New("course not found")
		}
		return nil, errors.New("failed to get course")
	}

	// Check course ownership
	if course.UserID == nil || *course.UserID != userID {
		return nil, errors.New("unauthorized access to course")
	}

	// Get topic
	topic := &models.Topic{}
	if err := s.topicRepo.GetByID(req.TopicID, topic); err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, errors.New("topic not found")
		}
		return nil, errors.New("failed to get topic")
	}

	// Get chapter
	chapter := &models.Chapter{}
	if err := s.chapterRepo.GetByID(req.ChapterID, chapter); err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, errors.New("chapter not found")
		}
		return nil, errors.New("failed to get chapter")
	}

	// Get subject
	subject := &models.Subject{}
	if err := s.subjectRepo.GetByID(req.SubjectID, subject); err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, errors.New("subject not found")
		}
		return nil, errors.New("failed to get subject")
	}

	// Verify relationships
	if subject.CourseID != req.CourseID {
		return nil, errors.New("subject does not belong to the specified course")
	}
	if chapter.SubjectID != req.SubjectID {
		return nil, errors.New("chapter does not belong to the specified subject")
	}
	if topic.ChapterID != req.ChapterID {
		return nil, errors.New("topic does not belong to the specified chapter")
	}

	// Check if content already exists
	existingContent, err := s.contentRepo.GetContentByTopicID(req.TopicID)
	if err != nil {
		return nil, errors.New("failed to check existing content")
	}
	if existingContent != nil {
		return existingContent, nil
	}

	// Generate content using Gemini
	ctx := context.Background()
	generatedContent, err := s.geminiHelper.GenerateTopicContent(
		ctx,
		topic.Name,
		chapter.Name,
		subject.Name,
		course.Name,
	)
	if err != nil {
		logrus.Errorf("Error generating content with Gemini: %v", err)
		return nil, errors.New("failed to generate content")
	}

	// Create content model
	content := &models.Content{
		TopicID: req.TopicID,
		Content: generatedContent,
	}

	// Save content
	if err := s.contentRepo.CreateContent(content); err != nil {
		logrus.Errorf("Error saving content: %v", err)
		return nil, errors.New("failed to save content")
	}

	logrus.Infof("Generated content for topic: %s", topic.Name)
	return content, nil
}

// GetContentByTopicID returns content for a specific topic
func (s *ContentServiceImpl) GetContentByTopicID(topicID, userID uint) (*models.Content, error) {
	// Get topic first to verify ownership
	topic := &models.Topic{}
	if err := s.topicRepo.GetByID(topicID, topic); err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, errors.New("topic not found")
		}
		return nil, errors.New("failed to get topic")
	}

	// Get chapter to verify ownership chain
	chapter := &models.Chapter{}
	if err := s.chapterRepo.GetByID(topic.ChapterID, chapter); err != nil {
		return nil, errors.New("failed to get chapter")
	}

	// Get subject to verify ownership chain
	subject := &models.Subject{}
	if err := s.subjectRepo.GetByID(chapter.SubjectID, subject); err != nil {
		return nil, errors.New("failed to get subject")
	}

	// Get course to verify ownership
	course := &models.Course{}
	if err := s.courseRepo.GetByID(subject.CourseID, course); err != nil {
		return nil, errors.New("failed to get course")
	}

	// Check ownership
	if course.UserID == nil || *course.UserID != userID {
		return nil, errors.New("unauthorized access to content")
	}

	// Get content
	content, err := s.contentRepo.GetContentByTopicID(topicID)
	if err != nil {
		return nil, errors.New("failed to get content")
	}
	if content == nil {
		return nil, errors.New("content not found")
	}

	return content, nil
}

// UpdateContent updates existing content
func (s *ContentServiceImpl) UpdateContent(contentID, userID uint, newContent string) (*models.Content, error) {
	// Get existing content
	content := &models.Content{}
	if err := s.contentRepo.GetByID(contentID, content); err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, errors.New("content not found")
		}
		return nil, errors.New("failed to get content")
	}

	// Verify ownership through the content chain
	_, err := s.GetContentByTopicID(content.TopicID, userID)
	if err != nil {
		return nil, err
	}

	// Sanitize and update content
	content.Content = utils.SanitizeString(newContent)

	if err := s.contentRepo.UpdateContent(content); err != nil {
		logrus.Errorf("Error updating content: %v", err)
		return nil, errors.New("failed to update content")
	}

	logrus.Infof("Content updated successfully: %d", contentID)
	return content, nil
}

// DeleteContent deletes content
func (s *ContentServiceImpl) DeleteContent(contentID, userID uint) error {
	// Get existing content
	content := &models.Content{}
	if err := s.contentRepo.GetByID(contentID, content); err != nil {
		if err == gorm.ErrRecordNotFound {
			return errors.New("content not found")
		}
		return errors.New("failed to get content")
	}

	// Verify ownership through the content chain
	_, err := s.GetContentByTopicID(content.TopicID, userID)
	if err != nil {
		return err
	}

	// Delete content
	if err := s.contentRepo.Delete(contentID, &models.Content{}); err != nil {
		logrus.Errorf("Error deleting content: %v", err)
		return errors.New("failed to delete content")
	}

	logrus.Infof("Content deleted successfully: %d", contentID)
	return nil
}