#!/bin/bash
# SIMPLIFIED deployment for Cloud Run (no Docker required!)
# This uses Cloud Run's source deployment feature
# Perfect for hackathon demos when you want quick deployment

set -e

PROJECT_ID="${GCP_PROJECT_ID:-nexus-hackathon-2026}"
REGION="${GCP_REGION:-asia-south1}"
SERVICE_NAME="nexus-backend"

echo "============================================"
echo "  Nexus Quick Deploy (Source-based)"
echo "============================================"
echo ""
echo "Project: $PROJECT_ID"
echo "Region:  $REGION"
echo ""

# Set project
gcloud config set project $PROJECT_ID

# Enable APIs
echo "Enabling APIs..."
gcloud services enable run.googleapis.com secretmanager.googleapis.com cloudbuild.googleapis.com

# Deploy backend directly from source
echo ""
echo "Deploying backend from source..."
cd "$(dirname "$0")/../backend"

gcloud run deploy $SERVICE_NAME \
    --source=. \
    --region=$REGION \
    --allow-unauthenticated \
    --memory=2Gi \
    --cpu=2 \
    --timeout=300 \
    --set-env-vars="ENVIRONMENT=production" \
    --set-secrets="GOOGLE_API_KEY=GOOGLE_API_KEY:latest" \
    --set-secrets="NEWS_API_KEY=NEWS_API_KEY:latest" \
    --set-secrets="GNEWS_API_KEY=GNEWS_API_KEY:latest"

# Get URL
BACKEND_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')

echo ""
echo "============================================"
echo "  Backend Deployed!"
echo "============================================"
echo ""
echo "URL: $BACKEND_URL"
echo ""
echo "Test endpoints:"
echo "  curl $BACKEND_URL/health"
echo "  curl $BACKEND_URL/news/latest"
echo "  curl $BACKEND_URL/stats"
echo ""
echo "For frontend, you can:"
echo "  1. Use Vercel/Netlify to deploy the React app"
echo "  2. Or run locally pointing to this backend URL"
echo ""
