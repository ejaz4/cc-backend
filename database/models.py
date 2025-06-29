from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .connection import Base

class ConversationSession(Base):
    """Generic conversation session model for any platform"""
    __tablename__ = 'conversation_sessions'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    platform = Column(String(50), nullable=False)  # whatsapp, instagram, discord, etc.
    group_name = Column(String(255), nullable=False)
    main_user = Column(String(255), nullable=False)
    status = Column(String(50), default='uploaded')  # uploaded, processing, summarized, completed
    file_path = Column(String(500))
    total_messages = Column(Integer, default=0)
    conversation_type = Column(String(50), default='group')  # group, direct, channel
    platform_specific_data = Column(JSON)
    date_range = Column(JSON)  # start_date, end_date
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = relationship("PlatformMessage", back_populates="conversation_session", cascade="all, delete-orphan")
    summary = relationship("Summary", back_populates="conversation_session", uselist=False, cascade="all, delete-orphan")
    audio_files = relationship("AudioFile", back_populates="conversation_session", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_session_id', 'session_id'),
        Index('idx_platform_main_user', 'platform', 'main_user'),
        Index('idx_status', 'status'),
        Index('idx_created_at', 'created_at'),
    )

class PlatformMessage(Base):
    """Generic message model for any platform"""
    __tablename__ = 'platform_messages'
    
    id = Column(Integer, primary_key=True)
    conversation_session_id = Column(Integer, ForeignKey('conversation_sessions.id'), nullable=False)
    username = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    message_type = Column(String(50), default='text')  # text, media, system, reaction
    is_important = Column(Boolean, default=False)
    platform_specific_data = Column(JSON)  # Platform-specific metadata
    reactions = Column(JSON)  # For platforms with reactions
    reply_to = Column(String(255))  # For threaded conversations
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation_session = relationship("ConversationSession", back_populates="messages")
    
    # Indexes
    __table_args__ = (
        Index('idx_conversation_session_id', 'conversation_session_id'),
        Index('idx_username', 'username'),
        Index('idx_timestamp', 'timestamp'),
        Index('idx_is_important', 'is_important'),
    )

class MainUser(Base):
    """Main user (app owner) model"""
    __tablename__ = 'main_users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    voice_id = Column(String(255))  # ElevenLabs voice ID
    voice_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    preferences = Column(JSON)
    connected_platforms = Column(JSON)  # List of platforms they use
    platform_credentials = Column(JSON)  # Encrypted platform tokens
    default_voice_settings = Column(JSON)
    summary_preferences = Column(JSON)
    privacy_settings = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conversation_sessions = relationship("ConversationSession", backref="main_user_obj")
    user_profiles = relationship("UserProfile", back_populates="main_user_obj")
    assistant_sessions = relationship("AssistantSession", back_populates="main_user_obj")
    calendar_events = relationship("CalendarEvent", back_populates="main_user_obj")
    platform_integrations = relationship("PlatformIntegration", back_populates="main_user_obj")
    
    # Indexes
    __table_args__ = (
        Index('idx_username', 'username'),
        Index('idx_email', 'email'),
        Index('idx_is_active', 'is_active'),
    )

class UserProfile(Base):
    """User profile for people the main user talks to"""
    __tablename__ = 'user_profiles'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False)
    platform = Column(String(50), nullable=False)
    main_user_id = Column(Integer, ForeignKey('main_users.id'), nullable=False)
    display_name = Column(String(255))
    voice_id = Column(String(255))  # ElevenLabs voice ID
    voice_name = Column(String(255))
    profile_picture = Column(String(500))
    is_active = Column(Boolean, default=True)
    
    # Personality and context data
    personality_traits = Column(JSON)  # friendly, professional, etc.
    interests = Column(JSON)  # topics they talk about
    communication_style = Column(JSON)  # formal, casual, emoji_heavy, etc.
    frequency_score = Column(Float, default=0.0)  # How often they interact
    last_interaction = Column(DateTime)
    
    # Platform-specific data
    platform_user_id = Column(String(255))  # Platform's internal user ID
    platform_specific_data = Column(JSON)
    
    # Relationship context
    relationship_type = Column(String(50), default='friend')  # friend, family, colleague, etc.
    trust_score = Column(Float, default=0.5)  # 0-1 scale
    preferred_topics = Column(JSON)
    avoided_topics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    main_user_obj = relationship("MainUser", back_populates="user_profiles")
    
    # Indexes
    __table_args__ = (
        Index('idx_username_platform_main_user', 'username', 'platform', 'main_user_id'),
        Index('idx_main_user_id', 'main_user_id'),
        Index('idx_platform', 'platform'),
        Index('idx_relationship_type', 'relationship_type'),
        Index('idx_frequency_score', 'frequency_score'),
        Index('idx_trust_score', 'trust_score'),
    )

