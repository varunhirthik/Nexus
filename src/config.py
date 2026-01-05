"""Configuration management using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Gemini API Configuration
    gemini_api_key: str
    llm_model: str = "gemini-1.5-flash"
    llm_temperature: float = 0.3
    max_context_chunks: int = 5
    
    # RSS Feed Configuration
    rss_poll_interval: int = 60  # seconds
    rss_feeds: str = (
        "http://feeds.bbci.co.uk/news/rss.xml,"
        "http://feeds.reuters.com/reuters/topNews,"
        "https://news.ycombinator.com/rss,"
        "https://techcrunch.com/feed/"
    )
    
    # Pathway Configuration
    pathway_host: str = "0.0.0.0"
    pathway_port: int = 8000
    autocommit_duration_ms: int = 1000
    
    # Alert Configuration
    alert_keywords: str = "Tesla,Bitcoin,Fed,inflation,crash,China,Apple,Google"
    alert_threshold: int = 3  # mentions in time window
    
    # Sentiment Analysis
    sentiment_window_minutes: int = 10
    
    # File Watcher Configuration
    breaking_news_dir: str = "data/breaking_news"
    
    @property
    def rss_feed_list(self) -> List[str]:
        """Parse RSS feeds from comma-separated string."""
        return [url.strip() for url in self.rss_feeds.split(",") if url.strip()]
    
    @property
    def alert_keyword_list(self) -> List[str]:
        """Parse alert keywords from comma-separated string."""
        return [kw.strip() for kw in self.alert_keywords.split(",") if kw.strip()]


# Global settings instance
settings = Settings()
