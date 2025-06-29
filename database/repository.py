"""
Repository classes for database operations using Supabase SDK.
Replaces SQLAlchemy ORM with direct Supabase table operations.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from .supabase import get_supabase_client
from .connection import get_current_timestamp

logger = logging.getLogger(__name__)

class BaseRepository:
    """Base repository with common CRUD operations using Supabase"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.supabase = get_supabase_client()
    
    def create(self, data: Dict[str, Any]) -> Optional[int]:
        """Create a new record"""
        try:
            # Add timestamps if not present
            if 'created_at' not in data:
                data['created_at'] = get_current_timestamp()
            if 'updated_at' not in data:
                data['updated_at'] = get_current_timestamp()
            
            # Handle UUID generation for session_id fields
            if 'session_id' in data and not data['session_id']:
                data['session_id'] = str(uuid.uuid4())
            
            response = self.supabase.table(self.table_name).insert(data).execute()
            
            if response.data:
                return response.data[0]['id']
            return None
        except Exception as e:
            logger.error(f"Error creating record in {self.table_name}: {e}")
            return None
    
    def find_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """Find record by ID"""
        try:
            response = self.supabase.table(self.table_name).select("*").eq("id", record_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error finding record by ID in {self.table_name}: {e}")
            return None
    
    def find_all(self, filter_dict: Dict[str, Any] = None, limit: int = None, 
                 sort_by: str = None, order: str = 'desc') -> List[Dict[str, Any]]:
        """Find all records with optional filter"""
        try:
            query = self.supabase.table(self.table_name).select("*")
            
            # Apply filters
            if filter_dict:
                for key, value in filter_dict.items():
                    if isinstance(value, list):
                        query = query.in_(key, value)
                    else:
                        query = query.eq(key, value)
            
            # Apply sorting
            if sort_by:
                if order == 'desc':
                    query = query.order(sort_by, desc=True)
                else:
                    query = query.order(sort_by, desc=False)
            
            # Apply limit
            if limit:
                query = query.limit(limit)
            
            response = query.execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error finding records in {self.table_name}: {e}")
            return []
    
    def update(self, record_id: int, data: Dict[str, Any]) -> bool:
        """Update record by ID"""
        try:
            # Add updated timestamp
            data['updated_at'] = get_current_timestamp()
            
            response = self.supabase.table(self.table_name).update(data).eq("id", record_id).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error updating record in {self.table_name}: {e}")
            return False
    
    def delete(self, record_id: int) -> bool:
        """Delete record by ID"""
        try:
            response = self.supabase.table(self.table_name).delete().eq("id", record_id).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error deleting record in {self.table_name}: {e}")
            return False
    
    def count(self, filter_dict: Dict[str, Any] = None) -> int:
        """Count records with optional filter"""
        try:
            query = self.supabase.table(self.table_name).select("id", count="exact")
            
            if filter_dict:
                for key, value in filter_dict.items():
                    if isinstance(value, list):
                        query = query.in_(key, value)
                    else:
                        query = query.eq(key, value)
            
            response = query.execute()
            return response.count or 0
        except Exception as e:
            logger.error(f"Error counting records in {self.table_name}: {e}")
            return 0

class ConversationSessionRepository(BaseRepository):
    """Conversation session repository for all platforms"""
    
    def __init__(self):
        super().__init__("conversation_sessions")
    
    def find_by_session_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Find conversation session by session ID"""
        try:
            response = self.supabase.table(self.table_name).select("*").eq("session_id", session_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error finding session by session_id: {e}")
            return None
    
    def find_by_platform(self, platform: str, main_user: str) -> List[Dict[str, Any]]:
        """Find sessions by platform and main user"""
        return self.find_all({
            'platform': platform,
            'main_user': main_user
        })
    
    def find_by_status(self, status: str, main_user: str = None) -> List[Dict[str, Any]]:
        """Find sessions by status"""
        filter_dict = {'status': status}
        if main_user:
            filter_dict['main_user'] = main_user
        return self.find_all(filter_dict)
    
    def update_status(self, session_id: str, status: str) -> bool:
        """Update session status"""
        try:
            response = self.supabase.table(self.table_name).update({
                'status': status,
                'updated_at': get_current_timestamp()
            }).eq("session_id", session_id).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error updating session status: {e}")
            return False
    
    def find_recent_sessions(self, main_user: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find recent conversation sessions for a user"""
        return self.find_all(
            filter_dict={'main_user': main_user},
            limit=limit,
            sort_by='created_at',
            order='desc'
        )
    
    def find_by_participant(self, participant: str, main_user: str) -> List[Dict[str, Any]]:
        """Find sessions by participant (requires joining with messages)"""
        try:
            # First get message IDs for the participant
            message_response = self.supabase.table("platform_messages").select(
                "conversation_session_id"
            ).eq("username", participant).execute()
            
            if not message_response.data:
                return []
            
            session_ids = list(set([msg['conversation_session_id'] for msg in message_response.data]))
            
            # Then get the sessions
            response = self.supabase.table(self.table_name).select("*").in_(
                "id", session_ids
            ).eq("main_user", main_user).execute()
            
            return response.data or []
        except Exception as e:
            logger.error(f"Error finding sessions by participant: {e}")
            return []
    
    def add_message(self, session_id: str, message: Dict[str, Any]) -> bool:
        """Add a message to a conversation session"""
        try:
            # Get the conversation session ID
            session = self.find_by_session_id(session_id)
            if not session:
                return False
            
            # Add the conversation session ID to the message
            message['conversation_session_id'] = session['id']
            
            # Create the message
            message_repo = PlatformMessageRepository()
            message_id = message_repo.create(message)
            
            if message_id:
                # Update the total messages count
                self.update(session['id'], {
                    'total_messages': session.get('total_messages', 0) + 1
                })
                return True
            return False
        except Exception as e:
            logger.error(f"Error adding message to session: {e}")
            return False

class PlatformMessageRepository(BaseRepository):
    """Platform message repository"""
    
    def __init__(self):
        super().__init__("platform_messages")
    
    def find_by_session(self, conversation_session_id: int) -> List[Dict[str, Any]]:
        """Find all messages for a conversation session"""
        return self.find_all(
            filter_dict={'conversation_session_id': conversation_session_id},
            sort_by='timestamp',
            order='asc'
        )
    
    def find_important_messages(self, conversation_session_id: int) -> List[Dict[str, Any]]:
        """Find important messages for a conversation session"""
        return self.find_all({
            'conversation_session_id': conversation_session_id,
            'is_important': True
        })

class MainUserRepository(BaseRepository):
    """Main user repository"""
    
    def __init__(self):
        super().__init__("main_users")
    
    def find_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Find main user by username"""
        try:
            response = self.supabase.table(self.table_name).select("*").eq("username", username).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error finding user by username: {e}")
            return None
    
    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find main user by email"""
        try:
            response = self.supabase.table(self.table_name).select("*").eq("email", email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error finding user by email: {e}")
            return None
    
    def update_voice_id(self, user_id: int, voice_id: str, voice_name: str) -> bool:
        """Update user's voice ID and name"""
        return self.update(user_id, {
            'voice_id': voice_id,
            'voice_name': voice_name
        })
    
    def find_active_users(self) -> List[Dict[str, Any]]:
        """Find all active users"""
        return self.find_all({'is_active': True})
    
    def add_connected_platform(self, user_id: int, platform: str) -> bool:
        """Add a platform to user's connected platforms"""
        try:
            user = self.find_by_id(user_id)
            if not user:
                return False
            
            connected_platforms = user.get('connected_platforms', [])
            if platform not in connected_platforms:
                connected_platforms.append(platform)
                return self.update(user_id, {'connected_platforms': connected_platforms})
            return True
        except Exception as e:
            logger.error(f"Error adding connected platform: {e}")
            return False

class UserProfileRepository(BaseRepository):
    """User profile repository"""
    
    def __init__(self):
        super().__init__("user_profiles")
    
    def find_by_username(self, username: str, platform: str, main_user_id: int) -> Optional[Dict[str, Any]]:
        """Find user profile by username, platform, and main user"""
        try:
            response = self.supabase.table(self.table_name).select("*").eq("username", username).eq(
                "platform", platform
            ).eq("main_user_id", main_user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error finding profile by username: {e}")
            return None
    
    def find_by_main_user(self, main_user_id: int, platform: str = None) -> List[Dict[str, Any]]:
        """Find all profiles for a main user"""
        filter_dict = {'main_user_id': main_user_id}
        if platform:
            filter_dict['platform'] = platform
        return self.find_all(filter_dict)
    
    def find_by_relationship_type(self, main_user_id: int, relationship_type: str) -> List[Dict[str, Any]]:
        """Find profiles by relationship type"""
        return self.find_all({
            'main_user_id': main_user_id,
            'relationship_type': relationship_type
        })
    
    def update_personality_data(self, profile_id: int, personality_data: Dict[str, Any]) -> bool:
        """Update personality data for a profile"""
        return self.update(profile_id, personality_data)
    
    def update_frequency_score(self, profile_id: int, frequency_score: float) -> bool:
        """Update frequency score for a profile"""
        return self.update(profile_id, {
            'frequency_score': frequency_score,
            'last_interaction': get_current_timestamp()
        })
    
    def find_frequent_contacts(self, main_user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Find most frequent contacts for a user"""
        return self.find_all(
            filter_dict={'main_user_id': main_user_id},
            limit=limit,
            sort_by='frequency_score',
            order='desc'
        )
    
    def find_by_interests(self, main_user_id: int, interests: List[str]) -> List[Dict[str, Any]]:
        """Find profiles by interests (requires JSON overlap query)"""
        try:
            # This is a simplified version - Supabase supports JSON operations
            # but the exact syntax may vary based on your setup
            response = self.supabase.table(self.table_name).select("*").eq(
                "main_user_id", main_user_id
            ).execute()
            
            # Filter in Python for now - can be optimized with proper JSON queries
            profiles = response.data or []
            matching_profiles = []
            
            for profile in profiles:
                profile_interests = profile.get('interests', [])
                if any(interest in profile_interests for interest in interests):
                    matching_profiles.append(profile)
            
            return matching_profiles
        except Exception as e:
            logger.error(f"Error finding profiles by interests: {e}")
            return []
    
    def create_or_update_profile(self, profile_data: Dict[str, Any]) -> Optional[int]:
        """Create or update a user profile"""
        try:
            # Check if profile exists
            existing = self.find_by_username(
                profile_data['username'],
                profile_data['platform'],
                profile_data['main_user_id']
            )
            
            if existing:
                # Update existing profile
                self.update(existing['id'], profile_data)
                return existing['id']
            else:
                # Create new profile
                return self.create(profile_data)
        except Exception as e:
            logger.error(f"Error creating or updating profile: {e}")
            return None

class SummaryRepository(BaseRepository):
    """Summary repository"""
    
    def __init__(self):
        super().__init__("summaries")
    
    def find_by_session_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Find summary by conversation session ID"""
        try:
            # First get the conversation session
            session_repo = ConversationSessionRepository()
            session = session_repo.find_by_session_id(session_id)
            if not session:
                return None
            
            # Then find the summary
            response = self.supabase.table(self.table_name).select("*").eq(
                "conversation_session_id", session['id']
            ).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error finding summary by session_id: {e}")
            return None
    
    def find_recent_summaries(self, main_user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Find recent summaries for a user"""
        return self.find_all(
            filter_dict={'main_user_id': main_user_id},
            limit=limit,
            sort_by='created_at',
            order='desc'
        )
    
    def find_by_participants(self, participants: List[str], main_user_id: int) -> List[Dict[str, Any]]:
        """Find summaries by participants (requires complex query)"""
        try:
            # This would require a more complex query involving joins
            # For now, return recent summaries for the user
            return self.find_recent_summaries(main_user_id, limit=20)
        except Exception as e:
            logger.error(f"Error finding summaries by participants: {e}")
            return []

class AudioFileRepository(BaseRepository):
    """Audio file repository"""
    
    def __init__(self):
        super().__init__("audio_files")
    
    def find_by_session_id(self, session_id: str) -> List[Dict[str, Any]]:
        """Find all audio files for a conversation session"""
        try:
            # First get the conversation session
            session_repo = ConversationSessionRepository()
            session = session_repo.find_by_session_id(session_id)
            if not session:
                return []
            
            # Then find the audio files
            response = self.supabase.table(self.table_name).select("*").eq(
                "conversation_session_id", session['id']
            ).order("line_number", desc=False).execute()
            
            return response.data or []
        except Exception as e:
            logger.error(f"Error finding audio files by session_id: {e}")
            return []
    
    def find_by_username(self, session_id: str, username: str) -> List[Dict[str, Any]]:
        """Find audio files for a specific user in a session"""
        try:
            # First get the conversation session
            session_repo = ConversationSessionRepository()
            session = session_repo.find_by_session_id(session_id)
            if not session:
                return []
            
            # Then find the audio files for the user
            response = self.supabase.table(self.table_name).select("*").eq(
                "conversation_session_id", session['id']
            ).eq("username", username).order("line_number", desc=False).execute()
            
            return response.data or []
        except Exception as e:
            logger.error(f"Error finding audio files by username: {e}")
            return []
    
    def update_status(self, audio_file_id: int, status: str, file_path: str = None) -> bool:
        """Update audio file status"""
        update_data = {'status': status}
        if file_path:
            update_data['file_path'] = file_path
        return self.update(audio_file_id, update_data)
    
    def find_completed_audio(self, session_id: str) -> List[Dict[str, Any]]:
        """Find completed audio files for a session"""
        try:
            # First get the conversation session
            session_repo = ConversationSessionRepository()
            session = session_repo.find_by_session_id(session_id)
            if not session:
                return []
            
            # Then find the completed audio files
            response = self.supabase.table(self.table_name).select("*").eq(
                "conversation_session_id", session['id']
            ).eq("status", "completed").order("line_number", desc=False).execute()
            
            return response.data or []
        except Exception as e:
            logger.error(f"Error finding completed audio files: {e}")
            return []

class AssistantSessionRepository(BaseRepository):
    """Assistant session repository"""
    
    def __init__(self):
        super().__init__("assistant_sessions")
    
    def find_by_session_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Find assistant session by session ID"""
        try:
            response = self.supabase.table(self.table_name).select("*").eq("session_id", session_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error finding assistant session by session_id: {e}")
            return None
    
    def find_active_sessions(self, main_user_id: int) -> List[Dict[str, Any]]:
        """Find active assistant sessions for a user"""
        return self.find_all({
            'main_user_id': main_user_id,
            'is_active': True
        })
    
    def add_message(self, session_id: str, message: Dict[str, Any]) -> bool:
        """Add a message to an assistant session"""
        try:
            session = self.find_by_session_id(session_id)
            if not session:
                return False
            
            messages = session.get('messages', [])
            messages.append(message)
            
            return self.update(session['id'], {'messages': messages})
        except Exception as e:
            logger.error(f"Error adding message to assistant session: {e}")
            return False

class CalendarEventRepository(BaseRepository):
    """Calendar event repository"""
    
    def __init__(self):
        super().__init__("calendar_events")
    
    def find_by_user_id(self, main_user_id: int) -> List[Dict[str, Any]]:
        """Find all calendar events for a user"""
        return self.find_all(
            filter_dict={'main_user_id': main_user_id},
            sort_by='start_time',
            order='asc'
        )
    
    def find_upcoming_events(self, main_user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Find upcoming calendar events for a user"""
        try:
            current_time = get_current_timestamp()
            response = self.supabase.table(self.table_name).select("*").eq(
                "main_user_id", main_user_id
            ).gte("start_time", current_time).order("start_time", desc=False).limit(limit).execute()
            
            return response.data or []
        except Exception as e:
            logger.error(f"Error finding upcoming events: {e}")
            return []
    
    def update_google_event_id(self, event_id: int, google_event_id: str) -> bool:
        """Update Google Calendar event ID"""
        return self.update(event_id, {
            'google_event_id': google_event_id,
            'status': 'created'
        })

class PlatformIntegrationRepository(BaseRepository):
    """Platform integration repository"""
    
    def __init__(self):
        super().__init__("platform_integrations")
    
    def find_by_user_and_platform(self, main_user_id: int, platform: str) -> Optional[Dict[str, Any]]:
        """Find platform integration by user and platform"""
        try:
            response = self.supabase.table(self.table_name).select("*").eq(
                "main_user_id", main_user_id
            ).eq("platform", platform).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error finding platform integration: {e}")
            return None
    
    def find_connected_platforms(self, main_user_id: int) -> List[Dict[str, Any]]:
        """Find all connected platforms for a user"""
        return self.find_all({
            'main_user_id': main_user_id,
            'is_connected': True
        })
    
    def update_credentials(self, integration_id: int, credentials: Dict[str, Any]) -> bool:
        """Update platform credentials"""
        return self.update(integration_id, {'credentials': credentials})
    
    def update_sync_status(self, integration_id: int, last_sync: datetime) -> bool:
        """Update last sync timestamp"""
        return self.update(integration_id, {'last_sync': last_sync.isoformat()}) 