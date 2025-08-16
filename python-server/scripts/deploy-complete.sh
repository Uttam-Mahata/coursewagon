#!/bin/bash

# CourseWagon Backend - Complete Azure Container Apps Deployment Script
# This script deploys the backend to Azure Container Apps with proper environment variable handling

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions for consistent output
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

echo -e "${BLUE}=== CourseWagon Backend - Azure Container Apps Deployment ===${NC}"

# Configuration (using consistent port 8000 for FastAPI)
RESOURCE_GROUP="coursewagon-rg"
LOCATION="southeastasia"
ACR_NAME="coursewagoracr"
APP_ENV="coursewagon-env"
APP_NAME="coursewagon-backend"
IMAGE_NAME="coursewagon-backend"
TAG="latest"
TARGET_PORT="8000"

echo -e "${YELLOW}Using configuration:${NC}"
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo "ACR Name: $ACR_NAME"
echo "App Environment: $APP_ENV"
echo "App Name: $APP_NAME"
echo

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please ensure .env file exists with all required environment variables"
    exit 1
fi

# Check if Azure CLI is installed and logged in
if ! command -v az &> /dev/null; then
    echo -e "${RED}Error: Azure CLI is not installed${NC}"
    echo "Please install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}Please log in to Azure CLI:${NC}"
    az login
fi

echo -e "${BLUE}Step 1: Creating Resource Group (if not exists)...${NC}"
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION \
    --output table

echo -e "${BLUE}Step 2: Creating Azure Container Registry...${NC}"
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true \
    --output table

echo -e "${BLUE}Step 3: Building and pushing Docker image using Azure...${NC}"
# Use Azure Container Registry to build the image directly from source
az acr build \
    --registry $ACR_NAME \
    --image $IMAGE_NAME:$TAG \
    --file Dockerfile \
    . \
    --platform linux

echo -e "${BLUE}Step 4: Creating Container Apps Environment...${NC}"
az containerapp env create \
    --name $APP_ENV \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --output table

echo -e "${BLUE}Step 5: Reading environment variables from .env file...${NC}"

# Function to safely extract env var from .env file
get_env_var() {
    local var_name="$1"
    local value=$(grep "^$var_name=" .env | cut -d '=' -f 2- | sed 's/^"//' | sed 's/"$//')
    echo "$value"
}

# Extract all environment variables
API_KEY=$(get_env_var "API_KEY")
GEMINI_API_KEY=$(get_env_var "GEMINI_API_KEY")
GEMINI_IMAGE_GENERATION_API_KEY=$(get_env_var "GEMINI_IMAGE_GENERATION_API_KEY")
DB_HOST=$(get_env_var "DB_HOST")
DB_PORT=$(get_env_var "DB_PORT")
DB_USER=$(get_env_var "DB_USER")
DB_PASS=$(get_env_var "DB_PASS")
DB_NAME=$(get_env_var "DB_NAME")
JWT_SECRET_KEY=$(get_env_var "JWT_SECRET_KEY")
JWT_ACCESS_TOKEN_EXPIRES_HOURS=$(get_env_var "JWT_ACCESS_TOKEN_EXPIRES_HOURS")
JWT_REFRESH_TOKEN_EXPIRES_DAYS=$(get_env_var "JWT_REFRESH_TOKEN_EXPIRES_DAYS")
SECRET_KEY=$(get_env_var "SECRET_KEY")
SECURITY_PASSWORD_SALT=$(get_env_var "SECURITY_PASSWORD_SALT")
ENCRYPTION_KEY=$(get_env_var "ENCRYPTION_KEY")
ENCRYPTION_SALT=$(get_env_var "ENCRYPTION_SALT")
FIREBASE_STORAGE_BUCKET=$(get_env_var "FIREBASE_STORAGE_BUCKET")
MAIL_SERVER=$(get_env_var "MAIL_SERVER")
MAIL_PORT=$(get_env_var "MAIL_PORT")
MAIL_USE_TLS=$(get_env_var "MAIL_USE_TLS")
MAIL_USE_SSL=$(get_env_var "MAIL_USE_SSL")
MAIL_USERNAME=$(get_env_var "MAIL_USERNAME")
MAIL_PASSWORD=$(get_env_var "MAIL_PASSWORD")
MAIL_DEFAULT_SENDER=$(get_env_var "MAIL_DEFAULT_SENDER")
MAIL_CONTACT_EMAIL=$(get_env_var "MAIL_CONTACT_EMAIL")
APP_NAME_ENV=$(get_env_var "APP_NAME")
FRONTEND_URL=$(get_env_var "FRONTEND_URL")
MAILGUN_API_KEY=$(get_env_var "MAILGUN_API_KEY")
MAILGUN_DOMAIN=$(get_env_var "MAILGUN_DOMAIN")
AZURE_STORAGE_ACCOUNT_NAME=$(get_env_var "AZURE_STORAGE_ACCOUNT_NAME")
AZURE_STORAGE_CONNECTION_STRING=$(get_env_var "AZURE_STORAGE_CONNECTION_STRING")
AZURE_STORAGE_CONTAINER_NAME=$(get_env_var "AZURE_STORAGE_CONTAINER_NAME")
DATABASE_URL=$(get_env_var "DATABASE_URL")

