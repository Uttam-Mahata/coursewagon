# Migration to Cloud Run Service Identity

This document outlines the migration from using explicit service account keys (`GOOGLE_APPLICATION_CREDENTIALS`) to using Cloud Run's built-in service identity for Google Cloud API authentication.

## What Changed

### 1. Deployment Configuration (.github/workflows/deploy.yml)
- **Removed**: `GOOGLE_APPLICATION_CREDENTIALS` environment variable
- **Removed**: GCS service account JSON secret mount (`/etc/secrets/gcs/service-account.json`)
- **Kept**: Firebase Admin SDK credentials (Firebase requires explicit credentials)

### 2. GCS Storage Helper (python-server/utils/gcs_storage_helper.py)
- **Changed**: Now prefers Application Default Credentials (ADC) over explicit credentials
- **Benefit**: Automatically uses Cloud Run service identity for authentication
- **Fallback**: Still supports explicit credentials for local development

## Why This Is Better

1. **Security**: No need to store or manage service account keys in secrets
2. **Simplicity**: Cloud Run automatically handles authentication via metadata server
3. **Best Practice**: Google Cloud recommends using service identity over key files
4. **Automatic Rotation**: Service identity credentials are automatically rotated by Google

## Required Permissions

Ensure the Cloud Run service account has the necessary IAM permissions:

```bash
# Get the service account email (usually: PROJECT_NUMBER-compute@developer.gserviceaccount.com)
gcloud run services describe coursewagon-api --region=us-central1 --format='value(spec.template.spec.serviceAccountName)'

# Grant Storage Admin role (or more granular permissions)
gcloud projects add-iam-policy-binding mitra-348d9 \
  --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
  --role="roles/storage.admin"

# Or use more granular permissions:
gcloud projects add-iam-policy-binding mitra-348d9 \
  --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
  --role="roles/storage.objectAdmin"
```

**Alternative**: Grant permissions directly on the GCS bucket:

```bash
gsutil iam ch serviceAccount:SERVICE_ACCOUNT_EMAIL:objectAdmin gs://coursewagon-storage-bucket
```

## Deployment Steps

1. **Commit and push changes**:
   ```bash
   git add .github/workflows/deploy.yml python-server/utils/gcs_storage_helper.py
   git commit -m "Migrate to Cloud Run service identity for GCS authentication"
   git push origin main
   ```

2. **Verify IAM permissions** (see above)

3. **Deploy the updated application** (GitHub Actions will trigger automatically)

4. **Monitor logs** for successful GCS initialization:
   ```bash
   gcloud run services logs read coursewagon-api --region=us-central1 --limit=50
   ```

   Look for: `"GCS initialized with Application Default Credentials (service identity)"`

## Testing

### In Production (Cloud Run)
- Upload an image via your API
- Check logs to confirm ADC is being used
- Verify image appears in GCS bucket

### Local Development
- Set `GOOGLE_APPLICATION_CREDENTIALS` to a service account key file path
- Run the application locally
- It should fallback to explicit credentials automatically

## Troubleshooting

### Error: "Failed to initialize with ADC"
**Cause**: Service account lacks necessary permissions

**Solution**: Grant `roles/storage.objectAdmin` or `roles/storage.admin` to the Cloud Run service account

### Error: "Could not create/access bucket"
**Cause**: Service account doesn't have permission to create buckets

**Solution**:
- Either grant `roles/storage.admin` (allows bucket creation)
- Or manually create the bucket and grant `roles/storage.objectAdmin`

### Local Development Issues
**Solution**: Set up Application Default Credentials locally:
```bash
gcloud auth application-default login
```

Or use a service account key:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

## Rollback Plan

If you need to rollback, restore the previous configuration:

1. Add back to `.github/workflows/deploy.yml`:
   ```yaml
   --set-env-vars="GOOGLE_APPLICATION_CREDENTIALS=/etc/secrets/gcs/service-account.json,..." \
   --set-secrets="/etc/secrets/gcs/service-account.json=COURSEWAGON-GCS-SERVICE-ACCOUNT-JSON:latest,..."
   ```

2. Revert `gcs_storage_helper.py` to check credentials file first:
   ```bash
   git revert <commit-hash>
   ```

## Notes

- Firebase Admin SDK still uses explicit credentials (this is expected and correct)
- The `COURSEWAGON-GCS-SERVICE-ACCOUNT-JSON` secret in Google Cloud Secret Manager is no longer needed but kept for backward compatibility
- This change only affects production/Cloud Run deployments; local development workflow remains the same
