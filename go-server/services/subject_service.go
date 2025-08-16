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

type SubjectService interface {
	GenerateSubjects(courseID uint) ([]models.Subject, error)
	GetSubjectsByCourseID(courseID uint) ([]models.Subject, error)
	GetSubjectByID(subjectID uint) (*models.Subject, error)
	CreateSubjects(subjects []models.Subject) error
	UpdateSubject(subjectID uint, name string) (*models.Subject, error)
	DeleteSubject(subjectID uint) error
	DeleteSubjectsByCourseID(courseID uint) error
}

type SubjectServiceImpl struct {
	subjectRepo  repositories.SubjectRepository
	courseRepo   repositories.CourseRepository
	geminiHelper *utils.GeminiHelper
}

func NewSubjectService(subjectRepo repositories.SubjectRepository, courseRepo repositories.CourseRepository) SubjectService {
	return &SubjectServiceImpl{
		subjectRepo:  subjectRepo,
		courseRepo:   courseRepo,
		geminiHelper: utils.NewGeminiHelper(),
	}
}

// GenerateSubjects generates subjects for a course using Gemini AI
func (s *SubjectServiceImpl) GenerateSubjects(courseID uint) ([]models.Subject, error) {
	// Get course details
	course := &models.Course{}
	if err := s.courseRepo.GetByID(courseID, course); err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, errors.New("course not found")
		}
		return nil, errors.New("failed to get course")
	}

	// Check if subjects already exist
	existingSubjects, err := s.subjectRepo.GetSubjectsByCourseID(courseID)
	if err != nil {
		return nil, errors.New("failed to check existing subjects")
	}

	// If updating, clear existing subjects first
	if course.HasSubjects && len(existingSubjects) > 0 {
		if err := s.subjectRepo.DeleteSubjectsByCourseID(courseID); err != nil {
			logrus.Errorf("Error deleting existing subjects: %v", err)
		}
	}

	// Generate subjects using Gemini
	ctx := context.Background()
	prompt := fmt.Sprintf(`Based on the course '%s' with description '%s', 
	generate a list of relevant subjects that should be included in this course.
	Consider the following:
	1. If it's a school/college/university course, align with their typical curriculum
	2. Don't include the course name as a subject
	3. Keep subjects relevant and practical
	4. Generate maximum 5 core subjects for the course`, course.Name, course.Description)

	subjectNames, err := s.geminiHelper.GenerateSubjects(ctx, course.Name, course.Description)
	if err != nil {
		logrus.Errorf("Error generating subjects with Gemini: %v", err)
		return nil, errors.New("failed to generate subjects")
	}

	// Create subject models
	var subjects []models.Subject
	for _, name := range subjectNames {
		subjects = append(subjects, models.Subject{
			Name:     name,
			CourseID: courseID,
		})
	}

	// Save subjects
	if err := s.subjectRepo.CreateSubjects(subjects); err != nil {
		logrus.Errorf("Error saving subjects: %v", err)
		return nil, errors.New("failed to save subjects")
	}

	// Update course has_subjects flag
	if err := s.courseRepo.UpdateHasSubjects(courseID, true); err != nil {
		logrus.Errorf("Error updating has_subjects flag: %v", err)
		// Don't fail the operation for this
	}

	logrus.Infof("Generated %d subjects for course: %s", len(subjects), course.Name)
	return subjects, nil
}

// GetSubjectsByCourseID returns all subjects for a course
func (s *SubjectServiceImpl) GetSubjectsByCourseID(courseID uint) ([]models.Subject, error) {
	subjects, err := s.subjectRepo.GetSubjectsByCourseID(courseID)
	if err != nil {
		logrus.Errorf("Error getting subjects by course ID: %v", err)
		return nil, errors.New("failed to get subjects")
	}
	return subjects, nil
}

// GetSubjectByID returns a specific subject
func (s *SubjectServiceImpl) GetSubjectByID(subjectID uint) (*models.Subject, error) {
	subject := &models.Subject{}
	if err := s.subjectRepo.GetByID(subjectID, subject); err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, errors.New("subject not found")
		}
		logrus.Errorf("Error getting subject: %v", err)
		return nil, errors.New("failed to get subject")
	}
	return subject, nil
}

// CreateSubjects creates multiple subjects
func (s *SubjectServiceImpl) CreateSubjects(subjects []models.Subject) error {
	if err := s.subjectRepo.CreateSubjects(subjects); err != nil {
		logrus.Errorf("Error creating subjects: %v", err)
		return errors.New("failed to create subjects")
	}
	return nil
}

// UpdateSubject updates a subject's name
func (s *SubjectServiceImpl) UpdateSubject(subjectID uint, name string) (*models.Subject, error) {
	subject := &models.Subject{}
	if err := s.subjectRepo.GetByID(subjectID, subject); err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, errors.New("subject not found")
		}
		return nil, errors.New("failed to get subject")
	}

	subject.Name = utils.SanitizeString(name)
	if err := s.subjectRepo.Update(subject); err != nil {
		logrus.Errorf("Error updating subject: %v", err)
		return nil, errors.New("failed to update subject")
	}

	return subject, nil
}

// DeleteSubject deletes a subject
func (s *SubjectServiceImpl) DeleteSubject(subjectID uint) error {
	if err := s.subjectRepo.Delete(subjectID, &models.Subject{}); err != nil {
		logrus.Errorf("Error deleting subject: %v", err)
		return errors.New("failed to delete subject")
	}
	return nil
}

// DeleteSubjectsByCourseID deletes all subjects for a course
func (s *SubjectServiceImpl) DeleteSubjectsByCourseID(courseID uint) error {
	if err := s.subjectRepo.DeleteSubjectsByCourseID(courseID); err != nil {
		logrus.Errorf("Error deleting subjects by course ID: %v", err)
		return errors.New("failed to delete subjects")
	}
	return nil
}