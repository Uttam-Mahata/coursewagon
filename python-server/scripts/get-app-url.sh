#!/bin/bash

# CourseWagon Backend - Get Application URL Utility
# This script retrieves the current deployed application URL from Azure Container Apps

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RESOURCE_GROUP="coursewagon-rg"
APP_NAME="coursewagon-backend"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to get application URL with retry logic
get_app_url() {
    local max_attempts=3
    local wait_time=5
    
    for i in $(seq 1 $max_attempts); do
        local url=$(az containerapp show \
            --name "$APP_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --query properties.configuration.ingress.fqdn \
            --output tsv 2>/dev/null)
        
        if [ -n "$url" ] && [ "$url" != "null" ]; then
            echo "$url"
            return 0
        fi
        
        if [ $i -lt $max_attempts ]; then
            print_status "Attempt $i failed, retrying in ${wait_time}s..."
            sleep $wait_time
        fi
    done
    
    return 1
}

# Check if Azure CLI is available and user is logged in
if ! command -v az &> /dev/null; then
    print_error "Azure CLI is not installed"
    echo "Install it from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

if ! az account show &> /dev/null; then
    print_error "Not logged in to Azure CLI"
    echo "Run: az login"
    exit 1
fi

print_status "Retrieving application URL for $APP_NAME..."

APP_URL=$(get_app_url)

if [ $? -eq 0 ] && [ -n "$APP_URL" ]; then
    print_success "Application URL retrieved successfully"
    echo ""
    echo "🌐 Application URL: https://$APP_URL"
    echo "🔍 Health Check: https://$APP_URL/health"
    echo "📚 API Documentation: https://$APP_URL/docs"
    echo "📊 OpenAPI Schema: https://$APP_URL/openapi.json"
    echo ""
    
    # Test if the application is responding
    print_status "Testing application availability..."
    if curl -f -s -m 10 "https://$APP_URL/health" &> /dev/null; then
        print_success "✓ Application is responding"
    else
        echo -e "${YELLOW}⚠ Application not responding at health endpoint${NC}"
        echo -e "${YELLOW}  This might be normal if the app is starting up${NC}"
    fi
    
    # Show deployment status
    print_status "Current deployment status:"
    az containerapp show \
        --name "$APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query "{
            name: name,
            status: properties.runningStatus,
            replicas: properties.template.scale.minReplicas,
            maxReplicas: properties.template.scale.maxReplicas,
            image: properties.template.containers[0].image,
            port: properties.configuration.ingress.targetPort
        }" \
        --output table
        
else
    print_error "Could not retrieve application URL"
    echo ""
    echo "Possible reasons:"
    echo "1. Container app is not deployed yet"
    echo "2. Ingress is not configured"
    echo "3. Application is still starting up"
    echo ""
    echo "To check deployment status:"
    echo "az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP"
    echo ""
    echo "To deploy the application:"
    echo "./scripts/deploy-complete.sh"
    exit 1
fi
