"""
Database package initialization for Supabase integration.
"""

from .supabase import get_supabase_client
from .connection import init_database, check_connection, get_current_timestamp
from .repository import (
    ConversationSessionRepository,
    PlatformMessageRepository,
    MainUserRepository,
    UserProfileRepository,
    SummaryRepository,
    AudioFileRepository,
    AssistantSessionRepository,
    CalendarEventRepository,
    PlatformIntegrationRepository
)
from .migrations import DatabaseMigrator, run_migration

__all__ = [
    'get_supabase_client',
    'init_database',
    'check_connection',
    'get_current_timestamp',
    'ConversationSessionRepository',
    'PlatformMessageRepository',
    'MainUserRepository',
    'UserProfileRepository',
    'SummaryRepository',
    'AudioFileRepository',
    'AssistantSessionRepository',
    'CalendarEventRepository',
    'PlatformIntegrationRepository',
    'DatabaseMigrator',
    'run_migration'
] 