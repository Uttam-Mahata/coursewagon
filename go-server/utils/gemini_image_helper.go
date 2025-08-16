package utils

import (
	"context"
	"fmt"
	"os"

	"github.com/sirupsen/logrus"
	"google.golang.org/genai"
)

type GeminiImageGenerator struct {
	client   *genai.Client
	apiKey   string
	modelName string
}

// NewGeminiImageGenerator creates a new Gemini image generator instance
func NewGeminiImageGenerator() *GeminiImageGenerator {
	apiKey := os.Getenv("GEMINI_IMAGE_GENERATION_API_KEY")
	if apiKey == "" {
		apiKey = os.Getenv("API_KEY")
	}
	
	if apiKey == "" {
		logrus.Warning("No API_KEY found in environment variables. Image generation functionality will not work.")
		return &GeminiImageGenerator{apiKey: ""}
	}

	return &GeminiImageGenerator{
		apiKey:    apiKey,
		modelName: "gemini-2.0-flash-exp-image-generation",
	}
}

// InitClient initializes the Gemini client for image generation
func (gig *GeminiImageGenerator) InitClient(ctx context.Context) error {
	if gig.apiKey == "" {
		return fmt.Errorf("no API key available for Gemini image generation")
	}

	client, err := genai.NewClient(ctx, nil)
	if err != nil {
		return fmt.Errorf("failed to create Gemini client: %w", err)
	}

	gig.client = client
	return nil
}

// GenerateCourseImage generates a cover image for a course based on its name and description
func (gig *GeminiImageGenerator) GenerateCourseImage(ctx context.Context, courseName, courseDescription string) ([]byte, error) {
	if gig.apiKey == "" {
		logrus.Error("Cannot generate image: No API key available")
		return nil, fmt.Errorf("no API key available for image generation")
	}

	if err := gig.InitClient(ctx); err != nil {
		return nil, err
	}
	defer gig.client.Close()

	// Create a prompt for the image generation
	prompt := fmt.Sprintf("Create a professional, educational 3D rendered cover image for a course titled '%s'.", courseName)
	
	if courseDescription != "" {
		// Add brief description context if available
		shortened := courseDescription
		if len(courseDescription) > 200 {
			shortened = courseDescription[:200] + "..."
		}
		prompt += fmt.Sprintf(" The course is about: %s", shortened)
	}
	
	prompt += " The image should be modern, clean, and visually appealing with educational elements. Use vibrant but professional colors. Make it suitable for a course thumbnail."

	logrus.Infof("Generating course image with prompt: %s", prompt)

	// Configure for image generation
	config := &genai.GenerateContentConfig{
		ResponseModalities: []string{"TEXT", "IMAGE"},
	}

	// Generate content with image
	result, err := gig.client.Models.GenerateContent(
		ctx,
		gig.modelName,
		genai.Text(prompt),
		config,
	)
	if err != nil {
		logrus.Errorf("Error generating image with Gemini: %v", err)
		return nil, fmt.Errorf("failed to generate image: %w", err)
	}

	// Extract image bytes from response
	var imageBytes []byte
	for _, part := range result.Candidates[0].Content.Parts {
		if part.InlineData != nil {
			imageBytes = part.InlineData.Data
			break
		}
	}

	if len(imageBytes) == 0 {
		return nil, fmt.Errorf("no image data received from Gemini")
	}

	logrus.Infof("Generated course image successfully, size: %d bytes", len(imageBytes))
	return imageBytes, nil
}

// GenerateSubjectImage generates a cover image for a subject
func (gig *GeminiImageGenerator) GenerateSubjectImage(ctx context.Context, subjectName, courseName string) ([]byte, error) {
	if gig.apiKey == "" {
		logrus.Error("Cannot generate image: No API key available")
		return nil, fmt.Errorf("no API key available for image generation")
	}

	if err := gig.InitClient(ctx); err != nil {
		return nil, err
	}
	defer gig.client.Close()

	// Create a prompt for subject image generation
	prompt := fmt.Sprintf("Create a professional, educational 3D rendered cover image for the subject '%s' from the course '%s'. The image should represent the subject matter visually with modern, clean design and educational elements. Use vibrant but professional colors suitable for academic content.", subjectName, courseName)

	logrus.Infof("Generating subject image for: %s", subjectName)

	// Configure for image generation
	config := &genai.GenerateContentConfig{
		ResponseModalities: []string{"TEXT", "IMAGE"},
	}

	// Generate content with image
	result, err := gig.client.Models.GenerateContent(
		ctx,
		gig.modelName,
		genai.Text(prompt),
		config,
	)
	if err != nil {
		logrus.Errorf("Error generating subject image with Gemini: %v", err)
		return nil, fmt.Errorf("failed to generate subject image: %w", err)
	}

	// Extract image bytes from response
	var imageBytes []byte
	for _, part := range result.Candidates[0].Content.Parts {
		if part.InlineData != nil {
			imageBytes = part.InlineData.Data
			break
		}
	}

	if len(imageBytes) == 0 {
		return nil, fmt.Errorf("no image data received from Gemini for subject")
	}

	logrus.Infof("Generated subject image successfully, size: %d bytes", len(imageBytes))
	return imageBytes, nil
}

// GenerateCustomImage generates an image based on custom prompt
func (gig *GeminiImageGenerator) GenerateCustomImage(ctx context.Context, prompt string) ([]byte, error) {
	if gig.apiKey == "" {
		logrus.Error("Cannot generate image: No API key available")
		return nil, fmt.Errorf("no API key available for image generation")
	}

	if err := gig.InitClient(ctx); err != nil {
		return nil, err
	}
	defer gig.client.Close()

	logrus.Infof("Generating custom image with prompt: %s", prompt)

	// Configure for image generation
	config := &genai.GenerateContentConfig{
		ResponseModalities: []string{"TEXT", "IMAGE"},
	}

	// Generate content with image
	result, err := gig.client.Models.GenerateContent(
		ctx,
		gig.modelName,
		genai.Text(prompt),
		config,
	)
	if err != nil {
		logrus.Errorf("Error generating custom image with Gemini: %v", err)
		return nil, fmt.Errorf("failed to generate custom image: %w", err)
	}

	// Extract image bytes from response
	var imageBytes []byte
	for _, part := range result.Candidates[0].Content.Parts {
		if part.InlineData != nil {
			imageBytes = part.InlineData.Data
			break
		}
	}

	if len(imageBytes) == 0 {
		return nil, fmt.Errorf("no image data received from Gemini for custom prompt")
	}

	logrus.Infof("Generated custom image successfully, size: %d bytes", len(imageBytes))
	return imageBytes, nil
}

// IsAvailable checks if image generation is available
func (gig *GeminiImageGenerator) IsAvailable() bool {
	return gig.apiKey != ""
}