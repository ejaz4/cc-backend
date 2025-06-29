import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from collections import Counter

from database.repository import ConversationSessionRepository, UserProfileRepository, MainUserRepository
from services.whatsapp_parser import WhatsAppParser

logger = logging.getLogger(__name__)

class ConversationProcessor:
    """Service for processing conversations from multiple platforms and creating user profiles"""
    
    def __init__(self):
        self.conversation_repo = ConversationSessionRepository()
        self.user_profile_repo = UserProfileRepository()
        self.main_user_repo = MainUserRepository()
        self.whatsapp_parser = WhatsAppParser()
    
    def process_conversation(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process conversation data from any platform
        
        Args:
            conversation_data: JSON data containing conversation information
            
        Returns:
            Processing result with session_id and user profiles
        """
        try:
            # Extract basic information
            platform = conversation_data.get('platform', 'unknown')
            main_user = conversation_data.get('main_user')
            group_name = conversation_data.get('group_name', 'Unknown Group')
            conversation_type = conversation_data.get('conversation_type', 'group')
            
            if not main_user:
                return {'error': 'main_user is required'}
            
            # Process messages based on platform
            if platform == 'whatsapp':
                messages = self._process_whatsapp_messages(conversation_data)
            elif platform == 'instagram':
                messages = self._process_instagram_messages(conversation_data)
            elif platform == 'discord':
                messages = self._process_discord_messages(conversation_data)
            else:
                messages = self._process_generic_messages(conversation_data)
            
            if not messages:
                return {'error': 'No valid messages found'}
            
            # Extract participants and create user profiles
            participants = self._extract_participants(messages, main_user)
            user_profiles = self._create_user_profiles(participants, platform, main_user, messages)
            
            # Create conversation session
            session_data = {
                'platform': platform,
                'group_name': group_name,
                'main_user': main_user,
                'messages': messages,
                'participants': participants,
                'status': 'uploaded',
                'total_messages': len(messages),
                'conversation_type': conversation_type,
                'platform_specific_data': conversation_data.get('platform_specific_data', {}),
                'date_range': self._calculate_date_range(messages)
            }
            
            session_id = self.conversation_repo.create(session_data)
            
            # Update main user's connected platforms
            self.main_user_repo.add_connected_platform(main_user, platform)
            
            return {
                'success': True,
                'session_id': session_data['session_id'],
                'participants': participants,
                'user_profiles_created': len(user_profiles),
                'total_messages': len(messages),
                'date_range': session_data['date_range']
            }
            
        except Exception as e:
            logger.error(f"Error processing conversation: {e}")
            return {'error': str(e)}
    
    def _process_whatsapp_messages(self, conversation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process WhatsApp messages"""
        if 'conversation' in conversation_data:
            # If conversation is provided as text, parse it
            return self.whatsapp_parser.parse_chat_content(conversation_data['conversation'])['messages']
        elif 'messages' in conversation_data:
            # If messages are already structured
            return conversation_data['messages']
        else:
            return []
    
    def _process_instagram_messages(self, conversation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process Instagram messages"""
        messages = []
        
        if 'messages' in conversation_data:
            for msg in conversation_data['messages']:
                message = {
                    'username': msg.get('username', 'Unknown'),
                    'content': msg.get('content', ''),
                    'timestamp': self._parse_timestamp(msg.get('timestamp')),
                    'message_type': msg.get('type', 'text'),
                    'is_important': self._is_important_message(msg.get('content', '')),
                    'platform_specific_data': {
                        'instagram_data': {
                            'message_id': msg.get('message_id'),
                            'is_dm': msg.get('is_dm', False),
                            'has_media': msg.get('has_media', False),
                            'reactions': msg.get('reactions', [])
                        }
                    },
                    'reactions': msg.get('reactions', []),
                    'reply_to': msg.get('reply_to')
                }
                messages.append(message)
        
        return messages
    
    def _process_discord_messages(self, conversation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process Discord messages"""
        messages = []
        
        if 'messages' in conversation_data:
            for msg in conversation_data['messages']:
                message = {
                    'username': msg.get('username', 'Unknown'),
                    'content': msg.get('content', ''),
                    'timestamp': self._parse_timestamp(msg.get('timestamp')),
                    'message_type': msg.get('type', 'text'),
                    'is_important': self._is_important_message(msg.get('content', '')),
                    'platform_specific_data': {
                        'discord_data': {
                            'message_id': msg.get('message_id'),
                            'channel_id': msg.get('channel_id'),
                            'guild_id': msg.get('guild_id'),
                            'is_bot': msg.get('is_bot', False),
                            'attachments': msg.get('attachments', [])
                        }
                    },
                    'reactions': msg.get('reactions', []),
                    'reply_to': msg.get('reply_to')
                }
                messages.append(message)
        
        return messages
    
    def _process_generic_messages(self, conversation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process generic messages from any platform"""
        messages = []
        
        if 'messages' in conversation_data:
            for msg in conversation_data['messages']:
                # Support both old format (username) and new format (sender)
                sender = msg.get('sender') or msg.get('username', 'Unknown')
                
                message = {
                    'username': sender,  # Keep username for backward compatibility
                    'sender': sender,    # Add sender field for new format
                    'content': msg.get('content', ''),
                    'timestamp': self._parse_timestamp(msg.get('timestamp')),
                    'message_type': msg.get('type', 'text'),
                    'is_important': self._is_important_message(msg.get('content', '')),
                    'platform_specific_data': {
                        'is_group': msg.get('isGroup', False),
                        'conversation_name': msg.get('conversationName', ''),
                        'app_id': msg.get('appId', ''),
                        **msg.get('platform_specific_data', {})
                    },
                    'reactions': msg.get('reactions', []),
                    'reply_to': msg.get('reply_to')
                }
                messages.append(message)
        
        return messages
    
    def _extract_participants(self, messages: List[Dict[str, Any]], main_user: str) -> List[str]:
        """Extract unique participants from messages"""
        participants = set()
        for msg in messages:
            # Support both old format (username) and new format (sender)
            sender = msg.get('sender') or msg.get('username', '')
            if sender and sender != main_user:
                participants.add(sender)
        return list(participants)
    
    def _create_user_profiles(self, participants: List[str], platform: str, main_user: str, messages: List[Dict[str, Any]]) -> List[str]:
        """Create or update user profiles for participants"""
        created_profiles = []
        
        for participant in participants:
            # Get messages from this participant (support both sender and username fields)
            participant_messages = [
                msg for msg in messages 
                if (msg.get('sender') == participant or msg.get('username') == participant)
            ]
            
            if not participant_messages:
                continue
            
            # Analyze personality and communication style
            personality_data = self._analyze_personality(participant_messages)
            
            # Create profile data
            profile_data = {
                'username': participant,
                'platform': platform,
                'main_user': main_user,
                'display_name': participant,
                'personality_traits': personality_data['traits'],
                'interests': personality_data['interests'],
                'communication_style': personality_data['communication_style'],
                'frequency_score': self._calculate_frequency_score(participant_messages, messages),
                'last_interaction': max(msg['timestamp'] for msg in participant_messages),
                'relationship_type': self._determine_relationship_type(participant_messages),
                'trust_score': self._calculate_trust_score(participant_messages),
                'preferred_topics': personality_data['preferred_topics'],
                'avoided_topics': personality_data['avoided_topics']
            }
            
            # Create or update profile
            profile_id = self.user_profile_repo.create_or_update_profile(profile_data)
            if profile_id:
                created_profiles.append(profile_id)
        
        return created_profiles
    
    def _analyze_personality(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze personality traits from messages"""
        all_content = ' '.join([msg.get('content', '') for msg in messages])
        content_lower = all_content.lower()
        
        # Personality traits
        traits = []
        if any(word in content_lower for word in ['haha', 'lol', '😂', '😄', 'funny']):
            traits.append('humorous')
        if any(word in content_lower for word in ['thanks', 'thank you', 'appreciate']):
            traits.append('grateful')
        if any(word in content_lower for word in ['sorry', 'apologize', 'my bad']):
            traits.append('apologetic')
        if any(word in content_lower for word in ['help', 'support', 'assist']):
            traits.append('helpful')
        if any(word in content_lower for word in ['work', 'job', 'career', 'business']):
            traits.append('professional')
        
        # Interests (topics they talk about)
        interests = []
        interest_keywords = {
            'technology': ['tech', 'coding', 'programming', 'computer', 'software'],
            'sports': ['football', 'basketball', 'soccer', 'game', 'match'],
            'music': ['song', 'music', 'concert', 'artist', 'album'],
            'travel': ['travel', 'trip', 'vacation', 'flight', 'hotel'],
            'food': ['food', 'restaurant', 'cooking', 'dinner', 'lunch'],
            'movies': ['movie', 'film', 'watch', 'cinema', 'series']
        }
        
        for interest, keywords in interest_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                interests.append(interest)
        
        # Communication style
        communication_style = {
            'emoji_heavy': len(re.findall(r'[😀-🙏🌀-🗿]', all_content)) > len(messages) * 0.5,
            'formal': any(word in content_lower for word in ['sir', 'madam', 'please', 'kindly']),
            'casual': any(word in content_lower for word in ['hey', 'yo', 'sup', 'cool']),
            'question_heavy': all_content.count('?') > len(messages) * 0.3,
            'exclamation_heavy': all_content.count('!') > len(messages) * 0.2
        }
        
        # Preferred and avoided topics
        preferred_topics = interests[:3]  # Top 3 interests
        avoided_topics = []  # Could be enhanced with more analysis
        
        return {
            'traits': traits,
            'interests': interests,
            'communication_style': communication_style,
            'preferred_topics': preferred_topics,
            'avoided_topics': avoided_topics
        }
    
    def _calculate_frequency_score(self, participant_messages: List[Dict[str, Any]], all_messages: List[Dict[str, Any]]) -> float:
        """Calculate interaction frequency score"""
        if not all_messages:
            return 0.0
        
        participant_count = len(participant_messages)
        total_count = len(all_messages)
        
        # Normalize to 0-1 scale
        return min(participant_count / total_count * 10, 1.0)
    
    def _determine_relationship_type(self, messages: List[Dict[str, Any]]) -> str:
        """Determine relationship type based on message content"""
        all_content = ' '.join([msg.get('content', '') for msg in messages]).lower()
        
        # Family indicators
        if any(word in all_content for word in ['mom', 'dad', 'family', 'home', 'parents']):
            return 'family'
        
        # Work indicators
        if any(word in all_content for word in ['work', 'office', 'meeting', 'project', 'boss']):
            return 'colleague'
        
        # Close friend indicators
        if any(word in all_content for word in ['best', 'close', 'love', 'miss', 'heart']):
            return 'close_friend'
        
        return 'friend'
    
    def _calculate_trust_score(self, messages: List[Dict[str, Any]]) -> float:
        """Calculate trust score based on message content"""
        all_content = ' '.join([msg.get('content', '') for msg in messages]).lower()
        
        # Positive trust indicators
        positive_indicators = ['trust', 'reliable', 'honest', 'confidential', 'secret']
        positive_count = sum(1 for indicator in positive_indicators if indicator in all_content)
        
        # Negative trust indicators
        negative_indicators = ['lie', 'fake', 'untrustworthy', 'suspicious']
        negative_count = sum(1 for indicator in negative_indicators if indicator in all_content)
        
        # Base score of 0.5, adjust based on indicators
        base_score = 0.5
        adjustment = (positive_count - negative_count) * 0.1
        
        return max(0.0, min(1.0, base_score + adjustment))
    
    def _is_important_message(self, content: str) -> bool:
        """Determine if a message is important"""
        if not content:
            return False
        
        content_lower = content.lower()
        
        # Important keywords
        important_keywords = [
            'meeting', 'call', 'event', 'party', 'dinner', 'lunch', 'coffee',
            'deadline', 'due', 'urgent', 'important', 'reminder', 'schedule',
            'tomorrow', 'today', 'tonight', 'weekend', 'birthday', 'anniversary',
            'travel', 'flight', 'hotel', 'booking', 'reservation', 'appointment'
        ]
        
        # Check for important keywords
        for keyword in important_keywords:
            if keyword in content_lower:
                return True
        
        # Check for questions or exclamations
        if '?' in content or '!' in content:
            return True
        
        return False
    
    def _parse_timestamp(self, timestamp) -> datetime:
        """Parse timestamp from various formats"""
        if isinstance(timestamp, datetime):
            return timestamp
        elif isinstance(timestamp, (int, float)):
            # Handle Unix timestamp
            try:
                return datetime.fromtimestamp(timestamp)
            except (ValueError, OSError):
                return datetime.utcnow()
        elif isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                return datetime.utcnow()
        else:
            return datetime.utcnow()
    
    def _calculate_date_range(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate date range from messages"""
        if not messages:
            return {}
        
        timestamps = [msg.get('timestamp') for msg in messages if msg.get('timestamp')]
        if not timestamps:
            return {}
        
        start_date = min(timestamps)
        end_date = max(timestamps)
        
        return {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }
    
    def get_user_context(self, main_user: str, participant: str, platform: str = None) -> Dict[str, Any]:
        """Get context about a specific user for better summarization"""
        try:
            # Get user profile
            profile = self.user_profile_repo.find_by_username(participant, platform or 'any', main_user)
            
            # Get recent conversations with this user
            recent_sessions = self.conversation_repo.find_by_participant(participant, main_user)
            
            # Get recent summaries involving this user
            recent_summaries = self.user_profile_repo.find_by_main_user(main_user, platform)
            
            return {
                'profile': profile,
                'recent_conversations': len(recent_sessions),
                'last_interaction': profile.get('last_interaction') if profile else None,
                'relationship_type': profile.get('relationship_type') if profile else 'unknown',
                'trust_score': profile.get('trust_score') if profile else 0.5,
                'personality_traits': profile.get('personality_traits', []) if profile else [],
                'interests': profile.get('interests', []) if profile else []
            }
        except Exception as e:
            logger.error(f"Error getting user context: {e}")
            return {} 