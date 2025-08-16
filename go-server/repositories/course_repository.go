package repositories

import (
	"go-server/models"

	"github.com/sirupsen/logrus"
	"gorm.io/gorm"
)

type CourseRepository interface {
	BaseRepository
	GetUserCourses(userID uint) ([]models.Course, error)
	GetCourseWithSubjects(courseID uint) (*models.Course, error)
	UpdateHasSubjects(courseID uint, hasSubjects bool) error
	SearchCourses(query string, limit int) ([]models.Course, error)
}

type CourseRepositoryImpl struct {
	*BaseRepositoryImpl
}

func NewCourseRepository(db *gorm.DB) CourseRepository {
	return &CourseRepositoryImpl{
		BaseRepositoryImpl: NewBaseRepository(db),
	}
}

// GetUserCourses gets all courses for a specific user
func (r *CourseRepositoryImpl) GetUserCourses(userID uint) ([]models.Course, error) {
	var courses []models.Course
	err := r.DB.Where("user_id = ?", userID).Find(&courses).Error
	if err != nil {
		logrus.Errorf("Error getting user courses: %v", err)
		return nil, err
	}
	return courses, nil
}

// GetCourseWithSubjects gets a course with its subjects
func (r *CourseRepositoryImpl) GetCourseWithSubjects(courseID uint) (*models.Course, error) {
	var course models.Course
	err := r.DB.Preload("Subjects").First(&course, courseID).Error
	if err != nil {
		logrus.Errorf("Error getting course with subjects: %v", err)
		return nil, err
	}
	return &course, nil
}

// UpdateHasSubjects updates the has_subjects flag for a course
func (r *CourseRepositoryImpl) UpdateHasSubjects(courseID uint, hasSubjects bool) error {
	err := r.DB.Model(&models.Course{}).Where("id = ?", courseID).Update("has_subjects", hasSubjects).Error
	if err != nil {
		logrus.Errorf("Error updating has_subjects flag: %v", err)
	}
	return err
}

// SearchCourses searches courses by name or description
func (r *CourseRepositoryImpl) SearchCourses(query string, limit int) ([]models.Course, error) {
	var courses []models.Course
	searchPattern := "%" + query + "%"
	err := r.DB.Where("name LIKE ? OR description LIKE ?", searchPattern, searchPattern).
		Limit(limit).Find(&courses).Error
	if err != nil {
		logrus.Errorf("Error searching courses: %v", err)
		return nil, err
	}
	return courses, nil
}