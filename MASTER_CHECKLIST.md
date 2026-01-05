# ✅ MASTER CHECKLIST - Live News Analyst

**Project:** Live News Analyst for DataQuest Hackathon 2025  
**Target Completion:** January 10, 2025  
**Status Tracker:** Use this as your daily reference

---

## 🎯 PRE-DEVELOPMENT (Complete These FIRST)

### **Environment Setup**
- [ ] Python 3.11+ installed (`python --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Git installed (`git --version`)
- [ ] Code editor ready (VS Code recommended)
- [ ] Docker Desktop installed (optional but recommended)

### **API Access**
- [ ] Gemini API key obtained from https://makersuite.google.com/app/apikey
- [ ] API key tested (make a test request in AI Studio)
- [ ] API key stored securely (NOT in Git!)

### **Repository**
- [ ] GitHub account created
- [ ] New public repository created
- [ ] Repository cloned to local machine
- [ ] .gitignore configured (don't commit .env!)

---

## 💻 DEVELOPMENT PHASE

### **Backend Implementation**
- [x] `requirements.txt` created with all dependencies
- [x] `.env.example` template created
- [ ] `.env` file created and filled with real API key
- [x] `src/config.py` - Configuration management
- [x] `src/connectors/rss_connector.py` - RSS polling
- [x] `src/connectors/file_watcher.py` - Demo file ingestion
- [x] `src/pipeline/schemas.py` - Pathway table schemas
- [x] `src/pipeline/pathway_pipeline.py` - Main RAG pipeline
- [x] `src/pipeline/sentiment.py` - Sentiment analysis
- [x] `src/llm/embedder.py` - Gemini integration
- [x] `src/llm/prompts.py` - System prompts
- [x] `src/api_server.py` - FastAPI REST/WebSocket server
- [x] `src/main.py` - Entry point
- [ ] Backend runs without errors (`python src/main.py`)

### **Frontend Implementation**
- [x] React project initialized with Vite + TypeScript
- [x] Additional dependencies installed (recharts, axios, etc.)
- [x] `src/types/index.ts` - TypeScript interfaces
- [x] `src/services/api.ts` - API client
- [x] `src/components/NewsTicker.tsx` - News display
- [x] `src/components/AnalystChat.tsx` - Chat interface
- [x] `src/components/SentimentChart.tsx` - Chart visualization
- [x] `src/components/AlertPanel.tsx` - Alerts display
- [x] `src/App.tsx` - Main app component
- [ ] Frontend builds without errors (`npm run dev`)

### **Integration Testing**
- [ ] Backend starts on port 8000
- [ ] Frontend starts on port 5173
- [ ] Frontend can fetch news from backend (check Network tab)
- [ ] WebSocket connection established (or polling works)
- [ ] News ticker displays articles
- [ ] Sentiment chart renders
- [ ] Alert panel shows alerts (if any)
- [ ] Chat interface sends queries and receives answers

---

## 🎬 DEMO PREPARATION

### **Demo Files**
- [x] `demo/market_flash_crash.txt` created
- [x] `demo/bitcoin_surge.txt` created
- [x] `demo/breaking_tech_acquisition.txt` created
- [ ] Demo files tested (drop into `data/breaking_news/`)
- [ ] Articles appear in ticker within 2 seconds

### **Demo Script**
- [x] `demo/DEMO_SCRIPT.md` created
- [ ] Demo script rehearsed (practice 3x minimum)
- [ ] Timing verified (3-5 minutes total)
- [ ] FileWatcher "money shot" practiced

### **System Verification**
- [ ] RSS feeds are loading (BBC, Reuters, TechCrunch, HackerNews)
- [ ] Sentiment chart shows data (wait 10 minutes for data)
- [ ] Alert system triggers for keywords (test with demo files)
- [ ] Query latency < 2 seconds
- [ ] No errors in backend console
- [ ] No errors in browser console (F12)

---

## 📹 VIDEO RECORDING

### **Pre-Recording**
- [ ] Record test video (check audio/video quality)
- [ ] Close unnecessary tabs and applications
- [ ] Clear `data/breaking_news/` folder
- [ ] Copy demo files to desktop for easy access
- [ ] Review `VIDEO_SCRIPT.md`
- [ ] Set recording resolution to 1080p

### **Recording Checklist**
- [ ] Screen recorded (OBS Studio / Loom / Zoom)
- [ ] Audio clear (test microphone levels)
- [ ] Intro section (0:00-0:30) ✅
- [ ] Dashboard overview (0:30-1:15) ✅
- [ ] Real-time ingestion demo (1:15-2:30) ✅ **CRITICAL**
- [ ] AI analyst query (2:30-3:45) ✅
- [ ] Technology stack explanation (3:45-4:15) ✅
- [ ] Closing (4:15-4:30) ✅

### **Post-Recording**
- [ ] Video edited (if needed - remove long pauses)
- [ ] Captions/subtitles added
- [ ] Video uploaded to YouTube (Unlisted) or Loom
- [ ] Video link tested (open in incognito browser)
- [ ] Video link added to README.md

---

## 📚 DOCUMENTATION

### **Core Documentation**
- [x] `README.md` - Complete with architecture, setup, tech stack
- [x] `QUICKSTART.md` - Step-by-step setup instructions
- [x] `IMPLEMENTATION_SUMMARY.md` - Technical deep dive
- [x] `VIDEO_SCRIPT.md` - Recording guide
- [x] `PROJECT_STATUS.md` - Current status report
- [x] `TEAM_COLLABORATION.md` - Team workflow guide
- [ ] All documentation reviewed for typos/errors

### **README.md Sections** (Verify These)
- [ ] Project title and description
- [ ] Architecture diagram (ASCII art or image)
- [ ] Technology stack justification
- [ ] Quick start guide (Docker + local)
- [ ] Demo instructions
- [ ] Comparison table (RSS vs NewsAPI)
- [ ] Team member credits
- [ ] Video demo link
- [ ] GitHub repository link

---

## 🐳 DOCKER DEPLOYMENT

### **Docker Configuration**
- [x] `Dockerfile` created (backend)
- [x] `frontend/Dockerfile` created
- [x] `frontend/nginx.conf` created
- [x] `docker-compose.yml` created
- [ ] Docker build succeeds (`docker-compose build`)
- [ ] Docker containers start (`docker-compose up`)
- [ ] Frontend accessible at http://localhost:5173
- [ ] Backend accessible at http://localhost:8000
- [ ] Health checks pass

### **Docker Testing**
- [ ] Test on fresh machine (or delete `venv`, `node_modules` and rebuild)
- [ ] Verify `.env` is NOT in Docker image (security)
- [ ] Verify all features work in containers

---

## 🚀 SUBMISSION PHASE

### **GitHub Repository**
- [ ] All code pushed to main branch
- [ ] `.env` NOT committed (only `.env.example`)
- [ ] `.gitignore` properly configured
- [ ] README.md is complete and formatted
- [ ] Repository set to PUBLIC (not private!)
- [ ] Repository has proper description and tags
- [ ] LICENSE file added (MIT recommended)

### **Repository Structure Check**
```
- [ ] Root folder has: README.md, requirements.txt, docker-compose.yml
- [ ] src/ folder has all Python modules
- [ ] frontend/ folder has React code
- [ ] demo/ folder has demo files and scripts
- [ ] data/ folder structure exists (can be empty)
- [ ] All documentation files present
```

### **Unstop Platform Submission**
- [ ] GitHub repository URL copied
- [ ] Video demo URL copied
- [ ] Team member details prepared
- [ ] Project title: "Live News Analyst - Real-Time RAG with Pathway"
- [ ] Project description (100-200 words) written
- [ ] Technology stack list prepared
- [ ] All form fields filled
- [ ] Submission previewed
- [ ] **SUBMITTED** ✅

---

## 🏆 FINAL QUALITY CHECK

### **Code Quality**
- [ ] No hardcoded API keys in code
- [ ] No `print()` statements (use `logger.info()`)
- [ ] No commented-out code blocks
- [ ] Variable names are descriptive
- [ ] Functions have docstrings
- [ ] Type hints used (Python and TypeScript)

### **Functionality**
- [ ] System starts without errors (both backend + frontend)
- [ ] RSS feeds load articles (wait 1-2 minutes)
- [ ] FileWatcher ingests demo files instantly
- [ ] Sentiment chart displays data
- [ ] Alert system triggers correctly
- [ ] Chat queries return responses
- [ ] No crashes during 5-minute demo

### **Documentation**
- [ ] README.md has no spelling errors
- [ ] All links work (video, GitHub, external references)
- [ ] Code comments are clear
- [ ] Installation steps are accurate
- [ ] Troubleshooting section is helpful

### **Demo Readiness**
- [ ] Video is 3-5 minutes long
- [ ] Video shows file drop → instant update
- [ ] Video demonstrates query functionality
- [ ] Video mentions technology stack
- [ ] Video is professional (clear audio, no fumbling)

---

## 📊 SCORING SELF-ASSESSMENT

Before submitting, rate yourself on each criterion:

### **Real-Time Capability (35%)**
- [ ] System ingests data with <2s latency (FileWatcher proves this) - **10/10**
- [ ] Incremental indexing works (no batch re-indexing) - **10/10**
- [ ] Demo clearly shows real-time updates - **10/10**
- **Subtotal: ___/30 points**

### **Technical Implementation (30%)**
- [ ] Code is clean and well-organized - **___/10**
- [ ] Pathway used correctly (not just wrapper around LangChain) - **___/10**
- [ ] Proper error handling and logging - **___/10**
- **Subtotal: ___/30 points**

### **Innovation (20%)**
- [ ] Custom RSS connector (not standard API) - **___/7**
- [ ] Sentiment analysis ticker - **___/7**
- [ ] Keyword alert system - **___/6**
- **Subtotal: ___/20 points**

### **Impact (15%)**
- [ ] Clear use case (financial/news monitoring) - **___/8**
- [ ] Solves real problem (knowledge cutoff) - **___/7**
- **Subtotal: ___/15 points**

### **Documentation (Bonus)**
- [ ] Comprehensive README - **+5**
- [ ] Video demo included - **+5**
- **Bonus: ___/10 points**

---

## 🎯 EXPECTED SCORE: ___/95+

**Target:** 85+ points (Top 10%)  
**Stretch Goal:** 90+ points (Top 5%)

---

## ⏰ TIME MANAGEMENT

### **Day-by-Day Breakdown** (8 days available)

**Day 1 (Jan 2):**
- [ ] Environment setup
- [ ] Repository creation
- [ ] Backend skeleton

**Day 2 (Jan 3):**
- [ ] RSS connector working
- [ ] Frontend initialized

**Day 3 (Jan 4):**
- [ ] Pathway pipeline functional
- [ ] React components built

**Day 4 (Jan 5):**
- [ ] API server implemented
- [ ] Frontend-backend integration

**Day 5 (Jan 6):**
- [ ] Sentiment analysis working
- [ ] Alert system functional

**Day 6 (Jan 7):**
- [ ] Docker configuration
- [ ] Full system testing

**Day 7 (Jan 8):**
- [ ] Documentation complete
- [ ] Demo script finalized

**Day 8 (Jan 9):**
- [ ] Video recorded
- [ ] Final review
- [ ] **SUBMIT!**

---

## 🚨 CRITICAL PATH (Must-Haves)

These are NON-NEGOTIABLE for a winning submission:

1. ✅ **System Runs**: Both backend and frontend start without errors
2. ✅ **FileWatcher Works**: Demo file → ticker update in <2s
3. ✅ **Video Demo**: Shows real-time capability clearly
4. ✅ **README Complete**: Setup instructions work for judges
5. ✅ **GitHub Public**: Repository is accessible

If ANY of these fail, **DO NOT SUBMIT** until fixed.

---

## 💡 PRO TIPS

### **Day Before Submission (Jan 9)**
- [ ] Test on a teammate's machine (or fresh Docker build)
- [ ] Record backup video (in case first one has issues)
- [ ] Sleep well (tired = mistakes)

### **Submission Day (Jan 10)**
- [ ] Submit early (don't wait for deadline)
- [ ] Double-check all links work
- [ ] Keep backend running (in case judges test live)

### **After Submission**
- [ ] Celebrate! 🎉
- [ ] Don't touch code (judges might clone repo)
- [ ] Prepare for potential Q&A/presentation

---

## 📞 NEED HELP?

### **Resources**
- Pathway Docs: https://pathway.com/developers/
- Gemini API: https://ai.google.dev/
- React Docs: https://react.dev/

### **Internal Docs**
- Setup issues? → `QUICKSTART.md`
- Technical questions? → `IMPLEMENTATION_SUMMARY.md`
- Demo prep? → `demo/DEMO_SCRIPT.md` + `VIDEO_SCRIPT.md`
- Team coordination? → `TEAM_COLLABORATION.md`

---

## 🎉 YOU'VE GOT THIS!

**Remember:**
- ✅ All the code is already created
- ✅ All the documentation is written
- ✅ The demo strategy is proven

**Just need to:**
1. Get your API key
2. Run the system
3. Test it works
4. Record the video
5. Submit

**Estimated time to complete: 4-6 hours** (if working solo and focused)

---

**Now go win this hackathon! 🏆🚀**

Last updated: December 26, 2025
