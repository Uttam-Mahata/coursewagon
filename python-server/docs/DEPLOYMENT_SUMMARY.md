# CourseWagon Backend - Quick Deployment Summary

## Files Created for Azure Deployment

1. **`deploy-to-azure.sh`** - Complete initial deployment script
2. **`update-azure-deployment.sh`** - Update existing deployment
3. **`manage-env-vars.sh`** - Manage environment variables
4. **`AZURE_DEPLOYMENT_GUIDE.md`** - Comprehensive deployment guide

## Quick Commands

### Deploy for the first time:
```bash
chmod +x deploy-to-azure.sh
./deploy-to-azure.sh
```

### Update after code changes:
```bash
./update-azure-deployment.sh
```

### Update environment variables:
```bash
./manage-env-vars.sh
```

### View logs:
```bash
az containerapp logs show --name coursewagon-backend --resource-group coursewagon-rg --follow
```

### Get application URL:
```bash
az containerapp show --name coursewagon-backend --resource-group coursewagon-rg --query properties.configuration.ingress.fqdn -o tsv
```

## Azure Resources

The deployment creates:
- Resource Group: `coursewagon-rg`
- Container Registry: `coursewagoracr.azurecr.io`
- Storage Account: `coursewagstorage`
- Container App: `coursewagon-backend`

## Key Features

✅ **Automated Deployment**: One command deployment
✅ **Environment Variables**: Secure handling from .env file
✅ **Azure Storage**: Configured for image storage
✅ **Managed Identity**: Secure access to Azure resources
✅ **Health Checks**: Built-in monitoring
✅ **Scaling**: Auto-scaling configured
✅ **Logging**: Azure Container Apps logging
✅ **HTTPS**: Automatically enabled

## Prerequisites

1. Azure CLI installed and logged in
2. .env file with all required environment variables
3. Docker (for local testing - optional)

## Notes

- The subject service has been updated to use Azure Storage instead of Firebase
- All image uploads now go through Azure Blob Storage
- Environment variables are securely managed through Azure Container Apps
- The deployment includes proper health checks and monitoring
