#!/bin/bash

# CourseWagon Azure Storage Setup Script
# This script creates Azure Storage resources and retrieves the connection string

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== CourseWagon Azure Storage Setup ===${NC}"

# Configuration
RESOURCE_GROUP="coursewagon-rg"
LOCATION="southeastasia"
STORAGE_ACCOUNT="coursewagstorage"
CONTAINER_NAME="coursewagon-images"

echo -e "${YELLOW}Using configuration:${NC}"
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo "Storage Account: $STORAGE_ACCOUNT"
echo "Container Name: $CONTAINER_NAME"
echo

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

echo -e "${BLUE}Step 1: Creating Resource Group...${NC}"
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION \
    --output table

echo -e "${BLUE}Step 2: Creating Storage Account...${NC}"
az storage account create \
    --name $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku Standard_LRS \
    --kind StorageV2 \
    --access-tier Hot \
    --allow-blob-public-access true \
    --output table

echo -e "${BLUE}Step 3: Getting Storage Account Key...${NC}"
STORAGE_KEY=$(az storage account keys list \
    --resource-group $RESOURCE_GROUP \
    --account-name $STORAGE_ACCOUNT \
    --query '[0].value' \
    --output tsv)

echo -e "${BLUE}Step 4: Creating Blob Container...${NC}"
az storage container create \
    --name $CONTAINER_NAME \
    --account-name $STORAGE_ACCOUNT \
    --account-key $STORAGE_KEY \
    --public-access blob \
    --output table

echo -e "${BLUE}Step 5: Getting Connection String...${NC}"
CONNECTION_STRING=$(az storage account show-connection-string \
    --resource-group $RESOURCE_GROUP \
    --name $STORAGE_ACCOUNT \
    --output tsv)

echo -e "${GREEN}=== Azure Storage Setup Complete! ===${NC}"
echo
echo -e "${YELLOW}Storage Account Details:${NC}"
echo "Account Name: $STORAGE_ACCOUNT"
echo "Container Name: $CONTAINER_NAME"
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo

echo -e "${YELLOW}Add these to your .env file:${NC}"
echo "AZURE_STORAGE_ACCOUNT_NAME=$STORAGE_ACCOUNT"
echo "AZURE_STORAGE_CONTAINER_NAME=$CONTAINER_NAME"
echo "AZURE_STORAGE_CONNECTION_STRING=\"$CONNECTION_STRING\""
echo

# Save to a temporary file for easy copying
cat > .env.azure.temp << EOF
# Azure Storage Configuration
AZURE_STORAGE_ACCOUNT_NAME=$STORAGE_ACCOUNT
AZURE_STORAGE_CONTAINER_NAME=$CONTAINER_NAME
AZURE_STORAGE_CONNECTION_STRING="$CONNECTION_STRING"
EOF

echo -e "${GREEN}Connection string saved to .env.azure.temp${NC}"
echo -e "${YELLOW}You can copy these values to your .env file${NC}"
echo

# Test the storage account
echo -e "${BLUE}Step 6: Testing Storage Account...${NC}"
az storage blob list \
    --container-name $CONTAINER_NAME \
    --account-name $STORAGE_ACCOUNT \
    --account-key $STORAGE_KEY \
    --output table

echo -e "${GREEN}Storage account is working correctly!${NC}"
echo
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Copy the environment variables to your .env file"
echo "2. Run your application to test the storage connection"
echo "3. Deploy to Azure Container Apps if needed"
