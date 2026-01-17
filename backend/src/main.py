"""
Main entry point for the Live News Analyst backend.

This script initializes and runs the Pathway pipeline with all
real-time components including the News API scheduler.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from pipeline.pathway_pipeline import LiveNewsAnalystPipeline
from connectors.news_scheduler import init_scheduler
from llm.rag_query import init_rag_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('data/output/pipeline.log')
    ]
)

logger = logging.getLogger(__name__)


def check_environment():
    """Validate environment configuration."""
    logger.info("Checking environment configuration...")
    
    # Check for Gemini API key
    if not settings.gemini_api_key or settings.gemini_api_key == "your_gemini_api_key_here":
        logger.error("="*60)
        logger.error("GEMINI_API_KEY not configured!")
        logger.error("Please set your API key in the .env file")
        logger.error("Get your key from: https://makersuite.google.com/app/apikey")
        logger.error("="*60)
        sys.exit(1)
    
    # Check News API keys
    if settings.news_enabled:
        if not settings.newsapi_key and not settings.gnews_key:
            logger.warning("="*60)
            logger.warning("NEWS API KEYS not configured!")
            logger.warning("Real-time news fetching will be disabled.")
            logger.warning("Set NEWSAPI_KEY and/or GNEWS_KEY in .env")
            logger.warning("="*60)
        else:
            if settings.newsapi_key:
                logger.info(f"✓ NewsAPI key configured")
            if settings.gnews_key:
                logger.info(f"✓ GNews key configured")
            logger.info(f"✓ News poll interval: {settings.news_poll_interval}s")
    
    # Check RSS feeds
    if not settings.rss_feed_list:
        logger.warning("No RSS feeds configured. Using defaults.")
    
    logger.info(f"✓ Gemini API Key configured")
    logger.info(f"✓ {len(settings.rss_feed_list)} RSS feeds configured")
    logger.info(f"✓ FileWatcher directory: {settings.breaking_news_dir}")
    
    # Ensure directories exist
    Path("data/output").mkdir(parents=True, exist_ok=True)
    Path(settings.breaking_news_dir).mkdir(parents=True, exist_ok=True)
    
    logger.info("✓ Directories created")


def print_startup_banner():
    """Print ASCII art banner."""
    news_api_status = "Enabled" if (settings.news_enabled and settings.has_news_api_keys) else "Disabled"
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║             NEXUS - LIVE NEWS ANALYST                    ║
    ║                                                           ║
    ║  Real-Time RAG System with News API Integration          ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    
    🚀 Powered by: Pathway | Google Gemini | React | NewsAPI
    
    📊 Features:
       ✓ Real-time News API fetching ({poll}s polling)
       ✓ Incremental vector indexing
       ✓ Sentiment analysis ticker
       ✓ Keyword alert system
       ✓ FileWatcher for demos
    
    ⚙️  Configuration:
       • Backend Port: {port}
       • LLM Model: {model}
       • News API: {news_status}
       • Alert Keywords: {keyword_count}
    
    📡 Endpoints:
       • GET  /news/latest  - Latest news
       • GET  /sentiment    - Sentiment data
       • POST /query        - RAG queries
       • GET  /news/status  - News API status
       • POST /news/fetch   - Manual fetch trigger
       • WS   /ws           - Live updates
    
    """.format(
        port=settings.pathway_port,
        model=settings.llm_model,
        poll=settings.news_poll_interval,
        news_status=news_api_status,
        keyword_count=len(settings.alert_keyword_list)
    )
    
    print(banner)


def main():
    """Main entry point."""
    news_scheduler = None
    
    try:
        # Load environment variables
        load_dotenv()
        
        # Print banner
        print_startup_banner()
        
        # Validate configuration
        check_environment()
        
        logger.info("Initializing pipeline...")
        
        # Initialize RAG Query Service
        logger.info("🤖 Initializing RAG Query Service (Gemini AI)...")
        rag_service = init_rag_service(
            api_key=settings.gemini_api_key,
            model=settings.llm_model,
            temperature=0.7
        )
        logger.info("   → RAG Service ready for AI queries")
        
        # Create and run pipeline
        pipeline = LiveNewsAnalystPipeline()
        
        logger.info("="*60)
        logger.info("🎬 STARTING NEXUS - LIVE NEWS ANALYST")
        logger.info("="*60)
        logger.info("")
        
        # Start News API Scheduler if configured
        if settings.news_enabled and settings.has_news_api_keys:
            logger.info("📡 Starting News API Scheduler...")
            news_scheduler = init_scheduler(
                newsapi_key=settings.newsapi_key or "",
                gnews_key=settings.gnews_key or "",
                poll_interval=settings.news_poll_interval,
                output_dir=settings.breaking_news_dir,
                keywords=settings.news_keyword_list
            )
            news_scheduler.start()
            logger.info(f"   → Poll interval: {settings.news_poll_interval}s")
            logger.info(f"   → Keywords: {', '.join(settings.news_keyword_list[:5])}...")
        else:
            logger.info("📡 News API Scheduler: DISABLED (no API keys)")
            logger.info("   → Using FileWatcher for demo data only")
        
        logger.info("")
        logger.info("💡 TIP: Drop .txt files into data/breaking_news/ for instant ingestion")
        logger.info("💡 TIP: Watch data/output/headlines.jsonl for real-time updates")
        logger.info("")
        logger.info("Press Ctrl+C to stop")
        logger.info("")
        
        # Start API server in background thread
        logger.info("🌐 Starting API server in background thread...")
        import threading
        from api_server import start_server
        
        api_thread = threading.Thread(
            target=start_server,
            args=(settings.pathway_host, settings.pathway_port),
            daemon=True
        )
        api_thread.start()
        logger.info(f"   → API Server: http://{settings.pathway_host}:{settings.pathway_port}")
        logger.info(f"   → WebSocket: ws://{settings.pathway_host}:{settings.pathway_port}/ws")
        
        # Give API server time to start
        import time
        time.sleep(2)
        
        # Run the pipeline (this blocks)
        logger.info("")
        logger.info("🚀 Starting Pathway pipeline (press Ctrl+C to stop)...")
        logger.info("="*60)
        pipeline.run()
    
    except KeyboardInterrupt:
        logger.info("")
        logger.info("="*60)
        logger.info("🛑 Shutting down gracefully...")
        if news_scheduler:
            news_scheduler.stop()
        logger.info("="*60)
        sys.exit(0)
    
    except Exception as e:
        logger.error("="*60)
        logger.error(f"❌ FATAL ERROR: {e}")
        logger.error("="*60)
        import traceback
        traceback.print_exc()
        if news_scheduler:
            news_scheduler.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()
