"""
FastAPI server for REST and WebSocket endpoints.

This module provides HTTP/WebSocket interfaces for the Pathway pipeline,
enabling the React frontend to query and receive real-time updates.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

logger = logging.getLogger(__name__)


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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
async def get_latest_news(limit: int = 20):
    """Get latest news articles from Pathway output files."""
    import os
    import json
    
    headlines_file = "data/output/headlines.jsonl"
    articles = []
    
    try:
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
            
            # Sort by timestamp (most recent first) and limit
            articles.sort(key=lambda x: x.get('published', ''), reverse=True)
            articles = articles[:limit]
            
            # Update state for other endpoints
            state.articles = articles
            state.stats["total_articles"] = len(articles)
            state.stats["last_update"] = int(datetime.now().timestamp())
    except Exception as e:
        logger.error(f"Error reading headlines: {e}")
    
    return articles


@app.get("/stats")
async def get_stats():
    """Get system statistics from stats service."""
    try:
        from services.stats_service import get_stats_service
        stats_service = get_stats_service()
        
        if stats_service:
            return stats_service.get_stats()
        else:
            # Fallback to basic stats
            return state.stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return state.stats


@app.get("/sentiment")
async def get_sentiment():
    """Get current sentiment data."""
    try:
        from services.stats_service import get_stats_service
        stats_service = get_stats_service()
        
        if stats_service:
            return {
                "current": stats_service.get_current_sentiment(),
                "history": stats_service.get_sentiment_history(30)
            }
        else:
            return {
                "current": {"sentiment_score": 0, "timestamp": 0, "sample_count": 0},
                "history": []
            }
    except Exception as e:
        logger.error(f"Error getting sentiment: {e}")
        return {"current": {"sentiment_score": 0}, "history": []}


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
async def trigger_news_fetch():
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
async def query_analyst(request: QueryRequest):
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
                query=request.query,
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
            headlines_file = "data/output/headlines.jsonl"
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
            lambda: rag_service.query(request.query, articles)
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
            query=request.query,
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
            query=request.query,
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
