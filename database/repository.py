from typing import List, Dict, Any, Optional
from bson import ObjectId
from datetime import datetime
import logging

from .connection import get_collection
from .models import (
    BaseModel, WhatsAppMessage, ChatSession, User, Summary, 
    AudioFile, AssistantSession, CalendarEvent
)

logger = logging.getLogger(__name__)

class BaseRepository:
    """Base repository with common CRUD operations"""
    
    def __init__(self, collection_name: str):
        self.collection = get_collection(collection_name)
    
    def create(self, data: Dict[str, Any]) -> Optional[str]:
        """Create a new document"""
        try:
            data['created_at'] = datetime.utcnow()
            data['updated_at'] = datetime.utcnow()
            result = self.collection.insert_one(data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            return None
    
    def find_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Find document by ID"""
        try:
            return self.collection.find_one({'_id': ObjectId(document_id)})
        except Exception as e:
            logger.error(f"Error finding document by ID: {e}")
            return None
    
    def find_all(self, filter_dict: Dict[str, Any] = None, limit: int = None, sort_by: str = None) -> List[Dict[str, Any]]:
        """Find all documents with optional filter"""
        try:
            filter_dict = filter_dict or {}
            cursor = self.collection.find(filter_dict)
            
            if sort_by:
                cursor = cursor.sort(sort_by, -1)
            if limit:
                cursor = cursor.limit(limit)
                
            return list(cursor)
        except Exception as e:
            logger.error(f"Error finding documents: {e}")
            return []
    
    def update(self, document_id: str, data: Dict[str, Any]) -> bool:
        """Update document by ID"""
        try:
            data['updated_at'] = datetime.utcnow()
            result = self.collection.update_one(
                {'_id': ObjectId(document_id)},
                {'$set': data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            return False
    
    def delete(self, document_id: str) -> bool:
        """Delete document by ID"""
        try:
            result = self.collection.delete_one({'_id': ObjectId(document_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False
    
    def count(self, filter_dict: Dict[str, Any] = None) -> int:
        """Count documents with optional filter"""
        try:
            filter_dict = filter_dict or {}
            return self.collection.count_documents(filter_dict)
        except Exception as e:
            logger.error(f"Error counting documents: {e}")
            return 0

class ChatSessionRepository(BaseRepository):
    """Chat session repository"""
    
    def __init__(self):
        super().__init__('chat_sessions')
    
    def find_by_session_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Find chat session by session ID"""
        return self.collection.find_one({'session_id': session_id})
    
    def find_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Find sessions by status"""
        return self.find_all({'status': status})
    
    def update_status(self, session_id: str, status: str) -> bool:
        """Update session status"""
        return self.update(session_id, {'status': status})
    
    def find_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Find recent chat sessions"""
        return self.find_all(limit=limit, sort_by='created_at')
    
    def add_message(self, session_id: str, message: Dict[str, Any]) -> bool:
        """Add a message to a chat session"""
        try:
            result = self.collection.update_one(
                {'session_id': session_id},
                {'$push': {'messages': message}, '$inc': {'total_messages': 1}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            return False

class UserRepository(BaseRepository):
    """User repository"""
    
    def __init__(self):
        super().__init__('users')
    
    def find_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Find user by username"""
        return self.collection.find_one({'username': username})
    
    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find user by email"""
        return self.collection.find_one({'email': email})
    
    def update_voice_id(self, user_id: str, voice_id: str, voice_name: str) -> bool:
        """Update user's voice ID"""
        return self.update(user_id, {'voice_id': voice_id, 'voice_name': voice_name})
    
    def find_active_users(self) -> List[Dict[str, Any]]:
        """Find all active users"""
        return self.find_all({'is_active': True})

class SummaryRepository(BaseRepository):
    """Summary repository"""
    
    def __init__(self):
        super().__init__('summaries')
    
    def find_by_session_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Find summary by session ID"""
        return self.collection.find_one({'session_id': session_id})
    
    def find_recent_summaries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Find recent summaries"""
        return self.find_all(limit=limit, sort_by='created_at')

class AudioFileRepository(BaseRepository):
    """Audio file repository"""
    
    def __init__(self):
        super().__init__('audio_files')
    
    def find_by_session_id(self, session_id: str) -> List[Dict[str, Any]]:
        """Find all audio files for a session"""
        return self.find_all({'session_id': session_id})
    
    def find_by_username(self, session_id: str, username: str) -> List[Dict[str, Any]]:
        """Find audio files for a specific user in a session"""
        return self.find_all({'session_id': session_id, 'username': username})
    
    def update_status(self, audio_file_id: str, status: str, file_path: str = None) -> bool:
        """Update audio file status"""
        update_data = {'status': status}
        if file_path:
            update_data['file_path'] = file_path
        return self.update(audio_file_id, update_data)
    
    def find_completed_audio(self, session_id: str) -> List[Dict[str, Any]]:
        """Find completed audio files for a session"""
        return self.find_all({'session_id': session_id, 'status': 'completed'})

class AssistantSessionRepository(BaseRepository):
    """Assistant session repository"""
    
    def __init__(self):
        super().__init__('assistant_sessions')
    
    def find_by_session_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Find assistant session by session ID"""
        return self.collection.find_one({'session_id': session_id})
    
    def find_active_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Find active assistant sessions for a user"""
        return self.find_all({'user_id': user_id, 'is_active': True})
    
    def add_message(self, session_id: str, message: Dict[str, Any]) -> bool:
        """Add a message to assistant session"""
        try:
            result = self.collection.update_one(
                {'session_id': session_id},
                {'$push': {'messages': message}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error adding message to assistant session: {e}")
            return False

class CalendarEventRepository(BaseRepository):
    """Calendar event repository"""
    
    def __init__(self):
        super().__init__('calendar_events')
    
    def find_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        """Find events for a user"""
        return self.find_all({'user_id': user_id}, sort_by='start_time')
    
    def find_upcoming_events(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find upcoming events for a user"""
        now = datetime.utcnow()
        return self.find_all(
            {'user_id': user_id, 'start_time': {'$gte': now}},
            limit=limit,
            sort_by='start_time'
        )
    
    def update_google_event_id(self, event_id: str, google_event_id: str) -> bool:
        """Update event with Google Calendar event ID"""
        return self.update(event_id, {
            'google_event_id': google_event_id,
            'status': 'created'
        }) 