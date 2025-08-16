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

type TopicService interface {
	GenerateTopics(courseID, subjectID, chapterID uint) ([]models.Topic, error)
	GetTopicsByChapterID(chapterID uint) ([]models.Topic, error)
	GetTopicByID(topicID uint) (*models.Topic, error)
	CreateTopics(topics []models.Topic) error
	UpdateTopic(topicID uint, name string) (*models.Topic, error)
	DeleteTopic(topicID uint) error
	DeleteTopicsByChapterID(chapterID uint) error
}

type TopicServiceImpl struct {
	topicRepo    repositories.TopicRepository
	chapterRepo  repositories.ChapterRepository
	subjectRepo  repositories.SubjectRepository
	courseRepo   repositories.CourseRepository
	geminiHelper *utils.GeminiHelper
}

func NewTopicService(topicRepo repositories.TopicRepository, chapterRepo repositories.ChapterRepository, subjectRepo repositories.SubjectRepository, courseRepo repositories.CourseRepository) TopicService {
	return &TopicServiceImpl{
		topicRepo:    topicRepo,
		chapterRepo:  chapterRepo,
		subjectRepo:  subjectRepo,
		courseRepo:   courseRepo,
		geminiHelper: utils.NewGeminiHelper(),
	}
}

// GenerateTopics generates topics for a chapter using Gemini AI
func (s *TopicServiceImpl) GenerateTopics(courseID, subjectID, chapterID uint) ([]models.Topic, error) {
	logrus.Infof("Starting topic generation for chapter_id: %d, subject_id: %d, course_id: %d", chapterID, subjectID, courseID)

	// Get chapter
	chapter := &models.Chapter{}
	if err := s.chapterRepo.GetByID(chapterID, chapter); err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, errors.New("chapter not found")
		}
		return nil, errors.New("failed to get chapter")
	}

	// Verify chapter belongs to subject
	if chapter.SubjectID != subjectID {
		return nil, errors.New("chapter does not belong to the specified subject")
	}

	// Get subject
	subject := &models.Subject{}
	if err := s.subjectRepo.GetByID(subjectID, subject); err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, errors.New("subject not found")
		}
		return nil, errors.New("failed to get subject")
	}

	// Verify subject belongs to course
	if subject.CourseID != courseID {
		return nil, errors.New("subject does not belong to the specified course")
	}

	// Get course
	course := &models.Course{}
	if err := s.courseRepo.GetByID(courseID, course); err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, errors.New("course not found")
		}
		return nil, errors.New("failed to get course")
	}

	logrus.Debugf("Found chapter: %s, subject: %s, course: %s", chapter.Name, subject.Name, course.Name)

	// Check if topics already exist
	existingTopics, err := s.topicRepo.GetTopicsByChapterID(chapterID)
	if err != nil {
		return nil, errors.New("failed to check existing topics")
	}

	// If topics exist, return them
	if len(existingTopics) > 0 {
		logrus.Infof("Topics already exist for chapter %s, returning existing topics", chapter.Name)
		return existingTopics, nil
	}

	// Generate topics using Gemini
	ctx := context.Background()
	prompt := fmt.Sprintf(`Generate a comprehensive list of topics for the chapter '%s' in subject '%s' for the course '%s'.
	Consider the following:
	1. Include topics from basic to advanced level within this chapter
	2. Each topic should be a distinct subtopic within the chapter
	3. Topics should follow a logical learning progression
	4. Generate maximum 6 topics for the chapter
	5. Keep topic names concise and clear
	6. Focus on specific concepts that can be taught individually`, chapter.Name, subject.Name, course.Name)

	topicNames, err := s.geminiHelper.GenerateTopics(ctx, chapter.Name, subject.Name, course.Name)
	if err != nil {
		logrus.Errorf("Error generating topics with Gemini: %v", err)
		return nil, errors.New("failed to generate topics")
	}

	logrus.Infof("Generated %d topics for chapter %s", len(topicNames), chapter.Name)

	// Create topic models
	var topics []models.Topic
	for _, name := range topicNames {
		topics = append(topics, models.Topic{
			Name:      name,
			ChapterID: chapterID,
		})
	}

	// Save topics
	if err := s.topicRepo.CreateTopics(topics); err != nil {
		logrus.Errorf("Error saving topics: %v", err)
		return nil, errors.New("failed to save topics")
	}

	logrus.Infof("Successfully created %d topics for chapter: %s", len(topics), chapter.Name)
	return topics, nil
}

// GetTopicsByChapterID returns all topics for a chapter
func (s *TopicServiceImpl) GetTopicsByChapterID(chapterID uint) ([]models.Topic, error) {
	topics, err := s.topicRepo.GetTopicsByChapterID(chapterID)
	if err != nil {
		logrus.Errorf("Error getting topics by chapter ID: %v", err)
		return nil, errors.New("failed to get topics")
	}
	return topics, nil
}

// GetTopicByID returns a specific topic
func (s *TopicServiceImpl) GetTopicByID(topicID uint) (*models.Topic, error) {
	topic := &models.Topic{}
	if err := s.topicRepo.GetByID(topicID, topic); err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, errors.New("topic not found")
		}
		logrus.Errorf("Error getting topic: %v", err)
		return nil, errors.New("failed to get topic")
	}
	return topic, nil
}

// CreateTopics creates multiple topics
func (s *TopicServiceImpl) CreateTopics(topics []models.Topic) error {
	if err := s.topicRepo.CreateTopics(topics); err != nil {
		logrus.Errorf("Error creating topics: %v", err)
		return errors.New("failed to create topics")
	}
	return nil
}

// UpdateTopic updates a topic's name
func (s *TopicServiceImpl) UpdateTopic(topicID uint, name string) (*models.Topic, error) {
	topic := &models.Topic{}
	if err := s.topicRepo.GetByID(topicID, topic); err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, errors.New("topic not found")
		}
		return nil, errors.New("failed to get topic")
	}

	topic.Name = utils.SanitizeString(name)
	if err := s.topicRepo.Update(topic); err != nil {
		logrus.Errorf("Error updating topic: %v", err)
		return nil, errors.New("failed to update topic")
	}

	return topic, nil
}

// DeleteTopic deletes a topic
func (s *TopicServiceImpl) DeleteTopic(topicID uint) error {
	if err := s.topicRepo.Delete(topicID, &models.Topic{}); err != nil {
		logrus.Errorf("Error deleting topic: %v", err)
		return errors.New("failed to delete topic")
	}
	return nil
}

// DeleteTopicsByChapterID deletes all topics for a chapter
func (s *TopicServiceImpl) DeleteTopicsByChapterID(chapterID uint) error {
	if err := s.topicRepo.DeleteTopicsByChapterID(chapterID); err != nil {
		logrus.Errorf("Error deleting topics by chapter ID: %v", err)
		return errors.New("failed to delete topics")
	}
	return nil
}