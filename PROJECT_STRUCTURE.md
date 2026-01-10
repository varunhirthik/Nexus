# 📂 Clean Project Structure (Docker-Only Setup)

**Last Updated**: January 11, 2026  
**Deployment Method**: Docker Compose Only

---

## 📁 Directory Tree

```
live-news-analyst/
│
├── 📄 README.md                 # Complete documentation (SINGLE source of truth)
├── 📄 COMMANDS.md               # Docker command reference
├── 📄 ARCHITECTURE_GUIDE.md     # Technical deep dive (THIS FILE explains everything)
│
├── 📁 backend/                  # Python + Pathway backend
│   ├── src/
│   │   ├── main.py             # Entry point
│   │   ├── config.py           # Environment configuration
│   │   ├── api_server.py       # FastAPI REST/WebSocket server
│   │   ├── connectors/
│   │   │   ├── rss_connector.py      # RSS polling (60s interval)
│   │   │   └── file_watcher.py       # Demo file ingestion (<2s)
│   │   ├── pipeline/
│   │   │   ├── pathway_pipeline.py   # Main Pathway orchestrator
│   │   │   ├── schemas.py            # Pathway table schemas
│   │   │   └── sentiment.py          # TextBlob sentiment analysis
│   │   └── llm/
│   │       ├── embedder.py     # Gemini API wrapper
│   │       └── prompts.py      # RAG prompt templates
│   ├── Dockerfile              # Python 3.11 + Pathway
│   ├── requirements.txt        # Python dependencies
│   └── .env.example            # Environment template
│
├── 📁 frontend/                 # React + TypeScript frontend
│   ├── src/
│   │   ├── App.tsx             # Main component
│   │   ├── main.tsx            # Entry point
│   │   ├── components/
│   │   │   ├── NewsTicker.tsx        # Scrolling headlines
│   │   │   ├── AnalystChat.tsx       # RAG query interface
│   │   │   ├── SentimentChart.tsx    # Recharts visualization
│   │   │   └── AlertPanel.tsx        # Keyword alerts
│   │   ├── services/
│   │   │   └── api.ts                # WebSocket + REST client
│   │   └── types/
│   │       └── index.ts              # TypeScript interfaces
│   ├── Dockerfile              # Node 20 + nginx
│   ├── package.json            # Node dependencies
│   ├── vite.config.ts          # Vite configuration
│   └── index.html              # HTML entry
│
├── 📁 deployment/               # Docker orchestration
│   ├── docker-compose.yml      # Multi-service setup (backend + frontend)
│   └── nginx.conf              # Nginx configuration
│
├── 📁 demo/                     # Demo assets for hackathon
│   ├── sample_articles/
│   │   ├── market_flash_crash.txt
│   │   ├── bitcoin_surge.txt
│   │   └── breaking_tech_acquisition.txt
│   ├── DEMO_GUIDE.md           # FileWatcher demo instructions
│   └── demo_script.md          # Presentation script
│
├── 📁 data/                     # Runtime data (gitignored)
│   ├── breaking_news/          # FileWatcher monitors this directory
│   └── output/                 # Pathway output sinks
│       ├── headlines.jsonl     # Latest headlines
│       ├── sentiment.jsonl     # Sentiment data
│       └── rss_cache.json      # Deduplication cache
│
├── 📁 docs/                     # Documentation assets
│   └── (reserved for diagrams/images)
│
├── .env                         # YOUR environment file (create from backend/.env.example)
├── .gitignore                   # Git exclusions (.env, venv, node_modules, etc.)
└── .dockerignore                # Docker build exclusions

```

---

## 🎯 Key Files Explained

### Root Level (Only 3 Documentation Files!)

| File | Purpose | Read When |
|------|---------|-----------|
| `README.md` | Complete guide (setup, architecture, deployment, troubleshooting) | First time setup |
| `COMMANDS.md` | Docker command cheat sheet | Daily development |
| `ARCHITECTURE_GUIDE.md` | Technical deep dive, flow diagrams, file explanations | Understanding codebase |

**That's it!** No more 12 scattered .md files. Everything in 3 docs.

---

## 🐳 Docker-Only Setup

