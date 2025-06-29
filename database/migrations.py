"""
Database migration utilities for MongoDB to Supabase transition
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any, List

from .connection import init_database, create_tables
from .repository import (
    ConversationSessionRepository, MainUserRepository, SummaryRepository,
    AudioFileRepository, AssistantSessionRepository, CalendarEventRepository,
    UserProfileRepository, PlatformIntegrationRepository
)

logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """Handles database migration and setup"""
    
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
        """Initialize database and create tables"""
        try:
            logger.info("Initializing database...")
            init_database()
            
            logger.info("Creating tables...")
            create_tables()
            
            logger.info("Database setup completed successfully")
            return True
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            return False
    
    def create_sample_data(self):
        """Create sample data for testing"""
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
                        'timestamp': datetime(2024, 1, 15, 10, 30, 0),
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
                        'timestamp': datetime(2024, 1, 15, 10, 32, 0),
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
                
                for message_data in sample_messages:
                    self.conversation_repo.add_message(
                        self.conversation_repo.find_by_id(session_id)['session_id'],
                        message_data
                    )
                
                logger.info("Added sample messages to conversation")
            
            logger.info("Sample data creation completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Sample data creation failed: {e}")
            return False
    
    def validate_database(self):
        """Validate database connection and structure"""
        try:
            logger.info("Validating database...")
            
            # Test basic operations
            test_user = self.main_user_repo.find_by_username('test_user')
            if test_user:
                logger.info("✓ Database validation successful")
                return True
            else:
                logger.warning("No test user found - database may be empty")
                return True
                
        except Exception as e:
            logger.error(f"Database validation failed: {e}")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data"""
        try:
            logger.info("Cleaning up test data...")
            
            # Find and delete test user
            test_user = self.main_user_repo.find_by_username('test_user')
            if test_user:
                self.main_user_repo.delete(test_user['id'])
                logger.info("Cleaned up test user")
            
            logger.info("Test data cleanup completed")
            return True
            
        except Exception as e:
            logger.error(f"Test data cleanup failed: {e}")
            return False

def run_migration():
    """Run the complete migration process"""
    migrator = DatabaseMigrator()
    
    print("🚀 Starting database migration...")
    
    # Setup database
    if not migrator.setup_database():
        print("❌ Database setup failed")
        return False
    
    # Validate database
    if not migrator.validate_database():
        print("❌ Database validation failed")
        return False
    
    # Create sample data (optional)
    create_samples = input("Create sample data? (y/n): ").lower().strip()
    if create_samples == 'y':
        if not migrator.create_sample_data():
            print("❌ Sample data creation failed")
            return False
    
    print("✅ Database migration completed successfully!")
    return True

if __name__ == '__main__':
    run_migration() 