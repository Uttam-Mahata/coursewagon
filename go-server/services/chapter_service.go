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

type ChapterService interface {
	GenerateChapters(courseID, subjectID uint) ([]models.Chapter, error)
	GetChaptersBySubjectID(subjectID uint) ([]models.Chapter, error)
	GetChapterByID(chapterID uint) (*models.Chapter, error)
	CreateChapters(chapters []models.Chapter) error
	UpdateChapter(chapterID uint, name string) (*models.Chapter, error)
	DeleteChapter(chapterID uint) error
	DeleteChaptersBySubjectID(subjectID uint) error
}

type ChapterServiceImpl struct {
	chapterRepo  repositories.ChapterRepository
	subjectRepo  repositories.SubjectRepository
	courseRepo   repositories.CourseRepository
	geminiHelper *utils.GeminiHelper
}

func NewChapterService(chapterRepo repositories.ChapterRepository, subjectRepo repositories.SubjectRepository, courseRepo repositories.CourseRepository) ChapterService {
	return &ChapterServiceImpl{
		chapterRepo:  chapterRepo,
		subjectRepo:  subjectRepo,
		courseRepo:   courseRepo,
		geminiHelper: utils.NewGeminiHelper(),
	}
}

// GenerateChapters generates chapters for a subject using Gemini AI
func (s *ChapterServiceImpl) GenerateChapters(courseID, subjectID uint) ([]models.Chapter, error) {
	logrus.Infof("Starting chapter generation for subject_id: %d, course_id: %d", subjectID, courseID)

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

	logrus.Debugf("Found subject: %s, course: %s", subject.Name, course.Name)

	// Check if chapters already exist
	existingChapters, err := s.chapterRepo.GetChaptersBySubjectID(subjectID)
	if err != nil {
		return nil, errors.New("failed to check existing chapters")
	}

	// If chapters exist, return them
	if len(existingChapters) > 0 {
		logrus.Infof("Chapters already exist for subject %s, returning existing chapters", subject.Name)
		return existingChapters, nil
	}

	// Generate chapters using Gemini
	ctx := context.Background()
	prompt := fmt.Sprintf(`Generate a comprehensive list of chapters for the subject '%s' under course '%s'.
	Consider the following:
	1. Include chapters from basic to advanced level
	2. Each chapter should be a distinct topic within the subject
	3. Chapters should follow a logical learning progression
	4. Generate maximum 8 chapters for the subject
	5. Keep chapter names concise and clear`, subject.Name, course.Name)

	chapterNames, err := s.geminiHelper.GenerateChapters(ctx, subject.Name, course.Name)
	if err != nil {
		logrus.Errorf("Error generating chapters with Gemini: %v", err)
		return nil, errors.New("failed to generate chapters")
	}

	logrus.Infof("Generated %d chapters for subject %s", len(chapterNames), subject.Name)

	// Create chapter models
	var chapters []models.Chapter
	for _, name := range chapterNames {
		chapters = append(chapters, models.Chapter{
			Name:      name,
			SubjectID: subjectID,
		})
	}

	// Save chapters
	if err := s.chapterRepo.CreateChapters(chapters); err != nil {
		logrus.Errorf("Error saving chapters: %v", err)
		return nil, errors.New("failed to save chapters")
	}

	logrus.Infof("Successfully created %d chapters for subject: %s", len(chapters), subject.Name)
	return chapters, nil
}

// GetChaptersBySubjectID returns all chapters for a subject
func (s *ChapterServiceImpl) GetChaptersBySubjectID(subjectID uint) ([]models.Chapter, error) {
	chapters, err := s.chapterRepo.GetChaptersBySubjectID(subjectID)
	if err != nil {
		logrus.Errorf("Error getting chapters by subject ID: %v", err)
		return nil, errors.New("failed to get chapters")
	}
	return chapters, nil
}

// GetChapterByID returns a specific chapter
func (s *ChapterServiceImpl) GetChapterByID(chapterID uint) (*models.Chapter, error) {
	chapter := &models.Chapter{}
	if err := s.chapterRepo.GetByID(chapterID, chapter); err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, errors.New("chapter not found")
		}
		logrus.Errorf("Error getting chapter: %v", err)
		return nil, errors.New("failed to get chapter")
	}
	return chapter, nil
}

// CreateChapters creates multiple chapters
func (s *ChapterServiceImpl) CreateChapters(chapters []models.Chapter) error {
	if err := s.chapterRepo.CreateChapters(chapters); err != nil {
		logrus.Errorf("Error creating chapters: %v", err)
		return errors.New("failed to create chapters")
	}
	return nil
}

// UpdateChapter updates a chapter's name
func (s *ChapterServiceImpl) UpdateChapter(chapterID uint, name string) (*models.Chapter, error) {
	chapter := &models.Chapter{}
	if err := s.chapterRepo.GetByID(chapterID, chapter); err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, errors.New("chapter not found")
		}
		return nil, errors.New("failed to get chapter")
	}

	chapter.Name = utils.SanitizeString(name)
	if err := s.chapterRepo.Update(chapter); err != nil {
		logrus.Errorf("Error updating chapter: %v", err)
		return nil, errors.New("failed to update chapter")
	}

	return chapter, nil
}

// DeleteChapter deletes a chapter
func (s *ChapterServiceImpl) DeleteChapter(chapterID uint) error {
	if err := s.chapterRepo.Delete(chapterID, &models.Chapter{}); err != nil {
		logrus.Errorf("Error deleting chapter: %v", err)
		return errors.New("failed to delete chapter")
	}
	return nil
}

// DeleteChaptersBySubjectID deletes all chapters for a subject
func (s *ChapterServiceImpl) DeleteChaptersBySubjectID(subjectID uint) error {
	if err := s.chapterRepo.DeleteChaptersBySubjectID(subjectID); err != nil {
		logrus.Errorf("Error deleting chapters by subject ID: %v", err)
		return errors.New("failed to delete chapters")
	}
	return nil
}