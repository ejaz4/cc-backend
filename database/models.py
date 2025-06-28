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

class WhatsAppMessage(BaseModel):
    """Individual WhatsApp message model"""
    
    def __init__(self, username: str, content: str, timestamp: datetime, **kwargs):
        super().__init__(**kwargs)
        self.username = username
        self.content = content
        self.timestamp = timestamp
        self.message_type = kwargs.get('message_type', 'text')  # text, media, system
        self.is_important = kwargs.get('is_important', False)
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'username': self.username,
            'content': self.content,
            'timestamp': self.timestamp,
            'message_type': self.message_type,
            'is_important': self.is_important
        })
        return data

class ChatSession(BaseModel):
    """WhatsApp group chat session model"""
    
    def __init__(self, group_name: str, **kwargs):
        super().__init__(**kwargs)
        self.group_name = group_name
        self.session_id = kwargs.get('session_id', str(uuid.uuid4()))
        self.messages = kwargs.get('messages', [])
        self.participants = kwargs.get('participants', [])
        self.status = kwargs.get('status', 'uploaded')  # uploaded, processing, summarized, completed
        self.file_path = kwargs.get('file_path')
        self.total_messages = kwargs.get('total_messages', 0)
        self.date_range = kwargs.get('date_range', {})  # start_date, end_date
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'group_name': self.group_name,
            'session_id': self.session_id,
            'messages': self.messages,
            'participants': self.participants,
            'status': self.status,
            'file_path': self.file_path,
            'total_messages': self.total_messages,
            'date_range': self.date_range
        })
        return data

class User(BaseModel):
    """User model for the app"""
    
    def __init__(self, username: str, email: str, **kwargs):
        super().__init__(**kwargs)
        self.username = username
        self.email = email
        self.voice_id = kwargs.get('voice_id')  # ElevenLabs voice ID
        self.voice_name = kwargs.get('voice_name')
        self.is_active = kwargs.get('is_active', True)
        self.preferences = kwargs.get('preferences', {})
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'username': self.username,
            'email': self.email,
            'voice_id': self.voice_id,
            'voice_name': self.voice_name,
            'is_active': self.is_active,
            'preferences': self.preferences
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
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'session_id': self.session_id,
            'summary_text': self.summary_text,
            'script_lines': self.script_lines,
            'participants': self.participants,
            'summary_type': self.summary_type,
            'word_count': self.word_count,
            'generated_by': self.generated_by
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
            'elevenlabs_generation_id': self.elevenlabs_generation_id
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
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'user_id': self.user_id,
            'session_id': self.session_id,
            'messages': self.messages,
            'context': self.context,
            'is_active': self.is_active,
            'assistant_type': self.assistant_type
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
            'error_message': self.error_message
        })
        return data 