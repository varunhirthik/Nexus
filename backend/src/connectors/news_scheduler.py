"""
News Scheduler - Periodically fetches news from APIs

Runs as a background thread, polling news APIs at configured intervals
and writing new articles to the FileWatcher directory.
"""

import threading
import time
import logging
from typing import Optional, Callable
from datetime import datetime

from .news_api_connector import NewsAPIConnector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsScheduler:
    """
    Background scheduler for fetching news at regular intervals.
    
    Features:
    - Configurable poll interval
    - Thread-safe operation
    - Graceful shutdown
    - Status monitoring
    """
    
    def __init__(
        self,
        connector: NewsAPIConnector,
        poll_interval: int = 600,  # 10 minutes default
        on_fetch_complete: Optional[Callable] = None
    ):
        """
        Initialize news scheduler.
        
        Args:
            connector: NewsAPIConnector instance
            poll_interval: Seconds between fetches (default 600 = 10 min)
            on_fetch_complete: Optional callback after each fetch
        """
        self.connector = connector
        self.poll_interval = poll_interval
        self.on_fetch_complete = on_fetch_complete
        
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_fetch: Optional[datetime] = None
        self._last_stats: dict = {}
        self._fetch_count = 0
        
        logger.info(f"NewsScheduler initialized with {poll_interval}s interval")
    
    def _run_loop(self):
        """Main scheduler loop running in background thread."""
        logger.info("📡 News scheduler started")
        
        # Initial fetch immediately
        self._do_fetch()
        
        while self._running:
            # Wait for next interval
            for _ in range(self.poll_interval):
                if not self._running:
                    break
                time.sleep(1)
            
            if self._running:
                self._do_fetch()
        
        logger.info("📡 News scheduler stopped")
    
    def _do_fetch(self):
        """Execute a single fetch operation."""
        try:
            logger.info(f"🔄 Starting scheduled fetch #{self._fetch_count + 1}")
            
            stats = self.connector.fetch_and_write()
            
            self._last_fetch = datetime.now()
            self._last_stats = stats
            self._fetch_count += 1
            
            if self.on_fetch_complete:
                try:
                    self.on_fetch_complete(stats)
                except Exception as e:
                    logger.error(f"Callback error: {e}")
            
            logger.info(f"✅ Fetch #{self._fetch_count} complete: {stats.get('written_to_files', 0)} new articles")
            
        except Exception as e:
            logger.error(f"❌ Fetch error: {e}")
            self._last_stats = {"error": str(e)}
    
    def start(self):
        """Start the scheduler in a background thread."""
        if self._running:
            logger.warning("Scheduler already running")
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        
        logger.info("🚀 News scheduler thread started")
    
    def stop(self):
        """Stop the scheduler gracefully."""
        if not self._running:
            return
        
        logger.info("Stopping news scheduler...")
        self._running = False
        
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None
        
        logger.info("News scheduler stopped")
    
    def fetch_now(self) -> dict:
        """Trigger an immediate fetch (can be called from API)."""
        logger.info("Manual fetch triggered")
        self._do_fetch()
        return self._last_stats
    
    def get_status(self) -> dict:
        """Get current scheduler status."""
        return {
            "running": self._running,
            "poll_interval_seconds": self.poll_interval,
            "last_fetch": self._last_fetch.isoformat() if self._last_fetch else None,
            "next_fetch_in": self._calculate_next_fetch(),
            "fetch_count": self._fetch_count,
            "last_stats": self._last_stats,
            "connector_status": self.connector.get_status()
        }
    
    def _calculate_next_fetch(self) -> Optional[int]:
        """Calculate seconds until next fetch."""
        if not self._running or not self._last_fetch:
            return None
        
        elapsed = (datetime.now() - self._last_fetch).total_seconds()
        remaining = max(0, self.poll_interval - elapsed)
        return int(remaining)
    
    @property
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._running


# Global scheduler instance (initialized by main.py)
_scheduler: Optional[NewsScheduler] = None


def get_scheduler() -> Optional[NewsScheduler]:
    """Get the global scheduler instance."""
    return _scheduler


def init_scheduler(
    newsapi_key: str,
    gnews_key: str,
    poll_interval: int = 600,
    output_dir: str = "data/breaking_news",
    keywords: Optional[list] = None
) -> NewsScheduler:
    """
    Initialize and return the global scheduler.
    
    Args:
        newsapi_key: NewsAPI.org API key
        gnews_key: GNews.io API key
        poll_interval: Seconds between fetches
        output_dir: Directory to write articles
        keywords: Keywords to search for
        
    Returns:
        Initialized NewsScheduler instance
    """
    global _scheduler
    
    connector = NewsAPIConnector(
        newsapi_key=newsapi_key,
        gnews_key=gnews_key,
        output_dir=output_dir,
        keywords=keywords
    )
    
    _scheduler = NewsScheduler(
        connector=connector,
        poll_interval=poll_interval
    )
    
    return _scheduler
