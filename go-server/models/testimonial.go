package models

import (
	"time"

	"gorm.io/gorm"
)

type Testimonial struct {
	ID         uint           `json:"id" gorm:"primaryKey;autoIncrement"`
	UserID     uint           `json:"user_id" gorm:"not null;index;constraint:OnDelete:CASCADE" validate:"required"`
	Quote      string         `json:"quote" gorm:"not null;type:text" validate:"required"`
	Rating     int            `json:"rating" gorm:"not null" validate:"required,min=1,max=5"`
	IsApproved bool           `json:"is_approved" gorm:"default:false"`
	CreatedAt  time.Time      `json:"created_at" gorm:"autoCreateTime"`
	UpdatedAt  time.Time      `json:"updated_at" gorm:"autoUpdateTime"`
	DeletedAt  gorm.DeletedAt `json:"-" gorm:"index"`

	// Relationships
	User User `json:"user,omitempty" gorm:"foreignKey:UserID"`
}

// ToDict converts testimonial to map for JSON response
func (t *Testimonial) ToDict() map[string]interface{} {
	author := ""
	if t.User.FirstName != nil && t.User.LastName != nil {
		author = *t.User.FirstName + " " + *t.User.LastName
	} else {
		author = t.User.Email
	}

	return map[string]interface{}{
		"id":          t.ID,
		"user_id":     t.UserID,
		"author":      author,
		"quote":       t.Quote,
		"rating":      t.Rating,
		"is_approved": t.IsApproved,
		"created_at":  t.CreatedAt.Format(time.RFC3339),
		"updated_at":  t.UpdatedAt.Format(time.RFC3339),
	}
}

// TableName specifies the table name for GORM
func (Testimonial) TableName() string {
	return "testimonials"
}