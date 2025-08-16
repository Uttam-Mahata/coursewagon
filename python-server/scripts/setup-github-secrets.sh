#!/bin/bash

# GitHub Secrets Setup Helper
# This script helps you set up GitHub secrets for Azure deployment

echo "🔐 GitHub Secrets Setup Helper for CourseWagon Azure Deployment"
echo "================================================================"

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo "   Install it from: https://cli.github.com/"
    echo "   Then run: gh auth login"
    exit 1
fi

# Check if logged into GitHub CLI
if ! gh auth status &> /dev/null; then
    echo "❌ Not logged into GitHub CLI."
    echo "   Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI is installed and authenticated"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found in current directory"
    echo "   Please run this script from the server directory with .env file"
    exit 1
fi

echo "✅ Found .env file"

# Load environment variables
source .env

echo ""
echo "📋 This script will help you set up GitHub secrets from your .env file"
echo "⚠️  Make sure you're in the correct GitHub repository"
echo ""

# Show current repository
CURRENT_REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "Unknown")
echo "🏠 Current repository: $CURRENT_REPO"
echo ""

read -p "❓ Do you want to continue setting up secrets for this repository? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled"
    exit 1
fi

echo ""
echo "🚀 Setting up GitHub secrets..."

# Function to set secret
set_secret() {
    local name=$1
    local value=$2
    
    if [ -n "$value" ]; then
        echo -n "Setting $name... "
        if echo "$value" | gh secret set "$name"; then
            echo "✅"
        else
            echo "❌ Failed"
        fi
    else
        echo "⚠️  $name is empty in .env file"
    fi
}

# Set all secrets from .env
echo "📝 Setting application secrets..."
set_secret "API_KEY" "$API_KEY"
set_secret "GEMINI_API_KEY" "$GEMINI_API_KEY"
set_secret "GEMINI_IMAGE_GENERATION_API_KEY" "$GEMINI_IMAGE_GENERATION_API_KEY"
set_secret "DB_HOST" "$DB_HOST"
set_secret "DB_PORT" "$DB_PORT"
set_secret "DB_USER" "$DB_USER"
set_secret "DB_PASS" "$DB_PASS"
set_secret "DB_NAME" "$DB_NAME"
set_secret "JWT_SECRET_KEY" "$JWT_SECRET_KEY"
set_secret "SECRET_KEY" "$SECRET_KEY"
set_secret "SECURITY_PASSWORD_SALT" "$SECURITY_PASSWORD_SALT"
set_secret "ENCRYPTION_KEY" "$ENCRYPTION_KEY"
set_secret "ENCRYPTION_SALT" "$ENCRYPTION_SALT"

echo ""
echo "☁️  Setting Azure Storage secrets..."
set_secret "AZURE_STORAGE_ACCOUNT_NAME" "$AZURE_STORAGE_ACCOUNT_NAME"
set_secret "AZURE_STORAGE_CONNECTION_STRING" "$AZURE_STORAGE_CONNECTION_STRING"
set_secret "AZURE_STORAGE_CONTAINER_NAME" "$AZURE_STORAGE_CONTAINER_NAME"

echo ""
echo "📧 Setting email configuration secrets..."
set_secret "MAIL_USERNAME" "$MAIL_USERNAME"
set_secret "MAIL_PASSWORD" "$MAIL_PASSWORD"
set_secret "MAIL_DEFAULT_SENDER" "$MAIL_DEFAULT_SENDER"
set_secret "MAIL_CONTACT_EMAIL" "$MAIL_CONTACT_EMAIL"
set_secret "MAILGUN_API_KEY" "$MAILGUN_API_KEY"
set_secret "MAILGUN_DOMAIN" "$MAILGUN_DOMAIN"
set_secret "FRONTEND_URL" "$FRONTEND_URL"

echo ""
echo "🔐 Azure Service Principal Setup"
echo "================================"
echo ""
echo "⚠️  You need to manually create the AZURE_CREDENTIALS secret:"
echo ""
echo "1. Run this command to create a service principal:"
echo ""
echo "   az ad sp create-for-rbac \\"
echo "     --name \"coursewagon-github-actions\" \\"
echo "     --role contributor \\"
echo "     --scopes /subscriptions/{YOUR_SUBSCRIPTION_ID}/resourceGroups/coursewagon-rg \\"
echo "     --sdk-auth"
echo ""
echo "2. Copy the entire JSON output"
echo "3. Set it as a GitHub secret named 'AZURE_CREDENTIALS'"
echo ""
echo "📝 To set AZURE_CREDENTIALS manually:"
echo "   gh secret set AZURE_CREDENTIALS"
echo "   (then paste the JSON when prompted)"
echo ""

# Get subscription ID if logged into Azure
if command -v az &> /dev/null && az account show &> /dev/null; then
    SUBSCRIPTION_ID=$(az account show --query id -o tsv)
    echo "💡 Your current Azure subscription ID: $SUBSCRIPTION_ID"
    echo ""
    echo "📋 Complete command with your subscription ID:"
    echo ""
    echo "   az ad sp create-for-rbac \\"
    echo "     --name \"coursewagon-github-actions\" \\"
    echo "     --role contributor \\"
    echo "     --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/coursewagon-rg \\"
    echo "     --sdk-auth"
fi

echo ""
echo "✅ GitHub secrets setup completed!"
echo ""
echo "🎯 Next steps:"
echo "1. Create the AZURE_CREDENTIALS secret (see instructions above)"
echo "2. Go to your GitHub repository → Actions tab"
echo "3. Run the 'Setup Azure Infrastructure' workflow (first time only)"
echo "4. Push code to main/master branch to trigger deployment"
echo ""
echo "📖 For more details, see: .github/workflows/README.md"
