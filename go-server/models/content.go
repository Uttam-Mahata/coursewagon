package models

import (
	"time"

	"gorm.io/gorm"
)

type Content struct {
	ID        uint           `json:"id" gorm:"primaryKey;autoIncrement"`
	TopicID   uint           `json:"topic_id" gorm:"not null;index;constraint:OnDelete:CASCADE" validate:"required"`
	Content   string         `json:"content" gorm:"not null;type:text" validate:"required"`
	CreatedAt time.Time      `json:"created_at" gorm:"autoCreateTime"`
	UpdatedAt time.Time      `json:"updated_at" gorm:"autoUpdateTime"`
	DeletedAt gorm.DeletedAt `json:"-" gorm:"index"`

	// Relationships
	Topic Topic `json:"topic,omitempty" gorm:"foreignKey:TopicID"`
}

// ToDict converts content to map for JSON response
func (c *Content) ToDict() map[string]interface{} {
	return map[string]interface{}{
		"id":       c.ID,
		"topic_id": c.TopicID,
		"content":  c.Content,
	}
}

// TableName specifies the table name for GORM
func (Content) TableName() string {
	return "content"
}