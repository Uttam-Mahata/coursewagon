#!/bin/bash

# CourseWagon Backend Deployment Verification Script

echo "🔍 CourseWagon Backend Deployment Verification"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RESOURCE_GROUP="coursewagon-rg"
CONTAINER_APP="coursewagon-backend"
CONTAINER_REGISTRY="coursewagoracr"
STORAGE_ACCOUNT="coursewagstorage"

# Function to get application URL dynamically
get_app_url() {
    local app_name="$1"
    local resource_group="$2"
    local url=$(az containerapp show \
        --name "$app_name" \
        --resource-group "$resource_group" \
        --query properties.configuration.ingress.fqdn \
        --output tsv 2>/dev/null)
    
    if [ -n "$url" ] && [ "$url" != "null" ]; then
        echo "$url"
        return 0
    fi
    return 1
}

# Function to check Azure CLI
check_azure_cli() {
    echo -e "${BLUE}Checking Azure CLI...${NC}"
    if ! command -v az &> /dev/null; then
        echo -e "${RED}❌ Azure CLI is not installed${NC}"
        return 1
    fi
    
    if ! az account show &> /dev/null; then
        echo -e "${RED}❌ Not logged in to Azure CLI${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ Azure CLI is ready${NC}"
    return 0
}

# Function to check GitHub CLI
check_github_cli() {
    echo -e "${BLUE}Checking GitHub CLI...${NC}"
    if ! command -v gh &> /dev/null; then
        echo -e "${YELLOW}⚠️  GitHub CLI not found (optional for manual setup)${NC}"
        return 1
    fi
    
    if ! gh auth status &> /dev/null; then
        echo -e "${YELLOW}⚠️  Not logged in to GitHub CLI${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ GitHub CLI is ready${NC}"
    return 0
}

# Function to check Azure resources
check_azure_resources() {
    echo -e "${BLUE}Checking Azure resources...${NC}"
    
    # Check Resource Group
    if az group show --name $RESOURCE_GROUP &> /dev/null; then
        echo -e "${GREEN}✅ Resource Group: $RESOURCE_GROUP${NC}"
    else
        echo -e "${RED}❌ Resource Group: $RESOURCE_GROUP not found${NC}"
        return 1
    fi
    
    # Check Container Registry
    if az acr show --name $CONTAINER_REGISTRY --resource-group $RESOURCE_GROUP &> /dev/null; then
        echo -e "${GREEN}✅ Container Registry: $CONTAINER_REGISTRY${NC}"
    else
        echo -e "${RED}❌ Container Registry: $CONTAINER_REGISTRY not found${NC}"
        return 1
    fi
    
    # Check Storage Account
    if az storage account show --name $STORAGE_ACCOUNT --resource-group $RESOURCE_GROUP &> /dev/null; then
        echo -e "${GREEN}✅ Storage Account: $STORAGE_ACCOUNT${NC}"
    else
        echo -e "${RED}❌ Storage Account: $STORAGE_ACCOUNT not found${NC}"
        return 1
    fi
    
    # Check Container App Environment
    if az containerapp env show --name coursewagon-env --resource-group $RESOURCE_GROUP &> /dev/null; then
        echo -e "${GREEN}✅ Container App Environment: coursewagon-env${NC}"
    else
        echo -e "${YELLOW}⚠️  Container App Environment: coursewagon-env not found${NC}"
        echo -e "${BLUE}   Run the 'Setup Azure Infrastructure' workflow${NC}"
    fi
    
    return 0
}

# Function to check container app deployment
check_deployment() {
    echo -e "${BLUE}Checking deployment status...${NC}"
    
    if az containerapp show --name $CONTAINER_APP --resource-group $RESOURCE_GROUP &> /dev/null; then
        echo -e "${GREEN}✅ Container App: $CONTAINER_APP is deployed${NC}"
        
        # Get app URL dynamically
        APP_URL=$(get_app_url "$CONTAINER_APP" "$RESOURCE_GROUP")
        if [ $? -eq 0 ] && [ -n "$APP_URL" ]; then
            echo -e "${GREEN}🌐 Application URL: https://$APP_URL${NC}"
            
            # Test health endpoint
            echo -e "${BLUE}Testing health endpoint...${NC}"
            if curl -f -s -m 10 "https://$APP_URL/health" &> /dev/null; then
                echo -e "${GREEN}✅ Health check passed${NC}"
                echo -e "${GREEN}📚 API Documentation: https://$APP_URL/docs${NC}"
            else
                echo -e "${RED}❌ Health check failed${NC}"
                echo -e "${YELLOW}   Application may still be starting up${NC}"
                echo -e "${YELLOW}   Manual check: curl https://$APP_URL/health${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️  Could not get application URL dynamically${NC}"
            echo -e "${BLUE}   Try: az containerapp show --name $CONTAINER_APP --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv${NC}"
        fi
        
        # Show container app status
        echo -e "${BLUE}Container App Status:${NC}"
        az containerapp show --name $CONTAINER_APP --resource-group $RESOURCE_GROUP --query "{
            name: name,
            status: properties.runningStatus,
            replicas: properties.template.scale,
            image: properties.template.containers[0].image
        }" --output table
        
    else
        echo -e "${YELLOW}⚠️  Container App: $CONTAINER_APP not deployed yet${NC}"
        echo -e "${BLUE}   Push code to main/master branch to trigger deployment${NC}"
    fi
}

# Function to check GitHub secrets
check_github_secrets() {
    echo -e "${BLUE}Checking GitHub repository...${NC}"
    
    if command -v gh &> /dev/null && gh auth status &> /dev/null; then
        REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "Unknown")
        echo -e "${GREEN}📁 Repository: $REPO${NC}"
        
        # List secrets (names only)
        echo -e "${BLUE}GitHub Secrets configured:${NC}"
        gh secret list --json name -q '.[].name' 2>/dev/null | while read secret; do
            echo -e "${GREEN}   ✅ $secret${NC}"
        done
    else
        echo -e "${YELLOW}⚠️  Cannot check GitHub secrets (GitHub CLI not configured)${NC}"
    fi
}

# Function to show next steps
show_next_steps() {
    echo ""
    echo -e "${BLUE}🎯 Next Steps:${NC}"
    echo -e "${BLUE}==============${NC}"
    
    if ! az group show --name $RESOURCE_GROUP &> /dev/null; then
        echo -e "${YELLOW}1. Run Azure setup script: ./setup-azure.sh${NC}"
    fi
    
    if ! gh auth status &> /dev/null 2>&1; then
        echo -e "${YELLOW}2. Login to GitHub CLI: gh auth login${NC}"
    fi
    
    echo -e "${YELLOW}3. Set up GitHub secrets: ./setup-github-secrets.sh${NC}"
    echo -e "${YELLOW}4. Run 'Setup Azure Infrastructure' workflow in GitHub Actions${NC}"
    echo -e "${YELLOW}5. Push code to main/master branch to trigger deployment${NC}"
    
    echo ""
    echo -e "${BLUE}📖 Documentation:${NC}"
    echo -e "${BLUE}   .github/workflows/README.md${NC}"
    echo ""
}

# Main execution
main() {
    check_azure_cli
    AZURE_OK=$?
    
    check_github_cli
    GITHUB_OK=$?
    
    if [ $AZURE_OK -eq 0 ]; then
        check_azure_resources
        check_deployment
    fi
    
    if [ $GITHUB_OK -eq 0 ]; then
        check_github_secrets
    fi
    
    show_next_steps
}

# Run the main function
main
