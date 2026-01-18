#!/bin/bash
# Setup secrets in Google Cloud Secret Manager
# Run this ONCE before deploying

set -e

PROJECT_ID="${GCP_PROJECT_ID:-nexus-hackathon-2026}"

echo "Setting up secrets for project: $PROJECT_ID"
echo ""

# Function to create or update a secret
create_secret() {
    SECRET_NAME=$1
    echo -n "Enter value for $SECRET_NAME: "
    read -s SECRET_VALUE
    echo ""
    
    # Check if secret exists
    if gcloud secrets describe $SECRET_NAME --project=$PROJECT_ID &>/dev/null; then
        echo "Updating existing secret: $SECRET_NAME"
        echo -n "$SECRET_VALUE" | gcloud secrets versions add $SECRET_NAME --data-file=- --project=$PROJECT_ID
    else
        echo "Creating new secret: $SECRET_NAME"
        echo -n "$SECRET_VALUE" | gcloud secrets create $SECRET_NAME --data-file=- --project=$PROJECT_ID
    fi
    echo "✓ $SECRET_NAME configured"
    echo ""
}

echo "This script will set up the following secrets:"
echo "  1. GOOGLE_API_KEY (Gemini API key)"
echo "  2. NEWS_API_KEY (NewsAPI.org key)"
echo "  3. GNEWS_API_KEY (GNews.io key)"
echo ""
read -p "Press Enter to continue..."
echo ""

# Enable Secret Manager API
echo "Enabling Secret Manager API..."
gcloud services enable secretmanager.googleapis.com --project=$PROJECT_ID

# Create secrets
create_secret "GOOGLE_API_KEY"
create_secret "NEWS_API_KEY"
create_secret "GNEWS_API_KEY"

# Grant Cloud Run access to secrets
echo "Granting Cloud Run access to secrets..."
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

for SECRET in GOOGLE_API_KEY NEWS_API_KEY GNEWS_API_KEY; do
    gcloud secrets add-iam-policy-binding $SECRET \
        --member="serviceAccount:$COMPUTE_SA" \
        --role="roles/secretmanager.secretAccessor" \
        --project=$PROJECT_ID \
        --quiet
done

echo ""
echo "=========================================="
echo "  Secrets setup complete!"
echo "=========================================="
echo ""
echo "You can now run: ./deploy.sh"
