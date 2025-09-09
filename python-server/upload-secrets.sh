#!/bin/bash

# Script to upload .env variables to Google Cloud Secret Manager with COURSEWAGON prefix

# Set project
gcloud config set project mitra-348d9

echo "🚀 Starting to upload secrets to Google Cloud Secret Manager..."

# Read the .env file and process each line
while IFS= read -r line; do
    # Skip empty lines and comments
    if [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]]; then
        continue
    fi
    
    # Extract variable name and value
    if [[ "$line" =~ ^([^=]+)=(.*)$ ]]; then
        var_name="${BASH_REMATCH[1]}"
        var_value="${BASH_REMATCH[2]}"
        
        # Remove quotes if they exist
        var_value=$(echo "$var_value" | sed 's/^"//; s/"$//')
        
        # Create secret name with COURSEWAGON prefix
        secret_name="COURSEWAGON-${var_name}"
        
        echo "📝 Processing: $var_name -> $secret_name"
        
        # Check if secret already exists
        if gcloud secrets describe "$secret_name" &>/dev/null; then
            echo "  ↗️ Secret already exists, adding new version..."
            echo -n "$var_value" | gcloud secrets versions add "$secret_name" --data-file=-
        else
            echo "  ✨ Creating new secret..."
            echo -n "$var_value" | gcloud secrets create "$secret_name" --replication-policy="automatic" --data-file=-
        fi
        
        # Grant access to the default Cloud Run service account
        # This will be the account that Cloud Run uses to access secrets
        default_sa="188702930872-compute@developer.gserviceaccount.com"
        gcloud secrets add-iam-policy-binding "$secret_name" \
            --member="serviceAccount:$default_sa" \
            --role="roles/secretmanager.secretAccessor" &>/dev/null
        
        echo "  ✅ Secret $secret_name uploaded and permissions granted"
    fi
done < .env

echo "🎉 All secrets uploaded to Google Cloud Secret Manager!"
echo ""
echo "📋 List of created secrets:"
gcloud secrets list --filter="name:COURSEWAGON" --format="table(name)"
