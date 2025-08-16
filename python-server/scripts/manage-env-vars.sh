#!/bin/bash

# CourseWagon Backend - Environment Variables Management Script
# This script helps manage environment variables for Azure Container Apps

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Azure Configuration (using consistent port 8000 for FastAPI)
RESOURCE_GROUP="coursewagon-rg"
APP_NAME="coursewagon-backend"
TARGET_PORT="8000"

print_status "Environment Variables Management for CourseWagon Backend"
echo ""
echo "Available actions:"
echo "1. Update environment variables from .env file"
echo "2. View current environment variables"
echo "3. Update specific environment variable"
echo "4. Remove environment variable"
echo ""

read -p "Choose an action (1-4): " action

case $action in
    1)
        # Update environment variables from .env file
        if [ ! -f ".env" ]; then
            print_error ".env file not found!"
            exit 1
        fi

        print_status "Loading environment variables from .env file..."
        export $(grep -v '^#' .env | xargs)

        # Get storage connection string
        AZURE_STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
            --name coursewagstorage \
            --resource-group $RESOURCE_GROUP \
            --query connectionString -o tsv)

        print_status "Updating Container App environment variables..."
        az containerapp update \
            --name $APP_NAME \
            --resource-group $RESOURCE_GROUP \
            --set-env-vars \
                "PORT=$TARGET_PORT" \
                "API_KEY=$API_KEY" \
                "GEMINI_API_KEY=$GEMINI_API_KEY" \
                "GEMINI_IMAGE_GENERATION_API_KEY=$GEMINI_IMAGE_GENERATION_API_KEY" \
                "DB_HOST=$DB_HOST" \
                "DB_PORT=$DB_PORT" \
                "DB_USER=$DB_USER" \
                "DB_PASS=$DB_PASS" \
                "DB_NAME=$DB_NAME" \
                "JWT_SECRET_KEY=$JWT_SECRET_KEY" \
                "JWT_ACCESS_TOKEN_EXPIRES_HOURS=$JWT_ACCESS_TOKEN_EXPIRES_HOURS" \
                "JWT_REFRESH_TOKEN_EXPIRES_DAYS=$JWT_REFRESH_TOKEN_EXPIRES_DAYS" \
                "SECRET_KEY=$SECRET_KEY" \
                "SECURITY_PASSWORD_SALT=$SECURITY_PASSWORD_SALT" \
                "ENCRYPTION_KEY=$ENCRYPTION_KEY" \
                "ENCRYPTION_SALT=$ENCRYPTION_SALT" \
                "FIREBASE_STORAGE_BUCKET=$FIREBASE_STORAGE_BUCKET" \
                "MAIL_SERVER=$MAIL_SERVER" \
                "MAIL_PORT=$MAIL_PORT" \
                "MAIL_USE_TLS=$MAIL_USE_TLS" \
                "MAIL_USE_SSL=$MAIL_USE_SSL" \
                "MAIL_USERNAME=$MAIL_USERNAME" \
                "MAIL_PASSWORD=$MAIL_PASSWORD" \
                "MAIL_DEFAULT_SENDER=$MAIL_DEFAULT_SENDER" \
                "MAIL_CONTACT_EMAIL=$MAIL_CONTACT_EMAIL" \
                "APP_NAME=$APP_NAME" \
                "FRONTEND_URL=$FRONTEND_URL" \
                "MAILGUN_API_KEY=$MAILGUN_API_KEY" \
                "MAILGUN_DOMAIN=$MAILGUN_DOMAIN" \
                "AZURE_STORAGE_ACCOUNT_NAME=coursewagstorage" \
                "AZURE_STORAGE_CONNECTION_STRING=$AZURE_STORAGE_CONNECTION_STRING" \
                "AZURE_STORAGE_CONTAINER_NAME=coursewagon-images" \
                "PYTHONUNBUFFERED=1" \
            --output table

        print_success "Environment variables updated successfully!"
        ;;

    2)
        # View current environment variables
        print_status "Current environment variables for $APP_NAME:"
        az containerapp show \
            --name $APP_NAME \
            --resource-group $RESOURCE_GROUP \
            --query "properties.template.containers[0].env" \
            --output table
        ;;

    3)
        # Update specific environment variable
        read -p "Enter environment variable name: " var_name
        read -p "Enter environment variable value: " var_value

        print_status "Updating $var_name..."
        az containerapp update \
            --name $APP_NAME \
            --resource-group $RESOURCE_GROUP \
            --set-env-vars "$var_name=$var_value" \
            --output table

        print_success "Environment variable $var_name updated successfully!"
        ;;

    4)
        # Remove environment variable
        read -p "Enter environment variable name to remove: " var_name

        print_status "Removing $var_name..."
        az containerapp update \
            --name $APP_NAME \
            --resource-group $RESOURCE_GROUP \
            --remove-env-vars "$var_name" \
            --output table

        print_success "Environment variable $var_name removed successfully!"
        ;;

    *)
        print_error "Invalid action selected!"
        exit 1
        ;;
esac

print_status "Done!"
