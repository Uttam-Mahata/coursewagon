#!/bin/bash

# Quick update script for Azure Container Apps deployment
# This rebuilds and redeploys the application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== CourseWagon Backend - Quick Update ===${NC}"

# Configuration (using consistent port 8000 for FastAPI)
RESOURCE_GROUP="coursewagon-rg"
ACR_NAME="coursewagoracr"
APP_NAME="coursewagon-backend"
IMAGE_NAME="coursewagon-backend"
TAG="latest"
TARGET_PORT="8000"

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

# Function to test health endpoint
test_health_endpoint() {
    local app_url="$1"
    local max_attempts=3
    local wait_time=15
    
    echo -e "${BLUE}Testing health endpoint...${NC}"
    
    for i in $(seq 1 $max_attempts); do
        echo -e "${BLUE}Attempt $i/$max_attempts - Testing https://$app_url/health${NC}"
        
        if curl -f -s -m 30 "https://$app_url/health" &> /dev/null; then
            echo -e "${GREEN}✓ Application is responding at health endpoint${NC}"
            return 0
        else
            if [ $i -lt $max_attempts ]; then
                echo -e "${YELLOW}Health check failed. Waiting ${wait_time}s before retry...${NC}"
                sleep $wait_time
            fi
        fi
    done
    
    echo -e "${YELLOW}⚠ Health check failed after $max_attempts attempts. Application might still be restarting.${NC}"
    return 1
}

echo -e "${BLUE}Step 1: Building and pushing updated Docker image...${NC}"
# Use Azure Container Registry to build the image directly from source
az acr build \
    --registry $ACR_NAME \
    --image $IMAGE_NAME:$TAG \
    --file Dockerfile \
    . \
    --platform linux

echo -e "${BLUE}Step 2: Updating Container App...${NC}"
az containerapp update \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --image "$ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG"

echo -e "${BLUE}Step 3: Getting application URL dynamically...${NC}"
APP_URL=$(get_app_url "$APP_NAME" "$RESOURCE_GROUP")

if [ -z "$APP_URL" ]; then
    echo -e "${RED}Error: Could not retrieve application URL${NC}"
    echo -e "${YELLOW}Check deployment status manually:${NC}"
    echo "az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP"
    exit 1
fi

echo -e "${GREEN}=== Update Complete! ===${NC}"
echo
echo -e "${YELLOW}Application URL: https://$APP_URL${NC}"
echo -e "${YELLOW}Health Endpoint: https://$APP_URL/health${NC}"
echo -e "${YELLOW}API Docs: https://$APP_URL/docs${NC}"
echo

# Test the updated deployment
test_health_endpoint "$APP_URL"

echo -e "${GREEN}✓ Deployment completed successfully${NC}"
echo -e "${BLUE}Useful commands:${NC}"
echo "View logs: az containerapp logs show --name $APP_NAME --resource-group $RESOURCE_GROUP --follow"
echo "Get URL: az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv"
