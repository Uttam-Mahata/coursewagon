package repositories

import (
	"gorm.io/gorm"
)

// BaseRepository defines common database operations
type BaseRepository interface {
	Create(entity interface{}) error
	GetByID(id uint, entity interface{}) error
	Update(entity interface{}) error
	Delete(id uint, entity interface{}) error
	GetAll(entities interface{}) error
	Count(entity interface{}) (int64, error)
}

// BaseRepositoryImpl implements BaseRepository
type BaseRepositoryImpl struct {
	DB *gorm.DB
}

// NewBaseRepository creates a new base repository
func NewBaseRepository(db *gorm.DB) *BaseRepositoryImpl {
	return &BaseRepositoryImpl{DB: db}
}

// Create creates a new entity
func (r *BaseRepositoryImpl) Create(entity interface{}) error {
	return r.DB.Create(entity).Error
}

// GetByID gets an entity by ID
func (r *BaseRepositoryImpl) GetByID(id uint, entity interface{}) error {
	return r.DB.First(entity, id).Error
}

// Update updates an entity
func (r *BaseRepositoryImpl) Update(entity interface{}) error {
	return r.DB.Save(entity).Error
}

// Delete soft deletes an entity
func (r *BaseRepositoryImpl) Delete(id uint, entity interface{}) error {
	return r.DB.Delete(entity, id).Error
}

// GetAll gets all entities
func (r *BaseRepositoryImpl) GetAll(entities interface{}) error {
	return r.DB.Find(entities).Error
}

// Count counts entities
func (r *BaseRepositoryImpl) Count(entity interface{}) (int64, error) {
	var count int64
	err := r.DB.Model(entity).Count(&count).Error
	return count, err
}

// GetWithPagination gets entities with pagination
func (r *BaseRepositoryImpl) GetWithPagination(entities interface{}, page, limit int) error {
	offset := (page - 1) * limit
	return r.DB.Offset(offset).Limit(limit).Find(entities).Error
}