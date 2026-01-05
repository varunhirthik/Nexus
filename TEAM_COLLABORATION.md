# 👥 Team Collaboration Guide

## 🎯 Recommended Team Structure (2-5 Members)

### **Optimal 3-Person Team**

| Role | Responsibilities | Time Estimate |
|------|------------------|---------------|
| **Backend Engineer** | Pathway pipeline, RSS connector, API | 12-15 hours |
| **Frontend Developer** | React components, UI/UX, charts | 10-12 hours |
| **DevOps + Documentation** | Docker, README, demo, video | 8-10 hours |

### **5-Person Team (Maximum Capacity)**

- **Person 1:** Pathway pipeline + RAG logic
- **Person 2:** API server (FastAPI) + WebSocket
- **Person 3:** React frontend components
- **Person 4:** Sentiment analysis + alerts + LLM integration
- **Person 5:** Docker, docs, demo script, video production

---

## 📂 Code Ownership (To Avoid Conflicts)

### **Backend (src/)**
```
src/
├── main.py                 # Person 1 (Pipeline Lead)
├── api_server.py           # Person 2 (API Lead)
├── config.py               # Shared (review by all)
├── connectors/
│   ├── rss_connector.py    # Person 1
│   └── file_watcher.py     # Person 1
├── pipeline/
│   ├── pathway_pipeline.py # Person 1
│   ├── sentiment.py        # Person 4
│   └── schemas.py          # Person 1
└── llm/
    ├── embedder.py         # Person 4
    └── prompts.py          # Person 4
```

### **Frontend (frontend/src/)**
```
frontend/src/
├── App.tsx                 # Person 3
├── components/
│   ├── NewsTicker.tsx      # Person 3
│   ├── AnalystChat.tsx     # Person 3
│   ├── SentimentChart.tsx  # Person 4 (if helping frontend)
│   └── AlertPanel.tsx      # Person 4 (if helping frontend)
├── services/
│   └── api.ts              # Person 2 (coordinates with backend)
└── types/
    └── index.ts            # Shared (Person 2 & 3 collaborate)
```

### **DevOps & Docs**
```
├── Dockerfile              # Person 5
├── docker-compose.yml      # Person 5
├── README.md               # Person 5 (all contribute sections)
├── QUICKSTART.md           # Person 5
├── demo/                   # Person 5
└── VIDEO_SCRIPT.md         # Person 5
```

---

## 🔄 Git Workflow

### **Branch Strategy**

```bash
main                    # Protected, only merge tested code
├── feature/backend     # Person 1 & 2
├── feature/frontend    # Person 3
├── feature/llm         # Person 4
└── feature/devops      # Person 5
```

### **Daily Workflow**

**Morning (15 min standup):**
1. What did you complete yesterday?
2. What are you working on today?
3. Any blockers?

**Work Session:**
```bash
# Pull latest from main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-component

# Make changes, commit often
git add .
git commit -m "feat: add RSS connector with polling"

# Push to your branch
git push origin feature/your-component

# Create Pull Request when done
# Get review from at least 1 team member
```

**Evening (30 min integration):**
- Merge approved PRs to `main`
- Run full system test
- Fix any integration issues

---

## 🔧 Development Setup (Each Team Member)

### **Initial Setup (First Day)**

```powershell
# Clone repository
git clone <your-repo-url>
cd RAG

# Backend setup
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Get shared .env file from team lead
# DO NOT commit .env to Git!

# Frontend setup
cd frontend
npm install
cd ..

# Test run
python src/main.py          # Terminal 1
cd frontend && npm run dev  # Terminal 2
```

### **Shared .env File**

**Team Lead creates:**
1. Get Gemini API key (share with team via secure method)
2. Create `.env` file
3. Share via Signal/Telegram (NOT GitHub)
4. Each member copies to their local machine

**DO NOT:**
- Commit `.env` to Git
- Share API keys in public channels
- Push sensitive data

---

## 📞 Communication Channels

### **Recommended Tools**

| Purpose | Tool | Frequency |
|---------|------|-----------|
| **Quick Messages** | Discord/Slack | Real-time |
| **Video Calls** | Zoom/Google Meet | Daily standup |
| **Code Review** | GitHub PR Comments | Before merge |
| **Documentation** | Google Docs (draft) → Markdown (final) | Continuous |
| **File Sharing** | GitHub (code), Google Drive (videos/PDFs) | As needed |

### **Communication Guidelines**

- 🔴 **Urgent (< 1 hour response)**: Deployment issues, broken main branch
- 🟡 **Normal (< 4 hours)**: Code reviews, feature discussions
- 🟢 **Low priority (< 24 hours)**: Documentation updates, nice-to-haves

---

## 🚨 Conflict Resolution

### **Code Conflicts**

```bash
# If you get merge conflicts
git checkout main
git pull origin main
git checkout feature/your-branch
git rebase main

# Resolve conflicts in files
# Then:
git add .
git rebase --continue
git push origin feature/your-branch --force
```

### **Design Disagreements**

