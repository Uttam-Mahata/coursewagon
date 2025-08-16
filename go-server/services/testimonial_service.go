package services

import (
	"errors"
	"go-server/models"
	"go-server/repositories"
	"go-server/utils"

	"github.com/sirupsen/logrus"
	"gorm.io/gorm"
)

type TestimonialService interface {
	CreateTestimonial(userID uint, req *models.TestimonialCreateRequest) (*models.Testimonial, error)
	GetUserTestimonials(userID uint) ([]models.Testimonial, error)
	GetApprovedTestimonials() ([]models.Testimonial, error)
	GetAllTestimonials() ([]models.Testimonial, error)
	UpdateTestimonial(testimonialID, userID uint, req *models.TestimonialUpdateRequest) (*models.Testimonial, error)
	DeleteTestimonial(testimonialID, userID uint) error
	ApproveTestimonial(testimonialID uint, isApproved bool) (*models.Testimonial, error)
	GetTestimonialByID(testimonialID uint) (*models.Testimonial, error)
}

type TestimonialServiceImpl struct {
	testimonialRepo repositories.TestimonialRepository
	userRepo        repositories.UserRepository
}

func NewTestimonialService(testimonialRepo repositories.TestimonialRepository, userRepo repositories.UserRepository) TestimonialService {
	return &TestimonialServiceImpl{
		testimonialRepo: testimonialRepo,
		userRepo:        userRepo,
	}
}

// CreateTestimonial creates a new testimonial
func (s *TestimonialServiceImpl) CreateTestimonial(userID uint, req *models.TestimonialCreateRequest) (*models.Testimonial, error) {
	// Validate request
	if err := utils.ValidateStruct(req); err != nil {
		return nil, errors.New("validation error: " + utils.FormatValidationErrors(err))
	}

	// Sanitize input
	req.Quote = utils.SanitizeString(req.Quote)

	// Verify user exists
	user := &models.User{}
	if err := s.userRepo.GetByID(userID, user); err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, errors.New("user not found")
		}
		return nil, errors.New("failed to verify user")
	}

	// Create testimonial
	testimonial := &models.Testimonial{
		UserID:     userID,
		Quote:      req.Quote,
		Rating:     req.Rating,
		IsApproved: false, // Requires admin approval
	}

	if err := s.testimonialRepo.Create(testimonial); err != nil {
		logrus.Errorf("Error creating testimonial: %v", err)
		return nil, errors.New("failed to create testimonial")
	}

	logrus.Infof("Testimonial created successfully for user: %d", userID)
	return testimonial, nil
}

// GetUserTestimonials returns all testimonials for a user
func (s *TestimonialServiceImpl) GetUserTestimonials(userID uint) ([]models.Testimonial, error) {
	testimonials, err := s.testimonialRepo.GetTestimonialsByUserID(userID)
	if err != nil {
		logrus.Errorf("Error getting user testimonials: %v", err)
		return nil, errors.New("failed to get testimonials")
	}
	return testimonials, nil
}

// GetApprovedTestimonials returns all approved testimonials
func (s *TestimonialServiceImpl) GetApprovedTestimonials() ([]models.Testimonial, error) {
	testimonials, err := s.testimonialRepo.GetApprovedTestimonials()
	if err != nil {
		logrus.Errorf("Error getting approved testimonials: %v", err)
		return nil, errors.New("failed to get approved testimonials")
	}
	return testimonials, nil
}

// GetAllTestimonials returns all testimonials (admin only)
func (s *TestimonialServiceImpl) GetAllTestimonials() ([]models.Testimonial, error) {
	testimonials, err := s.testimonialRepo.GetTestimonialsWithUser()
	if err != nil {
		logrus.Errorf("Error getting all testimonials: %v", err)
		return nil, errors.New("failed to get testimonials")
	}
	return testimonials, nil
}

// UpdateTestimonial updates a testimonial (user can only update their own)
func (s *TestimonialServiceImpl) UpdateTestimonial(testimonialID, userID uint, req *models.TestimonialUpdateRequest) (*models.Testimonial, error) {
	// Get existing testimonial
	testimonial := &models.Testimonial{}
	if err := s.testimonialRepo.GetByID(testimonialID, testimonial); err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, errors.New("testimonial not found")
		}
		return nil, errors.New("failed to get testimonial")
	}

	// Check ownership
	if testimonial.UserID != userID {
		return nil, errors.New("unauthorized to update this testimonial")
	}

	// Update fields
	if req.Quote != nil {
		testimonial.Quote = utils.SanitizeString(*req.Quote)
	}
	if req.Rating != nil {
		if *req.Rating < 1 || *req.Rating > 5 {
			return nil, errors.New("rating must be between 1 and 5")
		}
		testimonial.Rating = *req.Rating
	}
	if req.IsApproved != nil {
		// Only admin can update approval status, this should be handled in admin routes
		testimonial.IsApproved = *req.IsApproved
	}

	if err := s.testimonialRepo.Update(testimonial); err != nil {
		logrus.Errorf("Error updating testimonial: %v", err)
		return nil, errors.New("failed to update testimonial")
	}

	logrus.Infof("Testimonial updated successfully: %d", testimonialID)
	return testimonial, nil
}

// DeleteTestimonial deletes a testimonial (user can only delete their own)
func (s *TestimonialServiceImpl) DeleteTestimonial(testimonialID, userID uint) error {
	// Get existing testimonial
	testimonial := &models.Testimonial{}
	if err := s.testimonialRepo.GetByID(testimonialID, testimonial); err != nil {
		if err == gorm.ErrRecordNotFound {
			return errors.New("testimonial not found")
		}
		return errors.New("failed to get testimonial")
	}

	// Check ownership
	if testimonial.UserID != userID {
		return errors.New("unauthorized to delete this testimonial")
	}

	if err := s.testimonialRepo.Delete(testimonialID, &models.Testimonial{}); err != nil {
		logrus.Errorf("Error deleting testimonial: %v", err)
		return errors.New("failed to delete testimonial")
	}

	logrus.Infof("Testimonial deleted successfully: %d", testimonialID)
	return nil
}

// ApproveTestimonial approves or disapproves a testimonial (admin only)
func (s *TestimonialServiceImpl) ApproveTestimonial(testimonialID uint, isApproved bool) (*models.Testimonial, error) {
	if err := s.testimonialRepo.UpdateApprovalStatus(testimonialID, isApproved); err != nil {
		logrus.Errorf("Error updating testimonial approval: %v", err)
		return nil, errors.New("failed to update testimonial approval")
	}

	// Get updated testimonial
	testimonial, err := s.testimonialRepo.GetTestimonialWithUser(testimonialID)
	if err != nil {
		logrus.Errorf("Error getting updated testimonial: %v", err)
		return nil, errors.New("failed to get updated testimonial")
	}

	logrus.Infof("Testimonial approval updated: %d, approved: %v", testimonialID, isApproved)
	return testimonial, nil
}

// GetTestimonialByID returns a specific testimonial
func (s *TestimonialServiceImpl) GetTestimonialByID(testimonialID uint) (*models.Testimonial, error) {
	testimonial, err := s.testimonialRepo.GetTestimonialWithUser(testimonialID)
	if err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, errors.New("testimonial not found")
		}
		logrus.Errorf("Error getting testimonial: %v", err)
		return nil, errors.New("failed to get testimonial")
	}
	return testimonial, nil
}