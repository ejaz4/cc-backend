"""
Dependency injection for FastAPI
"""

from typing import Generator
from fastapi import Depends

from database.repository import (
    ConversationSessionRepository,
    MainUserRepository,
    SummaryRepository,
    AudioFileRepository,
    AssistantSessionRepository,
    CalendarEventRepository,
    UserProfileRepository,
    PlatformIntegrationRepository
)
from services.whatsapp_parser import WhatsAppParser
from services.summarizer import ChatSummarizer
from services.elevenlabs_service import ElevenLabsService
from services.assistant_service import AssistantService
from services.conversation_processor import ConversationProcessor

# Repository Dependencies
def get_conversation_repository() -> ConversationSessionRepository:
    """Get conversation session repository"""
    return ConversationSessionRepository()

def get_main_user_repository() -> MainUserRepository:
    """Get main user repository"""
    return MainUserRepository()

def get_summary_repository() -> SummaryRepository:
    """Get summary repository"""
    return SummaryRepository()

def get_audio_repository() -> AudioFileRepository:
    """Get audio file repository"""
    return AudioFileRepository()

def get_assistant_repository() -> AssistantSessionRepository:
    """Get assistant session repository"""
    return AssistantSessionRepository()

def get_calendar_repository() -> CalendarEventRepository:
    """Get calendar event repository"""
    return CalendarEventRepository()

def get_user_profile_repository() -> UserProfileRepository:
    """Get user profile repository"""
    return UserProfileRepository()

def get_platform_integration_repository() -> PlatformIntegrationRepository:
    """Get platform integration repository"""
    return PlatformIntegrationRepository()

# Service Dependencies
def get_whatsapp_parser() -> WhatsAppParser:
    """Get WhatsApp parser service"""
    return WhatsAppParser()

def get_summarizer() -> ChatSummarizer:
    """Get chat summarizer service"""
    return ChatSummarizer()

def get_elevenlabs_service() -> ElevenLabsService:
    """Get ElevenLabs service"""
    return ElevenLabsService()

def get_assistant_service() -> AssistantService:
    """Get assistant service"""
    return AssistantService()

def get_conversation_processor() -> ConversationProcessor:
    """Get conversation processor service"""
    return ConversationProcessor()

# Type aliases for cleaner dependency injection
ConversationRepo = Depends(get_conversation_repository)
MainUserRepo = Depends(get_main_user_repository)
SummaryRepo = Depends(get_summary_repository)
AudioRepo = Depends(get_audio_repository)
AssistantRepo = Depends(get_assistant_repository)
CalendarRepo = Depends(get_calendar_repository)
UserProfileRepo = Depends(get_user_profile_repository)
PlatformIntegrationRepo = Depends(get_platform_integration_repository)

WhatsAppParserService = Depends(get_whatsapp_parser)
SummarizerService = Depends(get_summarizer)
ElevenLabsService = Depends(get_elevenlabs_service)
AssistantService = Depends(get_assistant_service)
ConversationProcessorService = Depends(get_conversation_processor) 