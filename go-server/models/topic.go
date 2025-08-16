package models

import (
	"time"

	"gorm.io/gorm"
)

type Topic struct {
	ID        uint           `json:"id" gorm:"primaryKey;autoIncrement"`
	Name      string         `json:"name" gorm:"not null;size:255" validate:"required"`
	ChapterID uint           `json:"chapter_id" gorm:"not null;index" validate:"required"`
	CreatedAt time.Time      `json:"created_at" gorm:"autoCreateTime"`
	UpdatedAt time.Time      `json:"updated_at" gorm:"autoUpdateTime"`
	DeletedAt gorm.DeletedAt `json:"-" gorm:"index"`

	// Relationships
	Chapter  Chapter   `json:"chapter,omitempty" gorm:"foreignKey:ChapterID"`
	Contents []Content `json:"contents,omitempty" gorm:"foreignKey:TopicID"`
}

// ToDict converts topic to map for JSON response
func (t *Topic) ToDict() map[string]interface{} {
	return map[string]interface{}{
		"id":         t.ID,
		"name":       t.Name,
		"chapter_id": t.ChapterID,
		"created_at": t.CreatedAt.Format(time.RFC3339),
	}
}

// TableName specifies the table name for GORM
func (Topic) TableName() string {
	return "topics"
}