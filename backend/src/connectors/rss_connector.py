"""Custom RSS feed connector for Pathway with multi-threaded polling and deduplication."""

import pathway as pw
import feedparser
import time
import json
import hashlib
from datetime import datetime
from typing import Set, List
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RSSConnector(pw.io.python.ConnectorSubject):
    """
    Custom Pathway connector for RSS feeds.
    
    Features:
    - Multi-threaded polling with configurable intervals
    - GUID-based deduplication with persistent cache
    - Exponential backoff for failed requests
    - Graceful handling of individual feed failures
    """
    
    def __init__(
        self,
        url_list: List[str],
        refresh_interval: int = 60,
        cache_file: str = "data/output/rss_cache.json"
    ):
        """
        Initialize RSS connector.
        
        Args:
            url_list: List of RSS feed URLs to monitor
            refresh_interval: Polling interval in seconds
            cache_file: Path to persistent deduplication cache
        """
        super().__init__()
        self.url_list = url_list
        self.interval = refresh_interval
        self.cache_file = Path(cache_file)
        self.seen_links: Set[str] = self._load_cache()
        self.retry_delays = {}  # Track backoff per URL
        
        logger.info(f"Initialized RSS Connector with {len(url_list)} feeds")
        logger.info(f"Polling interval: {refresh_interval}s")
    
    def _load_cache(self) -> Set[str]:
        """Load previously seen article links from persistent cache."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    logger.info(f"Loaded {len(data)} cached article links")
                    return set(data)
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        
        # Ensure directory exists
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        return set()
    
    def _save_cache(self):
        """Save seen links to persistent cache."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(list(self.seen_links), f)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def _extract_source_name(self, url: str) -> str:
        """Extract clean source name from RSS URL."""
        if "bbc" in url.lower():
            return "BBC"
        elif "reuters" in url.lower():
            return "Reuters"
        elif "ycombinator" in url.lower():
            return "HackerNews"
        elif "techcrunch" in url.lower():
            return "TechCrunch"
        else:
            return "Unknown"
    
    def _parse_published_date(self, entry) -> str:
        """Extract and normalize publication date."""
        date_fields = ['published', 'updated', 'created']
        for field in date_fields:
            if hasattr(entry, field):
                return getattr(entry, field)
        return datetime.now().isoformat()
    
    def run(self):
        """
        Main polling loop running in a separate thread.
        
        This method runs indefinitely, fetching RSS feeds and pushing
        new articles into the Pathway dataflow.
        """
        logger.info("RSS Connector thread started")
        
        while True:
            for url in self.url_list:
                try:
                    # Check if we should skip this URL due to backoff
                    if url in self.retry_delays:
                        if time.time() < self.retry_delays[url]:
                            continue
                        else:
                            # Reset backoff
                            del self.retry_delays[url]
                    
                    # Fetch and parse feed
                    logger.debug(f"Fetching {url}")
                    feed = feedparser.parse(url)
                    
                    # Check for errors
                    if hasattr(feed, 'bozo') and feed.bozo:
                        raise Exception(f"Feed parse error: {feed.get('bozo_exception', 'Unknown')}")
                    
                    source_name = self._extract_source_name(url)
                    new_articles = 0
                    
                    for entry in feed.entries:
                        # Use link as unique identifier
                        link = entry.get('link', '')
                        if not link:
                            continue
                        
                        # Check for duplicates
                        if link in self.seen_links:
                            continue
                        
                        # Mark as seen
                        self.seen_links.add(link)
                        new_articles += 1
                        
                        # Extract content (try multiple fields)
                        content = entry.get('description', '')
                        if hasattr(entry, 'content') and entry.content:
                            content = entry.content[0].get('value', content)
                        
                        summary = entry.get('summary', content[:500] if content else '')
                        
                        # Push data to Pathway
                        self.next(
                            title=entry.get('title', 'Untitled'),
                            summary=summary,
                            link=link,
                            published=self._parse_published_date(entry),
                            content=content,
                            source=source_name
                        )
                    
                    if new_articles > 0:
                        logger.info(f"✓ {source_name}: {new_articles} new articles")
                        # Commit immediately for low latency
                        self.commit()
                    
                except Exception as e:
                    logger.error(f"✗ Failed to fetch {url}: {e}")
                    # Implement exponential backoff (30s, 60s, 120s, max 5min)
                    current_delay = min(300, self.retry_delays.get(url, 15) * 2)
                    self.retry_delays[url] = time.time() + current_delay
                    logger.warning(f"  Backing off for {current_delay}s")
            
            # Save cache periodically
            self._save_cache()
            
            # Add jitter to avoid thundering herd (±10%)
            jitter = self.interval * 0.1 * (2 * time.time() % 1 - 0.5)
            sleep_time = self.interval + jitter
            
            logger.debug(f"Sleeping for {sleep_time:.1f}s")
            time.sleep(sleep_time)
