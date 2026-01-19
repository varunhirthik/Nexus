#!/bin/bash
# Reliable Deploy Script for Cloud Shell
# Handles Cloud Shell networking issues
# Run: bash cloudrun/deploy-reliable.sh

set -e

PROJECT_ID="${GCP_PROJECT_ID:-nexus-hackathon-2026}"
REGION="${GCP_REGION:-asia-south1}"
BACKEND_SERVICE="nexus-backend"
FRONTEND_SERVICE="nexus-frontend"

echo "================================"
echo "  Nexus Reliable Deploy"
echo "================================"

gcloud config set project $PROJECT_ID

# ==========================================
# BACKEND - Async Build
# ==========================================
echo ""
echo "[1/4] Submitting backend build (async)..."
BUILD_ID=$(gcloud builds submit \
    --config cloudrun/cloudbuild-backend.yaml \
    --async \
    --format="value(id)" \
    .)

echo "Build ID: $BUILD_ID"
echo "Check status: https://console.cloud.google.com/cloud-build/builds/$BUILD_ID?project=$PROJECT_ID"
echo ""
echo "Waiting 3 minutes for build to complete..."
sleep 180

echo "Checking build status..."
gcloud builds describe $BUILD_ID --format="value(status)" || echo "Could not check status, proceeding..."

# ==========================================
# BACKEND - Deploy
# ==========================================
echo ""
echo "[2/4] Deploying backend..."
gcloud run deploy $BACKEND_SERVICE \
    --image=asia-south1-docker.pkg.dev/$PROJECT_ID/nexus-repo/nexus-backend:latest \
    --platform=managed \
    --region=$REGION \
    --allow-unauthenticated \
    --memory=2Gi \
    --cpu=2 \
    --timeout=300 \
    --port=8080 \
    --set-secrets="GOOGLE_API_KEY=GOOGLE_API_KEY:latest,NEWS_API_KEY=NEWS_API_KEY:latest,GNEWS_API_KEY=GNEWS_API_KEY:latest"

BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --region=$REGION --format='value(status.url)')
echo "✓ Backend deployed: $BACKEND_URL"

# ==========================================
# FRONTEND - Async Build
# ==========================================
echo ""
echo "[3/4] Submitting frontend build (async)..."
FRONTEND_BUILD_ID=$(gcloud builds submit \
    --config cloudrun/cloudbuild-frontend.yaml \
    --substitutions=_BACKEND_URL="${BACKEND_URL}" \
    --async \
    --format="value(id)" \
    .)

echo "Build ID: $FRONTEND_BUILD_ID"
echo "Waiting 3 minutes for build to complete..."
sleep 180

# ==========================================
# FRONTEND - Deploy
# ==========================================
echo ""
echo "[4/4] Deploying frontend..."
gcloud run deploy $FRONTEND_SERVICE \
    --image=asia-south1-docker.pkg.dev/$PROJECT_ID/nexus-repo/nexus-frontend:latest \
    --platform=managed \
    --region=$REGION \
    --allow-unauthenticated \
    --memory=512Mi \
    --cpu=1 \
    --timeout=60

FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --region=$REGION --format='value(status.url)')
echo "✓ Frontend deployed: $FRONTEND_URL"

# ==========================================
# UPDATE CORS
# ==========================================
echo ""
echo "Updating CORS..."
gcloud run services update $BACKEND_SERVICE \
    --region=$REGION \
    --set-env-vars="ALLOWED_ORIGINS=${FRONTEND_URL},http://localhost:5173"

# ==========================================
# RESULTS
# ==========================================
echo ""
echo "================================"
echo "  ✓ Deployment Complete!"
echo "================================"
echo ""
echo "Backend:  $BACKEND_URL"
echo "Frontend: $FRONTEND_URL"
echo ""
echo "Test backend: curl $BACKEND_URL/health"
echo ""