class Summary(Base):
    """Chat summary model"""
    __tablename__ = 'summaries'
    
    id = Column(Integer, primary_key=True)
    conversation_session_id = Column(Integer, ForeignKey('conversation_sessions.id'), nullable=False)
    main_user_id = Column(Integer, ForeignKey('main_users.id'), nullable=False)
    summary_text = Column(Text, nullable=False)
    script_lines = Column(JSON)  # List of dialogue lines
    participants = Column(JSON)
    summary_type = Column(String(50), default='dialogue')  # dialogue, bullet_points, etc.
    word_count = Column(Integer, default=0)
    generated_by = Column(String(50), default='gpt-4')
    
    # Context and personality data
    personality_context = Column(JSON)  # How personalities influenced summary
    relationship_context = Column(JSON)  # Relationship dynamics
    tone_analysis = Column(JSON)  # Overall conversation tone
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conversation_session = relationship("ConversationSession", back_populates="summary")
    main_user_obj = relationship("MainUser")
    
    # Indexes
    __table_args__ = (
        Index('idx_conversation_session_id', 'conversation_session_id'),
        Index('idx_main_user_id', 'main_user_id'),
        Index('idx_created_at', 'created_at'),
    )

class AudioFile(Base):
    """Audio file model for generated TTS"""
    __tablename__ = 'audio_files'
    
    id = Column(Integer, primary_key=True)
    conversation_session_id = Column(Integer, ForeignKey('conversation_sessions.id'), nullable=False)
    username = Column(String(255), nullable=False)
    line_number = Column(Integer, nullable=False)
    file_path = Column(String(500))
    file_name = Column(String(255))
    voice_id = Column(String(255))
    duration = Column(Float)  # in seconds
    file_size = Column(Integer)  # in bytes
    status = Column(String(50), default='pending')  # pending, processing, completed, failed
    error_message = Column(Text)
    elevenlabs_generation_id = Column(String(255))
    
    # Personality-based voice settings
    voice_settings = Column(JSON)  # Custom voice settings based on personality
    emotion_context = Column(JSON)  # Emotional context for voice generation
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conversation_session = relationship("ConversationSession", back_populates="audio_files")
    
    # Indexes
    __table_args__ = (
        Index('idx_conversation_session_id', 'conversation_session_id'),
        Index('idx_username', 'username'),
        Index('idx_status', 'status'),
        Index('idx_voice_id', 'voice_id'),
    )

class AssistantSession(Base):
    """Assistant conversation session model"""
    __tablename__ = 'assistant_sessions'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    main_user_id = Column(Integer, ForeignKey('main_users.id'), nullable=False)
    messages = Column(JSON)  # Array of message objects
    context = Column(JSON)  # Calendar events, user preferences, etc.
    is_active = Column(Boolean, default=True)
    assistant_type = Column(String(50), default='elevenlabs')  # elevenlabs, custom
    
    # User profile context
    user_profiles_context = Column(JSON)  # Relevant user profiles
    conversation_history_context = Column(JSON)  # Recent conversations
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    main_user_obj = relationship("MainUser", back_populates="assistant_sessions")
    
    # Indexes
    __table_args__ = (
        Index('idx_session_id', 'session_id'),
        Index('idx_main_user_id', 'main_user_id'),
        Index('idx_is_active', 'is_active'),
    )

class CalendarEvent(Base):
    """Calendar event model for assistant integration"""
    __tablename__ = 'calendar_events'
    
    id = Column(Integer, primary_key=True)
    main_user_id = Column(Integer, ForeignKey('main_users.id'), nullable=False)
    title = Column(String(255), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    description = Column(Text)
    location = Column(String(500))
    calendar_id = Column(String(255))  # Google Calendar ID
    google_event_id = Column(String(255))
    status = Column(String(50), default='pending')  # pending, created, failed
    error_message = Column(Text)
    
    # Related to conversation context
    related_conversation_id = Column(String(36))
    related_participants = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    main_user_obj = relationship("MainUser", back_populates="calendar_events")
    
    # Indexes
    __table_args__ = (
        Index('idx_main_user_id', 'main_user_id'),
        Index('idx_start_time', 'start_time'),
        Index('idx_status', 'status'),
        Index('idx_google_event_id', 'google_event_id'),
    )

class PlatformIntegration(Base):
    """Platform integration settings and credentials"""
    __tablename__ = 'platform_integrations'
    
    id = Column(Integer, primary_key=True)
    platform = Column(String(50), nullable=False)  # whatsapp, instagram, discord, etc.
    main_user_id = Column(Integer, ForeignKey('main_users.id'), nullable=False)
    is_connected = Column(Boolean, default=False)
    credentials = Column(JSON)  # Encrypted platform credentials
    settings = Column(JSON)  # Platform-specific settings
    last_sync = Column(DateTime)
    sync_frequency = Column(String(50), default='manual')  # manual, daily, weekly
    permissions = Column(JSON)  # What data we can access
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    main_user_obj = relationship("MainUser", back_populates="platform_integrations")
    
    # Indexes
    __table_args__ = (
        Index('idx_platform_main_user', 'platform', 'main_user_id'),
        Index('idx_is_connected', 'is_connected'),
        Index('idx_last_sync', 'last_sync'),
    ) 