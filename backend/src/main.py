"""
Main entry point for the Live News Analyst backend.

This script initializes and runs the Pathway pipeline with all
real-time components.
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
    
    # Check for API key
    if not settings.gemini_api_key or settings.gemini_api_key == "your_gemini_api_key_here":
        logger.error("="*60)
        logger.error("GEMINI_API_KEY not configured!")
        logger.error("Please set your API key in the .env file")
        logger.error("Get your key from: https://makersuite.google.com/app/apikey")
        logger.error("="*60)
        sys.exit(1)
    
    # Check RSS feeds
    if not settings.rss_feed_list:
        logger.warning("No RSS feeds configured. Using defaults.")
    
    logger.info(f"✓ API Key configured")
    logger.info(f"✓ {len(settings.rss_feed_list)} RSS feeds configured")
    logger.info(f"✓ Poll interval: {settings.rss_poll_interval}s")
    logger.info(f"✓ FileWatcher directory: {settings.breaking_news_dir}")
    
    # Ensure directories exist
    Path("data/output").mkdir(parents=True, exist_ok=True)
    Path(settings.breaking_news_dir).mkdir(parents=True, exist_ok=True)
    
    logger.info("✓ Directories created")


def print_startup_banner():
    """Print ASCII art banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║          LIVE NEWS ANALYST - PATHWAY EDITION             ║
    ║                                                           ║
    ║  Real-Time RAG System for DataQuest Hackathon 2025      ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    
    🚀 Powered by: Pathway | Google Gemini | React
    
    📊 Features:
       ✓ Real-time RSS ingestion (60s polling)
       ✓ Incremental vector indexing
       ✓ Sentiment analysis ticker
       ✓ Keyword alert system
       ✓ FileWatcher for demos
    
    ⚙️  Configuration:
       • Backend Port: {port}
       • LLM Model: {model}
       • RSS Feeds: {feed_count}
       • Alert Keywords: {keyword_count}
    
    📡 Endpoints (when REST API is ready):
       • GET  /headlines  - Latest news
       • GET  /sentiment  - Sentiment data
       • POST /query      - RAG queries
       • WS   /ws         - Live updates
    
    """.format(
        port=settings.pathway_port,
        model=settings.llm_model,
        feed_count=len(settings.rss_feed_list),
        keyword_count=len(settings.alert_keyword_list)
    )
    
    print(banner)


def main():
    """Main entry point."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Print banner
        print_startup_banner()
        
        # Validate configuration
        check_environment()
        
        logger.info("Initializing pipeline...")
        
        # Create and run pipeline
        pipeline = LiveNewsAnalystPipeline()
        
        logger.info("="*60)
        logger.info("🎬 STARTING LIVE NEWS ANALYST")
        logger.info("="*60)
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
        logger.info("="*60)
        sys.exit(0)
    
    except Exception as e:
        logger.error("="*60)
        logger.error(f"❌ FATAL ERROR: {e}")
        logger.error("="*60)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
