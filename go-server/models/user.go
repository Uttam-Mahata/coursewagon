package models

import (
	"time"

	"golang.org/x/crypto/bcrypt"
	"gorm.io/gorm"
)

type User struct {
	ID          uint           `json:"id" gorm:"primaryKey;autoIncrement"`
	Email       string         `json:"email" gorm:"uniqueIndex;not null;size:120" validate:"required,email"`
	PasswordHash string         `json:"-" gorm:"not null;size:255"`
	PasswordSalt string         `json:"-" gorm:"not null;size:255"`
	FirstName   *string        `json:"first_name" gorm:"size:50"`
	LastName    *string        `json:"last_name" gorm:"size:50"`
	CreatedAt   time.Time      `json:"created_at" gorm:"autoCreateTime"`
	UpdatedAt   time.Time      `json:"updated_at" gorm:"autoUpdateTime"`
	DeletedAt   gorm.DeletedAt `json:"-" gorm:"index"`
	IsActive    bool           `json:"is_active" gorm:"default:true"`
	IsAdmin     bool           `json:"is_admin" gorm:"default:false"`
	LastLogin   *time.Time     `json:"last_login"`

	// Relationships
	Courses []Course `json:"courses,omitempty" gorm:"foreignKey:UserID"`
}

// SetPassword hashes and sets the user's password
func (u *User) SetPassword(password string) error {
	// Generate salt
	salt, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return err
	}

	// Hash password with salt
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return err
	}

	u.PasswordSalt = string(salt)
	u.PasswordHash = string(hashedPassword)
	return nil
}

// CheckPassword compares provided password with stored hash
func (u *User) CheckPassword(password string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(u.PasswordHash), []byte(password))
	return err == nil
}

// ToDict converts user to map for JSON response (excluding sensitive data)
func (u *User) ToDict() map[string]interface{} {
	var firstName, lastName string
	if u.FirstName != nil {
		firstName = *u.FirstName
	}
	if u.LastName != nil {
		lastName = *u.LastName
	}

	return map[string]interface{}{
		"id":         u.ID,
		"email":      u.Email,
		"first_name": firstName,
		"last_name":  lastName,
		"created_at": u.CreatedAt.Format(time.RFC3339),
		"is_active":  u.IsActive,
		"is_admin":   u.IsAdmin,
	}
}

// TableName specifies the table name for GORM
func (User) TableName() string {
	return "user"
}