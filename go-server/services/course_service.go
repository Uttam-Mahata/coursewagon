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

type CourseService interface {
	CreateCourse(userID uint, req *models.CourseCreateRequest) (*models.Course, error)
	GetUserCourses(userID uint) ([]models.Course, error)
	GetCourseByID(courseID, userID uint) (*models.Course, error)
	UpdateCourse(courseID, userID uint, req *models.CourseUpdateRequest) (*models.Course, error)
	DeleteCourse(courseID, userID uint) error
	GenerateSubjects(courseID, userID uint) ([]models.Subject, error)
	SearchCourses(query string, limit int) ([]models.Course, error)
}

type CourseServiceImpl struct {
	courseRepo  repositories.CourseRepository
	subjectRepo repositories.SubjectRepository
	geminiHelper *utils.GeminiHelper
}

func NewCourseService(courseRepo repositories.CourseRepository, subjectRepo repositories.SubjectRepository) CourseService {
	return &CourseServiceImpl{
		courseRepo:   courseRepo,
		subjectRepo:  subjectRepo,
		geminiHelper: utils.NewGeminiHelper(),
	}
}

// CreateCourse creates a new course
func (s *CourseServiceImpl) CreateCourse(userID uint, req *models.CourseCreateRequest) (*models.Course, error) {
	// Validate request
	if err := utils.ValidateStruct(req); err != nil {
		return nil, fmt.Errorf("validation error: %s", utils.FormatValidationErrors(err))
	}

	// Sanitize input
	req.Name = utils.SanitizeString(req.Name)
	req.Description = utils.SanitizeString(req.Description)

	// Create course
	course := &models.Course{
		Name:        req.Name,
		Description: req.Description,
		UserID:      &userID,
		HasSubjects: false,
	}

	if err := s.courseRepo.Create(course); err != nil {
		logrus.Errorf("Error creating course: %v", err)
		return nil, errors.New("failed to create course")
	}

	logrus.Infof("Course created successfully: %s", course.Name)
	return course, nil
}

// GetUserCourses returns all courses for a user
func (s *CourseServiceImpl) GetUserCourses(userID uint) ([]models.Course, error) {
	courses, err := s.courseRepo.GetUserCourses(userID)
	if err != nil {
		logrus.Errorf("Error getting user courses: %v", err)
		return nil, errors.New("failed to get courses")
	}

	return courses, nil
}

// GetCourseByID returns a specific course if user owns it
func (s *CourseServiceImpl) GetCourseByID(courseID, userID uint) (*models.Course, error) {
	course := &models.Course{}
	if err := s.courseRepo.GetByID(courseID, course); err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, errors.New("course not found")
		}
		logrus.Errorf("Error getting course: %v", err)
		return nil, errors.New("failed to get course")
	}

	// Check ownership
	if course.UserID == nil || *course.UserID != userID {
		return nil, errors.New("unauthorized access to course")
	}

	return course, nil
}

// UpdateCourse updates a course
func (s *CourseServiceImpl) UpdateCourse(courseID, userID uint, req *models.CourseUpdateRequest) (*models.Course, error) {
	// Get existing course
	course, err := s.GetCourseByID(courseID, userID)
	if err != nil {
		return nil, err
	}

	// Update fields
	if req.Name != nil {
		course.Name = utils.SanitizeString(*req.Name)
	}
	if req.Description != nil {
		course.Description = utils.SanitizeString(*req.Description)
	}
	if req.ImageURL != nil {
		course.ImageURL = req.ImageURL
	}

	if err := s.courseRepo.Update(course); err != nil {
		logrus.Errorf("Error updating course: %v", err)
		return nil, errors.New("failed to update course")
	}

	logrus.Infof("Course updated successfully: %s", course.Name)
	return course, nil
}

// DeleteCourse deletes a course
func (s *CourseServiceImpl) DeleteCourse(courseID, userID uint) error {
	// Verify ownership
	_, err := s.GetCourseByID(courseID, userID)
	if err != nil {
		return err
	}

	// Delete associated subjects first
	if err := s.subjectRepo.DeleteSubjectsByCourseID(courseID); err != nil {
		logrus.Errorf("Error deleting subjects: %v", err)
		return errors.New("failed to delete course subjects")
	}

	// Delete course
	if err := s.courseRepo.Delete(courseID, &models.Course{}); err != nil {
		logrus.Errorf("Error deleting course: %v", err)
		return errors.New("failed to delete course")
	}

	logrus.Infof("Course deleted successfully: %d", courseID)
	return nil
}

// GenerateSubjects generates subjects for a course using Gemini AI
func (s *CourseServiceImpl) GenerateSubjects(courseID, userID uint) ([]models.Subject, error) {
	// Get course
	course, err := s.GetCourseByID(courseID, userID)
	if err != nil {
		return nil, err
	}

	// Check if subjects already exist
	existingSubjects, err := s.subjectRepo.GetSubjectsByCourseID(courseID)
	if err != nil {
		logrus.Errorf("Error checking existing subjects: %v", err)
		return nil, errors.New("failed to check existing subjects")
	}

	if len(existingSubjects) > 0 {
		return existingSubjects, nil
	}

	// Generate subjects using Gemini
	ctx := context.Background()
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

// SearchCourses searches for courses
func (s *CourseServiceImpl) SearchCourses(query string, limit int) ([]models.Course, error) {
	if query == "" {
		return []models.Course{}, nil
	}

	query = utils.SanitizeString(query)
	courses, err := s.courseRepo.SearchCourses(query, limit)
	if err != nil {
		logrus.Errorf("Error searching courses: %v", err)
		return nil, errors.New("failed to search courses")
	}

	return courses, nil
}