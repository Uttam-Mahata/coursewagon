package services

import (
	"bytes"
	"fmt"
	"html/template"
	"net/http"
	"net/url"
	"os"
	"strings"

	"github.com/sirupsen/logrus"
)

type EmailService interface {
	SendPasswordResetEmail(email, token string) error
	SendWelcomeEmail(email, name string) error
	SendEmail(to, subject, htmlBody, textBody string) error
}

type EmailServiceImpl struct {
	mailgunAPIKey string
	mailgunDomain string
	senderEmail   string
	contactEmail  string
	appName       string
	frontendURL   string
	isConfigured  bool
}

func NewEmailService() EmailService {
	service := &EmailServiceImpl{
		mailgunAPIKey: os.Getenv("MAILGUN_API_KEY"),
		mailgunDomain: os.Getenv("MAILGUN_DOMAIN"),
		senderEmail:   os.Getenv("MAIL_DEFAULT_SENDER"),
		contactEmail:  os.Getenv("MAIL_CONTACT_EMAIL"),
		appName:       os.Getenv("APP_NAME"),
		frontendURL:   os.Getenv("FRONTEND_URL"),
	}

	// Set defaults
	if service.mailgunDomain == "" {
		service.mailgunDomain = "mg.coursewagon.live"
	}
	if service.senderEmail == "" {
		service.senderEmail = "noreply@mg.coursewagon.live"
	}
	if service.contactEmail == "" {
		service.contactEmail = "contact@mg.coursewagon.live"
	}
	if service.appName == "" {
		service.appName = "Course Wagon"
	}
	if service.frontendURL == "" {
		service.frontendURL = "https://www.coursewagon.live"
	}

	// Check if properly configured
	service.isConfigured = service.mailgunAPIKey != "" && service.mailgunDomain != "" && service.senderEmail != ""

	if !service.isConfigured {
		logrus.Warning("Email service not configured properly. Missing MAILGUN_API_KEY, MAILGUN_DOMAIN, or MAIL_DEFAULT_SENDER")
	} else {
		logrus.Infof("Email service configured successfully using Mailgun domain: %s", service.mailgunDomain)
	}

	return service
}

// SendPasswordResetEmail sends a password reset email
func (s *EmailServiceImpl) SendPasswordResetEmail(email, token string) error {
	if !s.isConfigured {
		logrus.Warning("Email service not configured, skipping password reset email")
		return nil
	}

	subject := fmt.Sprintf("Password Reset - %s", s.appName)
	resetURL := fmt.Sprintf("%s/reset-password?token=%s", s.frontendURL, token)

	// HTML template
	htmlTemplate := `
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{.Subject}}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2c3e50;">Password Reset Request</h2>
        <p>Hello,</p>
        <p>We received a request to reset your password for your {{.AppName}} account.</p>
        <p>Click the button below to reset your password:</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{{.ResetURL}}" style="background-color: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Password</a>
        </div>
        <p>Or copy and paste this link into your browser:</p>
        <p style="word-break: break-all; background-color: #f8f9fa; padding: 10px; border-radius: 3px;">{{.ResetURL}}</p>
        <p><strong>This link will expire in 1 hour.</strong></p>
        <p>If you didn't request this password reset, please ignore this email or contact support if you have concerns.</p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        <p style="font-size: 12px; color: #7f8c8d;">
            Best regards,<br>
            The {{.AppName}} Team
        </p>
    </div>
</body>
</html>`

	// Text template
	textTemplate := `Password Reset Request

Hello,

We received a request to reset your password for your {{.AppName}} account.

Please click the following link to reset your password:
{{.ResetURL}}

This link will expire in 1 hour.

If you didn't request this password reset, please ignore this email or contact support if you have concerns.

Best regards,
The {{.AppName}} Team`

	data := map[string]string{
		"Subject":   subject,
		"AppName":   s.appName,
		"ResetURL":  resetURL,
		"Email":     email,
	}

	htmlBody, err := s.renderTemplate(htmlTemplate, data)
	if err != nil {
		return fmt.Errorf("failed to render HTML template: %w", err)
	}

	textBody, err := s.renderTemplate(textTemplate, data)
	if err != nil {
		return fmt.Errorf("failed to render text template: %w", err)
	}

	return s.SendEmail(email, subject, htmlBody, textBody)
}

