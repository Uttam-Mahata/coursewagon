package services

import (
	"errors"
	"fmt"
	"go-server/config"
	"go-server/models"
	"go-server/repositories"
	"go-server/utils"

	"github.com/sirupsen/logrus"
	"gorm.io/gorm"
)

type AuthService interface {
	Register(req *models.UserRegisterRequest) (*models.User, error)
	Login(req *models.UserLoginRequest) (*models.UserLoginResponse, error)
	RefreshToken(refreshToken string) (*models.UserLoginResponse, error)
	RequestPasswordReset(email string) error
	ResetPassword(token, newPassword string) error
	GetUserProfile(userID uint) (*models.User, error)
}

type AuthServiceImpl struct {
	userRepo    repositories.UserRepository
	jwtUtil     *utils.JWTUtil
	config      *config.Config
	emailService EmailService // We'll create this later
}

func NewAuthService(userRepo repositories.UserRepository, config *config.Config, emailService EmailService) AuthService {
	jwtUtil := utils.NewJWTUtil(
		config.JWTSecretKey,
		config.JWTAccessTokenExpires,
		config.JWTRefreshTokenExpires,
	)

	return &AuthServiceImpl{
		userRepo:     userRepo,
		jwtUtil:      jwtUtil,
		config:       config,
		emailService: emailService,
	}
}

// Register creates a new user account
func (s *AuthServiceImpl) Register(req *models.UserRegisterRequest) (*models.User, error) {
	// Validate request
	if err := utils.ValidateStruct(req); err != nil {
		return nil, fmt.Errorf("validation error: %s", utils.FormatValidationErrors(err))
	}

	// Sanitize input
	req.Email = utils.SanitizeString(req.Email)
	if req.FirstName != nil {
		firstName := utils.SanitizeString(*req.FirstName)
		req.FirstName = &firstName
	}
	if req.LastName != nil {
		lastName := utils.SanitizeString(*req.LastName)
		req.LastName = &lastName
	}

	// Check if user already exists
	existingUser, err := s.userRepo.GetByEmail(req.Email)
	if err != nil {
		logrus.Errorf("Error checking existing user: %v", err)
		return nil, errors.New("failed to check user existence")
	}
	if existingUser != nil {
		return nil, errors.New("user with this email already exists")
	}

	// Validate password strength
	if !utils.IsValidPassword(req.Password) {
		return nil, errors.New("password must be at least 6 characters and contain both letters and numbers")
	}

	// Create new user
	user := &models.User{
		Email:     req.Email,
		FirstName: req.FirstName,
		LastName:  req.LastName,
		IsActive:  true,
		IsAdmin:   false,
	}

	// Set password
	if err := user.SetPassword(req.Password); err != nil {
		logrus.Errorf("Error setting password: %v", err)
		return nil, errors.New("failed to process password")
	}

	// Save user
	if err := s.userRepo.CreateUser(user); err != nil {
		logrus.Errorf("Error creating user: %v", err)
		return nil, errors.New("failed to create user")
	}

	logrus.Infof("User registered successfully: %s", user.Email)
	return user, nil
}

