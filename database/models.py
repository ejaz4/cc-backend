"""
Database table schemas and field definitions for Supabase.
These are documentation stubs - actual table operations use the Supabase SDK.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass

# Type aliases for common field types
JsonField = Dict[str, Any]
DateTimeField = datetime
StringField = str
IntegerField = int
BooleanField = bool
FloatField = float

@dataclass
class ConversationSession:
    """
    conversation_sessions table
    
    Fields:
        id: Integer (Primary Key, Auto-increment)
        session_id: String(36) (Unique, UUID)
        platform: String(50) (Required) - whatsapp, instagram, discord, etc.
        group_name: String(255) (Required)
        main_user: String(255) (Required)
        status: String(50) (Default: 'uploaded') - uploaded, processing, summarized, completed
        file_path: String(500) (Optional)
        total_messages: Integer (Default: 0)
        conversation_type: String(50) (Default: 'group') - group, direct, channel
        platform_specific_data: JSON (Optional)
        date_range: JSON (Optional) - start_date, end_date
        created_at: DateTime (Default: now)
        updated_at: DateTime (Default: now, Auto-update)
    """
    id: Optional[IntegerField] = None
    session_id: Optional[StringField] = None
    platform: Optional[StringField] = None
    group_name: Optional[StringField] = None
    main_user: Optional[StringField] = None
    status: Optional[StringField] = None
    file_path: Optional[StringField] = None
    total_messages: Optional[IntegerField] = None
    conversation_type: Optional[StringField] = None
    platform_specific_data: Optional[JsonField] = None
    date_range: Optional[JsonField] = None
    created_at: Optional[DateTimeField] = None
    updated_at: Optional[DateTimeField] = None

@dataclass
class PlatformMessage:
    """
    platform_messages table
    
    Fields:
        id: Integer (Primary Key, Auto-increment)
        conversation_session_id: Integer (Foreign Key to conversation_sessions.id)
        username: String(255) (Required)
        content: Text (Required)
        timestamp: DateTime (Required)
        message_type: String(50) (Default: 'text') - text, media, system, reaction
        is_important: Boolean (Default: False)
        platform_specific_data: JSON (Optional) - Platform-specific metadata
        reactions: JSON (Optional) - For platforms with reactions
        reply_to: String(255) (Optional) - For threaded conversations
        created_at: DateTime (Default: now)
    """
    id: Optional[IntegerField] = None
    conversation_session_id: Optional[IntegerField] = None
    username: Optional[StringField] = None
    content: Optional[StringField] = None
    timestamp: Optional[DateTimeField] = None
    message_type: Optional[StringField] = None
    is_important: Optional[BooleanField] = None
    platform_specific_data: Optional[JsonField] = None
    reactions: Optional[JsonField] = None
    reply_to: Optional[StringField] = None
    created_at: Optional[DateTimeField] = None

@dataclass
class MainUser:
    """
    main_users table
    
    Fields:
        id: Integer (Primary Key, Auto-increment)
        username: String(255) (Unique, Required)
        email: String(255) (Unique, Required)
        voice_id: String(255) (Optional) - ElevenLabs voice ID
        voice_name: String(255) (Optional)
        is_active: Boolean (Default: True)
        preferences: JSON (Optional)
        connected_platforms: JSON (Optional) - List of platforms they use
        platform_credentials: JSON (Optional) - Encrypted platform tokens
        default_voice_settings: JSON (Optional)
        summary_preferences: JSON (Optional)
        privacy_settings: JSON (Optional)
        created_at: DateTime (Default: now)
        updated_at: DateTime (Default: now, Auto-update)
    """
    id: Optional[IntegerField] = None
    username: Optional[StringField] = None
    email: Optional[StringField] = None
    voice_id: Optional[StringField] = None
    voice_name: Optional[StringField] = None
    is_active: Optional[BooleanField] = None
    preferences: Optional[JsonField] = None
    connected_platforms: Optional[JsonField] = None
    platform_credentials: Optional[JsonField] = None
    default_voice_settings: Optional[JsonField] = None
    summary_preferences: Optional[JsonField] = None
    privacy_settings: Optional[JsonField] = None
    created_at: Optional[DateTimeField] = None
    updated_at: Optional[DateTimeField] = None

@dataclass
class UserProfile:
    """
    user_profiles table
    
    Fields:
        id: Integer (Primary Key, Auto-increment)
        username: String(255) (Required)
        platform: String(50) (Required)
        main_user_id: Integer (Foreign Key to main_users.id)
        display_name: String(255) (Optional)
        voice_id: String(255) (Optional) - ElevenLabs voice ID
        voice_name: String(255) (Optional)
        profile_picture: String(500) (Optional)
        is_active: Boolean (Default: True)
        personality_traits: JSON (Optional) - friendly, professional, etc.
        interests: JSON (Optional) - topics they talk about
        communication_style: JSON (Optional) - formal, casual, emoji_heavy, etc.
        frequency_score: Float (Default: 0.0) - How often they interact
        last_interaction: DateTime (Optional)
        platform_user_id: String(255) (Optional) - Platform's internal user ID
        platform_specific_data: JSON (Optional)
        relationship_type: String(50) (Default: 'friend') - friend, family, colleague, etc.
        trust_score: Float (Default: 0.5) - 0-1 scale
        preferred_topics: JSON (Optional)
        avoided_topics: JSON (Optional)
        created_at: DateTime (Default: now)
        updated_at: DateTime (Default: now, Auto-update)
    """
    id: Optional[IntegerField] = None
    username: Optional[StringField] = None
    platform: Optional[StringField] = None
    main_user_id: Optional[IntegerField] = None
    display_name: Optional[StringField] = None
    voice_id: Optional[StringField] = None
    voice_name: Optional[StringField] = None
    profile_picture: Optional[StringField] = None
    is_active: Optional[BooleanField] = None
    personality_traits: Optional[JsonField] = None
    interests: Optional[JsonField] = None
    communication_style: Optional[JsonField] = None
    frequency_score: Optional[FloatField] = None
    last_interaction: Optional[DateTimeField] = None
    platform_user_id: Optional[StringField] = None
    platform_specific_data: Optional[JsonField] = None
    relationship_type: Optional[StringField] = None
    trust_score: Optional[FloatField] = None
    preferred_topics: Optional[JsonField] = None
    avoided_topics: Optional[JsonField] = None
    created_at: Optional[DateTimeField] = None
    updated_at: Optional[DateTimeField] = None

@dataclass
class Summary:
    """
    summaries table
    
    Fields:
        id: Integer (Primary Key, Auto-increment)
        conversation_session_id: Integer (Foreign Key to conversation_sessions.id)
        main_user_id: Integer (Foreign Key to main_users.id)
        summary_text: Text (Required)
        script_lines: JSON (Optional) - List of dialogue lines
        participants: JSON (Optional)
        summary_type: String(50) (Default: 'dialogue') - dialogue, bullet_points, etc.
        word_count: Integer (Default: 0)
        generated_by: String(50) (Default: 'gpt-4')
        personality_context: JSON (Optional) - How personalities influenced summary
        relationship_context: JSON (Optional) - Relationship dynamics
        tone_analysis: JSON (Optional) - Overall conversation tone
        created_at: DateTime (Default: now)
        updated_at: DateTime (Default: now, Auto-update)
    """
    id: Optional[IntegerField] = None
    conversation_session_id: Optional[IntegerField] = None
    main_user_id: Optional[IntegerField] = None
    summary_text: Optional[StringField] = None
    script_lines: Optional[JsonField] = None
    participants: Optional[JsonField] = None
    summary_type: Optional[StringField] = None
    word_count: Optional[IntegerField] = None
    generated_by: Optional[StringField] = None
    personality_context: Optional[JsonField] = None
    relationship_context: Optional[JsonField] = None
    tone_analysis: Optional[JsonField] = None
    created_at: Optional[DateTimeField] = None
    updated_at: Optional[DateTimeField] = None

@dataclass
class AudioFile:
    """
    audio_files table
    
    Fields:
        id: Integer (Primary Key, Auto-increment)
        conversation_session_id: Integer (Foreign Key to conversation_sessions.id)
        username: String(255) (Required)
        line_number: Integer (Required)
        file_path: String(500) (Optional)
        file_name: String(255) (Optional)
        voice_id: String(255) (Optional)
        duration: Float (Optional) - in seconds
        file_size: Integer (Optional) - in bytes
        status: String(50) (Default: 'pending') - pending, processing, completed, failed
        error_message: Text (Optional)
        elevenlabs_generation_id: String(255) (Optional)
        voice_settings: JSON (Optional) - Custom voice settings based on personality
        emotion_context: JSON (Optional) - Emotional context for voice generation
        created_at: DateTime (Default: now)
        updated_at: DateTime (Default: now, Auto-update)
    """
    id: Optional[IntegerField] = None
    conversation_session_id: Optional[IntegerField] = None
    username: Optional[StringField] = None
    line_number: Optional[IntegerField] = None
    file_path: Optional[StringField] = None
    file_name: Optional[StringField] = None
    voice_id: Optional[StringField] = None
    duration: Optional[FloatField] = None
    file_size: Optional[IntegerField] = None
    status: Optional[StringField] = None
    error_message: Optional[StringField] = None
    elevenlabs_generation_id: Optional[StringField] = None
    voice_settings: Optional[JsonField] = None
    emotion_context: Optional[JsonField] = None
    created_at: Optional[DateTimeField] = None
    updated_at: Optional[DateTimeField] = None

@dataclass
class AssistantSession:
    """
    assistant_sessions table
    
    Fields:
        id: Integer (Primary Key, Auto-increment)
        session_id: String(36) (Unique, UUID)
        main_user_id: Integer (Foreign Key to main_users.id)
        messages: JSON (Optional) - Array of message objects
        context: JSON (Optional) - Calendar events, user preferences, etc.
        is_active: Boolean (Default: True)
        assistant_type: String(50) (Default: 'elevenlabs') - elevenlabs, custom
        user_profiles_context: JSON (Optional) - Relevant user profiles
        conversation_history_context: JSON (Optional) - Recent conversations
        created_at: DateTime (Default: now)
        updated_at: DateTime (Default: now, Auto-update)
    """
    id: Optional[IntegerField] = None
    session_id: Optional[StringField] = None
    main_user_id: Optional[IntegerField] = None
    messages: Optional[JsonField] = None
    context: Optional[JsonField] = None
    is_active: Optional[BooleanField] = None
    assistant_type: Optional[StringField] = None
    user_profiles_context: Optional[JsonField] = None
    conversation_history_context: Optional[JsonField] = None
    created_at: Optional[DateTimeField] = None
    updated_at: Optional[DateTimeField] = None

@dataclass
class CalendarEvent:
    """
    calendar_events table
    
    Fields:
        id: Integer (Primary Key, Auto-increment)
        main_user_id: Integer (Foreign Key to main_users.id)
        title: String(255) (Required)
        start_time: DateTime (Required)
        end_time: DateTime (Optional)
        description: Text (Optional)
        location: String(500) (Optional)
        calendar_id: String(255) (Optional) - Google Calendar ID
        google_event_id: String(255) (Optional)
        status: String(50) (Default: 'pending') - pending, created, failed
        error_message: Text (Optional)
        related_conversation_id: String(36) (Optional)
        related_participants: JSON (Optional)
        created_at: DateTime (Default: now)
        updated_at: DateTime (Default: now, Auto-update)
    """
    id: Optional[IntegerField] = None
    main_user_id: Optional[IntegerField] = None
    title: Optional[StringField] = None
    start_time: Optional[DateTimeField] = None
    end_time: Optional[DateTimeField] = None
    description: Optional[StringField] = None
    location: Optional[StringField] = None
    calendar_id: Optional[StringField] = None
    google_event_id: Optional[StringField] = None
    status: Optional[StringField] = None
    error_message: Optional[StringField] = None
    related_conversation_id: Optional[StringField] = None
    related_participants: Optional[JsonField] = None
    created_at: Optional[DateTimeField] = None
    updated_at: Optional[DateTimeField] = None

@dataclass
class PlatformIntegration:
    """
    platform_integrations table
    
    Fields:
        id: Integer (Primary Key, Auto-increment)
        platform: String(50) (Required) - whatsapp, instagram, discord, etc.
        main_user_id: Integer (Foreign Key to main_users.id)
        is_connected: Boolean (Default: False)
        credentials: JSON (Optional) - Encrypted platform credentials
        settings: JSON (Optional) - Platform-specific settings
        last_sync: DateTime (Optional)
        sync_frequency: String(50) (Default: 'manual') - manual, daily, weekly
        permissions: JSON (Optional) - What data we can access
        created_at: DateTime (Default: now)
        updated_at: DateTime (Default: now, Auto-update)
    """
    id: Optional[IntegerField] = None
    platform: Optional[StringField] = None
    main_user_id: Optional[IntegerField] = None
    is_connected: Optional[BooleanField] = None
    credentials: Optional[JsonField] = None
    settings: Optional[JsonField] = None
    last_sync: Optional[DateTimeField] = None
    sync_frequency: Optional[StringField] = None
    permissions: Optional[JsonField] = None
    created_at: Optional[DateTimeField] = None
    updated_at: Optional[DateTimeField] = None 