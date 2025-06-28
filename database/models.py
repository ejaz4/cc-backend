from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId
import uuid

class BaseModel:
    """Base model with common fields"""
    
    def __init__(self, **kwargs):
        self._id = kwargs.get('_id')
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        data = {
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        if self._id:
            data['_id'] = self._id
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create model from dictionary"""
        return cls(**data)

class PlatformMessage(BaseModel):
    """Generic message model for any platform"""
    
    def __init__(self, username: str, content: str, timestamp: datetime, **kwargs):
        super().__init__(**kwargs)
        self.username = username
        self.content = content
        self.timestamp = timestamp
        self.message_type = kwargs.get('message_type', 'text')  # text, media, system, reaction
        self.is_important = kwargs.get('is_important', False)
        self.platform_specific_data = kwargs.get('platform_specific_data', {})  # Platform-specific metadata
        self.reactions = kwargs.get('reactions', [])  # For platforms with reactions
        self.reply_to = kwargs.get('reply_to')  # For threaded conversations
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'username': self.username,
            'content': self.content,
            'timestamp': self.timestamp,
            'message_type': self.message_type,
            'is_important': self.is_important,
            'platform_specific_data': self.platform_specific_data,
            'reactions': self.reactions,
            'reply_to': self.reply_to
        })
        return data

class ConversationSession(BaseModel):
    """Generic conversation session model for any platform"""
    
    def __init__(self, platform: str, group_name: str, main_user: str, **kwargs):
        super().__init__(**kwargs)
        self.platform = platform  # whatsapp, instagram, discord, etc.
        self.group_name = group_name
        self.main_user = main_user  # The user who uploaded/owns this conversation
        self.session_id = kwargs.get('session_id', str(uuid.uuid4()))
        self.messages = kwargs.get('messages', [])
        self.participants = kwargs.get('participants', [])
        self.status = kwargs.get('status', 'uploaded')  # uploaded, processing, summarized, completed
        self.file_path = kwargs.get('file_path')
        self.total_messages = kwargs.get('total_messages', 0)
        self.date_range = kwargs.get('date_range', {})  # start_date, end_date
        self.platform_specific_data = kwargs.get('platform_specific_data', {})  # Platform-specific metadata
        self.conversation_type = kwargs.get('conversation_type', 'group')  # group, direct, channel
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'platform': self.platform,
            'group_name': self.group_name,
            'main_user': self.main_user,
            'session_id': self.session_id,
            'messages': self.messages,
            'participants': self.participants,
            'status': self.status,
            'file_path': self.file_path,
            'total_messages': self.total_messages,
            'date_range': self.date_range,
            'platform_specific_data': self.platform_specific_data,
            'conversation_type': self.conversation_type
        })
        return data

class UserProfile(BaseModel):
    """User profile for people the main user talks to"""
    
    def __init__(self, username: str, platform: str, main_user: str, **kwargs):
        super().__init__(**kwargs)
        self.username = username
        self.platform = platform
        self.main_user = main_user  # The user who owns this profile
        self.display_name = kwargs.get('display_name', username)
        self.voice_id = kwargs.get('voice_id')  # ElevenLabs voice ID
        self.voice_name = kwargs.get('voice_name')
        self.profile_picture = kwargs.get('profile_picture')
        self.is_active = kwargs.get('is_active', True)
        
        # Personality and context data
        self.personality_traits = kwargs.get('personality_traits', [])  # friendly, professional, etc.
        self.interests = kwargs.get('interests', [])  # topics they talk about
        self.communication_style = kwargs.get('communication_style', {})  # formal, casual, emoji_heavy, etc.
        self.frequency_score = kwargs.get('frequency_score', 0)  # How often they interact
        self.last_interaction = kwargs.get('last_interaction')
        
        # Platform-specific data
        self.platform_user_id = kwargs.get('platform_user_id')  # Platform's internal user ID
        self.platform_specific_data = kwargs.get('platform_specific_data', {})
        
        # Relationship context
        self.relationship_type = kwargs.get('relationship_type', 'friend')  # friend, family, colleague, etc.
        self.trust_score = kwargs.get('trust_score', 0.5)  # 0-1 scale
        self.preferred_topics = kwargs.get('preferred_topics', [])
        self.avoided_topics = kwargs.get('avoided_topics', [])
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'username': self.username,
            'platform': self.platform,
            'main_user': self.main_user,
            'display_name': self.display_name,
            'voice_id': self.voice_id,
            'voice_name': self.voice_name,
            'profile_picture': self.profile_picture,
            'is_active': self.is_active,
            'personality_traits': self.personality_traits,
            'interests': self.interests,
            'communication_style': self.communication_style,
            'frequency_score': self.frequency_score,
            'last_interaction': self.last_interaction,
            'platform_user_id': self.platform_user_id,
            'platform_specific_data': self.platform_specific_data,
            'relationship_type': self.relationship_type,
            'trust_score': self.trust_score,
            'preferred_topics': self.preferred_topics,
            'avoided_topics': self.avoided_topics
        })
        return data

class MainUser(BaseModel):
    """Main user (app owner) model"""
    
    def __init__(self, username: str, email: str, **kwargs):
        super().__init__(**kwargs)
        self.username = username
        self.email = email
        self.voice_id = kwargs.get('voice_id')  # ElevenLabs voice ID
        self.voice_name = kwargs.get('voice_name')
        self.is_active = kwargs.get('is_active', True)
        self.preferences = kwargs.get('preferences', {})
        
        # Platform connections
        self.connected_platforms = kwargs.get('connected_platforms', [])  # List of platforms they use
        self.platform_credentials = kwargs.get('platform_credentials', {})  # Encrypted platform tokens
        
        # App settings
        self.default_voice_settings = kwargs.get('default_voice_settings', {})
        self.summary_preferences = kwargs.get('summary_preferences', {})
        self.privacy_settings = kwargs.get('privacy_settings', {})
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'username': self.username,
            'email': self.email,
            'voice_id': self.voice_id,
            'voice_name': self.voice_name,
            'is_active': self.is_active,
            'preferences': self.preferences,
            'connected_platforms': self.connected_platforms,
            'platform_credentials': self.platform_credentials,
            'default_voice_settings': self.default_voice_settings,
            'summary_preferences': self.summary_preferences,
            'privacy_settings': self.privacy_settings
        })
        return data

class Summary(BaseModel):
    """Chat summary model"""
    
    def __init__(self, session_id: str, summary_text: str, **kwargs):
        super().__init__(**kwargs)
        self.session_id = session_id
        self.summary_text = summary_text
        self.script_lines = kwargs.get('script_lines', [])  # List of dialogue lines
        self.participants = kwargs.get('participants', [])
        self.summary_type = kwargs.get('summary_type', 'dialogue')  # dialogue, bullet_points, etc.
        self.word_count = kwargs.get('word_count', 0)
        self.generated_by = kwargs.get('generated_by', 'gpt-4')
        
        # Context and personality data
        self.personality_context = kwargs.get('personality_context', {})  # How personalities influenced summary
        self.relationship_context = kwargs.get('relationship_context', {})  # Relationship dynamics
        self.tone_analysis = kwargs.get('tone_analysis', {})  # Overall conversation tone
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'session_id': self.session_id,
            'summary_text': self.summary_text,
            'script_lines': self.script_lines,
            'participants': self.participants,
            'summary_type': self.summary_type,
            'word_count': self.word_count,
            'generated_by': self.generated_by,
            'personality_context': self.personality_context,
            'relationship_context': self.relationship_context,
            'tone_analysis': self.tone_analysis
        })
        return data

class AudioFile(BaseModel):
    """Audio file model for generated TTS"""
    
    def __init__(self, session_id: str, username: str, line_number: int, **kwargs):
        super().__init__(**kwargs)
        self.session_id = session_id
        self.username = username
        self.line_number = line_number
        self.file_path = kwargs.get('file_path')
        self.file_name = kwargs.get('file_name')
        self.voice_id = kwargs.get('voice_id')
        self.duration = kwargs.get('duration')  # in seconds
        self.file_size = kwargs.get('file_size')  # in bytes
        self.status = kwargs.get('status', 'pending')  # pending, processing, completed, failed
        self.error_message = kwargs.get('error_message')
        self.elevenlabs_generation_id = kwargs.get('elevenlabs_generation_id')
        
        # Personality-based voice settings
        self.voice_settings = kwargs.get('voice_settings', {})  # Custom voice settings based on personality
        self.emotion_context = kwargs.get('emotion_context', {})  # Emotional context for voice generation
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'session_id': self.session_id,
            'username': self.username,
            'line_number': self.line_number,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'voice_id': self.voice_id,
            'duration': self.duration,
            'file_size': self.file_size,
            'status': self.status,
            'error_message': self.error_message,
            'elevenlabs_generation_id': self.elevenlabs_generation_id,
            'voice_settings': self.voice_settings,
            'emotion_context': self.emotion_context
        })
        return data

class AssistantSession(BaseModel):
    """Assistant conversation session model"""
    
    def __init__(self, user_id: str, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.session_id = kwargs.get('session_id', str(uuid.uuid4()))
        self.messages = kwargs.get('messages', [])
        self.context = kwargs.get('context', {})  # Calendar events, user preferences, etc.
        self.is_active = kwargs.get('is_active', True)
        self.assistant_type = kwargs.get('assistant_type', 'elevenlabs')  # elevenlabs, custom
        
        # User profile context
        self.user_profiles_context = kwargs.get('user_profiles_context', {})  # Relevant user profiles
        self.conversation_history_context = kwargs.get('conversation_history_context', [])  # Recent conversations
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'user_id': self.user_id,
            'session_id': self.session_id,
            'messages': self.messages,
            'context': self.context,
            'is_active': self.is_active,
            'assistant_type': self.assistant_type,
            'user_profiles_context': self.user_profiles_context,
            'conversation_history_context': self.conversation_history_context
        })
        return data

class CalendarEvent(BaseModel):
    """Calendar event model for assistant integration"""
    
    def __init__(self, user_id: str, title: str, start_time: datetime, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.title = title
        self.start_time = start_time
        self.end_time = kwargs.get('end_time')
        self.description = kwargs.get('description', '')
        self.location = kwargs.get('location', '')
        self.calendar_id = kwargs.get('calendar_id')  # Google Calendar ID
        self.google_event_id = kwargs.get('google_event_id')
        self.status = kwargs.get('status', 'pending')  # pending, created, failed
        self.error_message = kwargs.get('error_message')
        
        # Related to conversation context
        self.related_conversation_id = kwargs.get('related_conversation_id')
        self.related_participants = kwargs.get('related_participants', [])
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'user_id': self.user_id,
            'title': self.title,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'description': self.description,
            'location': self.location,
            'calendar_id': self.calendar_id,
            'google_event_id': self.google_event_id,
            'status': self.status,
            'error_message': self.error_message,
            'related_conversation_id': self.related_conversation_id,
            'related_participants': self.related_participants
        })
        return data

class PlatformIntegration(BaseModel):
    """Platform integration settings and credentials"""
    
    def __init__(self, platform: str, user_id: str, **kwargs):
        super().__init__(**kwargs)
        self.platform = platform  # whatsapp, instagram, discord, etc.
        self.user_id = user_id
        self.is_connected = kwargs.get('is_connected', False)
        self.credentials = kwargs.get('credentials', {})  # Encrypted platform credentials
        self.settings = kwargs.get('settings', {})  # Platform-specific settings
        self.last_sync = kwargs.get('last_sync')
        self.sync_frequency = kwargs.get('sync_frequency', 'manual')  # manual, daily, weekly
        self.permissions = kwargs.get('permissions', [])  # What data we can access
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'platform': self.platform,
            'user_id': self.user_id,
            'is_connected': self.is_connected,
            'credentials': self.credentials,
            'settings': self.settings,
            'last_sync': self.last_sync,
            'sync_frequency': self.sync_frequency,
            'permissions': self.permissions
        })
        return data 