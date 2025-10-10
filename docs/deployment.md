---
layout: default
title: Deployment Guide
nav_order: 7
description: "Deploy CourseWagon to production environments"
---

# Deployment Guide
{: .no_toc }

Step-by-step guide to deploy CourseWagon to production.
{: .fs-6 .fw-300 }

## Table of Contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Overview

CourseWagon can be deployed to various cloud platforms. This guide covers the recommended deployment configurations:

- **Frontend**: Firebase Hosting (recommended) or any static hosting
- **Backend**: Google Cloud Run (recommended) or Azure Container Apps
- **Database**: MySQL (Cloud SQL, Azure Database, or self-hosted)
- **Storage**: Google Cloud Storage (primary), Azure Blob Storage (fallback)

---

## Prerequisites

Before deploying, ensure you have:

- ✅ Google Cloud account (for Cloud Run & GCS)
- ✅ Firebase project configured
- ✅ MySQL database (cloud or self-hosted)
- ✅ Domain name (optional, for custom domains)
- ✅ All API keys (Gemini AI, Firebase, etc.)

---

## Frontend Deployment (Firebase Hosting)

### Step 1: Install Firebase CLI

```bash
npm install -g firebase-tools
```

### Step 2: Login to Firebase

```bash
firebase login
```

### Step 3: Initialize Firebase in Your Project

```bash
cd angular-client
firebase init
```

