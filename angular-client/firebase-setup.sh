#!/bin/bash

echo "🔥 Firebase CLI Setup for Angular Client"
echo "========================================"
echo ""

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "Installing Firebase CLI..."
    npm install -g firebase-tools
else
    echo "✅ Firebase CLI is already installed"
fi

echo ""
echo "🔐 Firebase Login"
echo "Run this command to login to Firebase:"
echo "firebase login"
echo ""

echo "🎯 Firebase Project Setup"
echo "Run this command to initialize or link Firebase project:"
echo "cd angular-client"
echo "firebase init hosting"
echo ""

echo "📋 Manual Steps:"
echo "1. Choose 'Use an existing project'"
echo "2. Select 'coursewagon' project"
echo "3. Set public directory to: dist/course-wagon-angular/browser"
echo "4. Choose 'Yes' for single-page app"
echo "5. Choose 'No' for GitHub Actions (we have custom workflow)"
echo ""

echo "🚀 Test Local Deployment:"
echo "npm run build"
echo "firebase serve"
