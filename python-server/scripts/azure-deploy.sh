# Azure Container Apps configuration
# Deploy using Azure CLI commands

# 1. Create resource group
az group create --name coursewagon-rg --location southeastasia

# 2. Create Azure Container Registry (ACR)
az acr create --resource-group coursewagon-rg --name coursewagoracr --sku Basic --location southeastasia

# 3. Create Azure Storage Account for images
az storage account create \
  --name coursewagstorage \
  --resource-group coursewagon-rg \
  --location southeastasia \
  --sku Standard_LRS \
  --kind StorageV2 \
  --access-tier Hot

# 4. Create storage container for images
az storage container create \
  --name coursewagon-images \
  --account-name coursewagstorage \
  --public-access blob

# 5. Create Container Apps environment
az containerapp env create \
  --name coursewagon-env \
  --resource-group coursewagon-rg \
  --location southeastasia

# 6. Build and push Docker image to ACR
az acr build --registry coursewagoracr --image coursewagon-backend:latest .

# 7. Deploy Container App
az containerapp create \
  --name coursewagon-backend \
  --resource-group coursewagon-rg \
  --environment coursewagon-env \
  --image coursewagoracr.azurecr.io/coursewagon-backend:latest \
  --target-port 8080 \
  --ingress external \
  --registry-server coursewagoracr.azurecr.io \
  --env-vars \
    "API_KEY=$API_KEY" \
    "GEMINI_API_KEY=$GEMINI_API_KEY" \
    "GEMINI_IMAGE_GENERATION_API_KEY=$GEMINI_IMAGE_GENERATION_API_KEY" \
    "DB_HOST=$DB_HOST" \
    "DB_PORT=$DB_PORT" \
    "DB_USER=$DB_USER" \
    "DB_PASS=$DB_PASS" \
    "DB_NAME=$DB_NAME" \
    "JWT_SECRET_KEY=$JWT_SECRET_KEY" \
    "SECRET_KEY=$SECRET_KEY" \
    "SECURITY_PASSWORD_SALT=$SECURITY_PASSWORD_SALT" \
    "ENCRYPTION_KEY=$ENCRYPTION_KEY" \
    "ENCRYPTION_SALT=$ENCRYPTION_SALT" \
    "MAIL_USERNAME=$MAIL_USERNAME" \
    "MAIL_PASSWORD=$MAIL_PASSWORD" \
    "MAILGUN_API_KEY=$MAILGUN_API_KEY" \
    "MAILGUN_DOMAIN=$MAILGUN_DOMAIN" \
    "FRONTEND_URL=$FRONTEND_URL" \
    "AZURE_STORAGE_ACCOUNT_NAME=coursewagstorage" \
    "AZURE_STORAGE_CONTAINER_NAME=coursewagon-images"

# 8. Enable system-assigned managed identity for the container app
az containerapp identity assign \
  --name coursewagon-backend \
  --resource-group coursewagon-rg \
  --system-assigned

# 9. Get the managed identity principal ID
PRINCIPAL_ID=$(az containerapp identity show \
  --name coursewagon-backend \
  --resource-group coursewagon-rg \
  --query principalId -o tsv)

# 10. Assign Storage Blob Data Contributor role to the managed identity
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "Storage Blob Data Contributor" \
  --scope "/subscriptions/$AZURE_SUBSCRIPTION_ID/resourceGroups/coursewagon-rg/providers/Microsoft.Storage/storageAccounts/coursewagstorage"

# Get application URL
az containerapp show \
  --name coursewagon-backend \
  --resource-group coursewagon-rg \
  --query properties.configuration.ingress.fqdn -o tsv
