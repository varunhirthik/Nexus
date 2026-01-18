# Google Cloud Run Deployment Guide for Nexus

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **API Keys** (you should already have these):
   - Google Gemini API Key
   - NewsAPI.org Key
   - GNews.io Key

## Quick Deploy Steps (Cloud Shell)

### 1. Open Google Cloud Shell
Go to https://console.cloud.google.com and click the Cloud Shell icon (>_) in the top right.

### 2. Clone the Repository (if not done)
```bash
git clone https://github.com/varunhirthik/Nexus.git
cd Nexus
```

### 3. Set Your Project
```bash
export GCP_PROJECT_ID="nexus-hackathon-2026"
export GCP_REGION="asia-south1"
gcloud config set project $GCP_PROJECT_ID
```

### 4. Setup API Keys as Secrets
```bash
chmod +x cloudrun/setup-secrets.sh
./cloudrun/setup-secrets.sh
```
When prompted, enter your API keys:
- GOOGLE_API_KEY: Your Gemini API key
- NEWS_API_KEY: Your NewsAPI.org key  
- GNEWS_API_KEY: Your GNews.io key

### 5. Deploy to Cloud Run
```bash
chmod +x cloudrun/deploy.sh
./cloudrun/deploy.sh
```

This will:
- Build and push the backend Docker image
- Deploy backend to Cloud Run
- Build and push the frontend Docker image (with backend URL)
- Deploy frontend to Cloud Run
- Output both URLs

## Expected Output

After deployment completes, you'll see:
```
==========================================
  Deployment Complete!
==========================================

Backend URL:  https://nexus-backend-xxxxx-el.a.run.app
Frontend URL: https://nexus-frontend-xxxxx-el.a.run.app

Your Nexus News Analyzer is now live!
```

## Verifying Deployment

1. **Health Check**: `curl https://nexus-backend-xxxxx.a.run.app/health`
2. **Frontend**: Open the frontend URL in your browser
3. **API Test**: `curl https://nexus-backend-xxxxx.a.run.app/news/latest`

## Troubleshooting

### View Logs
```bash
# Backend logs
gcloud run logs read nexus-backend --region=asia-south1

# Frontend logs
gcloud run logs read nexus-frontend --region=asia-south1
```

### Check Service Status
```bash
gcloud run services list --region=asia-south1
```

### Update Secrets
```bash
# Add new version of a secret
echo -n "NEW_API_KEY_VALUE" | gcloud secrets versions add GOOGLE_API_KEY --data-file=-

# Redeploy to pick up new secret
gcloud run services update nexus-backend --region=asia-south1
```

### Common Issues

1. **"Permission denied" on scripts**: Run `chmod +x cloudrun/*.sh`

2. **"Secret not found" error**: Make sure you ran `setup-secrets.sh` first

3. **Frontend shows "Failed to fetch"**: The backend URL might not be set correctly. Check the VITE_API_URL build arg.

4. **WebSocket not connecting**: Cloud Run has limited WebSocket support. The app will fall back to REST API polling.

## Cost Optimization

Cloud Run charges based on usage. With the default settings:
- Backend: min-instances=0 (scales to zero when idle)
- Frontend: min-instances=0 (scales to zero when idle)

For hackathon demo, this means minimal cost when not in use.

## Custom Domain (Optional)

To use a custom domain:
```bash
gcloud run domain-mappings create --service=nexus-frontend --domain=your-domain.com --region=asia-south1
```

## Architecture on Cloud Run

```
                    ┌─────────────────────────┐
                    │    Cloud Run Frontend   │
                    │   (nexus-frontend)      │
                    │   - Nginx + React       │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │    Cloud Run Backend    │
                    │   (nexus-backend)       │
                    │   - FastAPI + Gunicorn  │
                    │   - Pathway Pipeline    │
                    │   - Gemini AI           │
                    └───────────┬─────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
            ┌───────────────┐       ┌───────────────┐
            │  NewsAPI.org  │       │   GNews.io    │
            └───────────────┘       └───────────────┘
```
