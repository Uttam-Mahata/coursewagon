#!/bin/bash

# CourseWagon Backend - Azure Container Apps Update Script
# This script updates the existing deployment with new code changes

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
ACR_NAME="coursewagoracr"
APP_NAME="coursewagon-backend"
IMAGE_NAME="coursewagon-backend"
IMAGE_TAG="latest"
TARGET_PORT="8000"

# Function to get application URL dynamically
get_app_url() {
    local app_name="$1"
    local resource_group="$2"
    local max_attempts=5
    local wait_time=10
    
    for i in $(seq 1 $max_attempts); do
        local url=$(az containerapp show \
            --name "$app_name" \
            --resource-group "$resource_group" \
            --query properties.configuration.ingress.fqdn \
            --output tsv 2>/dev/null)
        
        if [ -n "$url" ] && [ "$url" != "null" ]; then
            echo "$url"
            return 0
        fi
        
        if [ $i -lt $max_attempts ]; then
            print_status "Waiting for URL to be available... (attempt $i/$max_attempts)"
            sleep $wait_time
        fi
    done
    
    print_error "Could not retrieve application URL after $max_attempts attempts"
    return 1
}

print_status "Starting Azure Container Apps update process..."

# Check if user is logged in to Azure
print_status "Checking Azure CLI login status..."
if ! az account show &> /dev/null; then
    print_warning "You are not logged in to Azure CLI. Please login first."
    az login
fi

# Step 1: Build and push new Docker image to ACR
print_status "Building and pushing updated Docker image to ACR..."
az acr build \
    --registry $ACR_NAME \
    --image $IMAGE_NAME:$IMAGE_TAG \
    --file Dockerfile \
    . \
    --output table

# Step 2: Update the Container App with the new image
print_status "Updating Container App: $APP_NAME"
az containerapp update \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --image $ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG \
    --output table

# Step 3: Get application URL dynamically
print_status "Getting application URL..."
APP_URL=$(get_app_url "$APP_NAME" "$RESOURCE_GROUP")

if [ $? -ne 0 ] || [ -z "$APP_URL" ]; then
    print_error "Failed to get application URL. Check deployment status:"
    echo "az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query '{name: name, status: properties.runningStatus}' --output table"
    exit 1
fi

# Step 4: Test the updated deployment
print_status "Testing the updated deployment..."
sleep 30  # Wait for the app to restart

if curl -f -s -m 30 "https://$APP_URL/health" &> /dev/null; then
    print_success "Update successful! Health check passed."
else
    print_warning "Update completed but health check failed. The app might still be restarting."
    print_status "Manual check: curl https://$APP_URL/health"
fi

print_success "Azure Container Apps update completed!"
echo ""
echo "🌐 Application URL: https://$APP_URL"
echo "🔍 Health Check: https://$APP_URL/health"
echo "📚 API Docs: https://$APP_URL/docs"
echo "🔧 View logs: az containerapp logs show --name $APP_NAME --resource-group $RESOURCE_GROUP --follow"
echo "📋 Get current URL: az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv"

print_success "🎉 Update completed successfully!"
