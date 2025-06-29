import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func

from .connection import get_db
from .models import (
    ConversationSession, PlatformMessage, MainUser, UserProfile, Summary, 
    AudioFile, AssistantSession, CalendarEvent, PlatformIntegration
)

logger = logging.getLogger(__name__)

class BaseRepository:
    """Base repository with common CRUD operations"""
    
    def __init__(self, model_class):
        self.model = model_class
    
    def create(self, data: Dict[str, Any]) -> Optional[int]:
        """Create a new record"""
        try:
            with get_db() as db:
                # Handle datetime fields
                if 'created_at' not in data:
                    data['created_at'] = datetime.utcnow()
                if 'updated_at' not in data:
                    data['updated_at'] = datetime.utcnow()
                
                # Create model instance
                instance = self.model(**data)
                db.add(instance)
                db.commit()
                db.refresh(instance)
                return instance.id
        except Exception as e:
            logger.error(f"Error creating record: {e}")
            return None
    
    def find_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """Find record by ID"""
        try:
            with get_db() as db:
                instance = db.query(self.model).filter(self.model.id == record_id).first()
                return self._to_dict(instance) if instance else None
        except Exception as e:
            logger.error(f"Error finding record by ID: {e}")
            return None
    
    def find_all(self, filter_dict: Dict[str, Any] = None, limit: int = None, sort_by: str = None, order: str = 'desc') -> List[Dict[str, Any]]:
        """Find all records with optional filter"""
        try:
            with get_db() as db:
                query = db.query(self.model)
                
                # Apply filters
                if filter_dict:
                    for key, value in filter_dict.items():
                        if hasattr(self.model, key):
                            if isinstance(value, list):
                                query = query.filter(getattr(self.model, key).in_(value))
                            else:
                                query = query.filter(getattr(self.model, key) == value)
                
                # Apply sorting
                if sort_by and hasattr(self.model, sort_by):
                    if order == 'desc':
                        query = query.order_by(desc(getattr(self.model, sort_by)))
                    else:
                        query = query.order_by(asc(getattr(self.model, sort_by)))
                
                # Apply limit
                if limit:
                    query = query.limit(limit)
                
                instances = query.all()
                return [self._to_dict(instance) for instance in instances]
        except Exception as e:
            logger.error(f"Error finding records: {e}")
            return []
    
    def update(self, record_id: int, data: Dict[str, Any]) -> bool:
        """Update record by ID"""
        try:
            with get_db() as db:
                instance = db.query(self.model).filter(self.model.id == record_id).first()
                if not instance:
                    return False
                
                # Update fields
                for key, value in data.items():
                    if hasattr(instance, key):
                        setattr(instance, key, value)
                
                instance.updated_at = datetime.utcnow()
                db.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating record: {e}")
            return False
    
    def delete(self, record_id: int) -> bool:
        """Delete record by ID"""
        try:
            with get_db() as db:
                instance = db.query(self.model).filter(self.model.id == record_id).first()
                if not instance:
                    return False
                
                db.delete(instance)
                db.commit()
                return True
        except Exception as e:
            logger.error(f"Error deleting record: {e}")
            return False
    
    def count(self, filter_dict: Dict[str, Any] = None) -> int:
        """Count records with optional filter"""
        try:
            with get_db() as db:
                query = db.query(func.count(self.model.id))
                
                if filter_dict:
                    for key, value in filter_dict.items():
                        if hasattr(self.model, key):
                            query = query.filter(getattr(self.model, key) == value)
                
                return query.scalar()
        except Exception as e:
            logger.error(f"Error counting records: {e}")
            return 0
    
    def _to_dict(self, instance) -> Dict[str, Any]:
        """Convert SQLAlchemy instance to dictionary"""
        if not instance:
            return {}
        
        result = {}
        for column in instance.__table__.columns:
            value = getattr(instance, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        
        return result

class ConversationSessionRepository(BaseRepository):
    """Conversation session repository for all platforms"""
    
    def __init__(self):
        super().__init__(ConversationSession)
    
    def find_by_session_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Find conversation session by session ID"""
        try:
            with get_db() as db:
                instance = db.query(ConversationSession).filter(
                    ConversationSession.session_id == session_id
                ).first()
                return self._to_dict(instance) if instance else None
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
            with get_db() as db:
                instance = db.query(ConversationSession).filter(
                    ConversationSession.session_id == session_id
                ).first()
                if not instance:
                    return False
                
                instance.status = status
                instance.updated_at = datetime.utcnow()
                db.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating session status: {e}")
            return False
    
    def find_recent_sessions(self, main_user: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find recent conversation sessions for a user"""
        return self.find_all(
            {'main_user': main_user}, 
            limit=limit, 
            sort_by='created_at'
        )
    
    def find_by_participant(self, participant: str, main_user: str) -> List[Dict[str, Any]]:
        """Find sessions where a specific participant was involved"""
        try:
            with get_db() as db:
                # This is a complex query that would need to be implemented
                # based on how participants are stored (JSON array or separate table)
                instances = db.query(ConversationSession).filter(
                    ConversationSession.main_user == main_user
                ).all()
                
                # Filter by participant (assuming participants is stored as JSON)
                result = []
                for instance in instances:
                    if instance.participants and participant in instance.participants:
                        result.append(self._to_dict(instance))
                
                return result
        except Exception as e:
            logger.error(f"Error finding sessions by participant: {e}")
            return []
    
    def add_message(self, session_id: str, message: Dict[str, Any]) -> bool:
        """Add a message to a conversation session"""
        try:
            with get_db() as db:
                # Find the session
                session = db.query(ConversationSession).filter(
                    ConversationSession.session_id == session_id
                ).first()
                if not session:
                    return False
                
                # Create message
                message['conversation_session_id'] = session.id
                message_instance = PlatformMessage(**message)
                db.add(message_instance)
                
                # Update total messages count
                session.total_messages += 1
                session.updated_at = datetime.utcnow()
                
                db.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            return False

class MainUserRepository(BaseRepository):
    """Main user repository"""
    
    def __init__(self):
        super().__init__(MainUser)
    
    def find_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Find main user by username"""
        try:
            with get_db() as db:
                instance = db.query(MainUser).filter(MainUser.username == username).first()
                return self._to_dict(instance) if instance else None
        except Exception as e:
            logger.error(f"Error finding user by username: {e}")
            return None
    
    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find main user by email"""
        try:
            with get_db() as db:
                instance = db.query(MainUser).filter(MainUser.email == email).first()
                return self._to_dict(instance) if instance else None
        except Exception as e:
            logger.error(f"Error finding user by email: {e}")
            return None
    
    def update_voice_id(self, user_id: int, voice_id: str, voice_name: str) -> bool:
        """Update user's voice ID"""
        return self.update(user_id, {
            'voice_id': voice_id,
            'voice_name': voice_name
        })
    
    def find_active_users(self) -> List[Dict[str, Any]]:
        """Find all active main users"""
        return self.find_all({'is_active': True})
    
    def add_connected_platform(self, user_id: int, platform: str) -> bool:
        """Add a platform to user's connected platforms"""
        try:
            with get_db() as db:
                user = db.query(MainUser).filter(MainUser.id == user_id).first()
                if not user:
                    return False
                
                # Get current platforms
                platforms = user.connected_platforms or []
                if platform not in platforms:
                    platforms.append(platform)
                    user.connected_platforms = platforms
                    user.updated_at = datetime.utcnow()
                    db.commit()
                
                return True
        except Exception as e:
            logger.error(f"Error adding connected platform: {e}")
            return False

class UserProfileRepository(BaseRepository):
    """User profile repository for people the main user talks to"""
    
    def __init__(self):
        super().__init__(UserProfile)
    
    def find_by_username(self, username: str, platform: str, main_user_id: int) -> Optional[Dict[str, Any]]:
        """Find user profile by username, platform, and main user"""
        try:
            with get_db() as db:
                instance = db.query(UserProfile).filter(
                    and_(
                        UserProfile.username == username,
                        UserProfile.platform == platform,
                        UserProfile.main_user_id == main_user_id
                    )
                ).first()
                return self._to_dict(instance) if instance else None
        except Exception as e:
            logger.error(f"Error finding profile by username: {e}")
            return None
    
    def find_by_main_user(self, main_user_id: int, platform: str = None) -> List[Dict[str, Any]]:
        """Find all user profiles for a main user"""
        filter_dict = {'main_user_id': main_user_id}
        if platform:
            filter_dict['platform'] = platform
        return self.find_all(filter_dict)
    
    def find_by_relationship_type(self, main_user_id: int, relationship_type: str) -> List[Dict[str, Any]]:
        """Find user profiles by relationship type"""
        return self.find_all({
            'main_user_id': main_user_id,
            'relationship_type': relationship_type
        })
    
    def update_personality_data(self, profile_id: int, personality_data: Dict[str, Any]) -> bool:
        """Update personality and context data"""
        return self.update(profile_id, personality_data)
    
    def update_frequency_score(self, profile_id: int, frequency_score: float) -> bool:
        """Update interaction frequency score"""
        return self.update(profile_id, {
            'frequency_score': frequency_score,
            'last_interaction': datetime.utcnow()
        })
    
    def find_frequent_contacts(self, main_user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Find most frequent contacts for a main user"""
        return self.find_all(
            {'main_user_id': main_user_id},
            limit=limit,
            sort_by='frequency_score'
        )
    
    def find_by_interests(self, main_user_id: int, interests: List[str]) -> List[Dict[str, Any]]:
        """Find user profiles by interests"""
        try:
            with get_db() as db:
                # This would need to be implemented based on how interests are stored
                # For now, return all profiles for the user
                return self.find_all({'main_user_id': main_user_id})
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
                profile_id = existing['id']
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
        super().__init__(Summary)
    
    def find_by_session_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Find summary by session ID"""
        try:
            with get_db() as db:
                # First find the conversation session
                session = db.query(ConversationSession).filter(
                    ConversationSession.session_id == session_id
                ).first()
                if not session:
                    return None
                
                # Then find the summary
                instance = db.query(Summary).filter(
                    Summary.conversation_session_id == session.id
                ).first()
                return self._to_dict(instance) if instance else None
        except Exception as e:
            logger.error(f"Error finding summary by session_id: {e}")
            return None
    
    def find_recent_summaries(self, main_user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Find recent summaries for a main user"""
        return self.find_all(
            {'main_user_id': main_user_id},
            limit=limit,
            sort_by='created_at'
        )
    
    def find_by_participants(self, participants: List[str], main_user_id: int) -> List[Dict[str, Any]]:
        """Find summaries involving specific participants"""
        try:
            with get_db() as db:
                # This would need to be implemented based on how participants are stored
                # For now, return all summaries for the user
                return self.find_all({'main_user_id': main_user_id})
        except Exception as e:
            logger.error(f"Error finding summaries by participants: {e}")
            return []

class AudioFileRepository(BaseRepository):
    """Audio file repository"""
    
    def __init__(self):
        super().__init__(AudioFile)
    
    def find_by_session_id(self, session_id: str) -> List[Dict[str, Any]]:
        """Find all audio files for a session"""
        try:
            with get_db() as db:
                # First find the conversation session
                session = db.query(ConversationSession).filter(
                    ConversationSession.session_id == session_id
                ).first()
                if not session:
                    return []
                
                # Then find the audio files
                instances = db.query(AudioFile).filter(
                    AudioFile.conversation_session_id == session.id
                ).all()
                return [self._to_dict(instance) for instance in instances]
        except Exception as e:
            logger.error(f"Error finding audio files by session_id: {e}")
            return []
    
    def find_by_username(self, session_id: str, username: str) -> List[Dict[str, Any]]:
        """Find audio files for a specific user in a session"""
        try:
            with get_db() as db:
                # First find the conversation session
                session = db.query(ConversationSession).filter(
                    ConversationSession.session_id == session_id
                ).first()
                if not session:
                    return []
                
                # Then find the audio files
                instances = db.query(AudioFile).filter(
                    and_(
                        AudioFile.conversation_session_id == session.id,
                        AudioFile.username == username
                    )
                ).all()
                return [self._to_dict(instance) for instance in instances]
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
            with get_db() as db:
                # First find the conversation session
                session = db.query(ConversationSession).filter(
                    ConversationSession.session_id == session_id
                ).first()
                if not session:
                    return []
                
                # Then find the completed audio files
                instances = db.query(AudioFile).filter(
                    and_(
                        AudioFile.conversation_session_id == session.id,
                        AudioFile.status == 'completed'
                    )
                ).all()
                return [self._to_dict(instance) for instance in instances]
        except Exception as e:
            logger.error(f"Error finding completed audio files: {e}")
            return []

class AssistantSessionRepository(BaseRepository):
    """Assistant session repository"""
    
    def __init__(self):
        super().__init__(AssistantSession)
    
    def find_by_session_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Find assistant session by session ID"""
        try:
            with get_db() as db:
                instance = db.query(AssistantSession).filter(
                    AssistantSession.session_id == session_id
                ).first()
                return self._to_dict(instance) if instance else None
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
        """Add a message to assistant session"""
        try:
            with get_db() as db:
                instance = db.query(AssistantSession).filter(
                    AssistantSession.session_id == session_id
                ).first()
                if not instance:
                    return False
                
                # Get current messages
                messages = instance.messages or []
                messages.append(message)
                instance.messages = messages
                instance.updated_at = datetime.utcnow()
                
                db.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding message to assistant session: {e}")
            return False

class CalendarEventRepository(BaseRepository):
    """Calendar event repository"""
    
    def __init__(self):
        super().__init__(CalendarEvent)
    
    def find_by_user_id(self, main_user_id: int) -> List[Dict[str, Any]]:
        """Find events for a user"""
        return self.find_all(
            {'main_user_id': main_user_id},
            sort_by='start_time'
        )
    
    def find_upcoming_events(self, main_user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Find upcoming events for a user"""
        try:
            with get_db() as db:
                now = datetime.utcnow()
                instances = db.query(CalendarEvent).filter(
                    and_(
                        CalendarEvent.main_user_id == main_user_id,
                        CalendarEvent.start_time >= now
                    )
                ).order_by(CalendarEvent.start_time).limit(limit).all()
                return [self._to_dict(instance) for instance in instances]
        except Exception as e:
            logger.error(f"Error finding upcoming events: {e}")
            return []
    
    def update_google_event_id(self, event_id: int, google_event_id: str) -> bool:
        """Update event with Google Calendar event ID"""
        return self.update(event_id, {
            'google_event_id': google_event_id,
            'status': 'created'
        })

class PlatformIntegrationRepository(BaseRepository):
    """Platform integration repository"""
    
    def __init__(self):
        super().__init__(PlatformIntegration)
    
    def find_by_user_and_platform(self, main_user_id: int, platform: str) -> Optional[Dict[str, Any]]:
        """Find integration by user ID and platform"""
        try:
            with get_db() as db:
                instance = db.query(PlatformIntegration).filter(
                    and_(
                        PlatformIntegration.main_user_id == main_user_id,
                        PlatformIntegration.platform == platform
                    )
                ).first()
                return self._to_dict(instance) if instance else None
        except Exception as e:
            logger.error(f"Error finding integration by user and platform: {e}")
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
        return self.update(integration_id, {'last_sync': last_sync}) 