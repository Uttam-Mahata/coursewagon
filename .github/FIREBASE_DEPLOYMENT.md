# Firebase Deployment Setup

This repository uses GitHub Actions to automatically deploy to Firebase Hosting.

## Required GitHub Secrets

To enable automatic deployments, you need to set up the following secrets in your GitHub repository:

**Settings → Secrets and variables → Actions → New repository secret**

### API Configuration
- `API_URL` - Production API URL (e.g., `https://api.coursewagon.live/api`)
- `API_BASE_URL` - Production API base URL (same as API_URL)
- `COURSE_API_URL` - Course API endpoint (e.g., `https://api.coursewagon.live/api/courses`)
- `AUTH_API_URL` - Auth API endpoint (e.g., `https://api.coursewagon.live/api/auth`)

### Firebase Configuration
- `FIREBASE_API_KEY` - Firebase API key
- `FIREBASE_AUTH_DOMAIN` - Firebase auth domain (e.g., `coursewagon.firebaseapp.com`)
- `FIREBASE_PROJECT_ID` - Firebase project ID
- `FIREBASE_STORAGE_BUCKET` - Firebase storage bucket
- `FIREBASE_MESSAGING_SENDER_ID` - Firebase messaging sender ID
- `FIREBASE_APP_ID` - Firebase app ID

### Service Account (Already Set)
- `FIREBASE_SERVICE_ACCOUNT_COURSEWAGON` - ✅ Already configured by Firebase CLI

## Setting Up Secrets

You can set up all secrets at once using the GitHub CLI:

```bash
gh secret set API_URL --body "https://api.coursewagon.live/api"
gh secret set API_BASE_URL --body "https://api.coursewagon.live/api"
gh secret set COURSE_API_URL --body "https://api.coursewagon.live/api/courses"
gh secret set AUTH_API_URL --body "https://api.coursewagon.live/api/auth"
gh secret set FIREBASE_API_KEY --body "YOUR_FIREBASE_API_KEY"
gh secret set FIREBASE_AUTH_DOMAIN --body "coursewagon.firebaseapp.com"
gh secret set FIREBASE_PROJECT_ID --body "coursewagon"
gh secret set FIREBASE_STORAGE_BUCKET --body "coursewagon.firebasestorage.app"
gh secret set FIREBASE_MESSAGING_SENDER_ID --body "YOUR_MESSAGING_SENDER_ID"
gh secret set FIREBASE_APP_ID --body "YOUR_APP_ID"
```

Or manually through the GitHub web interface:
1. Go to https://github.com/Uttam-Mahata/coursewagon/settings/secrets/actions
2. Click "New repository secret"
3. Add each secret with its corresponding value

## How It Works

1. **On Push to Main**: The `firebase-hosting-merge.yml` workflow:
   - Generates `environment.prod.ts` from GitHub Secrets
   - Builds the Angular app with production configuration
   - Deploys to Firebase Hosting (live)

2. **On Pull Request**: The `firebase-hosting-pull-request.yml` workflow:
   - Does the same as above
   - Creates a preview deployment for testing

## Local Development

For local development, copy the example file and add your values:

```bash
cd angular-client/src/environments
cp environment.prod.example.ts environment.prod.ts
# Edit environment.prod.ts with your values
```

**Note**: `environment.prod.ts` is gitignored and will never be committed to the repository.

## Verifying Setup

After setting up secrets, you can verify by:
1. Making a commit and pushing to a branch
2. Creating a pull request
3. Checking the GitHub Actions tab for the workflow run
4. If successful, you'll see a preview deployment link in the PR comments

## Troubleshooting

If the deployment fails with "secret not found" errors:
- Verify all secrets are set at https://github.com/Uttam-Mahata/coursewagon/settings/secrets/actions
- Check that secret names exactly match (case-sensitive)
- Re-run the failed workflow after adding missing secrets
