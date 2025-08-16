package repositories

import (
	"go-server/models"

	"github.com/sirupsen/logrus"
	"gorm.io/gorm"
)

type ChapterRepository interface {
	BaseRepository
	GetChaptersBySubjectID(subjectID uint) ([]models.Chapter, error)
	GetChapterWithTopics(chapterID uint) (*models.Chapter, error)
	CreateChapters(chapters []models.Chapter) error
	DeleteChaptersBySubjectID(subjectID uint) error
}

type ChapterRepositoryImpl struct {
	*BaseRepositoryImpl
}

func NewChapterRepository(db *gorm.DB) ChapterRepository {
	return &ChapterRepositoryImpl{
		BaseRepositoryImpl: NewBaseRepository(db),
	}
}

// GetChaptersBySubjectID gets all chapters for a specific subject
func (r *ChapterRepositoryImpl) GetChaptersBySubjectID(subjectID uint) ([]models.Chapter, error) {
	var chapters []models.Chapter
	err := r.DB.Where("subject_id = ?", subjectID).Find(&chapters).Error
	if err != nil {
		logrus.Errorf("Error getting chapters by subject ID: %v", err)
		return nil, err
	}
	return chapters, nil
}

// GetChapterWithTopics gets a chapter with its topics
func (r *ChapterRepositoryImpl) GetChapterWithTopics(chapterID uint) (*models.Chapter, error) {
	var chapter models.Chapter
	err := r.DB.Preload("Topics").First(&chapter, chapterID).Error
	if err != nil {
		logrus.Errorf("Error getting chapter with topics: %v", err)
		return nil, err
	}
	return &chapter, nil
}

// CreateChapters creates multiple chapters
func (r *ChapterRepositoryImpl) CreateChapters(chapters []models.Chapter) error {
	err := r.DB.CreateInBatches(&chapters, 100).Error
	if err != nil {
		logrus.Errorf("Error creating chapters: %v", err)
	}
	return err
}

// DeleteChaptersBySubjectID deletes all chapters for a subject
func (r *ChapterRepositoryImpl) DeleteChaptersBySubjectID(subjectID uint) error {
	err := r.DB.Where("subject_id = ?", subjectID).Delete(&models.Chapter{}).Error
	if err != nil {
		logrus.Errorf("Error deleting chapters by subject ID: %v", err)
	}
	return err
}