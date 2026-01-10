"""Pathway schema definitions for the Live News Analyst system."""

import pathway as pw
from datetime import datetime
from typing import Optional


class NewsSchema(pw.Schema):
    """Schema for news articles ingested from RSS feeds or file watcher."""
    
    title: str
    summary: str
    link: str
    published: str
    content: str
    source: str  # BBC, Reuters, FileWatcher, etc.


class NewsChunkSchema(pw.Schema):
    """Schema for chunked news articles with embeddings."""
    
    text: str
    original_link: str
    source: str
    published: str
    chunk_index: int


class QuerySchema(pw.Schema):
    """Schema for user queries to the RAG system."""
    
    query: str
    user: str


class ResponseSchema(pw.Schema):
    """Schema for RAG system responses."""
    
    query: str
    answer: str
    sources: str  # JSON string of source articles
    latency_ms: float


class HeadlineSchema(pw.Schema):
    """Schema for latest headlines output."""
    
    title: str
    summary: str
    link: str
    source: str
    published: str
    timestamp: str  # ISO format


class SentimentDataSchema(pw.Schema):
    """Schema for sentiment analysis output."""
    
    timestamp: str
    sentiment_score: float  # -1.0 (negative) to 1.0 (positive)
    article_count: int
    window_start: str
    window_end: str


class AlertSchema(pw.Schema):
    """Schema for keyword alert events."""
    
    keyword: str
    mention_count: int
    threshold: int
    triggered_at: str
    sample_headlines: str  # JSON array of headline strings
