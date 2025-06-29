"""
Supabase database connection and utility functions.
Replaces SQLAlchemy connection logic with Supabase SDK.
"""

import logging
from typing import Optional
from datetime import datetime

from .supabase import get_supabase_client

logger = logging.getLogger(__name__)

def init_database():
    """Initialize Supabase connection"""
    try:
        # Test connection by making a simple query
        supabase = get_supabase_client()
        response = supabase.table("conversation_sessions").select("id").limit(1).execute()
        logger.info("Supabase connection established successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Supabase: {e}")
        raise

def check_connection() -> bool:
    """Check if Supabase connection is working"""
    try:
        supabase = get_supabase_client()
        response = supabase.table("conversation_sessions").select("id").limit(1).execute()
        return True
    except Exception as e:
        logger.error(f"Supabase connection check failed: {e}")
        return False

def get_current_timestamp() -> str:
    """Get current timestamp in ISO format for Supabase"""
    return datetime.utcnow().isoformat()

# Legacy function stubs for compatibility (these are no-ops with Supabase)
def create_tables():
    """Tables are created via Supabase dashboard or SQL migrations"""
    logger.info("Tables should be created via Supabase dashboard or SQL migrations")
    return True

def drop_tables():
    """Tables should be dropped via Supabase dashboard or SQL"""
    logger.warning("Tables should be dropped via Supabase dashboard or SQL")
    return True

# Note: Session management is not needed with Supabase SDK
# The client handles connection pooling automatically 