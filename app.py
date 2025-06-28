#!/usr/bin/env python3
"""
WhatsApp Summarizer API
Flask REST API for summarizing WhatsApp group chats and generating TTS audio
"""

import os
import logging
from flask import Flask
from config import config, Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Import and register routes
    from api.routes import create_app as create_routes
    app = create_routes()
    
    return app

def main():
    """Main application entry point"""
    try:
        # Create app
        app = create_app()
        
        # Get port from environment or use default
        port = int(os.getenv('PORT', 5000))
        
        # Run app
        logger.info(f"Starting WhatsApp Summarizer API on port {port}")
        app.run(
            host='0.0.0.0',
            port=port,
            debug=Config.DEBUG
        )
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

if __name__ == '__main__':
    main() 