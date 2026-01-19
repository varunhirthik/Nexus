"""
FastAPI server for REST and WebSocket endpoints.

This module provides HT# FastAPI app
app = FastAPI(
    title="Live News Analyst API",
    description="Real-time news analysis powered by Pathway and Gemini",
    version="1.0.0"
)

# Import settings for CORS configuration
from config import settings as app_settings

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware - configure allowed origins from settings for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.allowed_origins_list,
    allow_credentials=False,  # Set to False when using specific origins for security
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)aces for the Pathway pipeline,
enabling the React frontend to query and receive real-time updates.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)


# Pydantic models for API
class QueryRequest(BaseModel):
    query: str
    user: str = "anonymous"
    top_k: int = 5


class QueryResponse(BaseModel):
    query: str
    answer: str
    context: List[Dict]
    latency_ms: float
    timestamp: int


class NewsArticle(BaseModel):
    id: str
    title: str
    summary: str
    content: str
    link: str
    published: str
    source: str
    timestamp: int


class SystemStats(BaseModel):
    total_articles: int
    articles_last_hour: int
    active_sources: int
    avg_latency_ms: float
    last_update: int


# Global state (to be replaced with Pathway tables)
class GlobalState:
    """Shared state between Pathway and FastAPI."""
    def __init__(self):
        self.articles: List[Dict] = []
        self.sentiment_data: List[Dict] = []
        self.alerts: List[Dict] = []
        self.stats: Dict = {
            "total_articles": 0,
            "articles_last_hour": 0,
            "active_sources": 0,
            "avg_latency_ms": 0,
            "last_update": int(datetime.now().timestamp())
        }
        self.connected_clients: Set[WebSocket] = set()

state = GlobalState()


# FastAPI app
app = FastAPI(
    title="Live News Analyst API",
    description="Real-time news analysis powered by Pathway and Gemini",
    version="1.0.0"
)

# Import settings for CORS configuration
from config import settings as app_settings

# CORS middleware - configure allowed origins from settings for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.allowed_origins_list,
    allow_credentials=False,  # Set to False when using specific origins for security
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Global exception handler to ensure CORS headers are always present
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "error": "Internal server error"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )


# Startup event to initialize services
@app.on_event("startup")
async def startup_event():
    """Initialize RAG service and other components on startup."""
    import os
    logger.info("="*60)
    logger.info("🚀 Starting Nexus API Server...")
    logger.info("="*60)
    
    # Get API key from environment (supports multiple names)
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    
    if api_key:
        logger.info("✓ API Key found, initializing RAG service...")
        try:
            from llm.rag_query import init_rag_service
            init_rag_service(
                api_key=api_key,
                model="models/gemini-2.5-flash",
                temperature=0.7
            )
            logger.info("✓ RAG Query Service initialized successfully!")
        except Exception as e:
            logger.error(f"✗ Failed to initialize RAG service: {e}")
    else:
        logger.warning("✗ No API key found! Set GOOGLE_API_KEY or GEMINI_API_KEY")
    
    # Initialize news scheduler if keys are available
    newsapi_key = os.environ.get("NEWS_API_KEY") or os.environ.get("NEWSAPI_KEY")
    gnews_key = os.environ.get("GNEWS_API_KEY") or os.environ.get("GNEWS_KEY")
    
    if newsapi_key or gnews_key:
        logger.info("✓ News API keys found, starting news scheduler...")
        try:
            from connectors.news_scheduler import init_scheduler
            scheduler = init_scheduler(
                newsapi_key=newsapi_key or "",
                gnews_key=gnews_key or "",
                poll_interval=600,  # 10 minutes
                output_dir="../data/breaking_news",
                keywords=["Tesla", "Bitcoin", "AI", "technology", "stock market"]
            )
            scheduler.start()
            logger.info("✓ News scheduler started!")
        except Exception as e:
            logger.error(f"✗ Failed to start news scheduler: {e}")
    else:
        logger.warning("✗ No News API keys found, news fetching disabled")
    
    # Start stats service
    try:
        from services.stats_service import start_stats_service
        start_stats_service(state, data_dir="../data/breaking_news")
        logger.info("✓ Stats service started!")
    except Exception as e:
        logger.error(f"✗ Failed to start stats service: {e}")
    
    # Initialize and start keyword alert service
    try:
        from services.alert_service import init_alert_service
        from config import settings as cfg
        
        alert_service = init_alert_service(
            keywords=cfg.alert_keyword_list,
            threshold=cfg.alert_threshold,
            window_minutes=10  # 10 minute window
        )
        logger.info(f"✓ Alert service initialized with {len(cfg.alert_keyword_list)} keywords!")
        
        # Start background alert monitoring
        asyncio.create_task(monitor_keyword_alerts())
        logger.info("✓ Keyword alert monitoring started!")
    except Exception as e:
        logger.error(f"✗ Failed to start alert service: {e}")
    
    logger.info("="*60)
    logger.info("🎯 Nexus API Server ready!")
    logger.info("="*60)


async def monitor_keyword_alerts():
    """Background task to monitor articles for keyword alerts using AlertService."""
    from services.alert_service import get_alert_service
    
    last_article_count = 0
    
    while True:
        try:
            await asyncio.sleep(15)  # Check every 15 seconds
            
            alert_service = get_alert_service()
            if not alert_service:
                continue
            
            # Process new articles
            current_article_count = len(state.articles)
            
            if current_article_count > last_article_count:
                # Get new articles (those we haven't processed yet)
                new_articles = state.articles[last_article_count:current_article_count]
                last_article_count = current_article_count
                
                for article in new_articles:
                    # Process article and get any new alerts
                    new_alerts = alert_service.process_article(article)
                    
                    # Broadcast new alerts via WebSocket
                    for alert in new_alerts:
                        alert_dict = alert.to_dict()
                        state.alerts.append(alert_dict)
                        
                        await manager.broadcast({
                            "type": "alert",
                            "data": alert_dict
                        })
                        
                        logger.info(f"🚨 Broadcast alert: {alert.keyword} ({alert.count} mentions)")
            
        except Exception as e:
            logger.error(f"Error in keyword monitoring: {e}")
            await asyncio.sleep(60)  # Wait longer on error


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: Dict):
        """Broadcast message to all connected clients."""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()


# REST Endpoints
@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "Live News Analyst",
        "version": "1.0.0",
        "timestamp": int(datetime.now().timestamp())
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker."""
    return {
        "status": "healthy",
        "service": "Live News Analyst Backend",
        "timestamp": int(datetime.now().timestamp())
    }


