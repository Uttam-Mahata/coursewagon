package repositories

import (
	"go-server/models"

	"github.com/sirupsen/logrus"
	"gorm.io/gorm"
)

type SubjectRepository interface {
	BaseRepository
	GetSubjectsByCourseID(courseID uint) ([]models.Subject, error)
	GetSubjectWithChapters(subjectID uint) (*models.Subject, error)
	CreateSubjects(subjects []models.Subject) error
	DeleteSubjectsByCourseID(courseID uint) error
}

type SubjectRepositoryImpl struct {
	*BaseRepositoryImpl
}

func NewSubjectRepository(db *gorm.DB) SubjectRepository {
	return &SubjectRepositoryImpl{
		BaseRepositoryImpl: NewBaseRepository(db),
	}
}

// GetSubjectsByCourseID gets all subjects for a specific course
func (r *SubjectRepositoryImpl) GetSubjectsByCourseID(courseID uint) ([]models.Subject, error) {
	var subjects []models.Subject
	err := r.DB.Where("course_id = ?", courseID).Find(&subjects).Error
	if err != nil {
		logrus.Errorf("Error getting subjects by course ID: %v", err)
		return nil, err
	}
	return subjects, nil
}

// GetSubjectWithChapters gets a subject with its chapters
func (r *SubjectRepositoryImpl) GetSubjectWithChapters(subjectID uint) (*models.Subject, error) {
	var subject models.Subject
	err := r.DB.Preload("Chapters").First(&subject, subjectID).Error
	if err != nil {
		logrus.Errorf("Error getting subject with chapters: %v", err)
		return nil, err
	}
	return &subject, nil
}

// CreateSubjects creates multiple subjects
func (r *SubjectRepositoryImpl) CreateSubjects(subjects []models.Subject) error {
	err := r.DB.CreateInBatches(&subjects, 100).Error
	if err != nil {
		logrus.Errorf("Error creating subjects: %v", err)
	}
	return err
}

// DeleteSubjectsByCourseID deletes all subjects for a course
func (r *SubjectRepositoryImpl) DeleteSubjectsByCourseID(courseID uint) error {
	err := r.DB.Where("course_id = ?", courseID).Delete(&models.Subject{}).Error
	if err != nil {
		logrus.Errorf("Error deleting subjects by course ID: %v", err)
	}
	return err
}