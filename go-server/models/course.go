package models

import (
	"time"

	"gorm.io/gorm"
)

type Course struct {
	ID          uint           `json:"id" gorm:"primaryKey;autoIncrement"`
	Name        string         `json:"name" gorm:"not null;size:255" validate:"required"`
	Description string         `json:"description" gorm:"not null;type:text" validate:"required"`
	UserID      *uint          `json:"user_id" gorm:"index"`
	CreatedAt   time.Time      `json:"created_at" gorm:"autoCreateTime"`
	UpdatedAt   time.Time      `json:"updated_at" gorm:"autoUpdateTime"`
	DeletedAt   gorm.DeletedAt `json:"-" gorm:"index"`
	HasSubjects bool           `json:"has_subjects" gorm:"default:false"`
	ImageURL    *string        `json:"image_url" gorm:"size:512"`

	// Relationships
	User     *User     `json:"user,omitempty" gorm:"foreignKey:UserID"`
	Subjects []Subject `json:"subjects,omitempty" gorm:"foreignKey:CourseID"`
}

// ToDict converts course to map for JSON response
func (c *Course) ToDict() map[string]interface{} {
	var imageURL string
	if c.ImageURL != nil {
		imageURL = *c.ImageURL
	}

	return map[string]interface{}{
		"id":           c.ID,
		"name":         c.Name,
		"description":  c.Description,
		"user_id":      c.UserID,
		"created_at":   c.CreatedAt.Format(time.RFC3339),
		"has_subjects": c.HasSubjects,
		"image_url":    imageURL,
	}
}

// TableName specifies the table name for GORM
func (Course) TableName() string {
	return "courses"
}