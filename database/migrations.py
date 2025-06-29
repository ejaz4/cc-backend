"""
Database migration utilities for Supabase.
Handles sample data creation using Supabase SDK.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, List

from .connection import init_database, get_current_timestamp
from .repository import (
    ConversationSessionRepository, MainUserRepository, SummaryRepository,
    AudioFileRepository, AssistantSessionRepository, CalendarEventRepository,
    UserProfileRepository, PlatformIntegrationRepository
)

logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """Handles database migration and setup for Supabase"""
    
    def __init__(self):
        self.conversation_repo = ConversationSessionRepository()
        self.main_user_repo = MainUserRepository()
        self.summary_repo = SummaryRepository()
        self.audio_repo = AudioFileRepository()
        self.assistant_repo = AssistantSessionRepository()
        self.calendar_repo = CalendarEventRepository()
        self.user_profile_repo = UserProfileRepository()
        self.platform_integration_repo = PlatformIntegrationRepository()
    
    def setup_database(self):
        """Initialize Supabase connection"""
        try:
            logger.info("Initializing Supabase connection...")
            init_database()
            
            logger.info("Supabase connection established successfully")
            return True
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            return False
    
    def create_sample_data(self):
        """Create sample data for testing using Supabase SDK"""
        try:
            logger.info("Creating sample data...")
            
            # Create a sample main user
            main_user_data = {
                'username': 'test_user',
                'email': 'test@example.com',
                'voice_id': 'pNInz6obpgDQGcFmaJgB',
                'voice_name': 'Adam',
                'is_active': True,
                'preferences': {
                    'summary_length': 'medium',
                    'voice_style': 'natural'
                },
                'connected_platforms': ['whatsapp', 'instagram'],
                'platform_credentials': {},
                'default_voice_settings': {
                    'stability': 0.5,
                    'similarity_boost': 0.75
                },
                'summary_preferences': {
                    'include_emotions': True,
                    'include_relationships': True
                },
                'privacy_settings': {
                    'share_analytics': False,
                    'store_audio': True
                }
            }
            
            main_user_id = self.main_user_repo.create(main_user_data)
            if not main_user_id:
                logger.error("Failed to create sample main user")
                return False
            
            logger.info(f"Created sample main user with ID: {main_user_id}")
            
            # Create sample user profiles
            sample_profiles = [
                {
                    'username': 'mom',
                    'platform': 'whatsapp',
                    'main_user_id': main_user_id,
                    'display_name': 'Mom',
                    'voice_id': 'EXAVITQu4vr4xnSDxMaL',
                    'voice_name': 'Bella',
                    'personality_traits': ['caring', 'supportive', 'loving'],
                    'interests': ['family', 'cooking', 'health'],
                    'communication_style': {
                        'formality': 'casual',
                        'emoji_usage': 'moderate',
                        'response_time': 'fast'
                    },
                    'relationship_type': 'family',
                    'trust_score': 0.95,
                    'frequency_score': 0.8
                },
                {
                    'username': 'best_friend',
                    'platform': 'instagram',
                    'main_user_id': main_user_id,
                    'display_name': 'Sarah',
                    'voice_id': '21m00Tcm4TlvDq8ikWAM',
                    'voice_name': 'Rachel',
                    'personality_traits': ['funny', 'loyal', 'adventurous'],
                    'interests': ['travel', 'music', 'photography'],
                    'communication_style': {
                        'formality': 'very_casual',
                        'emoji_usage': 'heavy',
                        'response_time': 'medium'
                    },
                    'relationship_type': 'friend',
                    'trust_score': 0.9,
                    'frequency_score': 0.7
                }
            ]
            
            for profile_data in sample_profiles:
                profile_id = self.user_profile_repo.create(profile_data)
                if profile_id:
                    logger.info(f"Created sample profile: {profile_data['display_name']}")
            
            # Create sample conversation session
            conversation_data = {
                'platform': 'whatsapp',
                'group_name': 'Family Group',
                'main_user': 'test_user',
                'status': 'uploaded',
                'total_messages': 2,
                'conversation_type': 'group',
                'platform_specific_data': {
                    'whatsapp_data': {
                        'export_date': '2024-01-15',
                        'participant_count': 4
                    }
                },
                'date_range': {
                    'start_date': '2024-01-15T00:00:00Z',
                    'end_date': '2024-01-15T23:59:59Z'
                }
            }
            
            session_id = self.conversation_repo.create(conversation_data)
            if session_id:
                logger.info(f"Created sample conversation session with ID: {session_id}")
                
                # Add sample messages
                sample_messages = [
                    {
                        'conversation_session_id': session_id,
                        'username': 'mom',
                        'content': 'Hey everyone! How\'s your day going? 😊',
                        'timestamp': '2024-01-15T10:30:00Z',
                        'message_type': 'text',
                        'is_important': False,
                        'platform_specific_data': {
                            'whatsapp_data': {
                                'message_id': 'msg_001',
                                'is_forwarded': False
                            }
                        }
                    },
                    {
                        'conversation_session_id': session_id,
                        'username': 'test_user',
                        'content': 'Pretty good! Just finished my project. How about you?',
                        'timestamp': '2024-01-15T10:32:00Z',
                        'message_type': 'text',
                        'is_important': False,
                        'platform_specific_data': {
                            'whatsapp_data': {
                                'message_id': 'msg_002',
                                'is_forwarded': False
                            }
                        }
                    }
                ]
                
                # Get the session to add messages
                session = self.conversation_repo.find_by_id(session_id)
                if session:
                    for message_data in sample_messages:
                        self.conversation_repo.add_message(session['session_id'], message_data)
                    
                    logger.info("Added sample messages to conversation")
            
            logger.info("Sample data creation completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Sample data creation failed: {e}")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data from database"""
        try:
            logger.info("Cleaning up test data...")
            
            # Delete test user and all related data
            test_user = self.main_user_repo.find_by_username('test_user')
            if test_user:
                user_id = test_user['id']
                
                # Delete related data first (foreign key constraints)
                # This would need to be done in the correct order based on your schema
                # For now, we'll just delete the main user and let Supabase handle cascading
                self.main_user_repo.delete(user_id)
                logger.info("Cleaned up test data successfully")
            
            return True
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return False

def run_migration():
    """Run the database migration"""
    migrator = DatabaseMigrator()
    
    # Setup database connection
    if not migrator.setup_database():
        logger.error("Failed to setup database")
        return False
    
    # Create sample data
    if not migrator.create_sample_data():
        logger.error("Failed to create sample data")
        return False
    
    logger.info("Migration completed successfully")
    return True

if __name__ == "__main__":
    run_migration() 