# 🧠 Live News Analyst - Application Flow & Architecture

**Date**: January 11, 2026  
**Purpose**: Complete technical understanding of the system

---

## 📋 Table of Contents

1. [High-Level Concept](#high-level-concept)
2. [Data Flow Diagram](#data-flow-diagram)
3. [Component Breakdown](#component-breakdown)
4. [File-by-File Explanation](#file-by-file-explanation)
5. [Execution Flow](#execution-flow)
6. [Key Technologies](#key-technologies)

---

## 🎯 High-Level Concept

**What is this app?**

Live News Analyst is a **real-time RAG (Retrieval-Augmented Generation) system** that:

1. **Continuously ingests** news from RSS feeds and file drops
2. **Analyzes sentiment** of each article in real-time
3. **Indexes content** using vector embeddings (Google Gemini)
4. **Answers questions** about recent news using LLM + retrieved context
5. **Displays live updates** in a React dashboard with WebSocket push

**Core Innovation**: Solves the "LLM knowledge cutoff" problem by maintaining an always-current knowledge base without manual re-indexing.

---

## 📊 Data Flow Diagram

```
┌─────────────────── DATA SOURCES ───────────────────┐
│                                                     │
│  ┌──────────────┐           ┌──────────────┐      │
│  │  RSS Feeds   │           │ FileWatcher  │      │
│  │  (BBC, etc.) │           │  (Demo Dir)  │      │
│  └──────┬───────┘           └──────┬───────┘      │
│         │                          │               │
└─────────┼──────────────────────────┼───────────────┘
          │                          │
          │   ┌──────────────────────┘
          │   │
          ▼   ▼
┌─────────────────────────────────────────────────────┐
│         PATHWAY DIFFERENTIAL DATAFLOW               │
│  ┌─────────────────────────────────────────────┐   │
│  │  1. RSSConnector / FileWatcherConnector     │   │
│  │     → Polls sources, deduplicates          │   │
│  │     → Pushes to Pathway table              │   │
│  └──────────────┬──────────────────────────────┘   │
│                 │                                   │
│  ┌──────────────▼──────────────────────────────┐   │
│  │  2. Processing Pipeline                     │   │
│  │     → Sentiment analysis (TextBlob)         │   │
│  │     → Keyword extraction                    │   │
│  │     → Enrichment with metadata              │   │
│  └──────────────┬──────────────────────────────┘   │
│                 │                                   │
│  ┌──────────────▼──────────────────────────────┐   │
│  │  3. RAG Components                          │   │
│  │     → Gemini embeddings (768-dim vectors)   │   │
│  │     → KNN index (incremental updates)       │   │
│  │     → Query processing                      │   │
│  └──────────────┬──────────────────────────────┘   │
│                 │                                   │
│  ┌──────────────▼──────────────────────────────┐   │
│  │  4. Output Sinks                            │   │
│  │     → headlines.jsonl (ticker data)         │   │
│  │     → sentiment.jsonl (chart data)          │   │
│  │     → alerts.jsonl (keyword alerts)         │   │
│  └──────────────┬──────────────────────────────┘   │
└─────────────────┼───────────────────────────────────┘
                  │
                  │
          ┌───────▼───────┐
          │  FastAPI      │
          │  REST/WS API  │
          └───────┬───────┘
                  │
                  │ WebSocket (real-time push)
                  │ REST (queries)
                  │
          ┌───────▼───────────────────────┐
          │  React Frontend               │
          │  ┌───────────────────────┐   │
          │  │  NewsTicker (ticker)  │   │
          │  │  SentimentChart       │   │
          │  │  AlertPanel           │   │
          │  │  AnalystChat (RAG UI) │   │
          │  └───────────────────────┘   │
          │                               │
          │  User sees:                   │
          │  - Live headlines scrolling   │
          │  - Sentiment over time        │
          │  - Keyword alerts             │
          │  - Can ask questions          │
          └───────────────────────────────┘
```

---

## 🔧 Component Breakdown

### Backend (Python + Pathway)

| Component | Purpose | Key Files |
|-----------|---------|-----------|
| **Entry Point** | Starts API server + Pathway pipeline | `main.py` |
| **Configuration** | Loads env vars, validates settings | `config.py` |
| **API Server** | REST/WebSocket endpoints for frontend | `api_server.py` |
| **RSS Connector** | Polls RSS feeds, deduplicates | `connectors/rss_connector.py` |
| **FileWatcher** | Monitors dir for demo files | `connectors/file_watcher.py` |
| **Pipeline Orchestrator** | Pathway dataflow graph | `pipeline/pathway_pipeline.py` |
| **Sentiment Analyzer** | TextBlob + rolling window | `pipeline/sentiment.py` |
| **Schemas** | Pathway table definitions | `pipeline/schemas.py` |
| **LLM Interface** | Gemini API wrapper | `llm/embedder.py` |
| **Prompts** | RAG prompt templates | `llm/prompts.py` |

### Frontend (React + TypeScript)

| Component | Purpose | Key Files |
|-----------|---------|-----------|
| **Main App** | Tab navigation, state management | `App.tsx` |
| **NewsTicker** | Scrolling headlines | `components/NewsTicker.tsx` |
| **AnalystChat** | RAG query interface | `components/AnalystChat.tsx` |
| **SentimentChart** | Line chart (Recharts) | `components/SentimentChart.tsx` |
| **AlertPanel** | Keyword alert notifications | `components/AlertPanel.tsx` |
| **API Service** | WebSocket + REST client | `services/api.ts` |
| **Type Definitions** | TypeScript interfaces | `types/index.ts` |

### Deployment

| Component | Purpose | Key Files |
|-----------|---------|-----------|
| **Docker Compose** | Multi-container orchestration | `deployment/docker-compose.yml` |
| **Backend Dockerfile** | Python 3.11 + Pathway | `backend/Dockerfile` |
| **Frontend Dockerfile** | Node build + nginx | `frontend/Dockerfile` |
| **Nginx Config** | Static file serving | `deployment/nginx.conf` |

---

## 📁 File-by-File Explanation

### Backend Files

#### `backend/src/main.py` (Entry Point)
```python
# RESPONSIBILITIES:
# 1. Load environment variables (.env file)
# 2. Validate GEMINI_API_KEY exists
# 3. Create necessary directories (data/output, data/breaking_news)
# 4. Print startup banner
# 5. Start FastAPI server in background thread
# 6. Run Pathway pipeline in main thread

# FLOW:
# main() → check_environment() → start API thread → pipeline.run()
```

**Key Functions**:
- `check_environment()`: Validates API key and config
- `print_startup_banner()`: ASCII art banner
- `main()`: Starts API server in thread, then runs Pathway pipeline

---

#### `backend/src/config.py` (Configuration)
```python
# RESPONSIBILITIES:
# 1. Load all environment variables using Pydantic
# 2. Provide type-safe access to settings
# 3. Parse comma-separated strings (RSS feeds, keywords)

# LOADED FROM .env:
# - GEMINI_API_KEY
# - LLM_MODEL (default: gemini-1.5-flash)
# - RSS_FEEDS (comma-separated URLs)
# - RSS_POLL_INTERVAL (seconds)
# - PATHWAY_HOST, PATHWAY_PORT
# - ALERT_KEYWORDS
# - SENTIMENT_WINDOW_MINUTES
```

**Key Properties**:
- `settings.gemini_api_key`: API key
- `settings.rss_feed_list`: Parsed RSS URLs (property method)
- `settings.alert_keyword_list`: Parsed keywords

---

#### `backend/src/api_server.py` (FastAPI Server)
```python
# RESPONSIBILITIES:
# 1. Provide REST endpoints (/health, /news/latest, /stats, /query)
# 2. WebSocket endpoint (/ws) for real-time push
# 3. CORS middleware for frontend access
# 4. Connection manager for WebSocket clients

# ENDPOINTS:
# GET  /health         → Docker healthcheck
# GET  /news/latest    → Latest 20 articles
# GET  /stats          → System statistics
# POST /query          → RAG question answering
# WS   /ws             → Live updates (news, sentiment, alerts)
```

**Key Classes**:
- `ConnectionManager`: Manages WebSocket connections, broadcasts messages
- `GlobalState`: Shared state between Pathway and API (simplified approach)

**Note**: In production, this would use Pathway's HTTP server directly. Current implementation is simplified for hackathon.

---

#### `backend/src/connectors/rss_connector.py` (RSS Polling)
```python
# RESPONSIBILITIES:
# 1. Poll multiple RSS feeds every 60 seconds
# 2. Deduplicate using GUID/link (persistent cache)
# 3. Extract title, summary, content, link, published date
# 4. Handle individual feed failures gracefully
# 5. Push new articles to Pathway via self.next()

# DEDUPLICATION STRATEGY:
# - Uses link URL as unique identifier
# - Maintains in-memory set of seen links
# - Persists to data/output/rss_cache.json
# - Prevents re-ingesting same article

# BACKOFF STRATEGY:
# - If feed fails, retry with exponential backoff
# - Tracks retry delays per URL
```

**Key Methods**:
- `run()`: Main polling loop (runs in Pathway thread)
- `_load_cache()`: Load seen links from JSON
- `_save_cache()`: Persist seen links
- `self.next()`: Push article to Pathway dataflow

---

#### `backend/src/connectors/file_watcher.py` (FileWatcher for Demo)
```python
# RESPONSIBILITIES:
# 1. Monitor data/breaking_news/ directory
# 2. Detect new .txt files every 1 second
# 3. Read file content, extract title from first line
# 4. Immediately push to Pathway (0.5s autocommit)
# 5. Optionally delete file after ingestion

# DEMO TECHNIQUE ("Wizard of Oz"):
# - Presenter drops demo file during presentation
# - System ingests within 2 seconds
# - Proves real-time capability without relying on external RSS
# - Critical for hackathon demo!

# FILE FORMAT:
# Line 1: Title
# Line 2+: Content
```

**Key Methods**:
- `run()`: Continuously scans directory
- `self.next()`: Push file content to Pathway
- `self.commit()`: Force immediate commit (fast ingestion)

---

#### `backend/src/pipeline/pathway_pipeline.py` (Main Pipeline)
```python
# RESPONSIBILITIES:
# 1. Orchestrate entire Pathway dataflow graph
# 2. Merge RSS + FileWatcher sources
# 3. Apply transformations (sentiment analysis)
# 4. Build RAG components (embeddings, KNN index)
# 5. Create output sinks (headlines.jsonl, sentiment.jsonl)
# 6. Process RAG queries

# PATHWAY COMPUTATION GRAPH:
#
# [RSS Table] ──┐
#               ├→ [Combined Table] → [Enriched Table] → [Chunks Table]
# [File Table] ─┘                          │                    │
#                                           │                    │
#                                           ▼                    ▼
#                                    [Sentiment Sink]      [Headline Sink]
#                                    sentiment.jsonl       headlines.jsonl
#
# INCREMENTAL NATURE:
# - Pathway automatically propagates only deltas through graph
# - No manual re-indexing needed
# - Efficient for streaming data
```

**Key Methods**:
- `create_ingestion_sources()`: Merge RSS + FileWatcher
- `build_processing_pipeline()`: Add sentiment scores
- `build_rag_components()`: Simplified chunking (can be enhanced)
- `create_headline_sink()`: Output latest headlines to JSONL
- `create_sentiment_sink()`: Output sentiment data to JSONL
- `process_rag_query()`: Query processing (simplified in this version)
- `run()`: Start Pathway engine with `pw.run()`

**Important Note**: This uses `pw.Table.concat().promise_universes_are_disjoint()` to merge RSS and FileWatcher tables (they have different sources, so disjoint is safe).

---

#### `backend/src/pipeline/sentiment.py` (Sentiment Analysis)
```python
# RESPONSIBILITIES:
# 1. Analyze sentiment of each article using TextBlob
# 2. Return score from -1.0 (negative) to +1.0 (positive)
# 3. Maintain rolling window of sentiment scores
# 4. Calculate average sentiment over 10-minute window

# SENTIMENT SCORING:
# - Uses TextBlob.polarity (simple, fast, no ML training needed)
# - Scores:
#   -1.0 to -0.3: Negative
#   -0.3 to  0.3: Neutral
#    0.3 to  1.0: Positive

# ROLLING WINDOW:
# - SentimentAggregator class maintains deque
# - Removes entries older than window (default 10 min)
# - Calculates average sentiment
# - Tracks trend (improving/declining/stable)
```

**Key Functions**:
- `analyze_article_sentiment(title, summary, content)`: Returns sentiment dict
- `SentimentAggregator.add_article()`: Add to rolling window
- `SentimentAggregator.get_current_sentiment()`: Get average + trend

---

#### `backend/src/llm/embedder.py` (Gemini LLM Wrapper)
```python
# RESPONSIBILITIES:
# 1. Initialize Google Gemini API client
# 2. Generate text embeddings (768-dimensional vectors)
# 3. Generate text responses (for RAG answers)
# 4. Handle retries and rate limiting

# EMBEDDING MODEL:
# - models/embedding-001 (768 dimensions)
# - Used for vector similarity search in RAG

# GENERATION MODEL:
# - gemini-1.5-flash (fast, free tier)
# - Used for answering questions with retrieved context

# RATE LIMITING:
# - Free tier: 15 requests/minute
# - Implements exponential backoff on 429 errors
```

**Key Methods**:
- `embed_text(text)`: Returns 768-dim vector
- `generate(prompt)`: Returns LLM response
- Handles errors gracefully with retries

---

### Frontend Files

#### `frontend/src/App.tsx` (Main Component)
```typescript
// RESPONSIBILITIES:
// 1. Tab navigation (ticker vs analyst chat)
// 2. WebSocket connection management
// 3. State management for articles, sentiment, alerts, stats
// 4. Polling fallback if WebSocket fails

// STATE:
// - articles: Latest news (max 50)
// - sentimentData: Chart data points (max 30)
// - alerts: Keyword alerts (max 10)
// - stats: System statistics
// - wsConnected: WebSocket status indicator

// DATA FLOW:
// 1. Initial fetch via REST API
// 2. Connect WebSocket for real-time updates
// 3. Handle incoming messages by type (news/sentiment/alert/stats)
// 4. Fallback polling every 5 seconds if WS disconnects
```

**Key Hooks**:
- `useEffect()`: Initialize data + WebSocket
- `handleWSMessage()`: Route incoming WS messages to state updaters

---

#### `frontend/src/components/NewsTicker.tsx` (Ticker Component)
```typescript
// RESPONSIBILITIES:
// 1. Display scrolling headlines in ticker format
// 2. Color-code by sentiment (red/yellow/green)
// 3. Show source badge
// 4. Auto-scroll horizontally

// RENDERING:
// - Maps articles array to ticker items
// - Sentiment color: 
//   < 0.3: red (negative)
//   0.3-0.6: yellow (neutral)
//   > 0.6: green (positive)
```

---

#### `frontend/src/components/AnalystChat.tsx` (RAG Interface)
```typescript
// RESPONSIBILITIES:
// 1. Chat UI for asking questions
// 2. Send queries to POST /query endpoint
// 3. Display LLM responses
// 4. Show loading state during query

// FLOW:
// User types question → POST /query → Backend RAG pipeline → Display answer
```

---

#### `frontend/src/components/SentimentChart.tsx` (Chart Component)
```typescript
// RESPONSIBILITIES:
// 1. Line chart using Recharts library
// 2. X-axis: Time
// 3. Y-axis: Sentiment score (-1 to +1)
// 4. Updates in real-time as sentiment data arrives

// VISUALIZATION:
// - Green area: Positive sentiment
// - Red area: Negative sentiment
// - Yellow: Neutral
```

---

#### `frontend/src/components/AlertPanel.tsx` (Alerts)
```typescript
// RESPONSIBILITIES:
// 1. Display keyword alerts
// 2. Badge with keyword and count
// 3. Timestamp and description

// ALERT LOGIC (backend):
// - When keyword appears in ≥3 articles in window → trigger alert
```

---

#### `frontend/src/services/api.ts` (API Client)
```typescript
// RESPONSIBILITIES:
// 1. Axios HTTP client for REST endpoints
// 2. WebSocket client for real-time updates
// 3. Handle reconnection logic
// 4. Type-safe API calls

// ENDPOINTS USED:
// - GET /news/latest?limit=20
// - GET /stats
// - POST /query
// - WS /ws

// WEBSOCKET PROTOCOL:
// {
//   type: 'news' | 'sentiment' | 'alert' | 'stats',
//   data: {...}
// }
```

---

## 🚀 Execution Flow

### 1. **System Startup (Docker)**

```bash
cd deployment
docker-compose up --build
```

**What Happens**:

1. **Build Phase**:
   - Backend: Install Python deps, copy code
   - Frontend: npm install, build React app, setup nginx

2. **Run Phase**:
   - Backend container starts: `python src/main.py`
   - Frontend container starts: nginx serves static files

---

### 2. **Backend Initialization**

```
main.py:main()
  ↓
check_environment()  # Validate API key, create dirs
  ↓
print_startup_banner()  # ASCII art
  ↓
Start API server in background thread
  ↓
pipeline = LiveNewsAnalystPipeline()
  ↓
pipeline.run()  # Start Pathway engine
```

**Pathway Pipeline Execution**:

```
LiveNewsAnalystPipeline.run()
  ↓
create_ingestion_sources()  # RSS + FileWatcher
  ↓
build_processing_pipeline()  # Add sentiment
  ↓
build_rag_components()  # Embeddings (simplified)
  ↓
create_headline_sink()  # Write to headlines.jsonl
  ↓
create_sentiment_sink()  # Write to sentiment.jsonl
  ↓
pw.run()  # Pathway engine starts (blocking, runs forever)
```

**Parallel Threads**:
- **Main Thread**: Pathway engine (differential dataflow)
- **API Thread**: FastAPI server (uvicorn)
- **RSS Thread**: RSSConnector.run() (polling loop)
- **FileWatcher Thread**: FileWatcherConnector.run() (directory monitoring)

---

### 3. **Data Ingestion (RSS)**

```
RSSConnector.run() [runs forever]
  ↓
for each URL in url_list:
  ↓
  feedparser.parse(url)
  ↓
  for each entry in feed.entries:
    ↓
    if link not in seen_links:  # Deduplication
      ↓
      self.next(  # Push to Pathway
        title=...,
        summary=...,
        content=...,
        ...
      )
      ↓
      seen_links.add(link)
  ↓
wait 60 seconds
↓
repeat
```

**Output**: New articles flow into Pathway's `rss_table`

---

### 4. **Data Ingestion (FileWatcher)**

```
FileWatcherConnector.run() [runs forever]
  ↓
for each .txt file in data/breaking_news/:
  ↓
  if file not in processed_files:
    ↓
    read file content
    ↓
    self.next(  # Push to Pathway
      title=first_line,
      content=full_content,
      source="FileWatcher"
    )
    ↓
    self.commit()  # Immediate commit (fast!)
    ↓
    processed_files.add(file)
  ↓
wait 1 second
↓
repeat
```

**Output**: Dropped files flow into Pathway's `file_table` within 2 seconds

---

### 5. **Pathway Processing**

```
[RSS Table] + [File Table]
  ↓
Table.concat() with promise_universes_are_disjoint()
  ↓
[Combined Table]
  ↓
Apply sentiment analysis (pw.apply)
  ↓
[Enriched Table with sentiment_score]
  ↓
Split into:
  1. Headline Sink → headlines.jsonl
  2. Sentiment Sink → sentiment.jsonl
```

**Incremental Updates**:
- Pathway only recomputes affected rows (delta propagation)
- No batch re-processing
- Efficient for streaming data

---

### 6. **Frontend Loading**

```
User opens http://localhost:5173
  ↓
React App.tsx loads
  ↓
useEffect() runs:
  ↓
  fetchInitialData()  # REST API calls
  ↓
  APIService.connectWebSocket()  # WS connection
```

**Initial Data Fetch**:
```
GET /news/latest?limit=20  → articles state
GET /stats               → stats state
```

**WebSocket Connection**:
```
WS /ws
  ↓
Server broadcasts messages:
  {type: 'news', data: {...}}
  {type: 'sentiment', data: {...}}
  {type: 'alert', data: {...}}
  ↓
handleWSMessage() → update state → re-render UI
```

---

### 7. **RAG Query Flow**

```
User types question in AnalystChat
  ↓
Submit button clicked
  ↓
POST /query
  {
    query: "What's the latest on Bitcoin?",
    top_k: 5
  }
  ↓
Backend: pipeline.process_rag_query()
  ↓
1. Embed query using Gemini
2. Vector similarity search (KNN)
3. Retrieve top 5 relevant chunks
4. Build prompt with context
5. Generate answer using Gemini
  ↓
Response:
  {
    answer: "Bitcoin surged to $45k...",
    context: [{title: "...", summary: "..."}],
    latency_ms: 1234
  }
  ↓
Display in chat UI
```

---

## 🔑 Key Technologies Explained

### Pathway (Differential Dataflow)

**What is it?**
- Rust-based streaming engine (like Apache Flink but simpler)
- Incremental computation: only recomputes changed data
- Python API for defining dataflow graphs

**Why use it?**
- Built specifically for RAG use cases
- No batch jobs needed
- Automatically handles incremental indexing
- Perfect for "real-time" hackathon criterion

**Core Concepts**:
```python
# Create source
table = pw.io.python.read(connector, schema=NewsSchema)

# Transform
enriched = table.select(
    title=pw.this.title,
    sentiment=pw.apply(analyze_sentiment, pw.this.content)
)

# Sink
pw.io.jsonlines.write(enriched, "output.jsonl")

# Run engine
pw.run()  # Starts differential dataflow
```

---

### Google Gemini 1.5 Flash

**What is it?**
- Fast LLM from Google (free tier available)
- 1 million token context window
- multimodal (text, image, video)

**Why use it?**
- **Free tier**: 15 requests/minute (enough for hackathon)
- **Fast**: Sub-second responses
- **Large context**: Can fit many news articles
- **Embeddings**: Built-in 768-dim vectors

**Alternatives**:
- OpenAI GPT-4: Paid, expensive for hackathon
- Groq Llama: Fast but small context (8k tokens)
- Anthropic Claude: Paid

---

### TextBlob (Sentiment Analysis)

**What is it?**
- Simple Python library for NLP
- Built on top of NLTK
- Pre-trained models (no training needed)

**Why use it?**
- **Fast**: No GPU needed
- **Simple**: One-liner sentiment scoring
- **Lightweight**: No heavy ML dependencies
- **Good enough**: Accuracy sufficient for demo

**Alternative**:
- VADER: Better for social media
- Transformers: More accurate but requires GPU

---

### React + TypeScript

**Frontend Stack**:
- **Vite**: Fast build tool (replaces Create React App)
- **TypeScript**: Type safety, better DX
- **Recharts**: Chart library
- **Axios**: HTTP client
- **Lucide React**: Icon library

**Why React?**
- **Professional**: Judges expect production-grade UI
- **Real-time**: Easy WebSocket integration
- **Component-based**: Reusable, maintainable

**Alternative**:
- Streamlit: Too basic, common in hackathons (less impressive)
- Gradio: Python-only, limited customization

---

### Docker Compose

**Why Docker?**
1. **Pathway requires Linux** (Rust deps won't compile on Windows)
2. **Reproducible**: Same environment everywhere
3. **Easy deployment**: One command to start
4. **Professional**: Production deployment ready

**Services**:
- `backend`: Python + Pathway (port 8000)
- `frontend`: nginx serving React (port 5173)
- `news-analyst-network`: Bridge network for communication

---

## 🎯 Critical Hackathon Features

### 1. **FileWatcher (35% of score - Real-Time Capability)**

**Why critical?**
- RSS feeds take 60 seconds to poll
- FileWatcher ingests in <2 seconds
- **Proves real-time without waiting**

**Demo Strategy**:
1. Show baseline: "No news about X"
2. Drop file: `demo/sample_articles/market_crash.txt`
3. Show update: "Breaking: Market crashes..."
4. **Timestamp proves <2s latency**

### 2. **Sentiment Analysis (20% of score - Innovation)**

**Why innovative?**
- Most RAG projects don't have this
- Shows domain expertise (finance/news)
- Real-time visualization

### 3. **Professional UI (30% of score - Technical Implementation)**

**Why impressive?**
- React + TypeScript (not Streamlit)
- WebSocket real-time (not polling)
- Clean design, responsive

### 4. **Custom RSS Connector (20% of score - Innovation)**

**Why better than NewsAPI.org?**
- NewsAPI free tier has 24-hour delay (disqualifies for "real-time")
- RSS is instant, free, unlimited
- Shows technical skill (custom Pathway connector)

---

## 📝 Summary

**In 3 Sentences**:

1. **Backend**: Pathway runs 4 parallel threads (RSS polling, FileWatcher, API server, differential dataflow engine) that continuously ingest news, analyze sentiment, and update vector index incrementally.

2. **Data Flow**: RSS/Files → Pathway table → Sentiment analysis → Output sinks (JSONL) → FastAPI → WebSocket → React frontend.

3. **Key Innovation**: No batch re-indexing needed—Pathway's differential engine automatically propagates only deltas, enabling true real-time RAG with <2 second latency.

---

**Questions? Check specific files in the sections above!** 📚
