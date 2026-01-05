# 🎥 Video Demo Script - Live News Analyst

## 📋 Pre-Recording Checklist

### **Setup (30 mins before)**
- [ ] Backend running: `python src/main.py`
- [ ] Frontend running: `npm run dev`
- [ ] Browser at http://localhost:5173
- [ ] Clear `data/breaking_news/` folder
- [ ] Prepare 3 demo files in desktop folder for easy access
- [ ] Close unnecessary tabs/apps (clean screen)
- [ ] Test audio (clear voice, no echo)
- [ ] Test screen recording (1080p minimum)

### **Recording Tools**
- **Windows:** OBS Studio (free) or Loom
- **Screen Resolution:** 1920x1080
- **Audio:** Clear microphone, minimal background noise
- **Duration Target:** 3-5 minutes

---

## 🎬 Video Script (4 minutes 30 seconds)

### **INTRO (0:00 - 0:30)**

> **[Show your face OR just screen with calm background music]**
>
> "Hello! I'm [Your Name], and this is our submission for the DataQuest Hackathon: the Live News Analyst.
>
> This is a real-time RAG system that solves a critical problem: traditional LLMs have knowledge cutoffs. If you ask ChatGPT about news from 10 seconds ago, it doesn't know.
>
> Our system uses Pathway's differential dataflow engine to continuously ingest, index, and make queryable live news streams with near-zero latency. Let me show you."

**[Transition to full-screen browser view]**

---

### **ACT 1: Dashboard Overview (0:30 - 1:15)**

> **[Browser showing Live News Analyst dashboard]**
>
> "Here's our dashboard. Notice the green 'Live' indicator in the top right—that means our system is actively streaming data from four RSS feeds: BBC, Reuters, TechCrunch, and Hacker News.
>
> **[Point to stats bar]**
>
> We can see the system has indexed 43 articles, with 12 coming in just the last hour. We're monitoring 4 active sources, and our average response latency is 127 milliseconds.
>
> **[Scroll through news ticker]**
>
> The news ticker shows real-time headlines. Notice they're color-coded by source—BBC in red, Reuters in blue, TechCrunch in green. Each article has a timestamp showing when it was ingested.
>
> **[Point to sentiment chart]**
>
> This sentiment chart analyzes headlines using a 10-minute rolling window. The score ranges from -1 (very negative) to +1 (very positive). Right now, the market sentiment is slightly negative at -0.15.
>
> **[Point to alert panel]**
>
> And down here, we have keyword alerts. The system monitors for trending topics like Bitcoin, Tesla, Fed announcements—anything that crosses a threshold triggers an alert."

---

### **ACT 2: Real-Time Ingestion Demo (1:15 - 2:30)** ⭐ **MOST IMPORTANT**

> "Now, here's where it gets impressive. Let me prove this is TRULY real-time, not batch processing.
>
> **[Split screen OR picture-in-picture: Show File Explorer + Browser]**
>
> I'm opening the File Explorer to our monitored directory, `data/breaking_news`. As you can see, it's currently empty.
>
> **[Pick up first demo file: market_flash_crash.txt]**
>
> I have a simulated breaking news article here about a market flash crash. Watch what happens when I drop it into this folder.
>
> **[Drag and drop file]**
>
> **[IMMEDIATELY switch back to browser - CRITICAL: Show timestamp]**
>
> There it is! In less than 2 seconds, the article appears at the top of our ticker. Notice the source says 'FileWatcher' and the timestamp says 'just now.'
>
> **[Scroll to alert panel]**
>
> And because the article contains the keywords 'crash,' 'Fed,' and 'volatility,' our alert system immediately flagged it.
>
> This is Pathway's differential dataflow in action. The moment data enters the system, it's:
> 1. Chunked
> 2. Embedded using Google Gemini
> 3. Indexed in our vector database
> 4. And immediately searchable
>
> No batch jobs. No manual re-indexing. Just continuous, incremental updates."

---

### **ACT 3: AI Analyst Query (2:30 - 3:45)**

> **[Click on 'AI Analyst Chat' tab]**
>
> "Now that the article is indexed, let's query our AI analyst about it.
>
> **[Type in chat: 'What happened with the market flash crash?']**
>
> I'm asking: 'What happened with the market flash crash?'
>
> **[While waiting for response]**
>
> Behind the scenes, the system is:
> - Embedding my query using Gemini
> - Performing a KNN search across all indexed articles
> - Retrieving the top 5 most relevant chunks
> - Feeding them to the LLM for generation
>
> **[Response appears]**
>
> And here's the answer! It correctly identifies the flash crash, mentions the 5.2% drop, and even references the Federal Reserve's monitoring—all from the article I added 20 seconds ago.
>
> **[Click 'Show sources']**
>
> If we expand the sources, we can see exactly which articles were used. There's our flash crash article with a link back to the original.
>
> Notice the latency: 542 milliseconds from question to answer. That's fast.
>
> **[Type second query: 'Should I be worried about my portfolio?']**
>
> Let me ask a follow-up: 'Should I be worried about my portfolio?'
>
> **[Show answer]**
>
> The AI responds based on the retrieved context, explaining the recovery and Fed's stabilization efforts. This is RAG in action—grounding the LLM's response in real, current data."

