from typing import List, Dict, Any, Optional
from bson import ObjectId
from datetime import datetime
import logging

from .connection import get_collection
from .models import (
    BaseModel, PlatformMessage, ConversationSession, MainUser, UserProfile, Summary, 
    AudioFile, AssistantSession, CalendarEvent, PlatformIntegration
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

class ConversationSessionRepository(BaseRepository):
    """Conversation session repository for all platforms"""
    
    def __init__(self):
        super().__init__('conversation_sessions')
    
    def find_by_session_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Find conversation session by session ID"""
        return self.collection.find_one({'session_id': session_id})
    
    def find_by_platform(self, platform: str, main_user: str) -> List[Dict[str, Any]]:
        """Find sessions by platform and main user"""
        return self.find_all({'platform': platform, 'main_user': main_user})
    
    def find_by_status(self, status: str, main_user: str = None) -> List[Dict[str, Any]]:
        """Find sessions by status"""
        filter_dict = {'status': status}
        if main_user:
            filter_dict['main_user'] = main_user
        return self.find_all(filter_dict)
    
    def update_status(self, session_id: str, status: str) -> bool:
        """Update session status"""
        return self.update(session_id, {'status': status})
    
    def find_recent_sessions(self, main_user: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find recent conversation sessions for a user"""
        return self.find_all({'main_user': main_user}, limit=limit, sort_by='created_at')
    
    def find_by_participant(self, participant: str, main_user: str) -> List[Dict[str, Any]]:
        """Find sessions where a specific participant was involved"""
        return self.find_all({'participants': participant, 'main_user': main_user})
    
    def add_message(self, session_id: str, message: Dict[str, Any]) -> bool:
        """Add a message to a conversation session"""
        try:
            result = self.collection.update_one(
                {'session_id': session_id},
                {'$push': {'messages': message}, '$inc': {'total_messages': 1}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            return False

class MainUserRepository(BaseRepository):
    """Main user repository"""
    
    def __init__(self):
        super().__init__('main_users')
    
    def find_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Find main user by username"""
        return self.collection.find_one({'username': username})
    
    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find main user by email"""
        return self.collection.find_one({'email': email})
    
    def update_voice_id(self, user_id: str, voice_id: str, voice_name: str) -> bool:
        """Update user's voice ID"""
        return self.update(user_id, {'voice_id': voice_id, 'voice_name': voice_name})
    
    def find_active_users(self) -> List[Dict[str, Any]]:
        """Find all active main users"""
        return self.find_all({'is_active': True})
    
    def add_connected_platform(self, user_id: str, platform: str) -> bool:
        """Add a platform to user's connected platforms"""
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$addToSet': {'connected_platforms': platform}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error adding connected platform: {e}")
            return False

class UserProfileRepository(BaseRepository):
    """User profile repository for people the main user talks to"""
    
    def __init__(self):
        super().__init__('user_profiles')
    
    def find_by_username(self, username: str, platform: str, main_user: str) -> Optional[Dict[str, Any]]:
        """Find user profile by username, platform, and main user"""
        return self.collection.find_one({
            'username': username,
            'platform': platform,
            'main_user': main_user
        })
    
    def find_by_main_user(self, main_user: str, platform: str = None) -> List[Dict[str, Any]]:
        """Find all user profiles for a main user"""
        filter_dict = {'main_user': main_user}
        if platform:
            filter_dict['platform'] = platform
        return self.find_all(filter_dict)
    
    def find_by_relationship_type(self, main_user: str, relationship_type: str) -> List[Dict[str, Any]]:
        """Find user profiles by relationship type"""
        return self.find_all({
            'main_user': main_user,
            'relationship_type': relationship_type
        })
    
    def update_personality_data(self, profile_id: str, personality_data: Dict[str, Any]) -> bool:
        """Update personality and context data"""
        return self.update(profile_id, personality_data)
    
    def update_frequency_score(self, profile_id: str, frequency_score: float) -> bool:
        """Update interaction frequency score"""
        return self.update(profile_id, {
            'frequency_score': frequency_score,
            'last_interaction': datetime.utcnow()
        })
    
    def find_frequent_contacts(self, main_user: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find most frequent contacts for a main user"""
        return self.find_all(
            {'main_user': main_user},
            limit=limit,
            sort_by='frequency_score'
        )
    
    def find_by_interests(self, main_user: str, interests: List[str]) -> List[Dict[str, Any]]:
        """Find user profiles by interests"""
        return self.find_all({
            'main_user': main_user,
            'interests': {'$in': interests}
        })
    
    def create_or_update_profile(self, profile_data: Dict[str, Any]) -> Optional[str]:
        """Create or update a user profile"""
        try:
            # Check if profile exists
            existing = self.find_by_username(
                profile_data['username'],
                profile_data['platform'],
                profile_data['main_user']
            )
            
            if existing:
                # Update existing profile
                profile_id = str(existing['_id'])
                self.update(profile_id, profile_data)
                return profile_id
            else:
                # Create new profile
                return self.create(profile_data)
        except Exception as e:
            logger.error(f"Error creating/updating profile: {e}")
            return None

class SummaryRepository(BaseRepository):
    """Summary repository"""
    
    def __init__(self):
        super().__init__('summaries')
    
    def find_by_session_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Find summary by session ID"""
        return self.collection.find_one({'session_id': session_id})
    
    def find_recent_summaries(self, main_user: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find recent summaries for a main user"""
        return self.find_all({'main_user': main_user}, limit=limit, sort_by='created_at')
    
    def find_by_participants(self, participants: List[str], main_user: str) -> List[Dict[str, Any]]:
        """Find summaries involving specific participants"""
        return self.find_all({
            'participants': {'$in': participants},
            'main_user': main_user
        })

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

class PlatformIntegrationRepository(BaseRepository):
    """Platform integration repository"""
    
    def __init__(self):
        super().__init__('platform_integrations')
    
    def find_by_user_and_platform(self, user_id: str, platform: str) -> Optional[Dict[str, Any]]:
        """Find integration by user ID and platform"""
        return self.collection.find_one({
            'user_id': user_id,
            'platform': platform
        })
    
    def find_connected_platforms(self, user_id: str) -> List[Dict[str, Any]]:
        """Find all connected platforms for a user"""
        return self.find_all({'user_id': user_id, 'is_connected': True})
    
    def update_credentials(self, integration_id: str, credentials: Dict[str, Any]) -> bool:
        """Update platform credentials"""
        return self.update(integration_id, {'credentials': credentials})
    
    def update_sync_status(self, integration_id: str, last_sync: datetime) -> bool:
        """Update last sync timestamp"""
        return self.update(integration_id, {'last_sync': last_sync}) 