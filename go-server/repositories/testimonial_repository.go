package repositories

import (
	"go-server/models"

	"github.com/sirupsen/logrus"
	"gorm.io/gorm"
)

type TestimonialRepository interface {
	BaseRepository
	GetApprovedTestimonials() ([]models.Testimonial, error)
	GetTestimonialsByUserID(userID uint) ([]models.Testimonial, error)
	GetTestimonialsWithUser() ([]models.Testimonial, error)
	UpdateApprovalStatus(testimonialID uint, isApproved bool) error
	GetTestimonialWithUser(testimonialID uint) (*models.Testimonial, error)
}

type TestimonialRepositoryImpl struct {
	*BaseRepositoryImpl
}

func NewTestimonialRepository(db *gorm.DB) TestimonialRepository {
	return &TestimonialRepositoryImpl{
		BaseRepositoryImpl: NewBaseRepository(db),
	}
}

// GetApprovedTestimonials gets all approved testimonials
func (r *TestimonialRepositoryImpl) GetApprovedTestimonials() ([]models.Testimonial, error) {
	var testimonials []models.Testimonial
	err := r.DB.Preload("User").Where("is_approved = ?", true).Find(&testimonials).Error
	if err != nil {
		logrus.Errorf("Error getting approved testimonials: %v", err)
		return nil, err
	}
	return testimonials, nil
}

// GetTestimonialsByUserID gets all testimonials for a specific user
func (r *TestimonialRepositoryImpl) GetTestimonialsByUserID(userID uint) ([]models.Testimonial, error) {
	var testimonials []models.Testimonial
	err := r.DB.Where("user_id = ?", userID).Find(&testimonials).Error
	if err != nil {
		logrus.Errorf("Error getting testimonials by user ID: %v", err)
		return nil, err
	}
	return testimonials, nil
}

// GetTestimonialsWithUser gets all testimonials with user information
func (r *TestimonialRepositoryImpl) GetTestimonialsWithUser() ([]models.Testimonial, error) {
	var testimonials []models.Testimonial
	err := r.DB.Preload("User").Find(&testimonials).Error
	if err != nil {
		logrus.Errorf("Error getting testimonials with user: %v", err)
		return nil, err
	}
	return testimonials, nil
}

// UpdateApprovalStatus updates the approval status of a testimonial
func (r *TestimonialRepositoryImpl) UpdateApprovalStatus(testimonialID uint, isApproved bool) error {
	err := r.DB.Model(&models.Testimonial{}).Where("id = ?", testimonialID).Update("is_approved", isApproved).Error
	if err != nil {
		logrus.Errorf("Error updating approval status: %v", err)
	}
	return err
}

// GetTestimonialWithUser gets a specific testimonial with user information
func (r *TestimonialRepositoryImpl) GetTestimonialWithUser(testimonialID uint) (*models.Testimonial, error) {
	var testimonial models.Testimonial
	err := r.DB.Preload("User").First(&testimonial, testimonialID).Error
	if err != nil {
		logrus.Errorf("Error getting testimonial with user: %v", err)
		return nil, err
	}
	return &testimonial, nil
}