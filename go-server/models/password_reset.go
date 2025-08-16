package models

import (
	"time"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

type PasswordReset struct {
	ID        uint           `json:"id" gorm:"primaryKey;autoIncrement"`
	UserID    uint           `json:"user_id" gorm:"not null;index" validate:"required"`
	Token     string         `json:"token" gorm:"uniqueIndex;not null;size:255"`
	CreatedAt time.Time      `json:"created_at" gorm:"autoCreateTime"`
	ExpiresAt time.Time      `json:"expires_at" gorm:"not null"`
	Used      bool           `json:"used" gorm:"default:false"`
	DeletedAt gorm.DeletedAt `json:"-" gorm:"index"`

	// Relationships
	User User `json:"user,omitempty" gorm:"foreignKey:UserID"`
}

// GenerateToken generates a unique token for password reset
func GenerateToken() string {
	return uuid.New().String()
}

// CreateForUser creates a new password reset token for a user
func CreateForUser(db *gorm.DB, userID uint, expiresInHours int) (*PasswordReset, error) {
	token := GenerateToken()
	reset := &PasswordReset{
		UserID:    userID,
		Token:     token,
		ExpiresAt: time.Now().Add(time.Duration(expiresInHours) * time.Hour),
	}

	if err := db.Create(reset).Error; err != nil {
		return nil, err
	}

	return reset, nil
}

// IsExpired checks if the token has expired
func (pr *PasswordReset) IsExpired() bool {
	return time.Now().After(pr.ExpiresAt)
}

// IsValid checks if the token is valid (not expired and not used)
func (pr *PasswordReset) IsValid() bool {
	return !pr.Used && !pr.IsExpired()
}

// UseToken marks the token as used
func (pr *PasswordReset) UseToken(db *gorm.DB) error {
	pr.Used = true
	return db.Save(pr).Error
}

// TableName specifies the table name for GORM
func (PasswordReset) TableName() string {
	return "password_reset"
}