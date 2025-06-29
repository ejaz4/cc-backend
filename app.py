"""
FastAPI application for Multi-Platform Conversation Summarizer
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from config import Config
from database.connection import init_database, check_connection
from api.routers import (
    conversations,
    users,
    assistant,
    audio,
    voices
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting up Multi-Platform Conversation Summarizer API...")
    
    # Validate configuration
    try:
        Config.validate_config()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        raise
    
    # Initialize database
    try:
        init_database()
        logger.info("Supabase database connection initialized successfully")
        
        if check_connection():
            logger.info("Supabase database connection test successful")
        else:
            logger.error("Supabase database connection test failed")
            raise Exception("Database connection failed")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    # Create necessary directories
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.AUDIO_FOLDER, exist_ok=True)
    logger.info("Application directories created")
    
    logger.info("Application startup completed successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Multi-Platform Conversation Summarizer API...")

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    # Create FastAPI app
    app = FastAPI(
        title="Multi-Platform Conversation Summarizer API",
        description="API for processing and summarizing conversations from multiple platforms",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add trusted host middleware for production
    if not Config.DEBUG:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configure appropriately for production
        )
    
    # Include routers
    app.include_router(
        conversations.router,
        prefix="/api/conversations",
        tags=["conversations"]
    )
    
    app.include_router(
        users.router,
        prefix="/api/users",
        tags=["users"]
    )
    
    app.include_router(
        assistant.router,
        prefix="/api/assistant",
        tags=["assistant"]
    )
    
    app.include_router(
        audio.router,
        prefix="/api/audio",
        tags=["audio"]
    )
    
    app.include_router(
        voices.router,
        prefix="/api/voices",
        tags=["voices"]
    )
    
    # Health check endpoint
    @app.get("/api/health", tags=["health"])
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "Multi-Platform Conversation Summarizer API",
            "version": "1.0.0"
        }
    
    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        """Root endpoint"""
        return {
            "message": "Multi-Platform Conversation Summarizer API",
            "docs": "/docs",
            "health": "/api/health"
        }
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler"""
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(exc)}
        )
    
    # 404 handler
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: Exception):
        """404 handler"""
        return JSONResponse(
            status_code=404,
            content={"error": "Not found", "detail": "The requested resource was not found"}
        )
    
    return app

# Create the app instance
app = create_app()

if __name__ == "__main__":
    # Run the application
    host = os.getenv('FASTAPI_HOST', '0.0.0.0')
    port = int(os.getenv('FASTAPI_PORT', 8000))
    reload = Config.DEBUG
    
    logger.info(f"Starting FastAPI application on {host}:{port}")
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    ) 