@app.get("/news/latest")
@limiter.limit(f"{app_settings.rate_limit_news_per_minute}/minute" if app_settings.rate_limit_enabled else "1000/minute")
async def get_latest_news(request: Request, limit: int = 20):
    """Get latest news articles from Pathway output files."""
    import os
    import json
    from pathlib import Path
    from datetime import datetime as _dt
    
    headlines_file = "../data/output/headlines.jsonl"
    articles = []

    def _read_breaking_texts(dir_path: str):
        """Read individual .txt article files from breaking_news and return list of article dicts."""
        items = []
        try:
            p = Path(dir_path)
            if not p.exists():
                return items

            for fp in sorted(p.glob("*.txt"), reverse=True):
                try:
                    text = fp.read_text(encoding='utf-8')
                except Exception:
                    continue

                # Basic parsing: look for Title:, Source:, Published: headers
                title = ""
                source = ""
                published = ""
                content = text

                for line in text.splitlines():
                    if line.startswith("Title:"):
                        title = line.split("Title:", 1)[1].strip()
                    elif line.startswith("Source:"):
                        source = line.split("Source:", 1)[1].strip()
                    elif line.startswith("Published:"):
                        published = line.split("Published:", 1)[1].strip()

                # Fallbacks
                if not title:
                    # take first non-empty line as title
                    for ln in text.splitlines():
                        if ln.strip():
                            title = ln.strip()
                            break

                # Build article dict matching pipeline output where possible
                items.append({
                    "id": fp.stem,
                    "title": title,
                    "summary": title,
                    "content": content,
                    "link": "",
                    "published": published or str(int(_dt.now().timestamp())),
                    "source": source or "news_source",
                    "timestamp": int(_dt.now().timestamp())
                })

        except Exception as e:
            logger.error(f"Error reading breaking_news files: {e}")

        return items

    try:
        # 1) Try reading Pathway-generated headlines JSONL
        if os.path.exists(headlines_file):
            with open(headlines_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            article = json.loads(line)
                            articles.append(article)
                        except json.JSONDecodeError:
                            continue

        # 2) If no articles found, fall back to reading breaking_news text files
        if not articles:
            articles = _read_breaking_texts("../data/breaking_news")

        # Normalize and sort by published/timestamp
        def _ts_key(a):
            # prefer timestamp int, then published string
            try:
                return int(a.get('timestamp') or 0)
            except Exception:
                try:
                    return int(float(a.get('published', 0)))
                except Exception:
                    return 0

        articles.sort(key=_ts_key, reverse=True)
        articles = articles[:limit]

        # Update state for other endpoints
        state.articles = articles
        state.stats["total_articles"] = len(articles)
        state.stats["last_update"] = int(_dt.now().timestamp())
    except Exception as e:
        logger.error(f"Error reading headlines: {e}")

    return articles


@app.get("/stats")
async def get_stats():
    """Get system statistics from stats service."""
    default_stats = {
        "total_articles": len(state.articles),
        "articles_last_hour": 0,
        "active_sources": len(set(a.get("source", "unknown") for a in state.articles)),
        "avg_latency_ms": 0,
        "last_update": int(datetime.now().timestamp())
    }
    try:
        from services.stats_service import get_stats_service
        stats_service = get_stats_service()
        
        if stats_service:
            return stats_service.get_stats()
        else:
            return default_stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return default_stats


@app.get("/sentiment")
async def get_sentiment():
    """Get current sentiment data."""
    default_sentiment = {
        "current": {"sentiment_score": 0.0, "timestamp": int(datetime.now().timestamp()), "sample_count": 0},
        "history": []
    }
    try:
        from services.stats_service import get_stats_service
        stats_service = get_stats_service()
        
        if stats_service:
            return {
                "current": stats_service.get_current_sentiment(),
                "history": stats_service.get_sentiment_history(30)
            }
        else:
            return default_sentiment
    except Exception as e:
        logger.error(f"Error getting sentiment: {e}")
        return default_sentiment


@app.get("/alerts")
async def get_alerts():
    """Get current keyword alerts from AlertService."""
    try:
        from services.alert_service import get_alert_service
        from config import settings as cfg
        
        alert_service = get_alert_service()
        
        if alert_service:
            # Get alerts from service
            alerts = alert_service.get_active_alerts(limit=20)
            keywords = cfg.alert_keyword_list
        else:
            # Fallback to state-based alerts
            alerts = state.alerts[-20:] if state.alerts else []
            keywords = cfg.alert_keyword_list
        
        return {
            "alerts": alerts,
            "keywords": keywords,
            "last_update": int(datetime.now().timestamp())
        }
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return {
            "alerts": [],
            "keywords": [],
            "last_update": int(datetime.now().timestamp()),
            "error": str(e)
        }


@app.get("/news/status")
async def get_news_api_status():
    """Get News API scheduler status."""
    try:
        from connectors.news_scheduler import get_scheduler
        scheduler = get_scheduler()
        
        if scheduler:
            return scheduler.get_status()
        else:
            return {
                "running": False,
                "message": "News scheduler not initialized",
                "reason": "API keys may not be configured"
            }
    except Exception as e:
        logger.error(f"Error getting news status: {e}")
        return {
            "running": False,
            "error": str(e)
        }


@app.post("/news/fetch")
@limiter.limit("1/minute")  # Very restrictive - manual trigger only
async def trigger_news_fetch(request: Request):
    """Manually trigger a news fetch from APIs."""
    try:
        from connectors.news_scheduler import get_scheduler
        scheduler = get_scheduler()
        
        if scheduler and scheduler.is_running:
            stats = scheduler.fetch_now()
            return {
                "success": True,
                "message": "Fetch triggered successfully",
                "stats": stats
            }
        else:
            return {
                "success": False,
                "message": "News scheduler is not running",
                "hint": "Ensure NEWSAPI_KEY or GNEWS_KEY is configured in .env"
            }
    except Exception as e:
        logger.error(f"Error triggering fetch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
@limiter.limit(f"{app_settings.rate_limit_query_per_minute}/minute" if app_settings.rate_limit_enabled else "1000/minute")
async def query_analyst(request: Request, query_request: QueryRequest):
    """
    Query the RAG system with AI-powered news analysis.
    
    This endpoint:
    1. Searches for relevant articles
    2. Builds context for Gemini
    3. Generates conversational AI response
    4. Falls back to general knowledge if no articles match
    """
    start_time = datetime.now()
    
    try:
        from llm.rag_query import get_rag_service
        
        rag_service = get_rag_service()
        
        if not rag_service:
            # RAG service not initialized - return helpful message
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            return QueryResponse(
                query=query_request.query,
                answer="I'm still warming up! The AI service is initializing. Please try again in a few seconds.",
                context=[],
                latency_ms=latency_ms,
                timestamp=int(datetime.now().timestamp())
            )
        
        # Get articles from state (populated by /news/latest)
        # Also try to load fresh articles if state is empty
        articles = state.articles
        
        if not articles:
            # Try to load from headlines file
            import os
            import json as json_module
            headlines_file = "../data/output/headlines.jsonl"
            if os.path.exists(headlines_file):
                with open(headlines_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                article = json_module.loads(line)
                                articles.append(article)
                            except:
                                continue
                state.articles = articles
        
        # Query the RAG service
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: rag_service.query(query_request.query, articles)
        )
        
        # Format context for response
        context = result.get("context", [])
        
        latency_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        # Record latency for stats
        try:
            from services.stats_service import get_stats_service
            stats_service = get_stats_service()
            if stats_service:
                stats_service.record_query_latency(latency_ms)
        except Exception:
            pass
        
        return QueryResponse(
            query=query_request.query,
            answer=result["answer"],
            context=context,
            latency_ms=latency_ms,
            timestamp=int(datetime.now().timestamp())
        )
    
    except Exception as e:
        logger.error(f"Query error: {e}")
        # Return a user-friendly error
        latency_ms = (datetime.now() - start_time).total_seconds() * 1000
        return QueryResponse(
            query=query_request.query,
            answer=f"I encountered an issue while analyzing that. Please try rephrasing your question or try again in a moment.",
            context=[],
            latency_ms=latency_ms,
            timestamp=int(datetime.now().timestamp())
        )


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates.
    
    Clients receive:
    - type: 'news' | 'sentiment' | 'alert' | 'stats'
    - data: corresponding payload
    """
    await manager.connect(websocket)
    
    try:
        # Send initial stats from stats service
        try:
            from services.stats_service import get_stats_service
            stats_service = get_stats_service()
            if stats_service:
                initial_stats = stats_service.get_stats()
                await websocket.send_json({
                    "type": "stats",
                    "data": initial_stats
                })
                
                # Send recent sentiment history
                sentiment_history = stats_service.get_sentiment_history(10)
                for sentiment in sentiment_history:
                    await websocket.send_json({
                        "type": "sentiment",
                        "data": sentiment
                    })
            else:
                await websocket.send_json({
                    "type": "stats",
                    "data": state.stats
                })
        except Exception as e:
            logger.error(f"Error sending initial WS data: {e}")
            await websocket.send_json({
                "type": "stats",
                "data": state.stats
            })
        
        # Keep connection alive and send periodic updates
        while True:
            try:
                # Listen for client messages with timeout
                data = await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
                logger.debug(f"Received from client: {data}")
            except asyncio.TimeoutError:
                # Send periodic stats update
                try:
                    from services.stats_service import get_stats_service
                    stats_service = get_stats_service()
                    if stats_service:
                        await websocket.send_json({
                            "type": "stats",
                            "data": stats_service.get_stats()
                        })
                except Exception:
                    pass
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# Helper function to update state from Pathway
async def broadcast_news_update(article: Dict):
    """Broadcast new article to all connected clients."""
    await manager.broadcast({
        "type": "news",
        "data": article
    })


async def broadcast_sentiment_update(sentiment: Dict):
    """Broadcast sentiment update."""
    await manager.broadcast({
        "type": "sentiment",
        "data": sentiment
    })


async def broadcast_alert(alert: Dict):
    """Broadcast alert to all clients."""
    await manager.broadcast({
        "type": "alert",
        "data": alert
    })


async def broadcast_stats_update(stats: Dict):
    """Broadcast stats update."""
    await manager.broadcast({
        "type": "stats",
        "data": stats
    })


def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the FastAPI server."""
    logger.info(f"Starting API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    start_server()
