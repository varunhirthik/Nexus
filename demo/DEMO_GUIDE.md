# Demo Guide - Live News Analyst

## FileWatcher Demo (Critical for Hackathon)

### Purpose
Prove <2 second real-time capability to judges without waiting for RSS feeds.

### Demo Files

Located in `demo/sample_articles/`:

1. **market_crash.txt** - Stock market crash scenario
2. **bitcoin_surge.txt** - Cryptocurrency rally
3. **tech_acquisition.txt** - Major tech acquisition

### Step-by-Step Demo

**1. Preparation** (Before presentation)
- Start both backend and frontend:
  ```powershell
  cd deployment
  docker-compose up -d
  ```
- Open browser to http://localhost:5173
- Keep File Explorer open to `data/breaking_news/` folder

**2. Baseline Query** (Show the "before" state)
- In the chat interface, ask: **"What's the latest on market crashes?"**
- Expected response: "No recent reports found" or generic response
- This proves the system doesn't have this information yet

**3. File Drop** (The "magic moment")
- Drag `demo/sample_articles/market_crash.txt` into `data/breaking_news/`
- OR use PowerShell:
  ```powershell
  Copy-Item demo\sample_articles\market_crash.txt data\breaking_news\breaking1.txt
  ```

**4. Verify Ingestion** (Within 2 seconds)
- Watch news ticker - the headline should appear immediately
- Check backend logs - you should see "FileWatcher detected new file"
- Note the timestamp

**5. Re-Query** (Prove RAG works)
- Ask again: **"What's the latest on market crashes?"**
- Expected: System now provides detailed answer citing the article
- Highlight: "Ingested and indexed in under 2 seconds"

### Video Recording Script (3-5 minutes)

**0:00-0:30 - Problem Statement**
> "Large Language Models have a knowledge cutoff problem. Even the latest GPT-4 or Claude don't know what happened in the news today. The Live News Analyst solves this with real-time RAG powered by Pathway's differential dataflow engine."

**0:30-1:00 - Architecture Overview**
- Show architecture diagram from README
- Explain: RSS feeds → Pathway → Incremental indexing → Real-time queries
- Emphasize: "No batch processing, no manual triggers, just continuous streaming"

**1:00-2:30 - Live Demo (CRITICAL!)**
- Show dashboard with news ticker
- Perform baseline query
- **Drop demo file while screen recording**
- Show immediate appearance in ticker
- Re-query and show answer
- Point to timestamp: "Less than 2 seconds from file drop to searchable"

**2:30-3:00 - Innovation Highlights**
- Custom RSS connector (free, no API delays)
- Sentiment analysis with rolling window
- Professional React dashboard (not Streamlit like most projects)
- 100% free tier deployment

**3:00-3:30 - Technical Snippet (Optional)**
- Show 1-2 code files:
  - `backend/src/connectors/rss_connector.py` - Custom connector
  - `backend/src/pipeline/pathway_pipeline.py` - Incremental indexing
- Emphasize clean, production-grade code

### Backup Scenarios

If one demo fails, have backups ready:

| Scenario | File | Query |
|----------|------|-------|
| Primary | market_crash.txt | "What's happening with market crashes?" |
| Backup 1 | bitcoin_surge.txt | "Tell me about Bitcoin's recent performance" |
| Backup 2 | tech_acquisition.txt | "What's the latest on tech acquisitions?" |

### Common Demo Mistakes to Avoid

❌ **Don't** wait for RSS feeds (they take 60 seconds)  
✅ **Do** use FileWatcher for instant demo

❌ **Don't** show your API key on screen  
✅ **Do** hide `.env` file during recording

❌ **Don't** skip the baseline query  
✅ **Do** show "before" state to prove real-time update

❌ **Don't** make video too long (judges have 100+ to watch)  
✅ **Do** keep it 3-5 minutes max

❌ **Don't** just show code without running it  
✅ **Do** show live working system

### Troubleshooting Demo Issues

**Issue: File not ingested**
- Check FileWatcher is running: `docker logs news-analyst-backend`
- Ensure file is `.txt` format
- Try renaming: `breaking1.txt`, `breaking2.txt`, etc.

**Issue: Ticker not updating**
- Refresh browser
- Check WebSocket connection in browser console
- Restart frontend container

**Issue: RAG returns generic answer**
- Wait 5 more seconds (embedding computation)
- Check backend logs for errors
- Try asking more specific question

### Recording Tools

**Recommended**:
- **OBS Studio** (Free, professional): https://obsproject.com/
- **Loom** (Easy, browser-based): https://www.loom.com/
- **Zoom** (If you have it): Start meeting, share screen, record

**Settings**:
- Resolution: 1080p (1920x1080)
- Frame rate: 30 FPS minimum
- Audio: Clear voice, no background music
- Cursor: Highlight cursor for visibility

### Upload Checklist

- [ ] Video is 3-5 minutes long
- [ ] Audio is clear (test before full recording)
- [ ] No API keys visible
- [ ] FileWatcher demo successfully shown
- [ ] YouTube: Set to "Unlisted" (NOT private!)
- [ ] Copy link and add to README.md
- [ ] Test link in incognito window

---

## Additional Demo Ideas

### Sentiment Analysis Demo
1. Drop multiple positive news files
2. Show sentiment chart trending upward
3. Drop negative news (market crash)
4. Show sentiment drop in real-time

### Alert System Demo
1. Configure alert keyword (e.g., "Tesla")
2. Drop 3+ articles mentioning Tesla
3. Show alert trigger in UI
4. Explain: "Automatic trending topic detection"

### Multi-Source Synthesis Demo
1. Drop 2 articles about same event from different sources
2. Ask question: "What are different perspectives on [topic]?"
3. Show RAG synthesizes both sources
4. Highlight: "Cross-source fact-checking capability"

---

**Remember**: The FileWatcher demo is your secret weapon. It proves real-time capability without relying on external RSS feeds that judges can't verify. **This alone justifies 30+ points (35% criterion)!**

**Good luck!** 🚀
