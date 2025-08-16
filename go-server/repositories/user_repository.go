package repositories

import (
	"go-server/models"
	"time"

	"github.com/sirupsen/logrus"
	"gorm.io/gorm"
)

type UserRepository interface {
	BaseRepository
	GetByEmail(email string) (*models.User, error)
	CreateUser(user *models.User) error
	UpdateLastLogin(userID uint) error
	GetUserWithCourses(userID uint) (*models.User, error)
	UpdatePassword(userID uint, hashedPassword string) error
}

type UserRepositoryImpl struct {
	*BaseRepositoryImpl
}

func NewUserRepository(db *gorm.DB) UserRepository {
	return &UserRepositoryImpl{
		BaseRepositoryImpl: NewBaseRepository(db),
	}
}

// GetByEmail gets a user by email address
func (r *UserRepositoryImpl) GetByEmail(email string) (*models.User, error) {
	var user models.User
	err := r.DB.Where("email = ?", email).First(&user).Error
	if err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, nil
		}
		logrus.Errorf("Error getting user by email: %v", err)
		return nil, err
	}
	return &user, nil
}

// CreateUser creates a new user
func (r *UserRepositoryImpl) CreateUser(user *models.User) error {
	err := r.DB.Create(user).Error
	if err != nil {
		logrus.Errorf("Error creating user: %v", err)
	}
	return err
}

// UpdateLastLogin updates the last login time for a user
func (r *UserRepositoryImpl) UpdateLastLogin(userID uint) error {
	now := time.Now()
	err := r.DB.Model(&models.User{}).Where("id = ?", userID).Update("last_login", &now).Error
	if err != nil {
		logrus.Errorf("Error updating last login: %v", err)
	}
	return err
}

// GetUserWithCourses gets a user with their courses
func (r *UserRepositoryImpl) GetUserWithCourses(userID uint) (*models.User, error) {
	var user models.User
	err := r.DB.Preload("Courses").First(&user, userID).Error
	if err != nil {
		logrus.Errorf("Error getting user with courses: %v", err)
		return nil, err
	}
	return &user, nil
}

// UpdatePassword updates a user's password
func (r *UserRepositoryImpl) UpdatePassword(userID uint, hashedPassword string) error {
	err := r.DB.Model(&models.User{}).Where("id = ?", userID).Update("password_hash", hashedPassword).Error
	if err != nil {
		logrus.Errorf("Error updating password: %v", err)
	}
	return err
}