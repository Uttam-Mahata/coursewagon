package utils

import (
	"fmt"
	"regexp"
	"strings"
	"time"

	"github.com/go-playground/validator/v10"
)

var validate *validator.Validate

func init() {
	validate = validator.New()
}

// ValidateStruct validates a struct using the validator package
func ValidateStruct(s interface{}) error {
	return validate.Struct(s)
}

// FormatValidationErrors formats validation errors into a readable string
func FormatValidationErrors(err error) string {
	var errorMessages []string

	if validationErrors, ok := err.(validator.ValidationErrors); ok {
		for _, fieldError := range validationErrors {
			errorMessage := formatFieldError(fieldError)
			errorMessages = append(errorMessages, errorMessage)
		}
	} else {
		errorMessages = append(errorMessages, err.Error())
	}

	return strings.Join(errorMessages, ", ")
}

func formatFieldError(fieldError validator.FieldError) string {
	fieldName := strings.ToLower(fieldError.Field())
	
	switch fieldError.Tag() {
	case "required":
		return fmt.Sprintf("%s is required", fieldName)
	case "email":
		return fmt.Sprintf("%s must be a valid email address", fieldName)
	case "min":
		return fmt.Sprintf("%s must be at least %s characters long", fieldName, fieldError.Param())
	case "max":
		return fmt.Sprintf("%s must be at most %s characters long", fieldName, fieldError.Param())
	case "len":
		return fmt.Sprintf("%s must be exactly %s characters long", fieldName, fieldError.Param())
	case "gt":
		return fmt.Sprintf("%s must be greater than %s", fieldName, fieldError.Param())
	case "gte":
		return fmt.Sprintf("%s must be greater than or equal to %s", fieldName, fieldError.Param())
	case "lt":
		return fmt.Sprintf("%s must be less than %s", fieldName, fieldError.Param())
	case "lte":
		return fmt.Sprintf("%s must be less than or equal to %s", fieldName, fieldError.Param())
	default:
		return fmt.Sprintf("%s is invalid", fieldName)
	}
}

// IsValidEmail validates email format
func IsValidEmail(email string) bool {
	emailRegex := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	return emailRegex.MatchString(email)
}

// IsValidPassword validates password strength
func IsValidPassword(password string) bool {
	// At least 6 characters
	if len(password) < 6 {
		return false
	}
	
	// Contains at least one letter and one number
	hasLetter := regexp.MustCompile(`[a-zA-Z]`).MatchString(password)
	hasNumber := regexp.MustCompile(`[0-9]`).MatchString(password)
	
	return hasLetter && hasNumber
}

// SanitizeString removes dangerous characters from string input
func SanitizeString(input string) string {
	// Remove potential script tags and other dangerous content
	scriptRegex := regexp.MustCompile(`(?i)<script[^>]*>.*?</script>`)
	input = scriptRegex.ReplaceAllString(input, "")
	
	// Remove HTML tags
	htmlRegex := regexp.MustCompile(`<[^>]*>`)
	input = htmlRegex.ReplaceAllString(input, "")
	
	return strings.TrimSpace(input)
}

// GenerateUniqueID generates a unique ID for various purposes
func GenerateUniqueID() uint {
	return uint(time.Now().UnixNano() / int64(time.Millisecond))
}