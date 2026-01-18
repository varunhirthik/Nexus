#!/bin/bash
# Deploy script for Google Cloud Run
# Run this from Cloud Shell after setting up your environment

set -e  # Exit on any error

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-nexus-hackathon-2026}"
REGION="${GCP_REGION:-asia-south1}"
BACKEND_SERVICE="nexus-backend"
FRONTEND_SERVICE="nexus-frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Nexus News Analyzer - Cloud Run Deploy${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if gcloud is configured
echo -e "${YELLOW}Checking gcloud configuration...${NC}"
gcloud config set project $PROJECT_ID
gcloud config set run/region $REGION

# Enable required APIs
echo -e "${YELLOW}Enabling required APIs...${NC}"
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com

# Create Artifact Registry repository if it doesn't exist
echo -e "${YELLOW}Setting up Artifact Registry...${NC}"
gcloud artifacts repositories create nexus-repo \
    --repository-format=docker \
    --location=$REGION \
    --description="Nexus Docker images" \
    --quiet 2>/dev/null || echo "Repository already exists"

# Configure Docker for Artifact Registry
echo -e "${YELLOW}Configuring Docker authentication...${NC}"
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

# ==========================================
# BUILD AND DEPLOY BACKEND
# ==========================================
echo ""
echo -e "${GREEN}Building Backend...${NC}"
cd "$(dirname "$0")/.."

BACKEND_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/nexus-repo/${BACKEND_SERVICE}:latest"

# Build backend image
docker build -f cloudrun/backend.Dockerfile -t $BACKEND_IMAGE .

# Push to Artifact Registry
echo -e "${YELLOW}Pushing backend image...${NC}"
docker push $BACKEND_IMAGE

# Deploy backend to Cloud Run
echo -e "${YELLOW}Deploying backend to Cloud Run...${NC}"
gcloud run deploy $BACKEND_SERVICE \
    --image=$BACKEND_IMAGE \
    --platform=managed \
    --region=$REGION \
    --allow-unauthenticated \
    --memory=2Gi \
    --cpu=2 \
    --min-instances=0 \
    --max-instances=10 \
    --timeout=300 \
    --set-env-vars="ENVIRONMENT=production" \
    --set-env-vars="LOG_LEVEL=INFO" \
    --set-secrets="GOOGLE_API_KEY=GOOGLE_API_KEY:latest" \
    --set-secrets="NEWS_API_KEY=NEWS_API_KEY:latest" \
    --set-secrets="GNEWS_API_KEY=GNEWS_API_KEY:latest"

# Get backend URL
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --region=$REGION --format='value(status.url)')
echo -e "${GREEN}Backend deployed at: ${BACKEND_URL}${NC}"

# ==========================================
# BUILD AND DEPLOY FRONTEND
# ==========================================
echo ""
echo -e "${GREEN}Building Frontend...${NC}"

FRONTEND_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/nexus-repo/${FRONTEND_SERVICE}:latest"

# Build frontend with backend URL
docker build -f cloudrun/frontend.Dockerfile \
    --build-arg VITE_API_URL="${BACKEND_URL}" \
    --build-arg VITE_WS_URL="${BACKEND_URL/https/wss}" \
    -t $FRONTEND_IMAGE .

# Push to Artifact Registry
echo -e "${YELLOW}Pushing frontend image...${NC}"
docker push $FRONTEND_IMAGE

# Deploy frontend to Cloud Run
echo -e "${YELLOW}Deploying frontend to Cloud Run...${NC}"
gcloud run deploy $FRONTEND_SERVICE \
    --image=$FRONTEND_IMAGE \
    --platform=managed \
    --region=$REGION \
    --allow-unauthenticated \
    --memory=512Mi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=5 \
    --timeout=60

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --region=$REGION --format='value(status.url)')

# ==========================================
# OUTPUT RESULTS
# ==========================================
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Backend URL:  ${YELLOW}${BACKEND_URL}${NC}"
echo -e "Frontend URL: ${YELLOW}${FRONTEND_URL}${NC}"
echo ""
echo -e "${GREEN}Your Nexus News Analyzer is now live!${NC}"
echo ""
echo -e "API Endpoints:"
echo -e "  - Health: ${BACKEND_URL}/health"
echo -e "  - News:   ${BACKEND_URL}/news/latest"
echo -e "  - Stats:  ${BACKEND_URL}/stats"
echo -e "  - Query:  ${BACKEND_URL}/query"
echo ""
