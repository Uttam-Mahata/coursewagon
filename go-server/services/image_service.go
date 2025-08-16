package services

import (
	"context"
	"errors"
	"fmt"
	"go-server/models"
	"go-server/repositories"
	"go-server/utils"
	"os"
	"path/filepath"

	"github.com/sirupsen/logrus"
	"gorm.io/gorm"
)

type ImageService interface {
	GenerateCourseImage(courseID uint) (string, error)
	GenerateSubjectImage(subjectID uint) (string, error) 
	GenerateCustomImage(prompt string) (string, error)
	UploadImage(imageData []byte, imagePath string) (string, error)
	DeleteImage(imagePath string) error
	ListImages(pathPrefix string) ([]string, error)
}

type ImageServiceImpl struct {
	courseRepo      repositories.CourseRepository
	subjectRepo     repositories.SubjectRepository
	azureStorage    *utils.AzureStorageHelper
	imageGenerator  *utils.GeminiImageGenerator
}

func NewImageService(courseRepo repositories.CourseRepository, subjectRepo repositories.SubjectRepository) ImageService {
	return &ImageServiceImpl{
		courseRepo:     courseRepo,
		subjectRepo:    subjectRepo,
		azureStorage:   utils.GetAzureStorageHelper(),
		imageGenerator: utils.NewGeminiImageGenerator(),
	}
}

// GenerateCourseImage generates and stores a cover image for a course
func (s *ImageServiceImpl) GenerateCourseImage(courseID uint) (string, error) {
	// Get course details
	course := &models.Course{}
	if err := s.courseRepo.GetByID(courseID, course); err != nil {
		if err == gorm.ErrRecordNotFound {
			return "", errors.New("course not found")
		}
		return "", fmt.Errorf("failed to get course: %w", err)
	}

	// Check if image generator is available
	if !s.imageGenerator.IsAvailable() {
		return "", errors.New("image generation not available - no API key configured")
	}

	// Check if Azure storage is available
	if !s.azureStorage.IsInitialized() {
		return "", errors.New("Azure storage not initialized - check configuration")
	}

	// Generate the image
	ctx := context.Background()
	logrus.Infof("Generating image for course '%s' (ID: %d)", course.Name, courseID)
	
	imageBytes, err := s.imageGenerator.GenerateCourseImage(ctx, course.Name, course.Description)
	if err != nil {
		return "", fmt.Errorf("failed to generate image: %w", err)
	}

	if len(imageBytes) == 0 {
		return "", errors.New("failed to generate image - no data received")
	}

	logrus.Infof("Image generated successfully, size: %d bytes", len(imageBytes))

	// Save a local debug copy if in debug mode
	if os.Getenv("DEBUG") == "true" {
		debugPath := fmt.Sprintf("/tmp/course_%d_image_debug.png", courseID)
		if err := os.WriteFile(debugPath, imageBytes, 0644); err != nil {
			logrus.Warnf("Could not save debug image: %v", err)
		} else {
			logrus.Infof("Debug image saved to %s", debugPath)
		}
	}

	// Upload the image to Azure Storage
	imagePath := fmt.Sprintf("courses/%d/cover", courseID)
	logrus.Infof("Uploading image to Azure Storage path: %s", imagePath)
	
	imageURL, err := s.azureStorage.UploadImage(imageBytes, imagePath)
	if err != nil {
		return "", fmt.Errorf("failed to upload image to Azure Storage: %w", err)
	}

	logrus.Infof("Image uploaded successfully, URL: %s", imageURL)

	// Update the course with the image URL
	course.ImageURL = &imageURL
	if err := s.courseRepo.Update(course); err != nil {
		logrus.Errorf("Failed to update course with image URL: %v", err)
		// Don't fail the operation, just log the error
	}

	return imageURL, nil
}