// Login authenticates a user and returns tokens
func (s *AuthServiceImpl) Login(req *models.UserLoginRequest) (*models.UserLoginResponse, error) {
	// Validate request
	if err := utils.ValidateStruct(req); err != nil {
		return nil, fmt.Errorf("validation error: %s", utils.FormatValidationErrors(err))
	}

	// Find user by email
	user, err := s.userRepo.GetByEmail(req.Email)
	if err != nil {
		logrus.Errorf("Error finding user: %v", err)
		return nil, errors.New("authentication failed")
	}
	if user == nil {
		return nil, errors.New("invalid email or password")
	}

	// Check if user is active
	if !user.IsActive {
		return nil, errors.New("account is deactivated")
	}

	// Verify password
	if !user.CheckPassword(req.Password) {
		return nil, errors.New("invalid email or password")
	}

	// Generate tokens
	accessToken, err := s.jwtUtil.GenerateAccessToken(user.ID, user.Email)
	if err != nil {
		logrus.Errorf("Error generating access token: %v", err)
		return nil, errors.New("failed to generate access token")
	}

	refreshToken, err := s.jwtUtil.GenerateRefreshToken(user.ID, user.Email)
	if err != nil {
		logrus.Errorf("Error generating refresh token: %v", err)
		return nil, errors.New("failed to generate refresh token")
	}

	// Update last login
	if err := s.userRepo.UpdateLastLogin(user.ID); err != nil {
		logrus.Errorf("Error updating last login: %v", err)
		// Don't fail the login for this
	}

	response := &models.UserLoginResponse{
		User:         user.ToDict(),
		AccessToken:  accessToken,
		RefreshToken: refreshToken,
	}

	logrus.Infof("User logged in successfully: %s", user.Email)
	return response, nil
}

// RefreshToken generates new tokens using refresh token
func (s *AuthServiceImpl) RefreshToken(refreshToken string) (*models.UserLoginResponse, error) {
	// Validate refresh token
	claims, err := s.jwtUtil.ValidateToken(refreshToken)
	if err != nil {
		return nil, errors.New("invalid or expired refresh token")
	}

	// Check if it's a refresh token
	if claims.Subject != "refresh_token" {
		return nil, errors.New("invalid token type")
	}

	// Get user
	user := &models.User{}
	if err := s.userRepo.GetByID(claims.UserID, user); err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, errors.New("user not found")
		}
		logrus.Errorf("Error finding user: %v", err)
		return nil, errors.New("failed to find user")
	}

	// Check if user is active
	if !user.IsActive {
		return nil, errors.New("account is deactivated")
	}

	// Generate new tokens
	newAccessToken, err := s.jwtUtil.GenerateAccessToken(user.ID, user.Email)
	if err != nil {
		logrus.Errorf("Error generating access token: %v", err)
		return nil, errors.New("failed to generate access token")
	}

	newRefreshToken, err := s.jwtUtil.GenerateRefreshToken(user.ID, user.Email)
	if err != nil {
		logrus.Errorf("Error generating refresh token: %v", err)
		return nil, errors.New("failed to generate refresh token")
	}

	response := &models.UserLoginResponse{
		User:         user.ToDict(),
		AccessToken:  newAccessToken,
		RefreshToken: newRefreshToken,
	}

	return response, nil
}

// RequestPasswordReset initiates password reset process
func (s *AuthServiceImpl) RequestPasswordReset(email string) error {
	// Find user by email
	user, err := s.userRepo.GetByEmail(email)
	if err != nil {
		logrus.Errorf("Error finding user: %v", err)
		return errors.New("failed to process request")
	}
	if user == nil {
		// Don't reveal if email exists for security
		logrus.Infof("Password reset requested for non-existent email: %s", email)
		return nil
	}

	// Create password reset token
	// This would need a password reset repository
	// For now, we'll just log it
	logrus.Infof("Password reset requested for user: %s", user.Email)

	// TODO: Send password reset email
	// return s.emailService.SendPasswordResetEmail(user.Email, resetToken)

	return nil
}

// ResetPassword resets user password using token
func (s *AuthServiceImpl) ResetPassword(token, newPassword string) error {
	// Validate password strength
	if !utils.IsValidPassword(newPassword) {
		return errors.New("password must be at least 6 characters and contain both letters and numbers")
	}

	// TODO: Implement password reset token validation
	// This would need a password reset repository
	
	logrus.Info("Password reset attempted")
	return errors.New("password reset not implemented yet")
}

// GetUserProfile returns user profile information
func (s *AuthServiceImpl) GetUserProfile(userID uint) (*models.User, error) {
	user := &models.User{}
	if err := s.userRepo.GetByID(userID, user); err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, errors.New("user not found")
		}
		logrus.Errorf("Error getting user profile: %v", err)
		return nil, errors.New("failed to get user profile")
	}

	return user, nil
}