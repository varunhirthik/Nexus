"""
Main Pathway RAG pipeline for the Live News Analyst system.

This module orchestrates the entire data flow:
1. Ingestion from RSS + FileWatcher
2. Deduplication and chunking
3. Embedding with Gemini
4. KNN indexing
5. RAG query processing
6. Sentiment analysis
7. Alert detection
"""

import pathway as pw
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

from config import settings
from connectors.rss_connector import RSSConnector
from connectors.file_watcher import FileWatcherConnector
from pipeline.schemas import NewsSchema, QuerySchema, HeadlineSchema, SentimentDataSchema
from pipeline.sentiment import analyze_article_sentiment, SentimentAggregator
from llm.embedder import GeminiLLM
from llm.prompts import build_rag_prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LiveNewsAnalystPipeline:
    """
    Main pipeline orchestrating all components of the Live News Analyst.
    
    This class builds the Pathway computation graph that processes
    news articles in real-time and serves RAG queries.
    """
    
    def __init__(self):
        """Initialize pipeline components."""
        self.llm = GeminiLLM(
            api_key=settings.gemini_api_key,
            model=settings.llm_model,
            temperature=settings.llm_temperature
        )
        
        self.sentiment_aggregator = SentimentAggregator(
            window_minutes=settings.sentiment_window_minutes
        )
        
        logger.info("Pipeline initialized")
    
    def create_ingestion_sources(self):
        """
        Create and merge multiple data sources.
        
        Returns:
            Pathway table with unified NewsSchema
        """
        logger.info("Creating ingestion sources...")
        
        # RSS Connector
        rss_connector = RSSConnector(
            url_list=settings.rss_feed_list,
            refresh_interval=settings.rss_poll_interval
        )
        
        rss_table = pw.io.python.read(
            rss_connector,
            schema=NewsSchema,
            autocommit_duration_ms=settings.autocommit_duration_ms
        )
        
        # FileWatcher Connector
        file_connector = FileWatcherConnector(
            watch_directory=settings.breaking_news_dir,
            poll_interval=1.0,  # Fast polling for demos
            auto_cleanup=True
        )
        
        file_table = pw.io.python.read(
            file_connector,
            schema=NewsSchema,
            autocommit_duration_ms=500  # Even faster for file drops
        )
        
        # Merge both sources - promise they are disjoint (different sources)
        rss_table_promised = rss_table.promise_universes_are_disjoint(file_table)
        combined_table = pw.Table.concat(rss_table_promised, file_table)
        
        logger.info("✓ Ingestion sources created")
        return combined_table
    
    def build_processing_pipeline(self, news_table):
        """
        Build the processing pipeline: deduplication, chunking, sentiment.
        
        Args:
            news_table: Input Pathway table with NewsSchema
        
        Returns:
            Tuple of (processed_table, sentiment_table)
        """
        logger.info("Building processing pipeline...")
        
        # Skipping deduplication - RSS connector uses GUID-based deduplication already
        # Pathway's incremental nature also handles duplicates well
        
        # Add sentiment scores directly to the news table
        enriched_table = news_table.select(
            title=pw.this.title,
            summary=pw.this.summary,
            link=pw.this.link,
            published=pw.this.published,
            content=pw.this.content,
            source=pw.this.source,
            sentiment_score=pw.apply(
                lambda title, summary, content: analyze_article_sentiment(title, summary, content)['sentiment_score'],
                pw.this.title,
                pw.this.summary,
                pw.this.content
            )
        )
        
        logger.info("✓ Processing pipeline built")
        return enriched_table
    
    def build_rag_components(self, processed_table):
        """
        Build RAG components: chunking, embedding, indexing.
        
        Args:
            processed_table: Processed news table
        
        Returns:
            Tuple of (chunks_table, index)
        """
        logger.info("Building RAG components...")
        
        # Note: Pathway's LLM xPack provides built-in chunking and embedding
        # For this implementation, we'll use a simplified approach
        # In production, use: from pathway.xpacks.llm import embedders, splitters
        
        # For now, we'll create a simple chunk table
        # Each article becomes one chunk (can be enhanced with TokenCountSplitter)
        chunks_table = processed_table.select(
            text=pw.this.content,
            title=pw.this.title,
            summary=pw.this.summary,
            link=pw.this.link,
            source=pw.this.source,
            published=pw.this.published,
            sentiment_score=pw.this.sentiment_score
        )
        
        logger.info("✓ RAG components built")
        return chunks_table
    
    def create_headline_sink(self, processed_table):
        """
        Create output sink for latest headlines (for frontend ticker).
        
        Args:
            processed_table: Processed news table
        """
        # Select latest 50 headlines
        headlines = processed_table.select(
            title=pw.this.title,
            summary=pw.this.summary,
            link=pw.this.link,
            source=pw.this.source,
            published=pw.this.published,
            sentiment_score=pw.this.sentiment_score
        )
        
        # Write to JSON file (frontend will poll this)
        pw.io.jsonlines.write(
            headlines,
            "data/output/headlines.jsonl"
        )
        
        logger.info("✓ Headline sink created")
    
    def create_sentiment_sink(self, processed_table):
        """
        Create output sink for sentiment analysis data.
        
        Args:
            processed_table: Processed news table with sentiment scores
        """
        # Aggregate sentiment over time
        # For simplicity, we'll output individual article sentiments
        # Frontend will aggregate for charts
        
        sentiment_output = processed_table.select(
            timestamp=pw.this.published,
            sentiment_score=pw.this.sentiment_score,
            title=pw.this.title,
            source=pw.this.source
        )
        
        pw.io.jsonlines.write(
            sentiment_output,
            "data/output/sentiment.jsonl"
        )
        
        logger.info("✓ Sentiment sink created")
    
    def process_rag_query(self, query: str, chunks_table, top_k: int = 5) -> Dict[str, Any]:
        """
        Process a RAG query against the knowledge base.
        
        Args:
            query: User's question
            chunks_table: Table with article chunks
            top_k: Number of chunks to retrieve
        
        Returns:
            Dict with answer, sources, and metadata
        """
        # Note: This is a simplified version
        # In production, use Pathway's VectorStore and KNN index
        
        # For now, return a placeholder
        # The actual implementation will be in the HTTP endpoint handler
        
        return {
            'query': query,
            'answer': 'RAG implementation in progress',
            'sources': [],
            'latency_ms': 0.0
        }
    
    def run(self):
        """
        Build and run the complete pipeline.
        
        This is the main entry point that constructs the Pathway
        computation graph and starts the streaming engine.
        """
        logger.info("="*60)
        logger.info("Starting Live News Analyst Pipeline")
        logger.info("="*60)
        
        # 1. Create ingestion sources
        news_table = self.create_ingestion_sources()
        
        # 2. Build processing pipeline
        processed_table = self.build_processing_pipeline(news_table)
        
        # 3. Build RAG components
        chunks_table = self.build_rag_components(processed_table)
        
        # 4. Create output sinks
        self.create_headline_sink(processed_table)
        self.create_sentiment_sink(processed_table)
        
        logger.info("="*60)
        logger.info("Pipeline ready - Starting Pathway engine")
        logger.info("="*60)
        
        # Run the Pathway engine
        pw.run(
            monitoring_level=pw.MonitoringLevel.NONE,
            # For production, use:
            # monitoring_level=pw.MonitoringLevel.ALL
        )


def create_simple_embedder(api_key: str):
    """
    Create a simple embedding function for Pathway.
    
    This wraps the Gemini embedder for use in Pathway transformations.
    """
    llm = GeminiLLM(api_key=api_key)
    
    def embed(text: str) -> List[float]:
        return llm.embed_text(text)
    
    return embed
