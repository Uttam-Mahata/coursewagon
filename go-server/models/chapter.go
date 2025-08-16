package models

import (
	"time"

	"gorm.io/gorm"
)

type Chapter struct {
	ID        uint           `json:"id" gorm:"primaryKey;autoIncrement"`
	Name      string         `json:"name" gorm:"not null;size:255" validate:"required"`
	SubjectID uint           `json:"subject_id" gorm:"not null;index" validate:"required"`
	CreatedAt time.Time      `json:"created_at" gorm:"autoCreateTime"`
	UpdatedAt time.Time      `json:"updated_at" gorm:"autoUpdateTime"`
	DeletedAt gorm.DeletedAt `json:"-" gorm:"index"`

	// Relationships
	Subject Subject `json:"subject,omitempty" gorm:"foreignKey:SubjectID"`
	Topics  []Topic `json:"topics,omitempty" gorm:"foreignKey:ChapterID"`
}

// ToDict converts chapter to map for JSON response
func (c *Chapter) ToDict() map[string]interface{} {
	return map[string]interface{}{
		"id":         c.ID,
		"name":       c.Name,
		"subject_id": c.SubjectID,
		"created_at": c.CreatedAt.Format(time.RFC3339),
	}
}

// TableName specifies the table name for GORM
func (Chapter) TableName() string {
	return "chapters"
}