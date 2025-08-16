# CourseWagon Backend - Azure Container Apps Deployment Guide

This comprehensive guide walks you through deploying the CourseWagon backend to Azure Container Apps using Azure CLI and Azure Container Registry (ACR).

## Prerequisites

1. **Azure CLI**: Install and configure Azure CLI
   ```bash
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   az login
   ```

2. **Docker**: Ensure Docker is installed (for local testing)

3. **Environment Variables**: Ensure your `.env` file contains all required variables

## Quick Start - Automated Deployment

### 1. Initial Deployment
```bash
./deploy-to-azure.sh
```

### 2. Update Existing Deployment
```bash
./update-azure-deployment.sh
```

### 3. Manage Environment Variables
```bash
./manage-env-vars.sh
```

## Environment Variables Required

Your `.env` file must contain the following variables:

```env
# Gemini API Configuration
API_KEY=your_gemini_api_key
GEMINI_API_KEY=your_gemini_api_key
GEMINI_IMAGE_GENERATION_API_KEY=your_gemini_image_api_key

# Database Configuration
DB_HOST=your_db_host
DB_PORT=your_db_port
DB_USER=your_db_user
DB_PASS=your_db_password
DB_NAME=your_db_name

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret
JWT_ACCESS_TOKEN_EXPIRES_HOURS=1
JWT_REFRESH_TOKEN_EXPIRES_DAYS=30

# Security Configuration
SECRET_KEY=your_flask_secret_key
SECURITY_PASSWORD_SALT=your_security_salt
ENCRYPTION_KEY=your_encryption_key
ENCRYPTION_SALT=your_encryption_salt

# Firebase Configuration
FIREBASE_STORAGE_BUCKET=your_firebase_bucket

# Email Configuration (Mailgun)
MAIL_SERVER=smtp.mailgun.org
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your_mailgun_username
MAIL_PASSWORD=your_mailgun_password
MAIL_DEFAULT_SENDER=noreply@yourdomain.com
MAIL_CONTACT_EMAIL=contact@yourdomain.com
MAILGUN_API_KEY=your_mailgun_api_key
MAILGUN_DOMAIN=your_mailgun_domain

# Frontend Configuration
FRONTEND_URL=https://yourdomain.com
APP_NAME="Course Wagon"
```

## Step 9: Deploy Container App
az containerapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $APP_ENV \
  --image "${ACR_NAME}.azurecr.io/coursewagon-backend:latest" \
  --target-port 8080 \
  --ingress external \
  --registry-server "${ACR_NAME}.azurecr.io" \
  --secrets \
    azure-storage-connection-string="$STORAGE_CONNECTION_STRING" \
  --env-vars \
    "PORT=8080" \
    "AZURE_STORAGE_ACCOUNT_NAME=$STORAGE_ACCOUNT" \
    "AZURE_STORAGE_CONTAINER_NAME=$CONTAINER_NAME" \
    "AZURE_STORAGE_CONNECTION_STRING=secretref:azure-storage-connection-string"

## Step 10: Update Container App with Environment Variables from .env
# You'll need to add all other environment variables from your .env file

## Step 11: Get Application URL
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv

## Cleanup (if needed)
# az group delete --name $RESOURCE_GROUP --yes --no-wait
