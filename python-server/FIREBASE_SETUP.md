# Firebase Service Account Setup Instructions

## To properly set up Firebase Admin SDK with service account:

### Step 1: Generate Service Account Key
1. Go to the Firebase Console: https://console.firebase.google.com/
2. Select your project: coursewagon
3. Go to Project Settings (gear icon) > Service Accounts
4. Click "Generate New Private Key"
5. Download the JSON file
6. Rename it to: coursewagon-firebase-adminsdk.json
7. Place it in the utils/ folder of your Python server

### Step 2: Set Environment Variables
Add to your .env file:
```
FIREBASE_PROJECT_ID=coursewagon
FIREBASE_CREDENTIALS_PATH=utils/coursewagon-firebase-adminsdk.json
```

### Step 3: Alternative - Use Environment Variable
Instead of a file, you can set the entire JSON as an environment variable:
```
FIREBASE_ADMIN_CREDENTIALS='{"type":"service_account","project_id":"coursewagon",...}'
```

### Step 4: Firebase Authentication Rules
In the Firebase Console:
1. Go to Authentication > Sign-in method
2. Enable Google sign-in provider
3. Add your domain to authorized domains
4. Set up OAuth consent screen

## Security Best Practices:
- Never commit service account keys to version control
- Add *.json to .gitignore
- Use environment variables in production
- Rotate keys regularly

## Testing:
After setup, test with:
```bash
curl -X GET "http://localhost:8000/api/test/firebase-auth-test"
```
