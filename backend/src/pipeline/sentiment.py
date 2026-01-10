"""Sentiment analysis module using keyword-based scoring and optional LLM enhancement."""

import logging
from typing import Dict, List
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Keyword-based sentiment lexicon (simple but fast)
POSITIVE_KEYWORDS = {
    'growth', 'gain', 'rally', 'surge', 'soar', 'profit', 'success', 'breakthrough',
    'innovation', 'record', 'boom', 'advance', 'rise', 'increase', 'recovery',
    'expansion', 'agreement', 'partnership', 'milestone', 'achievement'
}

NEGATIVE_KEYWORDS = {
    'crash', 'plunge', 'drop', 'fall', 'decline', 'loss', 'deficit', 'crisis',
    'recession', 'inflation', 'conflict', 'war', 'layoff', 'bankruptcy', 'scandal',
    'failure', 'collapse', 'threat', 'warning', 'concern', 'risk', 'downgrade'
}

VERY_POSITIVE_KEYWORDS = {
    'breakthrough', 'record-breaking', 'historic', 'unprecedented growth'
}

VERY_NEGATIVE_KEYWORDS = {
    'catastrophic', 'devastating', 'crisis', 'emergency', 'disaster'
}


def calculate_keyword_sentiment(text: str) -> float:
    """
    Calculate sentiment score using keyword matching.
    
    This is a fast, deterministic approach suitable for real-time processing.
    More sophisticated than simple positive/negative counting.
    
    Args:
        text: Article title + summary combined
    
    Returns:
        Sentiment score from -1.0 to 1.0
    """
    text_lower = text.lower()
    
    # Count keyword occurrences with weights
    positive_count = 0
    negative_count = 0
    
    for keyword in VERY_POSITIVE_KEYWORDS:
        if keyword in text_lower:
            positive_count += 2.0  # Higher weight
    
    for keyword in POSITIVE_KEYWORDS:
        if keyword in text_lower:
            positive_count += 1.0
    
    for keyword in VERY_NEGATIVE_KEYWORDS:
        if keyword in text_lower:
            negative_count += 2.0
    
    for keyword in NEGATIVE_KEYWORDS:
        if keyword in text_lower:
            negative_count += 1.0
    
    # Calculate score
    total = positive_count + negative_count
    if total == 0:
        return 0.0  # Neutral
    
    score = (positive_count - negative_count) / max(total, 1)
    
    # Clamp to [-1, 1]
    return max(-1.0, min(1.0, score))


def analyze_article_sentiment(title: str, summary: str, content: str = "") -> Dict:
    """
    Comprehensive sentiment analysis of an article.
    
    Args:
        title: Article title
        summary: Article summary
        content: Full article content (optional)
    
    Returns:
        Dict with sentiment_score, confidence, and reasoning
    """
    # Combine text for analysis (title weighted more heavily)
    analysis_text = f"{title} {title} {summary}"
    if content:
        analysis_text += f" {content[:500]}"  # Limit content length
    
    sentiment_score = calculate_keyword_sentiment(analysis_text)
    
    # Calculate confidence based on keyword density
    text_lower = analysis_text.lower()
    total_keywords = sum(1 for kw in POSITIVE_KEYWORDS | NEGATIVE_KEYWORDS if kw in text_lower)
    confidence = min(1.0, total_keywords / 5.0)  # Max confidence at 5+ keywords
    
    return {
        'sentiment_score': sentiment_score,
        'confidence': confidence,
        'interpretation': _interpret_sentiment(sentiment_score)
    }


def _interpret_sentiment(score: float) -> str:
    """Convert numerical sentiment to human-readable interpretation."""
    if score >= 0.5:
        return "Very Positive"
    elif score >= 0.2:
        return "Positive"
    elif score >= -0.2:
        return "Neutral"
    elif score >= -0.5:
        return "Negative"
    else:
        return "Very Negative"


class SentimentAggregator:
    """
    Aggregates sentiment over time windows for the ticker display.
    
    This class maintains a rolling window of sentiment scores and
    provides aggregated statistics for visualization.
    """
    
    def __init__(self, window_minutes: int = 10):
        """
        Initialize sentiment aggregator.
        
        Args:
            window_minutes: Size of rolling window in minutes
        """
        self.window_minutes = window_minutes
        self.sentiment_buffer: List[Dict] = []
    
    def add_article(self, sentiment_score: float, timestamp: datetime):
        """Add article sentiment to the buffer."""
        self.sentiment_buffer.append({
            'score': sentiment_score,
            'timestamp': timestamp
        })
        
        # Cleanup old entries
        self._cleanup_old_entries()
    
    def _cleanup_old_entries(self):
        """Remove entries older than the window."""
        cutoff = datetime.now() - timedelta(minutes=self.window_minutes)
        self.sentiment_buffer = [
            entry for entry in self.sentiment_buffer
            if entry['timestamp'] > cutoff
        ]
    
    def get_current_sentiment(self) -> Dict:
        """
        Calculate current aggregated sentiment.
        
        Returns:
            Dict with average score, article count, and time range
        """
        self._cleanup_old_entries()
        
        if not self.sentiment_buffer:
            return {
                'avg_score': 0.0,
                'article_count': 0,
                'window_start': None,
                'window_end': None
            }
        
        scores = [entry['score'] for entry in self.sentiment_buffer]
        timestamps = [entry['timestamp'] for entry in self.sentiment_buffer]
        
        return {
            'avg_score': sum(scores) / len(scores),
            'article_count': len(scores),
            'window_start': min(timestamps),
            'window_end': max(timestamps)
        }
    
    def get_sentiment_trend(self) -> str:
        """
        Determine if sentiment is improving, worsening, or stable.
        
        Returns:
            "improving", "worsening", or "stable"
        """
        if len(self.sentiment_buffer) < 4:
            return "stable"
        
        # Split into first half and second half
        mid = len(self.sentiment_buffer) // 2
        first_half_avg = sum(e['score'] for e in self.sentiment_buffer[:mid]) / mid
        second_half_avg = sum(e['score'] for e in self.sentiment_buffer[mid:]) / (len(self.sentiment_buffer) - mid)
        
        diff = second_half_avg - first_half_avg
        
        if diff > 0.1:
            return "improving"
        elif diff < -0.1:
            return "worsening"
        else:
            return "stable"
