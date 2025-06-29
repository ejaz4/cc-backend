#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///
"""
Main entry point for the FastAPI application
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import app
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main application entry point"""
    try:
        # Validate configuration
        Config.validate_config()
        logger.info("Configuration validated successfully")
        
        # Get configuration
        host = Config.HOST
        port = Config.PORT
        debug = Config.DEBUG
        
        logger.info(f"Starting FastAPI application on {host}:{port}")
        logger.info(f"Debug mode: {debug}")
        logger.info(f"API documentation available at: http://{host}:{port}/docs")
        
        # Import uvicorn here to avoid issues with multiprocessing
        import uvicorn
        
        # Run the application
        uvicorn.run(
            "app:app",
            host=host,
            port=port,
            reload=debug,
            log_level="info" if not debug else "debug"
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
