# Quick Command Reference

## 🚀 Starting the Application

### Using Docker (Recommended)
```powershell
cd deployment
docker-compose up --build
```

### Detached mode (runs in background)
```powershell
cd deployment
docker-compose up -d --build
```

### View logs
```powershell
cd deployment
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Stop containers
```powershell
cd deployment
docker-compose down
```

---

## 🛠️ Development Commands

### Backend (in WSL2/Linux)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

### Frontend (Windows/Linux/Mac)
```powershell
cd frontend
npm install
npm run dev
```

---

## 🎬 Demo Commands

### Test FileWatcher
```powershell
# Copy demo file to trigger ingestion
Copy-Item demo\sample_articles\market_flash_crash.txt data\breaking_news\test1.txt

# Watch backend logs for confirmation
docker logs -f news-analyst-backend
```

### Check Health
```powershell
# Backend health
curl http://localhost:8000/health

# Frontend (should return HTML)
curl http://localhost:5173
```

---

## 🐳 Docker Shortcuts

### Rebuild specific service
```powershell
cd deployment
docker-compose build backend
docker-compose build frontend
```

### Restart specific service
```powershell
cd deployment
docker-compose restart backend
docker-compose restart frontend
```

### Remove everything and start fresh
```powershell
cd deployment
docker-compose down -v
docker-compose up --build
```

### View running containers
```powershell
docker ps
```

### Exec into container
```powershell
docker exec -it news-analyst-backend /bin/bash
docker exec -it news-analyst-frontend /bin/sh
```

---

## 📝 Git Commands

### Commit reorganized structure
```powershell
git add .
git commit -m "refactor: reorganize directory structure"
git push origin master
```

### Check what changed
```powershell
git status
git diff
```

### View commit history
```powershell
git log --oneline --graph
```

---

## 🧪 Testing Commands

### Test backend API
```powershell
# Health check
curl http://localhost:8000/health

# API docs
Start-Process http://localhost:8000/docs

# Query endpoint
curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{\"question\":\"What'\''s the latest news?\"}'
```

### Check file ingestion
```powershell
# Monitor output files
Get-Content data\output\headlines.jsonl -Wait

# Check FileWatcher directory
Get-ChildItem data\breaking_news\
```

---

## 🔍 Debugging Commands

### Check Docker logs
```powershell
docker logs news-analyst-backend
docker logs news-analyst-frontend
```

### Check container stats
```powershell
docker stats
```

### Inspect network
```powershell
docker network ls
docker network inspect deployment_news-analyst-network
```

### Clean up Docker cache
```powershell
docker system prune -a
```

---

## 📦 Dependency Management

### Update backend dependencies
```bash
cd backend
pip install --upgrade pathway google-generativeai fastapi
pip freeze > requirements.txt
```

### Update frontend dependencies
```powershell
cd frontend
npm update
npm audit fix
```

---

## 🎯 One-Liner Quick Starts

**Full system (Docker)**:
```powershell
cd deployment; docker-compose up --build
```

**Backend only (Docker)**:
```powershell
cd deployment; docker-compose up backend
```

**Frontend only (Docker)**:
```powershell
cd deployment; docker-compose up frontend
```

**Stop everything**:
```powershell
cd deployment; docker-compose down
```

**Restart with clean slate**:
```powershell
cd deployment; docker-compose down -v; docker-compose up --build
```

---

## 🌐 Access URLs

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📋 Environment Setup

### First time setup
```powershell
# 1. Copy environment template
copy backend\.env.example .env

# 2. Edit and add API key
notepad .env

# 3. Start services
cd deployment
docker-compose up --build
```

---

## 🚨 Emergency Commands

### If containers won't stop
```powershell
docker-compose kill
docker rm -f news-analyst-backend news-analyst-frontend
```

### If port is in use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### If Docker is acting weird
```powershell
# Restart Docker Desktop
Restart-Service -Name "com.docker.service" -Force

# Or manually restart Docker Desktop app
```

---

**Tip**: Bookmark this file for quick reference! 📌
