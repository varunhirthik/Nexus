# Quick Deploy Guide

## 🎯 One-Command Deployment

### Full Stack (Backend + Frontend)
```bash
bash cloudrun/quick-deploy.sh
```
**What it does:**
1. Builds backend with Cloud Build (3-4 min)
2. Deploys backend with secrets
3. Builds frontend with backend URL
4. Deploys frontend
5. Updates CORS automatically
6. Shows both URLs

**Duration:** ~5-7 minutes

---

### Backend Only (Faster)
```bash
bash cloudrun/deploy-backend-only.sh
```
**What it does:**
1. Builds backend with Cloud Build
2. Deploys with secrets

**Duration:** ~4 minutes

---

## 📝 Manual Commands (What You've Been Doing)

### Backend
```bash
# Build
gcloud builds submit --config cloudrun/cloudbuild-backend.yaml .

# Deploy
gcloud run deploy nexus-backend \
    --image=asia-south1-docker.pkg.dev/nexus-hackathon-2026/nexus-repo/nexus-backend:latest \
    --platform=managed \
    --region=asia-south1 \
    --allow-unauthenticated \
    --memory=2Gi \
    --cpu=2 \
    --timeout=300 \
    --port=8080 \
    --set-secrets="GOOGLE_API_KEY=GOOGLE_API_KEY:latest,NEWS_API_KEY=NEWS_API_KEY:latest,GNEWS_API_KEY=GNEWS_API_KEY:latest"
```

### Frontend
```bash
# Build (must replace BACKEND_URL)
gcloud builds submit \
    --config cloudrun/cloudbuild-frontend.yaml \
    --substitutions=_BACKEND_URL="https://nexus-backend-99420505209.asia-south1.run.app" \
    .

# Deploy
gcloud run deploy nexus-frontend \
    --image=asia-south1-docker.pkg.dev/nexus-hackathon-2026/nexus-repo/nexus-frontend:latest \
    --platform=managed \
    --region=asia-south1 \
    --allow-unauthenticated \
    --memory=512Mi \
    --cpu=1 \
    --timeout=60
```

---

## ⚡ Typical Workflow

### During Development
```bash
# After making code changes
git add .
git commit -m "feat: your change"
git push

# Deploy just backend
bash cloudrun/deploy-backend-only.sh
```

### Before Demo/Production
```bash
# Full deployment
bash cloudrun/quick-deploy.sh
```

---

## 🔧 Configuration

Edit these in the scripts if needed:
- `PROJECT_ID`: Default is `nexus-hackathon-2026`
- `REGION`: Default is `asia-south1`
- `BACKEND_SERVICE`: Default is `nexus-backend`
- `FRONTEND_SERVICE`: Default is `nexus-frontend`

Or set environment variables:
```bash
export GCP_PROJECT_ID=your-project
export GCP_REGION=us-central1
bash cloudrun/quick-deploy.sh
```

---

## 🚨 Important Notes

1. **Secrets Must Exist:** Ensure these secrets are in Secret Manager:
   - `GOOGLE_API_KEY`
   - `NEWS_API_KEY`
   - `GNEWS_API_KEY`

2. **Don't Set PORT:** Cloud Run sets this automatically (you learned this!)

3. **CORS:** The full deploy script automatically configures CORS with the frontend URL

4. **First Time:** Run setup first:
   ```bash
   bash cloudrun/setup-secrets.sh
   ```

---

## 🎬 From Your Cloud Shell

```bash
# Clone/pull latest
git pull origin master

# Deploy everything
bash cloudrun/quick-deploy.sh

# Or just backend for quick iteration
bash cloudrun/deploy-backend-only.sh
```

That's it! No more typing long gcloud commands. 🎉
