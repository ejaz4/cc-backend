"""
Pydantic models for FastAPI request/response validation
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

# Enums
class PlatformType(str, Enum):
    WHATSAPP = "whatsapp"
    INSTAGRAM = "instagram"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    SLACK = "slack"

class ConversationType(str, Enum):
    GROUP = "group"
    DIRECT = "direct"
    CHANNEL = "channel"

class ConversationStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    SUMMARIZED = "summarized"
    COMPLETED = "completed"
    FAILED = "failed"

class MessageType(str, Enum):
    TEXT = "text"
    MEDIA = "media"
    SYSTEM = "system"
    REACTION = "reaction"

class RelationshipType(str, Enum):
    FRIEND = "friend"
    FAMILY = "family"
    COLLEAGUE = "colleague"
    ACQUAINTANCE = "acquaintance"

class AudioStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class AssistantType(str, Enum):
    ELEVENLABS = "elevenlabs"
    CUSTOM = "custom"

# Base Models
class ConversationBase(BaseModel):
    platform: PlatformType
    group_name: str = Field(..., min_length=1, max_length=255)
    main_user: str = Field(..., min_length=1, max_length=255)
    conversation_type: ConversationType = ConversationType.GROUP
    platform_specific_data: Optional[Dict[str, Any]] = None

class MessageBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    timestamp: datetime
    message_type: MessageType = MessageType.TEXT
    is_important: bool = False
    platform_specific_data: Optional[Dict[str, Any]] = None
    reactions: Optional[List[Dict[str, Any]]] = None
    reply_to: Optional[str] = None

class UserProfileBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=255)
    platform: PlatformType
    display_name: Optional[str] = Field(None, max_length=255)
    voice_id: Optional[str] = None
    voice_name: Optional[str] = None
    profile_picture: Optional[str] = None
    is_active: bool = True
    personality_traits: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    communication_style: Optional[Dict[str, Any]] = None
    relationship_type: RelationshipType = RelationshipType.FRIEND
    trust_score: float = Field(0.5, ge=0.0, le=1.0)
    preferred_topics: Optional[List[str]] = None
    avoided_topics: Optional[List[str]] = None

class SummaryBase(BaseModel):
    summary_text: str = Field(..., min_length=1)
    script_lines: Optional[List[str]] = None
    participants: Optional[List[str]] = None
    summary_type: str = "dialogue"
    word_count: int = Field(0, ge=0)
    generated_by: str = "gpt-4"
    personality_context: Optional[Dict[str, Any]] = None
    relationship_context: Optional[Dict[str, Any]] = None
    tone_analysis: Optional[Dict[str, Any]] = None

class AudioFileBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=255)
    line_number: int = Field(..., ge=1)
    voice_id: Optional[str] = None
    voice_settings: Optional[Dict[str, Any]] = None
    emotion_context: Optional[Dict[str, Any]] = None

class AssistantSessionBase(BaseModel):
    main_user_id: int = Field(..., gt=0)
    messages: Optional[List[Dict[str, Any]]] = None
    context: Optional[Dict[str, Any]] = None
    is_active: bool = True
    assistant_type: AssistantType = AssistantType.ELEVENLABS
    user_profiles_context: Optional[Dict[str, Any]] = None
    conversation_history_context: Optional[Dict[str, Any]] = None

class CalendarEventBase(BaseModel):
    main_user_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=255)
    start_time: datetime
    end_time: Optional[datetime] = None
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=500)
    calendar_id: Optional[str] = None
    related_conversation_id: Optional[str] = None
    related_participants: Optional[List[str]] = None

# Request Models
class ConversationUploadRequest(ConversationBase):
    messages: List[MessageBase]
    date_range: Optional[Dict[str, str]] = None

class ConversationFileUploadRequest(BaseModel):
    main_user: str = Field(..., min_length=1, max_length=255)
    group_name: str = Field(..., min_length=1, max_length=255)
    conversation_type: ConversationType = ConversationType.GROUP

class SummaryRequest(BaseModel):
    include_personality: bool = True
    include_relationships: bool = True
    summary_length: str = Field("medium", pattern="^(short|medium|long)$")

class AudioGenerationRequest(BaseModel):
    voice_settings: Optional[Dict[str, Any]] = None
    include_emotions: bool = True

class UserProfileUpdateRequest(BaseModel):
    display_name: Optional[str] = Field(None, max_length=255)
    voice_id: Optional[str] = None
    voice_name: Optional[str] = None
    personality_traits: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    communication_style: Optional[Dict[str, Any]] = None
    relationship_type: Optional[RelationshipType] = None
    trust_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    preferred_topics: Optional[List[str]] = None
    avoided_topics: Optional[List[str]] = None

class AssistantChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    context: Optional[Dict[str, Any]] = None
    include_calendar: bool = False
    include_user_profiles: bool = True

class CalendarEventRequest(CalendarEventBase):
    pass

class CalendarAuthRequest(BaseModel):
    user_id: int = Field(..., gt=0)
    redirect_uri: Optional[str] = None

# Response Models
class ConversationResponse(ConversationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    session_id: str
    status: ConversationStatus
    total_messages: int
    created_at: datetime
    updated_at: datetime

class MessageResponse(MessageBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    conversation_session_id: int
    created_at: datetime

class UserProfileResponse(UserProfileBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    main_user_id: int
    frequency_score: float
    last_interaction: Optional[datetime] = None
    platform_user_id: Optional[str] = None
    platform_specific_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

class SummaryResponse(SummaryBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    conversation_session_id: int
    main_user_id: int
    created_at: datetime
    updated_at: datetime

class AudioFileResponse(AudioFileBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    conversation_session_id: int
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    duration: Optional[float] = None
    file_size: Optional[int] = None
    status: AudioStatus
    error_message: Optional[str] = None
    elevenlabs_generation_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class AssistantSessionResponse(AssistantSessionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    session_id: str
    created_at: datetime
    updated_at: datetime

class CalendarEventResponse(CalendarEventBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    google_event_id: Optional[str] = None
    status: str = "pending"
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class VoiceResponse(BaseModel):
    voice_id: str
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    labels: Optional[Dict[str, str]] = None
    preview_url: Optional[str] = None
    similarity_boost: Optional[float] = None
    stability: Optional[float] = None
    style: Optional[float] = None
    use_speaker_boost: Optional[bool] = None

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: datetime

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

class SuccessResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

# List Response Models
class ConversationListResponse(BaseModel):
    conversations: List[ConversationResponse]
    total: int
    page: int
    per_page: int

class MessageListResponse(BaseModel):
    messages: List[MessageResponse]
    total: int

class UserProfileListResponse(BaseModel):
    profiles: List[UserProfileResponse]
    total: int

class AudioFileListResponse(BaseModel):
    audio_files: List[AudioFileResponse]
    total: int

class CalendarEventListResponse(BaseModel):
    events: List[CalendarEventResponse]
    total: int

class VoiceListResponse(BaseModel):
    voices: List[VoiceResponse]
    total: int

# Utility Models
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1, le=100)

class ConversationFilters(BaseModel):
    platform: Optional[PlatformType] = None
    status: Optional[ConversationStatus] = None
    main_user: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

class UserProfileFilters(BaseModel):
    platform: Optional[PlatformType] = None
    relationship_type: Optional[RelationshipType] = None
    is_active: Optional[bool] = None
    min_trust_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_trust_score: Optional[float] = Field(None, ge=0.0, le=1.0) 