# config.py
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database configurations
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_NAME = os.getenv("DB_NAME")
    API_KEY = os.getenv("API_KEY")
    
    # SQLAlchemy configurations
    SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT configurations
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')  # Make sure this is very secure in production
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES_HOURS', '1')))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES_DAYS', '30')))
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # Security configurations
    SECRET_KEY = os.getenv('SECRET_KEY')  # Flask secret key
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT')
    
    # CORS configurations
    CORS_HEADERS = 'Content-Type'
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_ALLOWED_HEADERS = ['Content-Type', 'Authorization']
    CORS_EXPOSE_HEADERS = ['Content-Range', 'X-Content-Range']
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_MAX_AGE = 600  # Maximum time to cache preflight requests (10 minutes)
    
    # Additional security headers
    SECURITY_HEADERS = {
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'X-Content-Type-Options': 'nosniff',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }
    
    # Email configurations for Gmail SMTP
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')  # Gmail address
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')  # Gmail App Password
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))
    MAIL_CONTACT_EMAIL = os.getenv('MAIL_CONTACT_EMAIL', 'contact@coursewagon.live')
    
    # Frontend URL for links in emails
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'https://coursewagon.live')
    
    # Application name
    APP_NAME = os.getenv('APP_NAME', 'Course Wagon')
    
    # Firebase Admin SDK Configuration
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', 'coursewagon')
    FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', 'coursewagon-firebase-adminsdk.json')
    FIREBASE_CLIENT_EMAIL = os.getenv('FIREBASE_CLIENT_EMAIL', 'firebase-adminsdk-biym7@coursewagon.iam.gserviceaccount.com')
    
    # Firebase configurations
    
    # Azure Storage configurations
    AZURE_STORAGE_ACCOUNT_NAME = os.environ.get('AZURE_STORAGE_ACCOUNT_NAME')
    AZURE_STORAGE_CONNECTION_STRING = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
    AZURE_STORAGE_CONTAINER_NAME = os.environ.get('AZURE_STORAGE_CONTAINER_NAME', 'coursewagon-images')
    
    # Azure Deployment configurations
    AZURE_RESOURCE_GROUP = os.environ.get('AZURE_RESOURCE_GROUP', 'coursewagon-rg')
    AZURE_LOCATION = os.environ.get('AZURE_LOCATION', 'southeastasia')
    AZURE_CONTAINER_REGISTRY = os.environ.get('AZURE_CONTAINER_REGISTRY', 'coursewagoracr')
    AZURE_CONTAINER_APP_ENV = os.environ.get('AZURE_CONTAINER_APP_ENV', 'coursewagon-env')
    AZURE_CONTAINER_APP_NAME = os.environ.get('AZURE_CONTAINER_APP_NAME', 'coursewagon-backend')