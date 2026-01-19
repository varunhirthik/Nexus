"""
Alert Service - Keyword Alert Tracking and Aggregation

This service monitors articles for keyword mentions and generates alerts
when keywords appear frequently within a time window.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from collections import defaultdict, deque
from dataclasses import dataclass, field
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AlertMention:
    """A single mention of a keyword in an article."""
    keyword: str
    article_title: str
    article_link: str
    article_source: str
    timestamp: float


@dataclass
class Alert:
    """An aggregated alert when keyword threshold is exceeded."""
    id: str
    keyword: str
    count: int
    window: str  # e.g., "last 10 minutes"
    timestamp: int
    articles: List[str]  # article links
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "keyword": self.keyword,
            "count": self.count,
            "window": self.window,
            "timestamp": self.timestamp,
            "articles": self.articles
        }


class AlertService:
    """
    Service for tracking keyword mentions and generating alerts.
    
    Features:
    - Time-window based mention tracking
    - Configurable threshold for alert generation
    - Deduplication of alerts
    - Automatic cleanup of old mentions
    """
    
    def __init__(
        self,
        keywords: List[str],
        threshold: int = 3,
        window_minutes: int = 10
    ):
        """
        Initialize Alert Service.
        
        Args:
            keywords: List of keywords to monitor
            threshold: Number of mentions required to trigger alert
            window_minutes: Time window for counting mentions (minutes)
        """
        self.keywords = [kw.lower() for kw in keywords]
        self.threshold = threshold
        self.window_minutes = window_minutes
        self.window_seconds = window_minutes * 60
        
        # Track mentions per keyword: keyword -> deque of AlertMention
        self.mentions: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Track seen articles to avoid duplicate processing
        self.seen_articles: Set[str] = set()
        
        # Track generated alerts to avoid duplicates
        self.active_alerts: Dict[str, Alert] = {}  # keyword -> Alert
        self.alert_cooldown: Dict[str, float] = {}  # keyword -> timestamp
        self.cooldown_seconds = 300  # 5 minutes cooldown per keyword
        
        logger.info(f"AlertService initialized: {len(keywords)} keywords, threshold={threshold}, window={window_minutes}min")
    
    def _generate_article_id(self, title: str, link: str) -> str:
        """Generate unique ID for article."""
        content = f"{title.lower().strip()}:{link.lower().strip()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _is_in_cooldown(self, keyword: str) -> bool:
        """Check if keyword is in alert cooldown period."""
        if keyword not in self.alert_cooldown:
            return False
        
        last_alert_time = self.alert_cooldown[keyword]
        return (time.time() - last_alert_time) < self.cooldown_seconds
    
    def _cleanup_old_mentions(self, keyword: str):
        """Remove mentions outside the time window."""
        if keyword not in self.mentions:
            return
        
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds
        
        # Remove mentions older than window
        mentions_list = list(self.mentions[keyword])
        valid_mentions = [m for m in mentions_list if m.timestamp >= cutoff_time]
        
        self.mentions[keyword] = deque(valid_mentions, maxlen=100)
    
    def _check_and_generate_alert(self, keyword: str) -> Optional[Alert]:
        """
        Check if keyword mentions exceed threshold and generate alert.
        
        Args:
            keyword: Keyword to check
            
        Returns:
            Alert object if threshold exceeded, None otherwise
        """
        # Clean up old mentions first
        self._cleanup_old_mentions(keyword)
        
        mentions_list = list(self.mentions[keyword])
        
        if len(mentions_list) < self.threshold:
            return None
        
        # Check if in cooldown
        if self._is_in_cooldown(keyword):
            return None
        
        # Generate alert
        alert_id = hashlib.md5(f"{keyword}:{time.time()}".encode()).hexdigest()[:16]
        
        # Collect unique article links
        article_links = list(set(m.article_link for m in mentions_list if m.article_link))[:5]
        
        alert = Alert(
            id=alert_id,
            keyword=keyword,
            count=len(mentions_list),
            window=f"last {self.window_minutes} minutes",
            timestamp=int(time.time()),
            articles=article_links
        )
        
        # Update cooldown and active alerts
        self.alert_cooldown[keyword] = time.time()
        self.active_alerts[keyword] = alert
        
        logger.info(f"🚨 Alert generated: {keyword} mentioned {len(mentions_list)}x in {self.window_minutes} minutes")
        
        return alert
    
    def process_article(self, article: Dict) -> List[Alert]:
        """
        Process an article and check for keyword mentions.
        
        Args:
            article: Article dictionary with 'title', 'content', 'link', 'source'
            
        Returns:
            List of newly generated alerts
        """
        title = article.get("title", "").lower()
        content = article.get("content", "").lower()
        link = article.get("link", "")
        source = article.get("source", "Unknown")
        
        # Generate article ID for deduplication
        article_id = self._generate_article_id(title, link)
        
        # Skip if already processed
        if article_id in self.seen_articles:
            return []
        
        self.seen_articles.add(article_id)
        
        # Keep cache size manageable
        if len(self.seen_articles) > 10000:
            # Convert to list, keep last 5000
            self.seen_articles = set(list(self.seen_articles)[-5000:])
        
        # Check for keyword mentions
        text = f"{title} {content}"
        new_alerts = []
        
        for keyword in self.keywords:
            if keyword in text:
                # Record mention
                mention = AlertMention(
                    keyword=keyword,
                    article_title=article.get("title", "Unknown"),
                    article_link=link,
                    article_source=source,
                    timestamp=time.time()
                )
                
                self.mentions[keyword].append(mention)
                
                # Check if alert should be generated
                alert = self._check_and_generate_alert(keyword)
                if alert:
                    new_alerts.append(alert)
        
        return new_alerts
    
    def get_active_alerts(self, limit: int = 20) -> List[Dict]:
        """
        Get list of active alerts.
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of alert dictionaries
        """
        # Sort by timestamp (most recent first)
        alerts = sorted(
            self.active_alerts.values(),
            key=lambda a: a.timestamp,
            reverse=True
        )
        
        return [a.to_dict() for a in alerts[:limit]]
    
    def get_mention_stats(self) -> Dict:
        """Get statistics about keyword mentions."""
        stats = {}
        
        for keyword in self.keywords:
            self._cleanup_old_mentions(keyword)
            mentions_list = list(self.mentions[keyword])
            
            stats[keyword] = {
                "mentions_in_window": len(mentions_list),
                "threshold": self.threshold,
                "in_cooldown": self._is_in_cooldown(keyword)
            }
        
        return stats


# Global alert service instance
_alert_service: Optional[AlertService] = None


def init_alert_service(
    keywords: List[str],
    threshold: int = 3,
    window_minutes: int = 10
) -> AlertService:
    """
    Initialize the global alert service.
    
    Args:
        keywords: List of keywords to monitor
        threshold: Mentions required to trigger alert
        window_minutes: Time window for mentions
        
    Returns:
        Initialized AlertService instance
    """
    global _alert_service
    
    _alert_service = AlertService(
        keywords=keywords,
        threshold=threshold,
        window_minutes=window_minutes
    )
    
    return _alert_service


def get_alert_service() -> Optional[AlertService]:
    """Get the global alert service instance."""
    return _alert_service
