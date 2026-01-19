#!/bin/bash
# Quick backend-only deploy
# Usage: ./cloudrun/deploy-backend-only.sh

set -e

PROJECT_ID="${GCP_PROJECT_ID:-nexus-hackathon-2026}"
REGION="${GCP_REGION:-asia-south1}"

echo "🚀 Building backend..."
gcloud builds submit --config cloudrun/cloudbuild-backend.yaml . --quiet

echo "📦 Deploying to Cloud Run..."
gcloud run deploy nexus-backend \
    --image=asia-south1-docker.pkg.dev/$PROJECT_ID/nexus-repo/nexus-backend:latest \
    --platform=managed \
    --region=$REGION \
    --allow-unauthenticated \
    --memory=2Gi \
    --cpu=2 \
    --timeout=300 \
    --port=8080 \
    --set-secrets="GOOGLE_API_KEY=GOOGLE_API_KEY:latest,NEWS_API_KEY=NEWS_API_KEY:latest,GNEWS_API_KEY=GNEWS_API_KEY:latest" \
    --quiet

BACKEND_URL=$(gcloud run services describe nexus-backend --region=$REGION --format='value(status.url)')
echo ""
echo "✅ Done! Backend: $BACKEND_URL"
echo "Test: ${BACKEND_URL}/health"
