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
        data_dir: str = "data/breaking_news",
        poll_interval: float = 5.0,  # seconds
        sentiment_window_minutes: int = 30
    ):
        """
        Initialize Stats Service.
        
        Args:
            headlines_file: Path to headlines JSONL file
            sentiment_file: Path to sentiment JSONL file
            data_dir: Path to breaking news text files directory
            poll_interval: How often to recalculate stats (seconds)
            sentiment_window_minutes: Window for sentiment aggregation
        """
        self.headlines_file = headlines_file
        self.sentiment_file = sentiment_file
        self.data_dir = data_dir
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
    
    def _read_text_files(self, directory: str) -> List[Dict]:
        """Read all text files from a directory and extract article info."""
        articles = []
        try:
            if os.path.exists(directory) and os.path.isdir(directory):
                for filename in os.listdir(directory):
                    if filename.endswith('.txt'):
                        filepath = os.path.join(directory, filename)
                        try:
                            # Extract timestamp from filename (format: hash_timestamp.txt)
                            parts = filename.replace('.txt', '').split('_')
                            file_timestamp = int(parts[-1]) if len(parts) > 1 else 0
                            
                            with open(filepath, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Parse the text file format
                            lines = content.strip().split('\n')
                            article = {
                                'title': '',
                                'source': '',
                                'timestamp': file_timestamp,
                                'content': content
                            }
                            
                            for line in lines:
                                if line.startswith('Title:'):
                                    article['title'] = line.replace('Title:', '').strip()
                                elif line.startswith('Source:'):
                                    article['source'] = line.replace('Source:', '').strip()
                                elif line.startswith('Published:'):
                                    article['published'] = line.replace('Published:', '').strip()
                            
                            articles.append(article)
                        except Exception as e:
                            logger.debug(f"Error reading {filename}: {e}")
                            continue
        except Exception as e:
            logger.error(f"Error reading directory {directory}: {e}")
        return articles
    
    def _calculate_stats(self):
        """Calculate system statistics from data files."""
        try:
            # Read from both JSONL files and text files directory
            articles = self._read_jsonl_file(self.headlines_file)
            text_articles = self._read_text_files(self.data_dir)
            
            # Combine both sources
            all_articles = articles + text_articles
            
            # Total articles
            total_articles = len(all_articles)
            
            # Articles in last hour
            one_hour_ago = datetime.now() - timedelta(hours=1)
            one_hour_ago_ts = int(one_hour_ago.timestamp())
            articles_last_hour = 0
            active_sources: Set[str] = set()
            
            for article in all_articles:
                # Check timestamp
                published = article.get('published', '')
                source = article.get('source', '')
                timestamp = article.get('timestamp', 0)
                
                if source:
                    active_sources.add(source)
                
                # Check if article is from last hour
                is_recent = False
                
                # Check by timestamp field
                if timestamp and timestamp > one_hour_ago_ts:
                    is_recent = True
                
                # Check by published date string
                if not is_recent and published:
                    try:
                        if 'T' in str(published):
                            # ISO format: 2026-01-17T17:22:39.809703
                            pub_dt = datetime.fromisoformat(str(published).replace('Z', '+00:00').split('+')[0])
                            if pub_dt > one_hour_ago:
                                is_recent = True
                    except (ValueError, TypeError):
                        pass
                
                if is_recent:
                    articles_last_hour += 1
            
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
        """Calculate aggregated sentiment from sentiment file and text files."""
        try:
            from textblob import TextBlob
        except ImportError:
            logger.warning("TextBlob not installed, sentiment analysis disabled")
            return
            
        try:
            # Read from sentiment JSONL file
            sentiments = self._read_jsonl_file(self.sentiment_file)
            
            # Also analyze sentiment from text files
            text_articles = self._read_text_files(self.data_dir)
            
            # Analyze sentiment for text articles
            for article in text_articles:
                content = article.get('content', '') or article.get('title', '')
                if content:
                    try:
                        blob = TextBlob(content[:500])  # Limit to first 500 chars
                        score = blob.sentiment.polarity  # -1 to 1
                        
                        sentiments.append({
                            'timestamp': datetime.fromtimestamp(article.get('timestamp', time.time())).isoformat(),
                            'sentiment_score': score,
                            'title': article.get('title', ''),
                            'source': article.get('source', '')
                        })
                    except Exception:
                        pass
            
            if not sentiments:
                return
            
            # Sort by timestamp
            sentiments.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Update sentiment history with latest entries
            self._sentiment_history = []
            for entry in sentiments[-50:]:  # Keep last 50
                sentiment_point = {
                    "timestamp": entry.get('timestamp', ''),
                    "sentiment_score": entry.get('sentiment_score', 0),
                    "title": entry.get('title', ''),
                    "source": entry.get('source', '')
                }
                self._sentiment_history.append(sentiment_point)
            
            # Calculate aggregate sentiment
            if self._sentiment_history:
                scores = [s.get('sentiment_score', 0) for s in self._sentiment_history]
                self._current_sentiment = sum(scores) / len(scores)
            
            # Notify callbacks
            for callback in self._sentiment_callbacks:
                try:
                    callback({
                        'current': self._current_sentiment,
                        'history': self._sentiment_history
                    })
                except Exception as e:
                    logger.error(f"Sentiment callback error: {e}")
            
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
    data_dir: str = "data/breaking_news",
    poll_interval: float = 5.0
) -> StatsService:
    """
    Initialize the global stats service.
    
    Args:
        headlines_file: Path to headlines JSONL file
        sentiment_file: Path to sentiment JSONL file
        data_dir: Path to breaking news text files directory
        poll_interval: Polling interval in seconds
        
    Returns:
        Initialized StatsService
    """
    global _stats_service
    
    _stats_service = StatsService(
        headlines_file=headlines_file,
        sentiment_file=sentiment_file,
        data_dir=data_dir,
        poll_interval=poll_interval
    )
    
    return _stats_service


def start_stats_service(global_state, data_dir: str = "data/breaking_news") -> StatsService:
    """
    Initialize and start the stats service, updating global state.
    
    Args:
        global_state: The global state object to update with stats
        data_dir: Directory containing news text files
        
    Returns:
        Started StatsService
    """
    global _stats_service
    
    _stats_service = StatsService(
        data_dir=data_dir,
        poll_interval=5.0
    )
    
    # Register callback to update global state
    def update_global_state(stats: Dict):
        global_state.stats.update(stats)
    
    _stats_service.register_stats_callback(update_global_state)
    _stats_service.start()
    
    return _stats_service