---

### **ACT 4: Technology Stack (3:45 - 4:15)**

> **[Optional: Show quick code snippet OR architecture diagram]**
>
> "So how does this work? Our stack is 100% free tier:
>
> - **Data Source:** RSS feeds—no 24-hour delays like NewsAPI's free tier
> - **Streaming Engine:** Pathway—handles differential dataflow and incremental indexing
> - **LLM:** Google Gemini 1.5 Flash—1 million token context window, completely free
> - **Frontend:** React with TypeScript, WebSocket for live updates
> - **Deployment:** Fully Dockerized for easy reproduction
>
> **[Show GitHub repo OR README]**
>
> Everything is open source and documented. Our README includes:
> - Full architecture diagram
> - Setup instructions (Docker one-liner)
> - Technology justification
> - And a demo script
>
> The repository also includes our Pathway pipeline code, the custom RSS connector, and all the React components."

---

### **CLOSING (4:15 - 4:30)**

> **[Back to dashboard OR show face]**
>
> "To summarize: we've built a production-ready, real-time RAG system that solves the knowledge cutoff problem. It ingests news continuously, updates the index incrementally, and answers queries based on the absolute latest data—all with sub-second latency.
>
> This architecture can scale to financial analysis, crisis monitoring, or any domain where recency matters.
>
> Thank you for watching, and we hope you found this impressive!
>
> **[Show text overlay]**
> GitHub: [Your repo link]
> Team: [Your names]
> Hackathon: DataQuest 2025"

**[Fade out with dashboard in background]**

---

## 🎞️ Editing Tips

### **Must-Have Shots**
1. ✅ File drop → Instant ticker update (use slow-motion if possible!)
2. ✅ Alert panel lighting up
3. ✅ Query latency metric (542ms)
4. ✅ "Live" indicator with green pulse

### **Visual Enhancements**
- Add on-screen annotations:
  - **Arrow pointing to:** "< 2 seconds latency"
  - **Circle highlighting:** Alert keywords
  - **Zoom effect:** When article appears
- Use transitions between sections (fade, not jarring cuts)
- Add subtle background music (low volume, no vocals)

### **Captions**
Include subtitles for accessibility (YouTube auto-generates them, but review for accuracy)

---

## 📤 Upload & Submission

### **YouTube Upload**
- **Title:** "Live News Analyst - Real-Time RAG with Pathway (DataQuest Hackathon 2025)"
- **Description:**
  ```
  A production-grade real-time RAG system built for the DataQuest Hackathon.
  
  🚀 Features:
  - Continuous RSS feed ingestion
  - Incremental vector indexing (Pathway)
  - Real-time sentiment analysis
  - Keyword alert system
  - AI-powered Q&A interface
  
  🛠️ Tech Stack:
  - Pathway (streaming engine)
  - Google Gemini 1.5 Flash (LLM)
  - React + TypeScript (frontend)
  - FastAPI (REST/WebSocket API)
  - Docker (deployment)
  
  📂 GitHub: [Your repo link]
  👥 Team: [Names]
  
  #Pathway #RAG #LiveAI #Hackathon #LLM #RealTime
  ```
- **Visibility:** Unlisted (or Public if you want portfolio piece)
- **Tags:** Pathway, RAG, LLM, Hackathon, Real-time AI, Gemini

### **Alternative: Loom**
- Simpler for quick recording
- Automatically generates shareable link
- No editing needed (good for time-constrained)

---

## ⚠️ Common Mistakes to Avoid

1. ❌ **Don't rely on live RSS during demo**
   - RSS might be slow → use FileWatcher technique

2. ❌ **Don't skip showing the timestamp**
   - Judges need to see "just now" to believe real-time

3. ❌ **Don't talk too fast**
   - 4:30 is plenty of time, speak clearly

4. ❌ **Don't forget to show sources**
   - Proving RAG retrieval is critical

5. ❌ **Don't use complex jargon**
   - Judges might not be technical → explain simply

---

## 🏆 What Makes This Video Win

### **Technical Credibility**
- ✅ Live demo (not screenshots)
- ✅ Visible latency metrics
- ✅ Source code reference

### **Wow Factor**
- ✅ File drop → instant update (this will impress judges)
- ✅ Alert system auto-triggering
- ✅ Query answering recent event

### **Professionalism**
- ✅ Clean UI
- ✅ Smooth narration
- ✅ Proper documentation

---

**Now go record an amazing demo! 🎥🏆**

Need help? Re-read this script 3x before recording. Practice the file drop timing—it's the money shot! 💰
