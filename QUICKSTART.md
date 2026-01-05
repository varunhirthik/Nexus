# 🚀 Quick Start Guide - Live News Analyst

## Option 1: Local Development (Recommended for Testing)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Google Gemini API Key (free tier)

### Step 1: Get Your Gemini API Key
1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

### Step 2: Backend Setup

```powershell
# Navigate to project root
cd C:\New-projs\RAG

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Create .env file from template
copy .env.example .env

# Edit .env file and add your API key
notepad .env
# Replace: GEMINI_API_KEY=your_gemini_api_key_here
# With: GEMINI_API_KEY=<your-actual-key>

# Run the backend
python src/main.py
```

**Expected Output:**
```
╔═══════════════════════════════════════════════════════════╗
║          LIVE NEWS ANALYST - PATHWAY EDITION             ║
╚═══════════════════════════════════════════════════════════╝

✓ API Key configured
✓ 4 RSS feeds configured
✓ Poll interval: 60s
✓ FileWatcher directory: data/breaking_news

🎬 STARTING LIVE NEWS ANALYST
💡 TIP: Drop .txt files into data/breaking_news/ for instant ingestion
```

### Step 3: Frontend Setup (New Terminal)

```powershell
# Open new PowerShell terminal
cd C:\New-projs\RAG\frontend

# Install dependencies (if not done already)
npm install

# Start development server
npm run dev
```

**Expected Output:**
```
  VITE v5.0.0  ready in 342 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Step 4: Open in Browser
Navigate to: **http://localhost:5173**

---

## Option 2: Docker (Production-Ready)

### Prerequisites
- Docker Desktop installed
- Docker Compose installed

### Steps

```powershell
# Navigate to project root
cd C:\New-projs\RAG

# Create .env file with your API key
copy .env.example .env
notepad .env  # Add your GEMINI_API_KEY

# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Stop services:**
```powershell
docker-compose down
```

---

## Testing the System

### 1. Verify Backend is Running
Open browser to: http://localhost:8000

You should see:
```json
{
  "status": "online",
  "service": "Live News Analyst",
  "version": "1.0.0"
}
```

### 2. Test Real-Time Ingestion
```powershell
# Copy a demo file into the watched directory
copy demo\market_flash_crash.txt data\breaking_news\

# Wait 1-2 seconds, then check the frontend
# You should see the article appear in the ticker
```

### 3. Test AI Analyst
1. Go to frontend (http://localhost:5173)
2. Click "🤖 AI Analyst Chat" tab
3. Type: "What's happening with the market?"
4. Hit Send
5. You should get a response within 1-2 seconds

---

## Troubleshooting

### Backend won't start
**Error:** `GEMINI_API_KEY not configured`
- **Fix:** Edit `.env` file and add your actual API key

**Error:** `ModuleNotFoundError: No module named 'pathway'`
- **Fix:** Activate virtual environment: `.\venv\Scripts\activate`
- **Fix:** Install dependencies: `pip install -r requirements.txt`

### Frontend shows connection error
**Error:** "Failed to fetch latest news"
- **Fix:** Ensure backend is running on port 8000
- **Fix:** Check `.env` in frontend folder has `VITE_API_URL=http://localhost:8000`

### WebSocket not connecting
**Symptom:** Status shows "Polling" instead of "Live"
- **Fix:** This is normal! The system falls back to polling. WebSocket implementation is a v2 feature.
- **Note:** Polling every 5 seconds is still real-time enough for the demo

### No articles appearing
**Cause:** RSS feeds might be slow
- **Fix:** Use FileWatcher demo technique
- **Fix:** Drop demo files from `demo/` folder into `data/breaking_news/`

---

## Development Commands

### Backend

```powershell
# Run with debug logging
python src/main.py --log-level DEBUG

# Run tests
pytest tests/

# Format code
black src/
isort src/
```

### Frontend

```powershell
cd frontend

# Development mode (hot reload)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint/type check
npm run lint
```

---

## File Structure Quick Reference

```
RAG/
├── src/                    # Backend Python code
│   ├── main.py            # Entry point
│   ├── api_server.py      # FastAPI REST/WebSocket server
│   ├── config.py          # Configuration
│   ├── connectors/        # RSS + FileWatcher
│   ├── pipeline/          # Pathway RAG pipeline
│   └── llm/               # Gemini integration
├── frontend/              # React + TypeScript
│   ├── src/
│   │   ├── App.tsx        # Main app component
│   │   ├── components/    # UI components
│   │   ├── services/      # API client
│   │   └── types/         # TypeScript interfaces
├── data/
│   ├── breaking_news/     # FileWatcher directory (demo)
│   └── output/            # Pipeline outputs (.jsonl files)
├── demo/                  # Demo files for presentation
├── .env                   # Your environment variables (CREATE THIS)
├── .env.example           # Template
├── requirements.txt       # Python dependencies
└── docker-compose.yml     # Multi-container orchestration
```

---

## Next Steps

1. ✅ **Test locally** with demo files
2. ✅ **Review the code** - it's well-documented
3. ✅ **Practice the demo** using `demo/DEMO_SCRIPT.md`
4. ✅ **Record video** showing real-time updates
5. ✅ **Deploy** (optional): Use Docker for judge testing

---

## Support

- **Pathway Docs:** https://pathway.com/developers/
- **Gemini API:** https://ai.google.dev/
- **React + Vite:** https://vitejs.dev/

**Good luck with the hackathon! 🎉**