# Construct DATABASE_URL if not present in .env
if [ -z "$DATABASE_URL" ]; then
    DATABASE_URL="mysql+mysqlconnector://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
    echo -e "${YELLOW}DATABASE_URL not found in .env, constructed from components: $DATABASE_URL${NC}"
fi

echo -e "${BLUE}Step 6: Creating Container App...${NC}"
az containerapp create \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $APP_ENV \
    --image "$ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG" \
    --target-port $TARGET_PORT \
    --ingress external \
    --registry-server "$ACR_NAME.azurecr.io" \
    --cpu 1.0 \
    --memory 2.0Gi \
    --min-replicas 1 \
    --max-replicas 3 \
    --secrets \
        api-key="$API_KEY" \
        gemini-api-key="$GEMINI_API_KEY" \
        gemini-image-generation-api-key="$GEMINI_IMAGE_GENERATION_API_KEY" \
        db-pass="$DB_PASS" \
        jwt-secret-key="$JWT_SECRET_KEY" \
        secret-key="$SECRET_KEY" \
        security-password-salt="$SECURITY_PASSWORD_SALT" \
        encryption-key="$ENCRYPTION_KEY" \
        encryption-salt="$ENCRYPTION_SALT" \
        mail-password="$MAIL_PASSWORD" \
        mailgun-api-key="$MAILGUN_API_KEY" \
        azure-storage-connection-string="$AZURE_STORAGE_CONNECTION_STRING" \
    --env-vars \
        "PORT=$TARGET_PORT" \
        "API_KEY=secretref:api-key" \
        "GEMINI_API_KEY=secretref:gemini-api-key" \
        "GEMINI_IMAGE_GENERATION_API_KEY=secretref:gemini-image-generation-api-key" \
        "DB_HOST=$DB_HOST" \
        "DB_PORT=$DB_PORT" \
        "DB_USER=$DB_USER" \
        "DB_PASS=secretref:db-pass" \
        "DB_NAME=$DB_NAME" \
        "DATABASE_URL=$DATABASE_URL" \
        "JWT_SECRET_KEY=secretref:jwt-secret-key" \
        "JWT_ACCESS_TOKEN_EXPIRES_HOURS=$JWT_ACCESS_TOKEN_EXPIRES_HOURS" \
        "JWT_REFRESH_TOKEN_EXPIRES_DAYS=$JWT_REFRESH_TOKEN_EXPIRES_DAYS" \
        "SECRET_KEY=secretref:secret-key" \
        "SECURITY_PASSWORD_SALT=secretref:security-password-salt" \
        "ENCRYPTION_KEY=secretref:encryption-key" \
        "ENCRYPTION_SALT=secretref:encryption-salt" \
        "FIREBASE_STORAGE_BUCKET=$FIREBASE_STORAGE_BUCKET" \
        "MAIL_SERVER=$MAIL_SERVER" \
        "MAIL_PORT=$MAIL_PORT" \
        "MAIL_USE_TLS=$MAIL_USE_TLS" \
        "MAIL_USE_SSL=$MAIL_USE_SSL" \
        "MAIL_USERNAME=$MAIL_USERNAME" \
        "MAIL_PASSWORD=secretref:mail-password" \
        "MAIL_DEFAULT_SENDER=$MAIL_DEFAULT_SENDER" \
        "MAIL_CONTACT_EMAIL=$MAIL_CONTACT_EMAIL" \
        "APP_NAME=$APP_NAME_ENV" \
        "FRONTEND_URL=$FRONTEND_URL" \
        "MAILGUN_API_KEY=secretref:mailgun-api-key" \
        "MAILGUN_DOMAIN=$MAILGUN_DOMAIN" \
        "AZURE_STORAGE_ACCOUNT_NAME=$AZURE_STORAGE_ACCOUNT_NAME" \
        "AZURE_STORAGE_CONNECTION_STRING=secretref:azure-storage-connection-string" \
        "AZURE_STORAGE_CONTAINER_NAME=$AZURE_STORAGE_CONTAINER_NAME" \
        "PYTHONUNBUFFERED=1" \
    --output table