// GenerateSubjectImage generates and stores a cover image for a subject
func (s *ImageServiceImpl) GenerateSubjectImage(subjectID uint) (string, error) {
	// Get subject details
	subject := &models.Subject{}
	if err := s.subjectRepo.GetByID(subjectID, subject); err != nil {
		if err == gorm.ErrRecordNotFound {
			return "", errors.New("subject not found")
		}
		return "", fmt.Errorf("failed to get subject: %w", err)
	}

	// Get course details for context
	course := &models.Course{}
	if err := s.courseRepo.GetByID(subject.CourseID, course); err != nil {
		return "", fmt.Errorf("failed to get course for subject: %w", err)
	}

	// Check if image generator is available
	if !s.imageGenerator.IsAvailable() {
		return "", errors.New("image generation not available - no API key configured")
	}

	// Check if Azure storage is available
	if !s.azureStorage.IsInitialized() {
		return "", errors.New("Azure storage not initialized - check configuration")
	}

	// Generate the image
	ctx := context.Background()
	logrus.Infof("Generating image for subject '%s' (ID: %d)", subject.Name, subjectID)
	
	imageBytes, err := s.imageGenerator.GenerateSubjectImage(ctx, subject.Name, course.Name)
	if err != nil {
		return "", fmt.Errorf("failed to generate subject image: %w", err)
	}

	if len(imageBytes) == 0 {
		return "", errors.New("failed to generate subject image - no data received")
	}

	logrus.Infof("Subject image generated successfully, size: %d bytes", len(imageBytes))

	// Upload the image to Azure Storage
	imagePath := fmt.Sprintf("subjects/%d/cover", subjectID)
	logrus.Infof("Uploading subject image to Azure Storage path: %s", imagePath)
	
	imageURL, err := s.azureStorage.UploadImage(imageBytes, imagePath)
	if err != nil {
		return "", fmt.Errorf("failed to upload subject image to Azure Storage: %w", err)
	}

	logrus.Infof("Subject image uploaded successfully, URL: %s", imageURL)

	return imageURL, nil
}

// GenerateCustomImage generates an image based on a custom prompt
func (s *ImageServiceImpl) GenerateCustomImage(prompt string) (string, error) {
	// Check if image generator is available
	if !s.imageGenerator.IsAvailable() {
		return "", errors.New("image generation not available - no API key configured")
	}

	// Check if Azure storage is available
	if !s.azureStorage.IsInitialized() {
		return "", errors.New("Azure storage not initialized - check configuration")
	}

	// Generate the image
	ctx := context.Background()
	logrus.Infof("Generating custom image with prompt: %s", prompt)
	
	imageBytes, err := s.imageGenerator.GenerateCustomImage(ctx, prompt)
	if err != nil {
		return "", fmt.Errorf("failed to generate custom image: %w", err)
	}

	if len(imageBytes) == 0 {
		return "", errors.New("failed to generate custom image - no data received")
	}

	logrus.Infof("Custom image generated successfully, size: %d bytes", len(imageBytes))

	// Upload the image to Azure Storage
	imagePath := fmt.Sprintf("custom/%d", utils.GenerateUniqueID())
	logrus.Infof("Uploading custom image to Azure Storage path: %s", imagePath)
	
	imageURL, err := s.azureStorage.UploadImage(imageBytes, imagePath)
	if err != nil {
		return "", fmt.Errorf("failed to upload custom image to Azure Storage: %w", err)
	}

	logrus.Infof("Custom image uploaded successfully, URL: %s", imageURL)

	return imageURL, nil
}

// UploadImage uploads an image directly to Azure Storage
func (s *ImageServiceImpl) UploadImage(imageData []byte, imagePath string) (string, error) {
	// Check if Azure storage is available
	if !s.azureStorage.IsInitialized() {
		return "", errors.New("Azure storage not initialized - check configuration")
	}

	if len(imageData) == 0 {
		return "", errors.New("no image data provided")
	}

	logrus.Infof("Uploading image to path: %s, size: %d bytes", imagePath, len(imageData))
	
	imageURL, err := s.azureStorage.UploadImage(imageData, imagePath)
	if err != nil {
		return "", fmt.Errorf("failed to upload image: %w", err)
	}

	logrus.Infof("Image uploaded successfully, URL: %s", imageURL)
	return imageURL, nil
}

// DeleteImage deletes an image from Azure Storage
func (s *ImageServiceImpl) DeleteImage(imagePath string) error {
	// Check if Azure storage is available
	if !s.azureStorage.IsInitialized() {
		return errors.New("Azure storage not initialized - check configuration")
	}

	// Extract just the path from the full URL if needed
	if filepath.IsAbs(imagePath) {
		// Extract the blob path from the full URL
		// This is a simple extraction, might need improvement for complex cases
		parts := filepath.Split(imagePath)
		imagePath = parts[1]
	}

	logrus.Infof("Deleting image: %s", imagePath)
	
	if err := s.azureStorage.DeleteImage(imagePath); err != nil {
		return fmt.Errorf("failed to delete image: %w", err)
	}

	logrus.Infof("Image deleted successfully: %s", imagePath)
	return nil
}

// ListImages lists all images in a specific path
func (s *ImageServiceImpl) ListImages(pathPrefix string) ([]string, error) {
	// Check if Azure storage is available
	if !s.azureStorage.IsInitialized() {
		return nil, errors.New("Azure storage not initialized - check configuration")
	}

	logrus.Infof("Listing images with prefix: %s", pathPrefix)
	
	imageURLs, err := s.azureStorage.ListImages(pathPrefix)
	if err != nil {
		return nil, fmt.Errorf("failed to list images: %w", err)
	}

	logrus.Infof("Found %d images with prefix: %s", len(imageURLs), pathPrefix)
	return imageURLs, nil
}