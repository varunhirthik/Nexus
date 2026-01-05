"""FileWatcher connector for demo purposes - monitors directory for new files."""

import pathway as pw
import time
import os
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileWatcherConnector(pw.io.python.ConnectorSubject):
    """
    Monitors a directory for new text files and ingests them immediately.
    
    This is the "Wizard of Oz" technique for hackathon demos - allows
    presenters to manually inject breaking news by dropping files into
    a watched directory, proving real-time capability without relying
    on external news sources during the demo.
    """
    
    def __init__(
        self,
        watch_directory: str,
        poll_interval: float = 1.0,
        auto_cleanup: bool = True
    ):
        """
        Initialize FileWatcher connector.
        
        Args:
            watch_directory: Path to directory to monitor
            poll_interval: How often to check for new files (seconds)
            auto_cleanup: Whether to delete files after ingestion
        """
        super().__init__()
        self.watch_dir = Path(watch_directory)
        self.poll_interval = poll_interval
        self.auto_cleanup = auto_cleanup
        self.processed_files = set()
        
        # Ensure directory exists
        self.watch_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"FileWatcher initialized: {watch_directory}")
        logger.info(f"Auto-cleanup: {auto_cleanup}")
    
    def run(self):
        """
        Main monitoring loop running in a separate thread.
        
        Continuously scans the directory for new .txt files and
        ingests them as breaking news articles.
        """
        logger.info("FileWatcher thread started")
        
        while True:
            try:
                # Scan for .txt files
                for file_path in self.watch_dir.glob("*.txt"):
                    # Skip if already processed
                    if file_path.name in self.processed_files:
                        continue
                    
                    logger.info(f"🔔 NEW FILE DETECTED: {file_path.name}")
                    
                    try:
                        # Read file content
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                        
                        if not content:
                            logger.warning(f"Empty file: {file_path.name}")
                            continue
                        
                        # Extract title from first line or filename
                        lines = content.split('\n', 1)
                        title = lines[0] if lines else file_path.stem
                        summary = lines[1][:200] if len(lines) > 1 else content[:200]
                        
                        # Push to Pathway
                        self.next(
                            title=title,
                            summary=summary,
                            link=f"file://{file_path.absolute()}",
                            published=datetime.now().isoformat(),
                            content=content,
                            source="FileWatcher"
                        )
                        
                        # Immediate commit for instant visibility
                        self.commit()
                        
                        logger.info(f"✓ Ingested: {title[:50]}...")
                        
                        # Mark as processed
                        self.processed_files.add(file_path.name)
                        
                        # Cleanup if enabled
                        if self.auto_cleanup:
                            file_path.unlink()
                            logger.info(f"  Cleaned up: {file_path.name}")
                    
                    except Exception as e:
                        logger.error(f"Failed to process {file_path.name}: {e}")
            
            except Exception as e:
                logger.error(f"FileWatcher error: {e}")
            
            # Short polling interval for responsive demos
            time.sleep(self.poll_interval)
