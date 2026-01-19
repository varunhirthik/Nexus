#!/bin/bash
# Quick Deploy Script for Nexus on Cloud Run
# Uses Cloud Build instead of local Docker
# Run: ./cloudrun/quick-deploy.sh

set -e  # Exit on error

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-nexus-hackathon-2026}"
REGION="${GCP_REGION:-asia-south1}"
BACKEND_SERVICE="nexus-backend"
FRONTEND_SERVICE="nexus-frontend"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}  Nexus Quick Deploy${NC}"
echo -e "${GREEN}================================${NC}"

# Set project
gcloud config set project $PROJECT_ID --quiet

# ==========================================
# DEPLOY BACKEND
# ==========================================
echo ""
echo -e "${YELLOW}[1/3] Building backend with Cloud Build...${NC}"
gcloud builds submit --config cloudrun/cloudbuild-backend.yaml . --quiet

echo -e "${YELLOW}[2/3] Deploying backend to Cloud Run...${NC}"
gcloud run deploy $BACKEND_SERVICE \
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

BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --region=$REGION --format='value(status.url)')
echo -e "${GREEN}✓ Backend: ${BACKEND_URL}${NC}"

# ==========================================
# DEPLOY FRONTEND
# ==========================================
echo ""
echo -e "${YELLOW}[3/3] Building & deploying frontend...${NC}"

# Build frontend with backend URL
gcloud builds submit \
    --config cloudrun/cloudbuild-frontend.yaml \
    --substitutions=_BACKEND_URL="${BACKEND_URL}" \
    . --quiet

gcloud run deploy $FRONTEND_SERVICE \
    --image=asia-south1-docker.pkg.dev/$PROJECT_ID/nexus-repo/nexus-frontend:latest \
    --platform=managed \
    --region=$REGION \
    --allow-unauthenticated \
    --memory=512Mi \
    --cpu=1 \
    --timeout=60 \
    --quiet

FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --region=$REGION --format='value(status.url)')

# ==========================================
# UPDATE BACKEND CORS
# ==========================================
echo ""
echo -e "${YELLOW}Updating backend CORS settings...${NC}"
gcloud run services update $BACKEND_SERVICE \
    --region=$REGION \
    --set-env-vars="ALLOWED_ORIGINS=${FRONTEND_URL},http://localhost:5173" \
    --quiet

# ==========================================
# RESULTS
# ==========================================
echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}  ✓ Deployment Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "Backend:  ${GREEN}${BACKEND_URL}${NC}"
echo -e "Frontend: ${GREEN}${FRONTEND_URL}${NC}"
echo ""
echo -e "Test: ${BACKEND_URL}/health"
echo ""