Select:
- ✅ Hosting
- Choose your Firebase project
- Public directory: `dist/angular-client/browser`
- Single-page app: Yes
- GitHub Actions: No (we'll use manual deployment)

### Step 4: Update Production Environment

Edit `src/environments/environment.prod.ts`:

```typescript
export const environment = {
  production: true,
  apiUrl: 'https://your-backend-url.run.app/api',
  firebase: {
    apiKey: "YOUR_PROD_FIREBASE_API_KEY",
    authDomain: "your-project.firebaseapp.com",
    projectId: "your-project-id",
    storageBucket: "your-project.appspot.com",
    messagingSenderId: "YOUR_SENDER_ID",
    appId: "YOUR_APP_ID"
  }
};
```

### Step 5: Build for Production

```bash
npm run build
```

This creates optimized production files in `dist/angular-client/browser/`.

### Step 6: Deploy to Firebase

```bash
firebase deploy --only hosting
```

### Step 7: Configure Custom Domain (Optional)

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Navigate to Hosting
3. Click "Add custom domain"
4. Follow instructions to verify domain ownership
5. Update DNS records as instructed

---

## Backend Deployment (Google Cloud Run)

### Option 1: Automated Deployment with GitHub Actions

#### Step 1: Set Up Google Cloud Project

```bash
# Install Google Cloud SDK
# Visit: https://cloud.google.com/sdk/docs/install

# Login
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID
```

#### Step 2: Enable Required APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

#### Step 3: Create Service Account

```bash
# Create service account for GitHub Actions
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions"

# Grant necessary permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.builder"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Create and download key
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

#### Step 4: Upload Secrets to Secret Manager

```bash
# Create secrets from .env file
cat python-server/.env | while read line; do
  if [[ ! -z "$line" && ! "$line" =~ ^# ]]; then
    key=$(echo $line | cut -d '=' -f 1)
    value=$(echo $line | cut -d '=' -f 2-)
    echo -n "$value" | gcloud secrets create "COURSEWAGON-$key" --data-file=- || \
    echo -n "$value" | gcloud secrets versions add "COURSEWAGON-$key" --data-file=-
  fi
done
```

#### Step 5: Add GitHub Secret

1. Go to GitHub repository settings
2. Navigate to: Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `GITHUB_ACTIONS_KEY`
5. Value: Contents of `github-actions-key.json`

#### Step 6: The GitHub Actions Workflow

The workflow is already configured in `.github/workflows/deploy.yml`. It will:
- Trigger on push to `main` branch
- Build Docker image using Cloud Build
- Deploy to Cloud Run
- Mount secrets from Secret Manager

Just push to main:
```bash
git push origin main
```

### Option 2: Manual Deployment

#### Step 1: Build Docker Image

```bash
cd python-server

# Build image
docker build -t coursewagon-api .

# Test locally
docker run -p 8000:8000 --env-file .env coursewagon-api
```

#### Step 2: Push to Artifact Registry

```bash
# Create repository
gcloud artifacts repositories create coursewagon-repo \
  --repository-format=docker \
  --location=us-central1

# Tag image
docker tag coursewagon-api \
  us-central1-docker.pkg.dev/YOUR_PROJECT_ID/coursewagon-repo/coursewagon-api:latest

# Configure Docker auth
gcloud auth configure-docker us-central1-docker.pkg.dev

# Push image
docker push \
  us-central1-docker.pkg.dev/YOUR_PROJECT_ID/coursewagon-repo/coursewagon-api:latest
```

#### Step 3: Deploy to Cloud Run

```bash
gcloud run deploy coursewagon-api \
  --image=us-central1-docker.pkg.dev/YOUR_PROJECT_ID/coursewagon-repo/coursewagon-api:latest \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --set-env-vars="DATABASE_URL=$DATABASE_URL" \
  --set-env-vars="JWT_SECRET_KEY=$JWT_SECRET_KEY" \
  # ... add all environment variables
```

**Or with secrets from Secret Manager:**

```bash
gcloud run deploy coursewagon-api \
  --image=us-central1-docker.pkg.dev/YOUR_PROJECT_ID/coursewagon-repo/coursewagon-api:latest \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --set-secrets="DATABASE_URL=COURSEWAGON-DATABASE_URL:latest" \
  --set-secrets="JWT_SECRET_KEY=COURSEWAGON-JWT_SECRET_KEY:latest"
  # ... add all secrets
```

---

## Backend Deployment (Azure Container Apps)

### Step 1: Install Azure CLI

```bash
# Visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

# Login
az login
```

### Step 2: Create Resources

```bash
# Create resource group
az group create --name coursewagon-rg --location eastus

# Create container registry
az acr create --resource-group coursewagon-rg \
  --name coursewagonacr --sku Basic

# Create container app environment
az containerapp env create \
  --name coursewagon-env \
  --resource-group coursewagon-rg \
  --location eastus
```

### Step 3: Build and Push Docker Image

```bash
cd python-server

# Login to ACR
az acr login --name coursewagonacr

# Build and push
az acr build --registry coursewagonacr \
  --image coursewagon-api:latest .
```

### Step 4: Deploy Container App

```bash
az containerapp create \
  --name coursewagon-api \
  --resource-group coursewagon-rg \
  --environment coursewagon-env \
  --image coursewagonacr.azurecr.io/coursewagon-api:latest \
  --target-port 8000 \
  --ingress 'external' \
  --registry-server coursewagonacr.azurecr.io \
  --env-vars "DATABASE_URL=secretref:database-url" \
  --secrets "database-url=$DATABASE_URL"
  # ... add all environment variables and secrets
```

---

## Database Setup

### Option 1: Google Cloud SQL

```bash
# Create MySQL instance
gcloud sql instances create coursewagon-db \
  --database-version=MYSQL_8_0 \
  --tier=db-f1-micro \
  --region=us-central1

# Create database
gcloud sql databases create coursewagon \
  --instance=coursewagon-db

# Create user
gcloud sql users create coursewagon-user \
  --instance=coursewagon-db \
  --password=YOUR_SECURE_PASSWORD
```

**Connection String:**
```
mysql+pymysql://coursewagon-user:password@/coursewagon?unix_socket=/cloudsql/PROJECT:REGION:coursewagon-db
```

### Option 2: Azure Database for MySQL

```bash
# Create MySQL server
az mysql flexible-server create \
  --resource-group coursewagon-rg \
  --name coursewagon-mysql \
  --location eastus \
  --admin-user coursewagonadmin \
  --admin-password YOUR_SECURE_PASSWORD \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --version 8.0.21

# Create database
az mysql flexible-server db create \
  --resource-group coursewagon-rg \
  --server-name coursewagon-mysql \
  --database-name coursewagon
```

**Connection String:**
```
mysql+pymysql://coursewagonadmin:password@coursewagon-mysql.mysql.database.azure.com:3306/coursewagon
```

---

## Storage Configuration

### Google Cloud Storage

```bash
# Create bucket
gsutil mb -p YOUR_PROJECT_ID \
  -c STANDARD \
  -l us-central1 \
  gs://coursewagon-storage-bucket

# Make publicly accessible
gsutil iam ch allUsers:objectViewer \
  gs://coursewagon-storage-bucket

# Create service account for storage
gcloud iam service-accounts create coursewagon-storage \
  --display-name="CourseWagon Storage"

# Grant storage permissions
gsutil iam ch \
  serviceAccount:coursewagon-storage@YOUR_PROJECT_ID.iam.gserviceaccount.com:objectAdmin \
  gs://coursewagon-storage-bucket

# Create and download key
gcloud iam service-accounts keys create gcs-service-account.json \
  --iam-account=coursewagon-storage@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

### Azure Blob Storage

```bash
# Create storage account
az storage account create \
  --name coursewagonstorage \
  --resource-group coursewagon-rg \
  --location eastus \
  --sku Standard_LRS

# Create container
az storage container create \
  --name coursewagon-images \
  --account-name coursewagonstorage \
  --public-access blob

# Get connection string
az storage account show-connection-string \
  --name coursewagonstorage \
  --resource-group coursewagon-rg
```

---

## Environment Variables

### Complete Environment Configuration

Create a comprehensive `.env` file for production:

```bash
# Database
DATABASE_URL=mysql+pymysql://user:password@host:3306/coursewagon

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_REFRESH_SECRET_KEY=your-refresh-secret-key
JWT_ACCESS_TOKEN_EXPIRES_HOURS=1
JWT_REFRESH_TOKEN_EXPIRES_DAYS=30

# Google Gemini AI
GEMINI_API_KEY=your-gemini-api-key

# Firebase
FIREBASE_CREDENTIALS_PATH=/app/coursewagon-firebase-adminsdk.json

# Google Cloud Storage
GCS_BUCKET_NAME=coursewagon-storage-bucket
GCS_PROJECT_ID=your-project-id
GCS_CREDENTIALS_PATH=/app/gcs-service-account.json

# Azure Storage (Fallback)
AZURE_STORAGE_CONNECTION_STRING=your-azure-connection-string

# Email (Gmail)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com

# Email (Mailgun Backup)
MAILGUN_API_KEY=your-mailgun-api-key
MAILGUN_DOMAIN=mg.yourdomain.com

# CORS
CORS_ORIGINS=https://www.coursewagon.live,https://coursewagon.live

# Application
LOG_LEVEL=INFO
```

---

## Post-Deployment

### 1. Verify Deployment

**Backend Health Check:**
```bash
curl https://your-backend-url.run.app/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-10-10T15:30:00Z"
}
```

### 2. Test Authentication

Visit your frontend and try to:
- Sign up a new account
- Log in
- Create a course
- Generate content

### 3. Monitor Logs

**Google Cloud Run:**
```bash
gcloud logging read "resource.type=cloud_run_revision" --limit 50
```

**Azure Container Apps:**
```bash
az containerapp logs show \
  --name coursewagon-api \
  --resource-group coursewagon-rg
```

### 4. Set Up Monitoring

**Google Cloud Monitoring:**
- Enable Cloud Monitoring
- Set up alerts for errors and latency
- Create dashboards

**Azure Monitor:**
- Enable Application Insights
- Set up alerts
- Create dashboards

---

## SSL/TLS Configuration

### Firebase Hosting

Firebase automatically provisions SSL certificates for:
- Default domain (`*.web.app`, `*.firebaseapp.com`)
- Custom domains

### Cloud Run

Cloud Run automatically provides HTTPS endpoints.

### Custom Domain

For custom domain with Cloud Run:

```bash
# Map domain
gcloud run domain-mappings create \
  --service coursewagon-api \
  --domain api.coursewagon.live \
  --region us-central1
```

Then update your DNS:
```
CNAME api.coursewagon.live -> ghs.googlehosted.com
```

---

## Performance Optimization

### Cloud Run Configuration

```bash
gcloud run deploy coursewagon-api \
  --image=... \
  --min-instances=1 \        # Keep 1 instance warm
  --max-instances=10 \       # Scale up to 10
  --memory=512Mi \           # Allocate 512MB RAM
  --cpu=1 \                  # 1 vCPU
  --concurrency=80 \         # Handle 80 concurrent requests
  --timeout=300              # 5 minute timeout
```

### Database Connection Pooling

Already configured in `extensions.py`:
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)
```

### CDN Configuration

Firebase Hosting includes CDN automatically.

For additional CDN:
- Configure Cloud CDN with Cloud Run
- Or use Cloudflare in front of your domain

---

## Backup Strategy

### Database Backups

**Cloud SQL:**
```bash
# Enable automated backups
gcloud sql instances patch coursewagon-db \
  --backup-start-time=03:00 \
  --enable-bin-log
```

**Manual Backup:**
```bash
gcloud sql backups create \
  --instance=coursewagon-db
```

### Storage Backups

**GCS Versioning:**
```bash
gsutil versioning set on gs://coursewagon-storage-bucket
```

**Lifecycle Management:**
```bash
# Create lifecycle.json
{
  "rule": [{
    "action": {"type": "Delete"},
    "condition": {"age": 365}
  }]
}

# Apply lifecycle policy
gsutil lifecycle set lifecycle.json gs://coursewagon-storage-bucket
```

---

## Scaling Considerations

### Horizontal Scaling

**Cloud Run** auto-scales based on traffic:
- Scales to zero when no requests
- Automatically adds instances under load
- Pay only for what you use

### Database Scaling

**Vertical Scaling:**
```bash
# Upgrade Cloud SQL tier
gcloud sql instances patch coursewagon-db \
  --tier=db-n1-standard-1
```

**Read Replicas:**
```bash
# Create read replica
gcloud sql instances create coursewagon-db-replica \
  --master-instance-name=coursewagon-db \
  --region=us-east1
```

---

## Cost Optimization

### Estimated Monthly Costs

**Small Scale (< 1000 users):**
- Cloud Run: ~$10-20
- Cloud SQL: ~$25-50 (f1-micro)
- Firebase Hosting: Free (Spark plan) or $25 (Blaze)
- Cloud Storage: ~$5-10
- **Total: ~$65-105/month**

**Medium Scale (1000-10000 users):**
- Cloud Run: ~$50-100
- Cloud SQL: ~$100-200
- Firebase Hosting: ~$25
- Cloud Storage: ~$20-40
- **Total: ~$195-365/month**

### Cost Reduction Tips

1. **Use minimum instances wisely**
   - Set min-instances=0 for dev environments
   - Use min-instances=1 only for production

2. **Optimize database tier**
   - Start with f1-micro
   - Upgrade only when needed

3. **Implement caching**
   - Use Redis for frequently accessed data
   - Reduce database queries

4. **Monitor and alert**
   - Set up budget alerts
   - Monitor for unusual spikes

---

## Troubleshooting

### Deployment Fails

**Check logs:**
```bash
# Cloud Build logs
gcloud builds log [BUILD_ID]

# Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50
```

**Common issues:**
- Missing environment variables
- Invalid secrets
- Database connection errors
- Insufficient permissions

### Application Errors

**500 Internal Server Error:**
- Check application logs
- Verify database connectivity
- Verify all secrets are set

**Authentication Failures:**
- Verify Firebase credentials
- Check JWT secret keys
- Verify CORS origins

### Database Connection Issues

**Cloud SQL:**
- Verify Cloud SQL Admin API is enabled
- Check connection string format
- Verify service account has cloudsql.client role

---

## Security Checklist

- [ ] All secrets stored in Secret Manager
- [ ] HTTPS enabled on all endpoints
- [ ] CORS properly configured
- [ ] Database credentials rotated
- [ ] Service account permissions minimal
- [ ] Rate limiting configured
- [ ] Backups enabled
- [ ] Monitoring and alerts set up
- [ ] Firewall rules configured
- [ ] Dependencies updated

---

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/deploy.yml`) handles:

1. ✅ Checkout code
2. ✅ Authenticate with Google Cloud
3. ✅ Build Docker image with Cloud Build
4. ✅ Push to Artifact Registry
5. ✅ Deploy to Cloud Run
6. ✅ Run health check
7. ✅ Notify on success/failure

**Trigger deployment:**
```bash
git push origin main
```

---

## Rollback Procedure

### Cloud Run Rollback

```bash
# List revisions
gcloud run revisions list --service=coursewagon-api

# Rollback to previous revision
gcloud run services update-traffic coursewagon-api \
  --to-revisions=coursewagon-api-00002-abc=100
```

### Database Rollback

```bash
# Restore from backup
gcloud sql backups restore [BACKUP_ID] \
  --backup-instance=coursewagon-db \
  --backup-id=[BACKUP_ID]
```

---

## Monitoring and Logging

### Key Metrics to Monitor

- **Request rate**: Requests per second
- **Error rate**: 4xx and 5xx responses
- **Latency**: P50, P95, P99 response times
- **Database connections**: Active connections
- **Storage usage**: Bytes stored

### Setting Up Alerts

**Cloud Monitoring:**
```bash
# Create alert policy for error rate
gcloud alpha monitoring policies create \
  --notification-channels=[CHANNEL_ID] \
  --display-name="High Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05
```

---

## Next Steps After Deployment

1. 📊 Set up monitoring and alerts
2. 🔄 Configure automated backups
3. 🚀 Set up staging environment
4. 📈 Implement analytics
5. 🔒 Security audit
6. 📝 Document custom configurations
7. 🧪 Load testing

---

## Need Help?

- 📧 Email: [contact@coursewagon.live](mailto:contact@coursewagon.live)
- 🐛 Issues: [GitHub Issues](https://github.com/Uttam-Mahata/coursewagon/issues)
- 📖 Docs: [Getting Started](getting-started) | [Architecture](architecture)
