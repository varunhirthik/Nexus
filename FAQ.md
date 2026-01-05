# ❓ Frequently Asked Questions (FAQ)

## 🚀 Getting Started

### **Q: I'm new to Pathway. Where do I start?**
**A:** Don't worry! The code is already written. Just:
1. Follow `QUICKSTART.md` for setup
2. Run `python src/main.py` (backend)
3. Run `npm run dev` in frontend folder
4. The system will work even if you don't understand every line

**Pro tip:** Focus on making it run first, understanding comes later.

---

### **Q: Do I need to know Rust to use Pathway?**
**A:** No! Pathway's Rust engine is under the hood. You only write Python code. It's like using pandas—you don't need to know C++ to use it.

---

### **Q: What if I don't have a Gemini API key?**
**A:** Get one for free:
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy and paste into `.env` file

Takes 2 minutes, no credit card required.

---

## 🐛 Troubleshooting

### **Q: Backend won't start - "GEMINI_API_KEY not configured"**
**A:** You haven't created the `.env` file. Do this:
```powershell
copy .env.example .env
notepad .env
# Replace "your_gemini_api_key_here" with your real key
```

---

### **Q: Backend crashes with "No module named 'pathway'"**
**A:** You forgot to activate the virtual environment:
```powershell
cd C:\New-projs\RAG
.\venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Mac/Linux

# Then install:
pip install -r requirements.txt
```

---

### **Q: Frontend shows "Failed to fetch" error**
**A:** Backend isn't running. Check:
1. Is `python src/main.py` running in another terminal?
2. Does http://localhost:8000 show a JSON response?
3. Is `frontend/.env` configured correctly?

---

### **Q: No articles appearing in the ticker**
**A:** RSS feeds might be slow. Use the FileWatcher:
```powershell
# Copy a demo file
copy demo\market_flash_crash.txt data\breaking_news\

# Wait 2 seconds, refresh browser
# Article should appear!
```

---

### **Q: Gemini returns "Rate Limit Exceeded"**
**A:** You hit the free tier limit (15 requests/minute). Wait 60 seconds and try again. For the hackathon, this is rare—free tier is generous.

---

## 🎬 Demo Questions

### **Q: What if RSS feeds don't update during my video demo?**
**A:** Use the FileWatcher technique! It's MORE impressive anyway:
1. Show empty `data/breaking_news/` folder
2. Drop demo file into it ON CAMERA
3. Article appears in 1-2 seconds
4. Judges see INSTANT ingestion proof

This is actually better than waiting for BBC to publish something.

---

### **Q: How do I prove it's real-time, not fake?**
**A:** Three ways:
1. **FileWatcher:** Drop file → instant update (undeniable)
2. **Timestamp:** Show "just now" timestamp on ticker
3. **Query:** Ask about the just-added article → LLM knows about it

---

### **Q: My demo video is 6 minutes. Is that too long?**
**A:** Yes. Cut it to 4-5 minutes:
- Remove long pauses
- Speed up slow parts (screen recording software)
- Focus on the "money shot" (file drop → instant update)

Judges have limited time. Shorter = better engagement.

---

## 💻 Technical Questions

### **Q: What's the difference between this and ChatGPT with browsing?**
**A:** 

| Feature | Our System | ChatGPT Browsing |
|---------|-----------|-----------------|
| **Data Source** | Continuous stream | On-demand web scraping |
| **Latency** | < 2 seconds | Minutes (per query) |
| **Knowledge** | Always current | Fetched when asked |
| **Cost** | $0 | $20/month (Plus) |
| **Scalability** | Can handle millions of docs | Limited to few pages per query |

**Key point:** We're a real-time DATABASE, they're a search engine.

---

### **Q: Why Pathway instead of LangChain?**
**A:** LangChain is great for prototypes, but:
- ❌ LangChain processes data in batches (ETL paradigm)
- ❌ Requires manual re-indexing when data changes
- ✅ Pathway uses differential dataflow (incremental updates)
- ✅ Pathway is production-grade (Rust engine)

