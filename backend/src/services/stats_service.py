"""
Stats and Sentiment Service

This module provides:
1. Real-time calculation of system statistics
2. Sentiment data aggregation and broadcasting
3. Query latency tracking
"""

import os
import json
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Set
from dataclasses import dataclass, field
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LatencyTracker:
    """Track query latencies with a rolling window."""
    window_size: int = 100
    latencies: deque = field(default_factory=lambda: deque(maxlen=100))
    
    def add(self, latency_ms: float):
        """Add a latency measurement."""
        self.latencies.append(latency_ms)
    
    def get_average(self) -> float:
        """Get average latency."""
        if not self.latencies:
            return 0.0
        return sum(self.latencies) / len(self.latencies)


class StatsService:
    """
    Service for calculating and broadcasting system statistics.
    
    Features:
    - Real-time stats calculation from data files
    - Sentiment aggregation and broadcasting
    - Query latency tracking
    - Background polling with configurable interval
    """
    
    def __init__(
        self,
        headlines_file: str = "data/output/headlines.jsonl",
        sentiment_file: str = "data/output/sentiment.jsonl",
        poll_interval: float = 5.0,  # seconds
        sentiment_window_minutes: int = 30
    ):
        """
        Initialize Stats Service.
        
        Args:
            headlines_file: Path to headlines JSONL file
            sentiment_file: Path to sentiment JSONL file
            poll_interval: How often to recalculate stats (seconds)
            sentiment_window_minutes: Window for sentiment aggregation
        """
        self.headlines_file = headlines_file
        self.sentiment_file = sentiment_file
        self.poll_interval = poll_interval
        self.sentiment_window_minutes = sentiment_window_minutes
        
        # Stats storage
        self._stats: Dict = {
            "total_articles": 0,
            "articles_last_hour": 0,
            "active_sources": 0,
            "avg_latency_ms": 0.0,
            "last_update": int(time.time())
        }
        
        # Sentiment storage
        self._current_sentiment: float = 0.0
        self._sentiment_history: List[Dict] = []
        self._last_sentiment_count: int = 0  # Track last read position
        
        # Latency tracking
        self._latency_tracker = LatencyTracker()
        
        # Callbacks for broadcasting
        self._stats_callbacks: List[Callable] = []
        self._sentiment_callbacks: List[Callable] = []
        
        # Background thread
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
        logger.info(f"StatsService initialized (poll interval: {poll_interval}s)")
    
    def register_stats_callback(self, callback: Callable[[Dict], None]):
        """Register a callback for stats updates."""
        self._stats_callbacks.append(callback)
    
    def register_sentiment_callback(self, callback: Callable[[Dict], None]):
        """Register a callback for sentiment updates."""
        self._sentiment_callbacks.append(callback)
    
    def record_query_latency(self, latency_ms: float):
        """Record a query latency measurement."""
        self._latency_tracker.add(latency_ms)
    
    def get_stats(self) -> Dict:
        """Get current system statistics."""
        return self._stats.copy()
    
    def get_current_sentiment(self) -> Dict:
        """Get current aggregated sentiment."""
        return {
            "sentiment_score": self._current_sentiment,
            "timestamp": int(time.time()),
            "sample_count": len(self._sentiment_history)
        }
    
    def get_sentiment_history(self, limit: int = 30) -> List[Dict]:
        """Get recent sentiment history."""
        return self._sentiment_history[-limit:]
    
    def _read_jsonl_file(self, filepath: str) -> List[Dict]:
        """Read all entries from a JSONL file."""
        entries = []
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                entries.append(json.loads(line))
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"Error reading {filepath}: {e}")
        return entries
    
    def _calculate_stats(self):
        """Calculate system statistics from data files."""
        try:
            articles = self._read_jsonl_file(self.headlines_file)
            
            # Total articles
            total_articles = len(articles)
            
            # Articles in last hour
            one_hour_ago = datetime.now() - timedelta(hours=1)
            articles_last_hour = 0
            active_sources: Set[str] = set()
            
            for article in articles:
                # Check timestamp
                published = article.get('published', '')
                source = article.get('source', '')
                
                if source:
                    active_sources.add(source)
                
                # Parse published date
                try:
                    if 'T' in published:
                        # ISO format: 2026-01-17T17:22:39.809703
                        pub_dt = datetime.fromisoformat(published.replace('Z', '+00:00').split('+')[0])
                        if pub_dt > one_hour_ago:
                            articles_last_hour += 1
                except (ValueError, TypeError):
                    pass
            
            # Average latency
            avg_latency = self._latency_tracker.get_average()
            
            # Update stats
            self._stats = {
                "total_articles": total_articles,
                "articles_last_hour": articles_last_hour,
                "active_sources": len(active_sources),
                "avg_latency_ms": round(avg_latency, 1),
                "last_update": int(time.time())
            }
            
            # Notify callbacks
            for callback in self._stats_callbacks:
                try:
                    callback(self._stats)
                except Exception as e:
                    logger.error(f"Stats callback error: {e}")
            
        except Exception as e:
            logger.error(f"Error calculating stats: {e}")
    
    def _calculate_sentiment(self):
        """Calculate aggregated sentiment from sentiment file."""
        try:
            sentiments = self._read_jsonl_file(self.sentiment_file)
            
            if not sentiments:
                return
            
            # Check if we have new data
            if len(sentiments) <= self._last_sentiment_count:
                return
            
            # Get new sentiment entries
            new_entries = sentiments[self._last_sentiment_count:]
            self._last_sentiment_count = len(sentiments)
            
            # Filter to sentiment window
            window_start = datetime.now() - timedelta(minutes=self.sentiment_window_minutes)
            recent_sentiments: List[float] = []
            
            for entry in sentiments:
                timestamp = entry.get('timestamp', '')
                score = entry.get('sentiment_score', 0)
                
                try:
                    if 'T' in str(timestamp):
                        ts_dt = datetime.fromisoformat(str(timestamp).replace('Z', '+00:00').split('+')[0])
                        if ts_dt > window_start:
                            recent_sentiments.append(score)
                except (ValueError, TypeError):
                    recent_sentiments.append(score)
            
            # Calculate aggregate sentiment
            if recent_sentiments:
                self._current_sentiment = sum(recent_sentiments) / len(recent_sentiments)
            
            # Update history with new entries
            for entry in new_entries:
                sentiment_point = {
                    "timestamp": entry.get('timestamp', ''),
                    "sentiment_score": entry.get('sentiment_score', 0),
                    "title": entry.get('title', ''),
                    "source": entry.get('source', '')
                }
                self._sentiment_history.append(sentiment_point)
                
                # Notify callbacks for each new sentiment
                for callback in self._sentiment_callbacks:
                    try:
                        callback(sentiment_point)
                    except Exception as e:
                        logger.error(f"Sentiment callback error: {e}")
            
            # Keep history bounded
            if len(self._sentiment_history) > 100:
                self._sentiment_history = self._sentiment_history[-100:]
            
        except Exception as e:
            logger.error(f"Error calculating sentiment: {e}")
    
    def _poll_loop(self):
        """Background polling loop."""
        logger.info("Stats service polling started")
        
        while self._running:
            try:
                self._calculate_stats()
                self._calculate_sentiment()
            except Exception as e:
                logger.error(f"Poll loop error: {e}")
            
            # Sleep in small intervals to allow quick shutdown
            for _ in range(int(self.poll_interval * 10)):
                if not self._running:
                    break
                time.sleep(0.1)
        
        logger.info("Stats service polling stopped")
    
    def start(self):
        """Start the background polling service."""
        if self._running:
            logger.warning("Stats service already running")
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
        logger.info("📊 Stats service started")
    
    def stop(self):
        """Stop the background polling service."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
            self._thread = None
        logger.info("📊 Stats service stopped")


# Global instance
_stats_service: Optional[StatsService] = None


def get_stats_service() -> Optional[StatsService]:
    """Get the global stats service instance."""
    return _stats_service


def init_stats_service(
    headlines_file: str = "data/output/headlines.jsonl",
    sentiment_file: str = "data/output/sentiment.jsonl",
    poll_interval: float = 5.0
) -> StatsService:
    """
    Initialize the global stats service.
    
    Args:
        headlines_file: Path to headlines JSONL file
        sentiment_file: Path to sentiment JSONL file
        poll_interval: Polling interval in seconds
        
    Returns:
        Initialized StatsService
    """
    global _stats_service
    
    _stats_service = StatsService(
        headlines_file=headlines_file,
        sentiment_file=sentiment_file,
        poll_interval=poll_interval
    )
    
    return _stats_service