1. Discuss in video call (don't argue in chat)
2. If no consensus, team lead makes final call
3. Document decision in GitHub issue

### **Who Decides What**

- **Architecture decisions**: Backend lead (Person 1)
- **UI/UX decisions**: Frontend lead (Person 3)
- **Tech stack**: Unanimous agreement
- **Deadlines**: Project manager (if assigned) or team vote

---

## 📅 Timeline (8 Days: Jan 2 - Jan 10)

### **Day 1-2 (Jan 2-3): Foundation**
- [ ] Repository setup (Person 5)
- [ ] Backend skeleton (Person 1)
- [ ] Frontend skeleton (Person 3)
- [ ] API contracts defined (Person 2)

### **Day 3-4 (Jan 4-5): Core Features**
- [ ] RSS connector working (Person 1)
- [ ] Pathway pipeline running (Person 1)
- [ ] React components built (Person 3)
- [ ] API endpoints live (Person 2)

### **Day 5-6 (Jan 6-7): Integration**
- [ ] Frontend ↔ Backend connected
- [ ] Sentiment analysis working (Person 4)
- [ ] Alert system working (Person 4)
- [ ] Full system test

### **Day 7 (Jan 8): Polish**
- [ ] Docker build working (Person 5)
- [ ] README complete (Person 5)
- [ ] Demo script finalized (Person 5)
- [ ] Code cleanup

### **Day 8 (Jan 9): Video & Submission**
- [ ] Record demo video (Person 5 + Person 3 for narration)
- [ ] Final testing
- [ ] GitHub repository public
- [ ] Submit on Unstop

---

## 🧪 Testing Strategy

### **Manual Testing Checklist** (Before Each Merge)

**Backend:**
- [ ] `python src/main.py` starts without errors
- [ ] RSS connector fetches articles
- [ ] FileWatcher detects new files
- [ ] API responds at http://localhost:8000

**Frontend:**
- [ ] `npm run dev` starts without errors
- [ ] News ticker displays articles
- [ ] Sentiment chart renders
- [ ] Chat interface sends queries

**Integration:**
- [ ] Frontend can fetch news from backend
- [ ] Query endpoint returns answers
- [ ] WebSocket (or polling) updates in real-time

### **Acceptance Criteria for Demo**

- [ ] File drop → article appears in <3 seconds
- [ ] Query about dropped article → correct answer
- [ ] Sentiment chart shows data
- [ ] Alert triggers for demo keywords

---

## 🏆 Team Contribution Recognition

### **In README.md, Add:**

```markdown
## 👥 Team

- **[Name 1]** - Backend Engineering (Pathway pipeline, RSS connector)
- **[Name 2]** - API Development (FastAPI, WebSocket integration)
- **[Name 3]** - Frontend Development (React components, UI/UX)
- **[Name 4]** - LLM Integration (Gemini embeddings, sentiment analysis)
- **[Name 5]** - DevOps & Documentation (Docker, README, demo video)
```

### **In Video Demo:**

> "This project was built by a team of [N] developers. [Name 1] handled the Pathway pipeline, [Name 2] built the API layer, [Name 3] crafted the React frontend, [Name 4] integrated Gemini, and [Name 5] managed deployment and documentation. It was truly a collaborative effort!"

---

## 💡 Tips for Success

### **For Backend Team**
1. Use `logger.info()` extensively (helps with debugging)
2. Test connectors individually before full pipeline
3. Cache embeddings to avoid Gemini rate limits

### **For Frontend Team**
1. Use mock data first (don't wait for backend)
2. Make components independent (easier to test)
3. Handle loading/error states gracefully

### **For DevOps**
1. Test Docker build early (don't wait until last day)
2. Write README as you go (not at the end)
3. Keep QUICKSTART.md updated

### **For Everyone**
1. Commit often with clear messages: `feat:`, `fix:`, `docs:`
2. Don't push broken code to `main`
3. Review others' PRs within 4 hours
4. Ask questions early (don't get stuck for hours)

---

## 🚫 Common Pitfalls

### ❌ **Don't:**
- Work in isolation for 3+ days
- Skip code reviews ("we trust each other")
- Leave documentation for the last day
- Test only on your machine (works on mine!)
- Argue in text (call instead)

### ✅ **Do:**
- Daily standups (even if short)
- Merge to main daily (small increments)
- Document as you code
- Test on fresh environments
- Celebrate small wins

---

## 📞 Emergency Contacts

| Issue | Contact | Backup |
|-------|---------|--------|
| **Backend broken** | Person 1 | Person 2 |
| **Frontend broken** | Person 3 | Person 2 |
| **Docker broken** | Person 5 | Person 1 |
| **LLM/API issues** | Person 4 | Person 2 |
| **Git conflicts** | Person 5 | Anyone with Git experience |

---

## 🎉 Let's Build Something Amazing!

**Remember:** The hackathon judges care about:
1. **Does it work?** (demo must be flawless)
2. **Is it innovative?** (custom connector, sentiment, alerts)
3. **Is it real-time?** (FileWatcher proves this)
4. **Is it documented?** (README, video)

**Your team has all the tools to win. Now go execute! 🚀**

---

**Questions?** Create a GitHub Discussion or ping the team lead.

**Let's make this the best submission at DataQuest 2025! 💪**
