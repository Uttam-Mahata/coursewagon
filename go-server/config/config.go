package config

import (
	"fmt"
	"os"
	"strconv"
	"time"

	"github.com/joho/godotenv"
	"github.com/sirupsen/logrus"
	"gorm.io/driver/mysql"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

type Config struct {
	// Database configurations
	DBHost string
	DBPort string
	DBUser string
	DBPass string
	DBName string

	// Server configurations
	Port        string
	Environment string
	Debug       bool

	// JWT configurations
	JWTSecretKey             string
	JWTAccessTokenExpires    time.Duration
	JWTRefreshTokenExpires   time.Duration

	// Security configurations
	SecretKey             string
	SecurityPasswordSalt  string

	// Email configurations
	MailServer        string
	MailPort          int
	MailUseTLS        bool
	MailUseSSL        bool
	MailUsername      string
	MailPassword      string
	MailDefaultSender string
	MailContactEmail  string

	// Application configurations
	FrontendURL string
	AppName     string

	// API configurations
	APIKey string

	// Azure Storage configurations
	AzureStorageAccountName     string
	AzureStorageConnectionString string
	AzureStorageContainerName   string

	// Azure Deployment configurations
	AzureResourceGroup     string
	AzureLocation          string
	AzureContainerRegistry string
	AzureContainerAppEnv   string
	AzureContainerAppName  string
}

func LoadConfig() (*Config, error) {
	// Load .env file if it exists
	if err := godotenv.Load(); err != nil {
		logrus.Warn("No .env file found, using environment variables")
	}

	config := &Config{
		// Database
		DBHost: getEnv("DB_HOST", "localhost"),
		DBPort: getEnv("DB_PORT", "3306"),
		DBUser: getEnv("DB_USER", "root"),
		DBPass: getEnv("DB_PASS", ""),
		DBName: getEnv("DB_NAME", "coursewagon"),

		// Server
		Port:        getEnv("PORT", "8000"),
		Environment: getEnv("ENVIRONMENT", "development"),
		Debug:       getBoolEnv("DEBUG", false),

		// JWT
		JWTSecretKey:             getEnv("JWT_SECRET_KEY", "your-secret-key"),
		JWTAccessTokenExpires:    getDurationEnv("JWT_ACCESS_TOKEN_EXPIRES_HOURS", 1) * time.Hour,
		JWTRefreshTokenExpires:   getDurationEnv("JWT_REFRESH_TOKEN_EXPIRES_DAYS", 30) * 24 * time.Hour,

		// Security
		SecretKey:             getEnv("SECRET_KEY", "your-secret-key"),
		SecurityPasswordSalt:  getEnv("SECURITY_PASSWORD_SALT", "your-salt"),

		// Email
		MailServer:        getEnv("MAIL_SERVER", "smtp.mailgun.org"),
		MailPort:          getIntEnv("MAIL_PORT", 587),
		MailUseTLS:        getBoolEnv("MAIL_USE_TLS", true),
		MailUseSSL:        getBoolEnv("MAIL_USE_SSL", false),
		MailUsername:      getEnv("MAIL_USERNAME", ""),
		MailPassword:      getEnv("MAIL_PASSWORD", ""),
		MailDefaultSender: getEnv("MAIL_DEFAULT_SENDER", "noreply@coursewagon.live"),
		MailContactEmail:  getEnv("MAIL_CONTACT_EMAIL", "contact@coursewagon.live"),

		// Application
		FrontendURL: getEnv("FRONTEND_URL", "https://coursewagon.live"),
		AppName:     getEnv("APP_NAME", "Course Wagon"),

		// API
		APIKey: getEnv("API_KEY", ""),

		// Azure Storage
		AzureStorageAccountName:     getEnv("AZURE_STORAGE_ACCOUNT_NAME", ""),
		AzureStorageConnectionString: getEnv("AZURE_STORAGE_CONNECTION_STRING", ""),
		AzureStorageContainerName:   getEnv("AZURE_STORAGE_CONTAINER_NAME", "coursewagon-images"),

		// Azure Deployment
		AzureResourceGroup:     getEnv("AZURE_RESOURCE_GROUP", "coursewagon-rg"),
		AzureLocation:          getEnv("AZURE_LOCATION", "southeastasia"),
		AzureContainerRegistry: getEnv("AZURE_CONTAINER_REGISTRY", "coursewagoracr"),
		AzureContainerAppEnv:   getEnv("AZURE_CONTAINER_APP_ENV", "coursewagon-env"),
		AzureContainerAppName:  getEnv("AZURE_CONTAINER_APP_NAME", "coursewagon-backend"),
	}

	return config, nil
}

func SetupDatabase(cfg *Config) (*gorm.DB, error) {
	// Create DSN (Data Source Name)
	dsn := fmt.Sprintf("%s:%s@tcp(%s:%s)/%s?charset=utf8mb4&parseTime=True&loc=Local",
		cfg.DBUser, cfg.DBPass, cfg.DBHost, cfg.DBPort, cfg.DBName)

	// Configure GORM logger
	gormLogger := logger.Default
	if cfg.Debug {
		gormLogger = logger.Default.LogMode(logger.Info)
	} else {
		gormLogger = logger.Default.LogMode(logger.Silent)
	}

	// Open database connection
	db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{
		Logger: gormLogger,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to connect to database: %w", err)
	}

	// Configure connection pool
	sqlDB, err := db.DB()
	if err != nil {
		return nil, fmt.Errorf("failed to get database instance: %w", err)
	}

	sqlDB.SetMaxIdleConns(10)
	sqlDB.SetMaxOpenConns(100)
	sqlDB.SetConnMaxLifetime(time.Hour)

	logrus.Info("Database connection established successfully")
	return db, nil
}

// Helper functions
func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getBoolEnv(key string, defaultValue bool) bool {
	if value := os.Getenv(key); value != "" {
		if parsed, err := strconv.ParseBool(value); err == nil {
			return parsed
		}
	}
	return defaultValue
}

func getIntEnv(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if parsed, err := strconv.Atoi(value); err == nil {
			return parsed
		}
	}
	return defaultValue
}

func getDurationEnv(key string, defaultValue int) time.Duration {
	if value := os.Getenv(key); value != "" {
		if parsed, err := strconv.Atoi(value); err == nil {
			return time.Duration(parsed)
		}
	}
	return time.Duration(defaultValue)
}