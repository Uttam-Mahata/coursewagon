#!/bin/bash

# Azure Deployment Setup Script for CourseWagon Backend

echo "🚀 Setting up Azure deployment for CourseWagon Backend"
echo "=================================================="

# Check if Azure CLI is installed and logged in
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first."
    exit 1
fi

# Check if logged in
if ! az account show &> /dev/null; then
    echo "❌ Not logged in to Azure CLI. Please run 'az login' first."
    exit 1
fi

echo "✅ Azure CLI is installed and you are logged in"

# Set environment variables
export RESOURCE_GROUP="coursewagon-rg"
export LOCATION="southeastasia"
export ACR_NAME="coursewagoracr"
export STORAGE_ACCOUNT="coursewagstorage"
export CONTAINER_NAME="coursewagon-images"
export APP_ENV="coursewagon-env"
export APP_NAME="coursewagon-backend"

echo "📋 Configuration:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Location: $LOCATION"
echo "  Container Registry: $ACR_NAME"
echo "  Storage Account: $STORAGE_ACCOUNT"
echo ""

# Step 1: Create Resource Group
echo "1️⃣  Creating Resource Group..."
az group create --name $RESOURCE_GROUP --location $LOCATION --output table

# Step 2: Create Azure Container Registry
echo "2️⃣  Creating Azure Container Registry..."
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --location $LOCATION --output table

# Step 3: Create Storage Account
echo "3️⃣  Creating Storage Account..."
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS \
  --kind StorageV2 \
  --access-tier Hot \
  --output table

# Step 4: Create Storage Container
echo "4️⃣  Creating Storage Container..."
az storage container create \
  --name $CONTAINER_NAME \
  --account-name $STORAGE_ACCOUNT \
  --public-access blob \
  --output table

# Step 5: Get Storage Connection String
echo "5️⃣  Getting Storage Connection String..."
STORAGE_CONNECTION_STRING=$(az storage account show-connection-string --name $STORAGE_ACCOUNT --resource-group $RESOURCE_GROUP --query connectionString -o tsv)

# Update .env file with Azure Storage configuration
echo "6️⃣  Updating .env file with Azure Storage configuration..."
sed -i "s/^AZURE_STORAGE_ACCOUNT_NAME=.*/AZURE_STORAGE_ACCOUNT_NAME=$STORAGE_ACCOUNT/" .env
sed -i "s|^AZURE_STORAGE_CONNECTION_STRING=.*|AZURE_STORAGE_CONNECTION_STRING=\"$STORAGE_CONNECTION_STRING\"|" .env
sed -i "s/^AZURE_STORAGE_CONTAINER_NAME=.*/AZURE_STORAGE_CONTAINER_NAME=$CONTAINER_NAME/" .env

echo "✅ Azure resources created successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Install Azure packages: pip install azure-storage-blob azure-identity"
echo "2. Test your application locally with the new Azure Storage configuration"
echo "3. When ready to deploy, run the container deployment commands"
echo ""
echo "🔗 Storage account URL: https://$STORAGE_ACCOUNT.blob.core.windows.net"
echo "🔗 Container URL: https://$STORAGE_ACCOUNT.blob.core.windows.net/$CONTAINER_NAME"
echo ""
echo "⚠️  Remember to add all your environment variables from .env to the container app when deploying!"