# Function to get application URL dynamically
get_app_url() {
    local app_name="$1"
    local resource_group="$2"
    local url=$(az containerapp show \
        --name "$app_name" \
        --resource-group "$resource_group" \
        --query properties.configuration.ingress.fqdn \
        --output tsv 2>/dev/null)
    echo "$url"
}

# Function to test health endpoint with retries
test_health_endpoint() {
    local app_url="$1"
    local max_attempts=6
    local wait_time=30
    
    print_status "Testing health endpoint (may take up to ${max_attempts} attempts)..."
    
    for i in $(seq 1 $max_attempts); do
        print_status "Attempt $i/$max_attempts - Testing https://$app_url/health"
        
        if curl -f -s -m 30 "https://$app_url/health" &> /dev/null; then
            print_success "✓ Application is responding at health endpoint"
            return 0
        else
            if [ $i -lt $max_attempts ]; then
                print_warning "Health check failed. Waiting ${wait_time}s before retry..."
                sleep $wait_time
            fi
        fi
    done
    
    print_warning "⚠ Health check failed after $max_attempts attempts. Application might still be starting."
    print_status "You can manually check: https://$app_url/health"
    return 1
}

echo -e "${BLUE}Step 7: Getting application URL dynamically...${NC}"
print_status "Waiting for container app to be fully provisioned..."
sleep 30

APP_URL=$(get_app_url "$APP_NAME" "$RESOURCE_GROUP")

if [ -z "$APP_URL" ]; then
    print_warning "Could not retrieve application URL. Checking deployment status..."
    az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query "{name: name, status: properties.runningStatus}" --output table
    exit 1
fi

echo -e "${GREEN}=== Deployment Complete! ===${NC}"
echo
echo -e "${YELLOW}Application Details:${NC}"
echo "Resource Group: $RESOURCE_GROUP"
echo "Container App: $APP_NAME"
echo "Image: $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG"
echo "Application URL: https://$APP_URL"
echo "Health Endpoint: https://$APP_URL/health"
echo
echo -e "${YELLOW}Useful Commands:${NC}"
echo "View logs: az containerapp logs show --name $APP_NAME --resource-group $RESOURCE_GROUP --follow"
echo "Update app: ./scripts/quick-update.sh"
echo "View app details: az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP"
echo "Get current URL: az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv"
echo

# Test the health endpoint with retries
test_health_endpoint "$APP_URL"

print_success "🎉 Deployment process completed!"
echo -e "${GREEN}Visit your application at: https://$APP_URL${NC}"
