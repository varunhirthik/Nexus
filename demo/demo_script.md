# Live News Analyst - Demo Script

## Overview
This demo showcases the **real-time capability** of the Live News Analyst system using the "Wizard of Oz" technique.

---

## Demo Flow (3 minutes)

### Part 1: System Introduction (0:00 - 0:30)

**Script:**
> "Welcome to the Live News Analyst - a real-time RAG system built with Pathway's differential dataflow engine. Unlike traditional batch-processed systems, our analyst updates its knowledge base continuously with zero manual intervention."

**Actions:**
- Show the dashboard homepage
- Point out the live news ticker scrolling
- Highlight the sentiment chart

---

### Part 2: Baseline Query (0:30 - 1:00)

**Script:**
> "Let's ask our analyst about a topic that hasn't been in the news yet."

**Actions:**
1. In the chat interface, type: **"What's happening with alien contact?"**
2. System responds: **"I don't have recent news about that topic."**
3. Say: "As expected - no aliens in the news... yet."

---

### Part 3: The "Wizard of Oz" Moment (1:00 - 2:00)

**Script:**
> "Now watch what happens when breaking news arrives. I'm going to simulate a news alert by dropping a file into our FileWatcher directory."

**Actions:**
1. Open File Explorer to `data/breaking_news/`
2. **Drag and drop** `demo/alien_invasion.txt` into the folder
3. **Immediately** (within 2-3 seconds):
   - Point to the ticker: "See - it's already appearing in the feed!"
   - The ticker shows: "Breaking: First Contact Confirmed..."
4. In chat, ask again: **"What's happening with alien contact?"**
5. System now responds with full details from the article
6. Highlight the **latency metric**: "Ingested and indexed in under 2 seconds."

---

### Part 4: Technical Explanation (2:00 - 2:45)

**Script:**
> "This demonstrates the power of Pathway's incremental indexing. The system didn't re-process the entire knowledge base - it simply propagated the delta through the computation graph."

**Actions:**
- Show the architecture diagram
- Explain: RSS feeds → Pathway engine → Real-time vector index
- Emphasize: "No batch jobs. No manual triggers. Just pure streaming."

---

### Part 5: Additional Features (2:45 - 3:00)

**Script:**
> "Beyond basic RAG, we've implemented sentiment analysis and keyword alerts."

**Actions:**
1. Point to sentiment chart: "Notice how sentiment dropped when the alien news arrived - uncertainty in markets"
2. Show keyword alerts: "The system automatically detected 'alien' trending and sent an alert"
3. Final statement: "This is the future of AI - always current, never outdated."

---

## Backup Demo Scenarios

### Scenario B: Market Crash
- Use: `demo/tesla_crash.txt`
- Query: "What's the latest on Tesla stock?"
- Demonstrates financial analysis capability

### Scenario C: Crypto Rally
- Use: `demo/bitcoin_rally.txt`
- Query: "Tell me about Bitcoin's recent performance"
- Shows multi-source synthesis (mentions Fed, JPMorgan, price data)

---

## Technical Deep Dive (Optional - 30s extension)

If judges ask about implementation:

1. **Custom RSS Connector:**
   ```python
   # Show code snippet
   class RSSConnector(pw.io.python.ConnectorSubject):
       def run(self):
           while True:
               # Poll feeds
               # Push to Pathway with self.next()
               self.commit()  # Low-latency commit
   ```

2. **Incremental Indexing:**
   - Explain differential dataflow vs. batch processing
   - Show `autocommit_duration_ms=1000` configuration

3. **Why RSS over NewsAPI:**
   - NewsAPI free tier has 24-hour delay
   - RSS gives instant access
   - Scores higher on "Real-Time Capability" criterion (35%)

---

## Common Questions & Answers

**Q: What happens if an RSS feed goes down?**
> "Our connector implements exponential backoff per-feed. If BBC fails, Reuters continues. The system is resilient."

**Q: How does this compare to ChatGPT with browsing?**
> "ChatGPT browses on-demand per query. We maintain a continuously updated index - much faster and more efficient for repeated queries."

**Q: Can it handle conflicting information?**
> "Yes - our prompt engineering instructs the LLM to prioritize recent data over older conflicting reports. We also include timestamps in the context."

**Q: What's the cost?**
> "100% free tier: RSS feeds (free), Google Gemini 1.5 Flash (free), Pathway (open-source). Production-ready at zero cost."

---

## Pre-Demo Checklist

- [ ] Backend running (`python src/main.py`)
- [ ] Frontend running (`npm run dev`)
- [ ] `data/breaking_news/` folder is **empty**
- [ ] Demo files ready in `demo/` folder
- [ ] Browser window open to dashboard
- [ ] File Explorer open to `data/breaking_news/`
- [ ] Network connection stable (for RSS feeds)
- [ ] Screen recording started (if creating video)

---

## Post-Demo Talking Points

**For Judges:**
1. "This architecture is production-ready. We could connect to Twitter, Reddit, or any real-time data source."
2. "The sentiment analysis could be enhanced with Gemini's LLM (currently using keyword-based for speed)."
3. "Keyword alerts could trigger automated actions - imagine auto-selling stocks on negative news."

**Innovation Highlights:**
- Custom Pathway connector (not in official docs)
- Dual-source ingestion (RSS + FileWatcher)
- Sub-2-second latency from publish to queryable
- Zero manual intervention required

---

## Troubleshooting

**Issue:** FileWatcher not detecting file
- **Fix:** Check `src/connectors/file_watcher.py` is running
- **Fix:** Ensure file has `.txt` extension
- **Fix:** Wait 2 seconds (poll interval)

**Issue:** Sentiment chart empty
- **Fix:** Wait for at least 3-5 articles to be ingested
- **Fix:** Check `data/output/sentiment.jsonl` exists

**Issue:** Chat not responding
- **Fix:** Check Gemini API key is valid
- **Fix:** Check rate limits (15 RPM for free tier)
- **Fix:** Check backend logs for errors

---

Good luck! 🚀