### Why Docker-Only?

1. **Pathway requires Linux** (won't install on Windows)
2. **Reproducible environment** (same everywhere)
3. **One command to start** (no manual setup)
4. **Production-ready** (same setup for deployment)

### How to Run

```powershell
# Navigate to deployment folder
cd deployment

# Start everything
docker-compose up --build

# Access:
# - Frontend: http://localhost:5173
# - Backend: http://localhost:8000
```

**That's it!** No `.bat` scripts, no `.sh` scripts, just Docker.

---

## 📦 What Was Removed (Cleanup)

### Deleted Files (Not Needed for Docker)

- ❌ `deployment/scripts/start.bat` - Windows startup script (use docker-compose instead)
- ❌ `deployment/scripts/start.sh` - Linux startup script (use docker-compose instead)
- ❌ `deployment/scripts/` - Entire directory (empty after removing scripts)
- ❌ `REORGANIZATION_SUMMARY.md` - One-time migration doc (no longer relevant)
- ❌ `package.json` (root level) - Frontend has its own
- ❌ `package-lock.json` (root level) - Frontend has its own
- ❌ `tests/` - Empty directory (no tests written yet)

### Kept Files

- ✅ `README.md` - Main documentation
- ✅ `COMMANDS.md` - Command reference
- ✅ `ARCHITECTURE_GUIDE.md` - Technical guide
- ✅ `.env` - User's environment file
- ✅ `.env.example` - Template for new users
- ✅ `.gitignore` - Git exclusions
- ✅ `.dockerignore` - Docker build exclusions

---

## 🔑 Critical Directories

### `backend/` - Python Application

**Contains**: All backend logic (Pathway pipeline, API server, connectors, LLM)

**Docker Build**:
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
CMD ["python", "src/main.py"]
```

### `frontend/` - React Application

**Contains**: All frontend code (React components, TypeScript types, API client)

**Docker Build**:
```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS build
RUN npm install
RUN npm run build
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
```

### `deployment/` - Orchestration

**Contains**: `docker-compose.yml` only

**Services**:
- `backend`: Python + Pathway (port 8000)
- `frontend`: nginx + React (port 5173)
- Bridge network for communication

### `demo/` - Hackathon Demo Assets

**Contains**: Sample articles for FileWatcher demo

**Purpose**: Drop these files into `data/breaking_news/` during presentation to prove <2s latency

### `data/` - Runtime Data (Gitignored)

**Contains**:
- `breaking_news/`: FileWatcher monitors this
- `output/`: Pathway writes JSONL files here

**Note**: This directory is created automatically and ignored by git

---

## 🎯 Simplified Workflow

### First-Time Setup

```powershell
# 1. Clone repo
git clone https://github.com/YOUR-USERNAME/live-news-analyst.git
cd live-news-analyst

# 2. Create .env
copy backend\.env.example .env
notepad .env  # Add GEMINI_API_KEY

# 3. Run
cd deployment
docker-compose up --build
```

**That's 3 steps!**

### Daily Development

```powershell
# Start
cd deployment
docker-compose up

# Stop
Ctrl+C
docker-compose down
```

---

## 📊 Benefits of This Structure

| Aspect | Before Reorganization | After Cleanup |
|--------|----------------------|---------------|
| **Documentation** | 12+ .md files | 3 .md files |
| **Startup Scripts** | .bat + .sh files | Just docker-compose |
| **Package Files** | 2 package.json (root + frontend) | 1 package.json (frontend only) |
| **Empty Folders** | tests/, scripts/ | Removed |
| **Onboarding** | "Read 5+ docs" | "Read README" |
| **Deployment** | "Run this .bat file" | "docker-compose up" |

---

## 🚀 Ready for Hackathon Submission

Your repository now has:

✅ **Clean structure** - Professional, easy to navigate  
✅ **Single README** - All info in one place  
✅ **Docker-ready** - One command to start  
✅ **No cruft** - Only essential files  
✅ **Clear separation** - backend/ frontend/ deployment/ demo/  

**This will impress the judges!** 🏆

---

**Questions?** Check `ARCHITECTURE_GUIDE.md` for technical details! 📚
