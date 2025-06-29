"""
Supabase client configuration and management
"""

import logging
from typing import Optional
from supabase import create_client, Client

from config import Config

logger = logging.getLogger(__name__)

# Global Supabase client instance
_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """
    Get the Supabase client instance.
    
    Returns:
        Client: Configured Supabase client
        
    Raises:
        ValueError: If Supabase configuration is missing
    """
    global _supabase_client
    
    if _supabase_client is None:
        _supabase_client = _create_supabase_client()
    
    return _supabase_client

def _create_supabase_client() -> Client:
    """
    Create and configure a new Supabase client.
    
    Returns:
        Client: Configured Supabase client
        
    Raises:
        ValueError: If Supabase configuration is missing
    """
    # Get configuration from Config class
    supabase_url = Config.SUPABASE_URI
    supabase_key = Config.SUPABASE_API_KEY
    
    # Validate configuration
    if not supabase_url:
        raise ValueError("SUPABASE_URI environment variable is required")
    
    if not supabase_key:
        raise ValueError("SUPABASE_API_KEY environment variable is required")
    
    try:
        # Create Supabase client
        client = create_client(supabase_url=supabase_url, supabase_key=supabase_key)
        
        # Test the connection
        logger.info("Supabase client created successfully")
        
        return client
        
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        raise ValueError(f"Failed to initialize Supabase client: {e}")

def reset_supabase_client():
    """
    Reset the global Supabase client instance.
    Useful for testing or when configuration changes.
    """
    global _supabase_client
    _supabase_client = None
    logger.info("Supabase client reset")

def test_supabase_connection() -> bool:
    """
    Test the Supabase connection.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        client = get_supabase_client()
        
        # Simple test query to verify connection
        # This will fail if the connection is not working
        response = client.table("conversation_sessions").select("id").limit(1).execute()
        
        logger.info("Supabase connection test successful")
        return True
        
    except Exception as e:
        logger.error(f"Supabase connection test failed: {e}")
        return False

# Example usage (keeping for reference)
# def example_query():
#     """Example of how to use the Supabase client"""
#     try:
#         client = get_supabase_client()
#         response = (
#             client.table("conversation_sessions")
#             .select("*")
#             .limit(10)
#             .execute()
#         )
#         return response.data
#     except Exception as e:
#         logger.error(f"Example query failed: {e}")
#         return None