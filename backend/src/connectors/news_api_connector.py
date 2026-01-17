"""
News API Connector - Fetches real-time news from NewsAPI.org and GNews.io

Implements a fallback strategy:
1. Primary: NewsAPI.org
2. Fallback: GNews.io
3. Final fallback: Continue with cached/demo data
"""

import requests
import hashlib
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class NewsArticle:
    """Normalized news article structure."""
    id: str
    title: str
    summary: str
    content: str
    link: str
    source: str
    published: str
    timestamp: float


class NewsAPIConnector:
    """
    Fetches news from NewsAPI.org with GNews.io fallback.
    
    Features:
    - Rate limit handling
    - Deduplication
    - Category filtering
    - Keyword search
    - Automatic fallback between providers
    """
    
    # API Endpoints
    NEWSAPI_BASE = "https://newsapi.org/v2"
    GNEWS_BASE = "https://gnews.io/api/v4"
    
    # Categories supported by both APIs
    CATEGORIES = ["general", "business", "technology", "science", "health", "entertainment"]
    
    def __init__(
        self,
        newsapi_key: str,
        gnews_key: str,
        output_dir: str = "data/breaking_news",
        cache_file: str = "data/output/seen_articles.json",
        keywords: Optional[List[str]] = None
    ):
        """
        Initialize News API connector.
        
        Args:
            newsapi_key: API key for NewsAPI.org
            gnews_key: API key for GNews.io
            output_dir: Directory to write fetched articles
            cache_file: File to track seen article hashes
            keywords: Optional list of keywords to filter articles
        """
        self.newsapi_key = newsapi_key
        self.gnews_key = gnews_key
        self.output_dir = Path(output_dir)
        self.cache_file = Path(cache_file)
        self.keywords = keywords or [
            "Tesla", "Bitcoin", "cryptocurrency", "AI", "artificial intelligence",
            "stock market", "Fed", "inflation", "tech", "startup",
            "merger", "acquisition", "IPO", "earnings"
        ]
        
        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load seen articles cache
        self.seen_hashes = self._load_cache()
        
        # Track API status
        self.newsapi_available = True
        self.gnews_available = True
        self.last_newsapi_error = None
        self.last_gnews_error = None
        
        logger.info(f"NewsAPIConnector initialized")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Keywords: {', '.join(self.keywords[:5])}...")
    
    def _load_cache(self) -> set:
        """Load seen article hashes from cache file."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('hashes', []))
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
        return set()
    
    def _save_cache(self):
        """Save seen article hashes to cache file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump({'hashes': list(self.seen_hashes)}, f)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def _generate_hash(self, title: str, url: str) -> str:
        """Generate unique hash for article deduplication."""
        content = f"{title.lower().strip()}:{url.lower().strip()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _is_duplicate(self, title: str, url: str) -> bool:
        """Check if article has already been processed."""
        hash_id = self._generate_hash(title, url)
        return hash_id in self.seen_hashes
    
    def _mark_seen(self, title: str, url: str):
        """Mark article as processed."""
        hash_id = self._generate_hash(title, url)
        self.seen_hashes.add(hash_id)
        
        # Keep cache size manageable (max 10000 articles)
        if len(self.seen_hashes) > 10000:
            # Remove oldest entries (convert to list, slice, convert back)
            self.seen_hashes = set(list(self.seen_hashes)[-5000:])
    
    def fetch_from_newsapi(self, category: str = "general") -> List[NewsArticle]:
        """
        Fetch articles from NewsAPI.org
        
        Args:
            category: News category to fetch
            
        Returns:
            List of NewsArticle objects
        """
        if not self.newsapi_available:
            return []
        
        articles = []
        
        try:
            # Fetch top headlines by category
            url = f"{self.NEWSAPI_BASE}/top-headlines"
            params = {
                "apiKey": self.newsapi_key,
                "category": category,
                "language": "en",
                "pageSize": 20
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 429:
                logger.warning("NewsAPI rate limit reached")
                self.newsapi_available = False
                self.last_newsapi_error = "Rate limit exceeded"
                return []
            
            if response.status_code == 401:
                logger.error("NewsAPI authentication failed - check API key")
                self.newsapi_available = False
                self.last_newsapi_error = "Invalid API key"
                return []
            
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "ok":
                logger.warning(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return []
            
            for item in data.get("articles", []):
                title = item.get("title", "").strip()
                url = item.get("url", "")
                
                # Skip if missing required fields
                if not title or not url or title == "[Removed]":
                    continue
                
                # Skip duplicates
                if self._is_duplicate(title, url):
                    continue
                
                # Parse timestamp
                published = item.get("publishedAt", "")
                try:
                    dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
                    timestamp = dt.timestamp()
                except:
                    timestamp = time.time()
                
                article = NewsArticle(
                    id=self._generate_hash(title, url),
                    title=title,
                    summary=item.get("description", "") or "",
                    content=item.get("content", "") or item.get("description", "") or "",
                    link=url,
                    source=item.get("source", {}).get("name", "NewsAPI"),
                    published=published,
                    timestamp=timestamp
                )
                
                articles.append(article)
                self._mark_seen(title, url)
            
            logger.info(f"NewsAPI [{category}]: Fetched {len(articles)} new articles")
            self.newsapi_available = True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"NewsAPI request error: {e}")
            self.last_newsapi_error = str(e)
        except Exception as e:
            logger.error(f"NewsAPI error: {e}")
            self.last_newsapi_error = str(e)
        
        return articles
    
    def fetch_from_gnews(self, category: str = "general") -> List[NewsArticle]:
        """
        Fetch articles from GNews.io (fallback)
        
        Args:
            category: News category to fetch
            
        Returns:
            List of NewsArticle objects
        """
        if not self.gnews_available:
            return []
        
        articles = []
        
        try:
            # Map category names (GNews uses slightly different names)
            gnews_category = category
            if category == "general":
                gnews_category = "general"
            
            url = f"{self.GNEWS_BASE}/top-headlines"
            params = {
                "token": self.gnews_key,
                "topic": gnews_category,
                "lang": "en",
                "max": 10
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 429:
                logger.warning("GNews rate limit reached")
                self.gnews_available = False
                self.last_gnews_error = "Rate limit exceeded"
                return []
            
            if response.status_code == 401 or response.status_code == 403:
                logger.error("GNews authentication failed - check API key")
                self.gnews_available = False
                self.last_gnews_error = "Invalid API key"
                return []
            
            response.raise_for_status()
            data = response.json()
            
            for item in data.get("articles", []):
                title = item.get("title", "").strip()
                url = item.get("url", "")
                
                if not title or not url:
                    continue
                
                if self._is_duplicate(title, url):
                    continue
                
                # Parse timestamp
                published = item.get("publishedAt", "")
                try:
                    dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
                    timestamp = dt.timestamp()
                except:
                    timestamp = time.time()
                
                article = NewsArticle(
                    id=self._generate_hash(title, url),
                    title=title,
                    summary=item.get("description", "") or "",
                    content=item.get("content", "") or item.get("description", "") or "",
                    link=url,
                    source=item.get("source", {}).get("name", "GNews"),
                    published=published,
                    timestamp=timestamp
                )
                
                articles.append(article)
                self._mark_seen(title, url)
            
            logger.info(f"GNews [{category}]: Fetched {len(articles)} new articles")
            self.gnews_available = True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"GNews request error: {e}")
            self.last_gnews_error = str(e)
        except Exception as e:
            logger.error(f"GNews error: {e}")
            self.last_gnews_error = str(e)
        
        return articles
    
    def fetch_all_categories(self) -> List[NewsArticle]:
        """
        Fetch articles from all categories with fallback strategy.
        
        Returns:
            List of all fetched NewsArticle objects
        """
        all_articles = []
        
        for category in self.CATEGORIES:
            # Try NewsAPI first
            articles = self.fetch_from_newsapi(category)
            
            # Fallback to GNews if NewsAPI failed
            if not articles and not self.newsapi_available:
                logger.info(f"Falling back to GNews for {category}")
                articles = self.fetch_from_gnews(category)
            
            all_articles.extend(articles)
            
            # Small delay between requests to be nice to APIs
            time.sleep(0.5)
        
        # Save cache after fetching
        self._save_cache()
        
        return all_articles
    
    def fetch_by_keywords(self) -> List[NewsArticle]:
        """
        Fetch articles matching configured keywords.
        
        Returns:
            List of NewsArticle objects matching keywords
        """
        articles = []
        
        # Build search query from keywords
        query = " OR ".join(self.keywords[:5])  # Limit to 5 keywords per query
        
        try:
            # NewsAPI everything endpoint for keyword search
            url = f"{self.NEWSAPI_BASE}/everything"
            params = {
                "apiKey": self.newsapi_key,
                "q": query,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 20,
                "from": (datetime.now() - timedelta(days=1)).isoformat()
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get("articles", []):
                    title = item.get("title", "").strip()
                    url = item.get("url", "")
                    
                    if not title or not url or title == "[Removed]":
                        continue
                    
                    if self._is_duplicate(title, url):
                        continue
                    
                    published = item.get("publishedAt", "")
                    try:
                        dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
                        timestamp = dt.timestamp()
                    except:
                        timestamp = time.time()
                    
                    article = NewsArticle(
                        id=self._generate_hash(title, url),
                        title=title,
                        summary=item.get("description", "") or "",
                        content=item.get("content", "") or item.get("description", "") or "",
                        link=url,
                        source=item.get("source", {}).get("name", "NewsAPI"),
                        published=published,
                        timestamp=timestamp
                    )
                    
                    articles.append(article)
                    self._mark_seen(title, url)
                
                logger.info(f"Keyword search: Fetched {len(articles)} new articles")
        
        except Exception as e:
            logger.error(f"Keyword search error: {e}")
        
        self._save_cache()
        return articles
    
    def write_articles_to_files(self, articles: List[NewsArticle]) -> int:
        """
        Write articles to individual text files for FileWatcher to pick up.
        
        Args:
            articles: List of articles to write
            
        Returns:
            Number of files written
        """
        written = 0
        
        for article in articles:
            try:
                # Create filename from article ID
                filename = f"{article.id}_{int(article.timestamp)}.txt"
                filepath = self.output_dir / filename
                
                # Format content for FileWatcher
                content = f"""{article.title}

{article.summary}

Source: {article.source}
Published: {article.published}
Link: {article.link}

{article.content}
"""
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.info(f"📰 Written: {article.title[:50]}...")
                written += 1
                
            except Exception as e:
                logger.error(f"Failed to write article: {e}")
        
        return written
    
    def fetch_and_write(self) -> Dict[str, Any]:
        """
        Main method: Fetch from all sources and write to files.
        
        Returns:
            Statistics about the fetch operation
        """
        start_time = time.time()
        
        # Fetch from categories
        category_articles = self.fetch_all_categories()
        
        # Fetch by keywords
        keyword_articles = self.fetch_by_keywords()
        
        # Combine and deduplicate
        all_articles = category_articles + keyword_articles
        unique_articles = {a.id: a for a in all_articles}.values()
        
        # Write to files
        written = self.write_articles_to_files(list(unique_articles))
        
        elapsed = time.time() - start_time
        
        stats = {
            "total_fetched": len(all_articles),
            "unique_articles": len(unique_articles),
            "written_to_files": written,
            "newsapi_available": self.newsapi_available,
            "gnews_available": self.gnews_available,
            "elapsed_seconds": round(elapsed, 2)
        }
        
        logger.info(f"✅ Fetch complete: {written} new articles in {elapsed:.1f}s")
        
        return stats
    
    def get_status(self) -> Dict[str, Any]:
        """Get current connector status."""
        return {
            "newsapi_available": self.newsapi_available,
            "newsapi_error": self.last_newsapi_error,
            "gnews_available": self.gnews_available,
            "gnews_error": self.last_gnews_error,
            "cached_articles": len(self.seen_hashes),
            "keywords": self.keywords
        }
