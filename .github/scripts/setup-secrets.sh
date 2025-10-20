#!/bin/bash

# Setup GitHub Secrets for Firebase Deployment
# This script helps you set up all required secrets for CI/CD

set -e

echo "🔐 GitHub Secrets Setup for Firebase Deployment"
echo "================================================"
echo ""
echo "This script will set up all required secrets for automatic Firebase deployments."
echo "You'll need to have the GitHub CLI (gh) installed and authenticated."
echo ""

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo "   Install it from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ You're not authenticated with GitHub CLI."
    echo "   Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI is installed and authenticated"
echo ""

# Set default values
API_URL="https://api.coursewagon.live/api"
API_BASE_URL="https://api.coursewagon.live/api"
COURSE_API_URL="https://api.coursewagon.live/api/courses"
AUTH_API_URL="https://api.coursewagon.live/api/auth"
FIREBASE_AUTH_DOMAIN="coursewagon.firebaseapp.com"
FIREBASE_PROJECT_ID="coursewagon"
FIREBASE_STORAGE_BUCKET="coursewagon.firebasestorage.app"

echo "📝 Please provide the following values:"
echo ""

# API URLs (with defaults)
read -p "API URL [$API_URL]: " input
API_URL="${input:-$API_URL}"

read -p "API Base URL [$API_BASE_URL]: " " input
API_BASE_URL="${input:-$API_BASE_URL}"

read -p "Course API URL [$COURSE_API_URL]: " input
COURSE_API_URL="${input:-$COURSE_API_URL}"

read -p "Auth API URL [$AUTH_API_URL]: " input
AUTH_API_URL="${input:-$AUTH_API_URL}"

echo ""
echo "🔥 Firebase Configuration:"
echo ""

read -p "Firebase API Key: " FIREBASE_API_KEY
read -p "Firebase Auth Domain [$FIREBASE_AUTH_DOMAIN]: " input
FIREBASE_AUTH_DOMAIN="${input:-$FIREBASE_AUTH_DOMAIN}"

read -p "Firebase Project ID [$FIREBASE_PROJECT_ID]: " input
FIREBASE_PROJECT_ID="${input:-$FIREBASE_PROJECT_ID}"

read -p "Firebase Storage Bucket [$FIREBASE_STORAGE_BUCKET]: " input
FIREBASE_STORAGE_BUCKET="${input:-$FIREBASE_STORAGE_BUCKET}"

read -p "Firebase Messaging Sender ID: " FIREBASE_MESSAGING_SENDER_ID
read -p "Firebase App ID: " FIREBASE_APP_ID

echo ""
echo "🚀 Setting up secrets..."
echo ""

# Set secrets
gh secret set API_URL --body "$API_URL" && echo "✅ API_URL set"
gh secret set API_BASE_URL --body "$API_BASE_URL" && echo "✅ API_BASE_URL set"
gh secret set COURSE_API_URL --body "$COURSE_API_URL" && echo "✅ COURSE_API_URL set"
gh secret set AUTH_API_URL --body "$AUTH_API_URL" && echo "✅ AUTH_API_URL set"
gh secret set FIREBASE_API_KEY --body "$FIREBASE_API_KEY" && echo "✅ FIREBASE_API_KEY set"
gh secret set FIREBASE_AUTH_DOMAIN --body "$FIREBASE_AUTH_DOMAIN" && echo "✅ FIREBASE_AUTH_DOMAIN set"
gh secret set FIREBASE_PROJECT_ID --body "$FIREBASE_PROJECT_ID" && echo "✅ FIREBASE_PROJECT_ID set"
gh secret set FIREBASE_STORAGE_BUCKET --body "$FIREBASE_STORAGE_BUCKET" && echo "✅ FIREBASE_STORAGE_BUCKET set"
gh secret set FIREBASE_MESSAGING_SENDER_ID --body "$FIREBASE_MESSAGING_SENDER_ID" && echo "✅ FIREBASE_MESSAGING_SENDER_ID set"
gh secret set FIREBASE_APP_ID --body "$FIREBASE_APP_ID" && echo "✅ FIREBASE_APP_ID set"

echo ""
echo "✅ All secrets have been set successfully!"
echo ""
echo "You can view your secrets at:"
echo "https://github.com/Uttam-Mahata/coursewagon/settings/secrets/actions"
echo ""
echo "🎉 Your repository is now ready for automatic Firebase deployments!"
