package models

import (
	"time"

	"gorm.io/gorm"
)

type Subject struct {
	ID        uint           `json:"id" gorm:"primaryKey;autoIncrement"`
	Name      string         `json:"name" gorm:"not null;size:255" validate:"required"`
	CourseID  uint           `json:"course_id" gorm:"not null;index" validate:"required"`
	CreatedAt time.Time      `json:"created_at" gorm:"autoCreateTime"`
	UpdatedAt time.Time      `json:"updated_at" gorm:"autoUpdateTime"`
	DeletedAt gorm.DeletedAt `json:"-" gorm:"index"`

	// Relationships
	Course   Course    `json:"course,omitempty" gorm:"foreignKey:CourseID"`
	Chapters []Chapter `json:"chapters,omitempty" gorm:"foreignKey:SubjectID"`
}

// ToDict converts subject to map for JSON response
func (s *Subject) ToDict() map[string]interface{} {
	return map[string]interface{}{
		"id":         s.ID,
		"name":       s.Name,
		"course_id":  s.CourseID,
		"created_at": s.CreatedAt.Format(time.RFC3339),
	}
}

// TableName specifies the table name for GORM
func (Subject) TableName() string {
	return "subjects"
}