"""
Connectors package - Data ingestion from various sources.

Available connectors:
- FileWatcherConnector: Monitors directory for demo/manual news injection
- NewsAPIConnector: Fetches from NewsAPI.org and GNews.io
- NewsScheduler: Background scheduler for periodic fetching
"""

from .file_watcher import FileWatcherConnector
from .news_api_connector import NewsAPIConnector
from .news_scheduler import NewsScheduler, init_scheduler, get_scheduler

__all__ = [
    "FileWatcherConnector",
    "NewsAPIConnector", 
    "NewsScheduler",
    "init_scheduler",
    "get_scheduler"
]