// SendWelcomeEmail sends a welcome email to new users
func (s *EmailServiceImpl) SendWelcomeEmail(email, name string) error {
	if !s.isConfigured {
		logrus.Warning("Email service not configured, skipping welcome email")
		return nil
	}

	subject := fmt.Sprintf("Welcome to %s!", s.appName)

	htmlTemplate := `
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{.Subject}}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2c3e50;">Welcome to {{.AppName}}!</h2>
        <p>Hello {{.Name}},</p>
        <p>Welcome to {{.AppName}}! We're excited to have you on board.</p>
        <p>You can now access all our features:</p>
        <ul>
            <li>Create and manage courses</li>
            <li>Generate AI-powered educational content</li>
            <li>Access comprehensive learning materials</li>
            <li>Track your progress</li>
        </ul>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{{.FrontendURL}}" style="background-color: #27ae60; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Get Started</a>
        </div>
        <p>If you have any questions, feel free to contact us at {{.ContactEmail}}.</p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        <p style="font-size: 12px; color: #7f8c8d;">
            Best regards,<br>
            The {{.AppName}} Team
        </p>
    </div>
</body>
</html>`

	textTemplate := `Welcome to {{.AppName}}!

Hello {{.Name}},

Welcome to {{.AppName}}! We're excited to have you on board.

You can now access all our features:
- Create and manage courses
- Generate AI-powered educational content
- Access comprehensive learning materials
- Track your progress

Visit our platform: {{.FrontendURL}}

If you have any questions, feel free to contact us at {{.ContactEmail}}.

Best regards,
The {{.AppName}} Team`

	data := map[string]string{
		"Subject":     subject,
		"AppName":     s.appName,
		"Name":        name,
		"FrontendURL": s.frontendURL,
		"ContactEmail": s.contactEmail,
	}

	htmlBody, err := s.renderTemplate(htmlTemplate, data)
	if err != nil {
		return fmt.Errorf("failed to render HTML template: %w", err)
	}

	textBody, err := s.renderTemplate(textTemplate, data)
	if err != nil {
		return fmt.Errorf("failed to render text template: %w", err)
	}

	return s.SendEmail(email, subject, htmlBody, textBody)
}

// SendEmail sends an email using Mailgun API
func (s *EmailServiceImpl) SendEmail(to, subject, htmlBody, textBody string) error {
	if !s.isConfigured {
		return fmt.Errorf("email service not configured")
	}

	// Prepare form data
	data := url.Values{}
	data.Set("from", s.senderEmail)
	data.Set("to", to)
	data.Set("subject", subject)
	data.Set("html", htmlBody)
	data.Set("text", textBody)

	// Create HTTP request
	mailgunURL := fmt.Sprintf("https://api.mailgun.net/v3/%s/messages", s.mailgunDomain)
	req, err := http.NewRequest("POST", mailgunURL, strings.NewReader(data.Encode()))
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	// Set headers
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.SetBasicAuth("api", s.mailgunAPIKey)

	// Send request
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return fmt.Errorf("failed to send email: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("mailgun API returned status: %d", resp.StatusCode)
	}

	logrus.Infof("Email sent successfully to: %s", to)
	return nil
}

// renderTemplate renders a template string with data
func (s *EmailServiceImpl) renderTemplate(templateStr string, data map[string]string) (string, error) {
	tmpl, err := template.New("email").Parse(templateStr)
	if err != nil {
		return "", err
	}

	var buf bytes.Buffer
	if err := tmpl.Execute(&buf, data); err != nil {
		return "", err
	}

	return buf.String(), nil
}