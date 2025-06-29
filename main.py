import os
import logging
from flask import Flask
from dotenv import load_dotenv

from config import Config
from database.connection import init_database, create_tables, check_connection
from api.routes import create_app

# Load environment variables
load_dotenv()

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
        
        # Initialize database
        init_database()
        logger.info("Database initialized successfully")
        
        # Create tables if they don't exist
        create_tables()
        logger.info("Database tables created/verified successfully")
        
        # Test database connection
        if check_connection():
            logger.info("Database connection test successful")
        else:
            logger.error("Database connection test failed")
            return
        
        # Create Flask app
        app = create_app()
        
        # Create necessary directories
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.AUDIO_FOLDER, exist_ok=True)
        
        # Run the application
        host = os.getenv('FLASK_HOST', '0.0.0.0')
        port = int(os.getenv('FLASK_PORT', 5000))
        debug = Config.DEBUG
        
        logger.info(f"Starting application on {host}:{port}")
        app.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

if __name__ == '__main__':
    main() 