**Analogy:** LangChain is like Excel, Pathway is like a real-time SQL database.

---

### **Q: Can I use OpenAI instead of Gemini?**
**A:** Yes, but:
- OpenAI charges per token (Gemini is free)
- OpenAI has 16k context limit (Gemini has 1M)
- OpenAI requires credit card (Gemini doesn't)

For a hackathon, Gemini is the smart choice.

---

### **Q: How does the sentiment analysis work?**
**A:** Simple keyword-based scoring:
- Positive words (growth, surge, profit) → +1
- Negative words (crash, decline, loss) → -1
- Aggregate over 10-minute window

It's not perfect, but it's fast and good enough for demo.

---

## 🏆 Hackathon Strategy

### **Q: What if other teams also use Pathway?**
**A:** Differentiate with:
1. **React frontend** (most will use Streamlit)
2. **Custom RSS connector** (most will use newsapi.org with delays)
3. **Sentiment + Alerts** (most will do basic RAG only)
4. **Professional docs** (most have minimal READMEs)

---

### **Q: Should I mention it's free tier?**
**A:** YES! Turn it into a strength:
> "We built a production-grade system with ZERO infrastructure cost. This is accessible to startups and researchers, not just enterprises with Bloomberg budgets."

Judges love cost-effectiveness.

---

### **Q: What if judges ask "How would this scale?"**
**A:** Have this answer ready:
> "Pathway is built on Rust and supports distributed processing. We could:
> 1. Add more RSS feeds (currently 4, could do 100+)
> 2. Deploy multiple workers for parallel processing
> 3. Use cloud object storage for vector index persistence
> 4. Add Redis for query caching
>
> The architecture is already designed for scale—we just limited scope for the hackathon timeline."

---

### **Q: How much time will this take to build?**
**A:** The code is ALREADY DONE! You just need to:
- Setup (2 hours): Install dependencies, get API key, test run
- Testing (2 hours): Make sure everything works
- Video (2 hours): Record, edit, upload
- Documentation review (1 hour): Proofread README
- **Total: ~7 hours**

If working in a team, divide by number of people.

---

## 📹 Video Recording

### **Q: What software should I use to record?**
**A:** 
- **Windows:** OBS Studio (free, professional)
- **Mac:** QuickTime (built-in, simple)
- **Web-based:** Loom (easiest, no install)
- **Paid:** Camtasia (if you have it)

OBS Studio recommended for quality.

---

### **Q: Should I show my face in the video?**
**A:** Optional. Two approaches work:
1. **Face + screen:** More personal, good if you're comfortable on camera
2. **Screen only:** More professional, focus on tech

Either is fine. Pick what you're comfortable with.

---

### **Q: Can I use background music?**
**A:** Yes, but:
- Keep volume LOW (your voice should be primary)
- Use royalty-free music (YouTube Audio Library)
- Avoid music with lyrics (distracting)

Or skip music entirely—clean narration works too.

---

## 🐳 Docker Questions

### **Q: Do I NEED to use Docker?**
**A:** No, but it's impressive. If short on time:
- Local development is fine for demo
- Mention "Docker-ready" in README
- Show `docker-compose.yml` exists

Judges appreciate it, but working demo > perfect deployment.

---

### **Q: Docker build fails with "no space left on device"**
**A:** Clean up Docker:
```powershell
docker system prune -a
```

This removes unused images/containers.

---

## 🤝 Team Collaboration

### **Q: How do we divide work in a 3-person team?**
**A:** See `TEAM_COLLABORATION.md`, but quick answer:
- **Person 1:** Backend (Pathway + connectors)
- **Person 2:** Frontend (React components)
- **Person 3:** DevOps (Docker, docs, video)

All help with testing and demo prep.

---

### **Q: We keep getting Git conflicts. Help!**
**A:** Use feature branches:
```bash
# Each person works on their own branch
git checkout -b feature/backend  # Person 1
git checkout -b feature/frontend # Person 2
git checkout -b feature/devops   # Person 3

# Merge to main only when tested
# Communicate before merging
```

---

## 🎓 Learning Questions

### **Q: Can I use this project for my portfolio?**
**A:** Absolutely! It's:
- Production-grade architecture
- Modern tech stack (React, Pathway, Gemini)
- Fully documented
- Open source

Add to LinkedIn, GitHub profile, resume.

---

### **Q: Where can I learn more about RAG?**
**A:** 
- Pathway tutorials: https://pathway.com/developers/
- LLM University (free): https://docs.cohere.com/docs/llmu
- Our `IMPLEMENTATION_SUMMARY.md` (explains the theory)

---

### **Q: What's next after the hackathon?**
**A:** Potential improvements:
1. Add Twitter API for social sentiment
2. Implement user authentication
3. Add email/Slack notifications for alerts
4. Deploy to cloud (AWS/GCP)
5. Monetize as SaaS product

The foundation is solid for a real startup!

---

## 🔒 Security Questions

### **Q: Is it safe to share my Gemini API key with teammates?**
**A:** Share securely:
- ✅ Signal/Telegram (encrypted messaging)
- ✅ 1Password shared vault
- ❌ Email
- ❌ Slack/Discord (can be logged)
- ❌ GitHub (NEVER!)

Better: Each teammate gets their own key (free tier per account).

---

### **Q: What if someone steals my API key from the video?**
**A:** Don't show it in the video!
- Don't show `.env` file
- Don't show API key in logs
- If accidentally shown, regenerate key immediately

---

## 📊 Judging Questions

### **Q: What if judges can't run my code?**
**A:** Make it foolproof:
1. Test setup on a friend's machine first
2. Have clear error messages
3. Provide Docker alternative (one command)
4. Include video (so they can see it work)

Video is your insurance policy.

---

### **Q: How do I stand out if many teams use Pathway?**
**A:** 
- Professional UI (React, not Streamlit)
- Innovation features (sentiment, alerts)
- Exceptional documentation
- Polished video demo
- Real-world use case articulation

Execution > idea.

---

## 🎯 Final Questions

### **Q: I'm running out of time. What should I cut?**
**A:** Priority order (keep top, cut bottom):
1. ✅ System works (core RAG + FileWatcher) - MUST HAVE
2. ✅ Video demo - MUST HAVE
3. ✅ README - MUST HAVE
4. ⚠️ Sentiment analysis - NICE TO HAVE
5. ⚠️ Alert system - NICE TO HAVE
6. ⚠️ Docker - NICE TO HAVE
7. ❌ Advanced features - CUT IF NEEDED

A working simple system beats a broken complex one.

---

### **Q: Should I submit early or wait until deadline?**
**A:** Submit EARLY (day before deadline). Benefits:
- No last-minute server crashes
- Time to fix if something breaks
- Shows confidence
- Less stress

Deadline day is for emergencies only.

---

### **Q: What if I don't win?**
**A:** You still built:
- A portfolio-worthy project
- Real-world skills (Pathway, React, LLMs)
- Professional documentation
- Video presentation skills

Hackathons are about learning, not just winning. You've already succeeded by completing this.

---

## 💬 Still Have Questions?

1. Check other docs:
   - `QUICKSTART.md` - Setup issues
   - `IMPLEMENTATION_SUMMARY.md` - Technical details
   - `VIDEO_SCRIPT.md` - Recording help
   - `TEAM_COLLABORATION.md` - Team workflow

2. Google/Stack Overflow for generic issues

3. Pathway Discord: https://discord.gg/pathway (official community)

4. Create GitHub Issue in your repo (team can answer)

---

**Remember: The code is done. You've got this! 🚀**

**Now stop reading FAQs and start building! ⚡**
