# Azure Deployment Guide for CourseWagon Backend

## Overview
This guide will help you deploy the CourseWagon backend to Azure using Azure Container Apps, which is equivalent to Google Cloud Run.

## Prerequisites
- Azure CLI installed and logged in (`az login`)
- Docker installed
- Your environment configured with all necessary variables

## Deployment Steps

### Phase 1: Azure Infrastructure Setup ✅ COMPLETED
You have already completed this phase by running `./setup-azure.sh`. The following resources are created:

- ✅ Resource Group: `coursewagon-rg`
- ✅ Container Registry: `coursewagoracr.azurecr.io`
- ✅ Storage Account: `coursewagstorage`
- ✅ Storage Container: `coursewagon-images`

### Phase 2: Environment Configuration ✅ COMPLETED
Your `.env` file has been updated with:

```bash
# Azure Storage configurations
AZURE_STORAGE_ACCOUNT_NAME=coursewagstorage
AZURE_STORAGE_CONNECTION_STRING="..."
AZURE_STORAGE_CONTAINER_NAME=coursewagon-images

# Azure Deployment configurations
AZURE_RESOURCE_GROUP=coursewagon-rg
AZURE_LOCATION=southeastasia
AZURE_CONTAINER_REGISTRY=coursewagoracr
AZURE_CONTAINER_APP_ENV=coursewagon-env
AZURE_CONTAINER_APP_NAME=coursewagon-backend
```

### Phase 3: Application Deployment

#### Step 1: Test Azure Storage Integration
```bash
# Make sure you're in the virtual environment
source /home/uttam/CourseWagon/.venv/bin/activate

# Test the Azure Storage integration
python test_azure_storage.py
```

#### Step 2: Deploy Container App
```bash
# Run the container deployment script
./deploy-container.sh
```

#### Step 3: Verify Deployment
After deployment, test your endpoints:
```bash
# Get the application URL
az containerapp show \
  --name coursewagon-backend \
  --resource-group coursewagon-rg \
  --query properties.configuration.ingress.fqdn -o tsv

# Test the health endpoint
curl https://YOUR-APP-URL/health
```

## Key Changes Made

### 1. Storage Migration
- ✅ Migrated from Firebase Storage to Azure Blob Storage
- ✅ Updated `ImageService` to use Azure Storage
- ✅ Updated `CourseService` to use Azure Storage
- ✅ Implemented SAS token-based secure access

### 2. Code Updates
- ✅ Created `AzureStorageHelper` class
- ✅ Updated service classes to use Azure Storage
- ✅ Added Azure packages to requirements.txt

### 3. Configuration
- ✅ Added Azure configurations to config.py
- ✅ Updated .env with Azure Storage settings

## Monitoring and Management

### View Container Logs
```bash
az containerapp logs show \
  --name coursewagon-backend \
  --resource-group coursewagon-rg \
  --follow
```

### Update Container App
```bash
# After making code changes, rebuild and update:
az acr build --registry coursewagoracr --image coursewagon-backend:latest .

az containerapp update \
  --name coursewagon-backend \
  --resource-group coursewagon-rg \
  --image coursewagoracr.azurecr.io/coursewagon-backend:latest
```

### Scale Container App
```bash
az containerapp update \
  --name coursewagon-backend \
  --resource-group coursewagon-rg \
  --min-replicas 1 \
  --max-replicas 10
```

## Cost Management
- Azure Container Apps uses a consumption-based pricing model
- Storage account uses standard blob storage pricing
- Container Registry Basic tier is cost-effective for this use case

## Security Notes
- Storage containers are private by default
- Images are accessed via SAS tokens with 1-year expiration
- All sensitive data is stored as secrets in Container Apps
- HTTPS is enforced for all traffic

## Troubleshooting

### Common Issues
1. **Container fails to start**: Check logs with `az containerapp logs show`
2. **Image upload fails**: Verify Azure Storage connection string
3. **Database connection fails**: Check if your database allows Azure IP ranges

### Useful Commands
```bash
# Check container app status
az containerapp show --name coursewagon-backend --resource-group coursewagon-rg

# Restart container app
az containerapp restart --name coursewagon-backend --resource-group coursewagon-rg

# View container app configuration
az containerapp show --name coursewagon-backend --resource-group coursewagon-rg --output yaml
```

## Next Steps
1. Run `./deploy-container.sh` to deploy your application
2. Update your frontend to use the new Azure backend URL
3. Configure custom domain if needed
4. Set up monitoring and alerting
