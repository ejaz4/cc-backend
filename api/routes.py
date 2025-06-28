import os
import logging
from flask import Flask, request, jsonify, send_file, current_app
from flask_cors import CORS
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

from database.connection import connect_db
from database.repository import (
    ConversationSessionRepository, MainUserRepository, SummaryRepository, 
    AudioFileRepository, AssistantSessionRepository, CalendarEventRepository,
    UserProfileRepository, PlatformIntegrationRepository
)
from services.whatsapp_parser import WhatsAppParser
from services.summarizer import ChatSummarizer
from services.elevenlabs_service import ElevenLabsService
from services.assistant_service import AssistantService
from services.conversation_processor import ConversationProcessor

logger = logging.getLogger(__name__)

def create_app():
    """Create and configure Flask app"""
    app = Flask(__name__)
    CORS(app)
    
    # Configure app
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Initialize database connection
    connect_db()
    
    # Initialize services
    whatsapp_parser = WhatsAppParser()
    summarizer = ChatSummarizer()
    elevenlabs_service = ElevenLabsService()
    assistant_service = AssistantService()
    conversation_processor = ConversationProcessor()
    
    # Initialize repositories
    conversation_repo = ConversationSessionRepository()
    main_user_repo = MainUserRepository()
    summary_repo = SummaryRepository()
    audio_repo = AudioFileRepository()
    assistant_repo = AssistantSessionRepository()
    calendar_repo = CalendarEventRepository()
    user_profile_repo = UserProfileRepository()
    platform_integration_repo = PlatformIntegrationRepository()
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'Multi-Platform Conversation Summarizer API'
        })
    
    @app.route('/api/conversations/upload', methods=['POST'])
    def upload_conversation():
        """Upload conversation data from any platform"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Validate required fields
            required_fields = ['platform', 'main_user']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'{field} is required'}), 400
            
            # Process conversation
            result = conversation_processor.process_conversation(data)
            
            if 'error' in result:
                return jsonify({'error': result['error']}), 500
            
            return jsonify(result), 201
            
        except Exception as e:
            logger.error(f"Error uploading conversation: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/conversations/upload-file', methods=['POST'])
    def upload_conversation_file():
        """Upload conversation file (legacy support for WhatsApp)"""
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Validate file type
            if not file.filename.endswith('.txt'):
                return jsonify({'error': 'Only .txt files are supported'}), 400
            
            # Generate session ID
            session_id = str(uuid.uuid4())
            
            # Save file
            filename = secure_filename(f"{session_id}_{file.filename}")
            file_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)
            
            # Parse chat content
            parsed_data = whatsapp_parser.parse_chat_file(file_path)
            
            if 'error' in parsed_data:
                return jsonify({'error': parsed_data['error']}), 500
            
            # Create conversation data
            conversation_data = {
                'platform': 'whatsapp',
                'main_user': request.form.get('main_user', 'unknown_user'),
                'group_name': request.form.get('group_name', 'Unknown Group'),
                'conversation': file.read().decode('utf-8'),
                'conversation_type': 'group'
            }
            
            # Process conversation
            result = conversation_processor.process_conversation(conversation_data)
            
            if 'error' in result:
                return jsonify({'error': result['error']}), 500
            
            return jsonify(result), 201
            
        except Exception as e:
            logger.error(f"Error uploading conversation file: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/conversations/<session_id>/summarize', methods=['POST'])
    def summarize_conversation(session_id):
        """Generate summary for a conversation session"""
        try:
            # Get conversation session
            conversation_session = conversation_repo.find_by_session_id(session_id)
            if not conversation_session:
                return jsonify({'error': 'Conversation session not found'}), 404
            
            # Update status to processing
            conversation_repo.update_status(session_id, 'processing')
            
            # Get user profiles for context
            participants = conversation_session['participants']
            main_user = conversation_session['main_user']
            platform = conversation_session['platform']
            
            # Get user context for better summarization
            user_contexts = {}
            for participant in participants:
                context = conversation_processor.get_user_context(main_user, participant, platform)
                user_contexts[participant] = context
            
            # Generate summary with context
            summary_data = summarizer.generate_summary_with_context(
                conversation_session['messages'],
                participants,
                user_contexts
            )
            
            if 'error' in summary_data:
                conversation_repo.update_status(session_id, 'failed')
                return jsonify({'error': summary_data['error']}), 500
            
            # Save summary
            summary_data['session_id'] = session_id
            summary_data['main_user'] = main_user
            summary_id = summary_repo.create(summary_data)
            
            # Update conversation session status
            conversation_repo.update_status(session_id, 'summarized')
            
            return jsonify({
                'success': True,
                'summary_id': summary_id,
                'summary_text': summary_data['summary_text'],
                'script_lines': summary_data['script_lines'],
                'participants': summary_data['participants'],
                'personality_context': summary_data.get('personality_context', {})
            }), 200
            
        except Exception as e:
            logger.error(f"Error summarizing conversation: {e}")
            conversation_repo.update_status(session_id, 'failed')
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/conversations/<session_id>/generate-audio', methods=['POST'])
    def generate_audio(session_id):
        """Generate TTS audio for script lines"""
        try:
            # Get summary
            summary = summary_repo.find_by_session_id(session_id)
            if not summary:
                return jsonify({'error': 'Summary not found'}), 404
            
            script_lines = summary.get('script_lines', [])
            if not script_lines:
                return jsonify({'error': 'No script lines found'}), 400
            
            # Get conversation session for context
            conversation_session = conversation_repo.find_by_session_id(session_id)
            if not conversation_session:
                return jsonify({'error': 'Conversation session not found'}), 404
            
            # Get user profiles for voice assignment
            participants = conversation_session['participants']
            main_user = conversation_session['main_user']
            platform = conversation_session['platform']
            
            # Generate audio files with personality-based voice settings
            audio_results = elevenlabs_service.generate_batch_speech_with_profiles(
                script_lines, 
                session_id, 
                participants, 
                main_user, 
                platform
            )
            
            # Save audio file records
            audio_files = []
            for result in audio_results:
                if result['success']:
                    audio_data = {
                        'session_id': session_id,
                        'username': result['username'],
                        'line_number': result['line_number'],
                        'file_path': result['file_path'],
                        'file_name': result['filename'],
                        'voice_id': result.get('voice_id'),
                        'duration': result.get('duration'),
                        'file_size': result.get('file_size'),
                        'status': 'completed',
                        'elevenlabs_generation_id': result.get('generation_id'),
                        'voice_settings': result.get('voice_settings', {}),
                        'emotion_context': result.get('emotion_context', {})
                    }
                    audio_id = audio_repo.create(audio_data)
                    audio_files.append({
                        'audio_id': audio_id,
                        'username': result['username'],
                        'filename': result['filename'],
                        'file_path': result['file_path']
                    })
                else:
                    # Save failed audio record
                    audio_data = {
                        'session_id': session_id,
                        'username': result['username'],
                        'line_number': result['line_number'],
                        'file_name': result['filename'],
                        'status': 'failed',
                        'error_message': result.get('error')
                    }
                    audio_repo.create(audio_data)
            
            # Update conversation session status
            conversation_repo.update_status(session_id, 'completed')
            
            return jsonify({
                'success': True,
                'audio_files': audio_files,
                'total_generated': len([r for r in audio_results if r['success']]),
                'total_failed': len([r for r in audio_results if not r['success']])
            }), 200
            
        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/audio/<session_id>/<filename>', methods=['GET'])
    def serve_audio(session_id, filename):
        """Serve audio files"""
        try:
            # Validate filename
            if not filename.endswith('.mp3'):
                return jsonify({'error': 'Invalid file type'}), 400
            
            # Construct file path
            file_path = os.path.join(
                current_app.config.get('AUDIO_FOLDER', 'audio'),
                session_id,
                filename
            )
            
            if not os.path.exists(file_path):
                return jsonify({'error': 'Audio file not found'}), 404
            
            return send_file(file_path, mimetype='audio/mpeg')
            
        except Exception as e:
            logger.error(f"Error serving audio: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/conversations/<session_id>', methods=['GET'])
    def get_conversation(session_id):
        """Get conversation session details"""
        try:
            # Get conversation session
            conversation_session = conversation_repo.find_by_session_id(session_id)
            if not conversation_session:
                return jsonify({'error': 'Session not found'}), 404
            
            # Get summary
            summary = summary_repo.find_by_session_id(session_id)
            
            # Get audio files
            audio_files = audio_repo.find_by_session_id(session_id)
            
            return jsonify({
                'conversation': conversation_session,
                'summary': summary,
                'audio_files': audio_files
            }), 200
            
        except Exception as e:
            logger.error(f"Error getting conversation: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/conversations', methods=['GET'])
    def list_conversations():
        """List all conversation sessions for a user"""
        try:
            main_user = request.args.get('main_user')
            platform = request.args.get('platform')
            limit = request.args.get('limit', 10, type=int)
            
            if not main_user:
                return jsonify({'error': 'main_user parameter is required'}), 400
            
            filter_dict = {'main_user': main_user}
            if platform:
                filter_dict['platform'] = platform
            
            conversations = conversation_repo.find_all(filter_dict, limit=limit, sort_by='created_at')
            
            return jsonify({
                'conversations': conversations,
                'total': len(conversations)
            }), 200
            
        except Exception as e:
            logger.error(f"Error listing conversations: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/users/profiles', methods=['GET'])
    def get_user_profiles():
        """Get user profiles for a main user"""
        try:
            main_user = request.args.get('main_user')
            platform = request.args.get('platform')
            relationship_type = request.args.get('relationship_type')
            
            if not main_user:
                return jsonify({'error': 'main_user parameter is required'}), 400
            
            filter_dict = {'main_user': main_user}
            if platform:
                filter_dict['platform'] = platform
            if relationship_type:
                filter_dict['relationship_type'] = relationship_type
            
            profiles = user_profile_repo.find_all(filter_dict)
            
            return jsonify({
                'profiles': profiles,
                'total': len(profiles)
            }), 200
            
        except Exception as e:
            logger.error(f"Error getting user profiles: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/users/profiles/<profile_id>', methods=['PUT'])
    def update_user_profile(profile_id):
        """Update user profile"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            success = user_profile_repo.update(profile_id, data)
            
            if success:
                return jsonify({'success': True, 'message': 'Profile updated successfully'}), 200
            else:
                return jsonify({'error': 'Failed to update profile'}), 500
                
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/users/profiles/frequent', methods=['GET'])
    def get_frequent_contacts():
        """Get most frequent contacts for a user"""
        try:
            main_user = request.args.get('main_user')
            limit = request.args.get('limit', 10, type=int)
            
            if not main_user:
                return jsonify({'error': 'main_user parameter is required'}), 400
            
            profiles = user_profile_repo.find_frequent_contacts(main_user, limit)
            
            return jsonify({
                'profiles': profiles,
                'total': len(profiles)
            }), 200
            
        except Exception as e:
            logger.error(f"Error getting frequent contacts: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/assistant/chat', methods=['POST'])
    def assistant_chat():
        """Chat with assistant"""
        try:
            data = request.get_json()
            message = data.get('message')
            user_id = data.get('user_id', 'default_user')
            session_id = data.get('session_id')
            
            if not message:
                return jsonify({'error': 'Message is required'}), 400
            
            # Get or create assistant session
            if session_id:
                assistant_session = assistant_repo.find_by_session_id(session_id)
                if not assistant_session:
                    return jsonify({'error': 'Assistant session not found'}), 404
            else:
                # Create new session
                session_data = {
                    'user_id': user_id,
                    'session_id': str(uuid.uuid4()),
                    'messages': [],
                    'is_active': True
                }
                session_id = assistant_repo.create(session_data)
                assistant_session = assistant_repo.find_by_session_id(session_id)
            
            # Get context (calendar events, user profiles, etc.)
            context = {}
            if user_id != 'default_user':
                # Get upcoming events
                upcoming_events = assistant_service.get_upcoming_events(user_id, max_results=5)
                if upcoming_events.get('success'):
                    context['upcoming_events'] = upcoming_events['events']
                
                # Get user profiles for context
                user_profiles = user_profile_repo.find_by_main_user(user_id)
                context['user_profiles'] = user_profiles[:5]  # Top 5 profiles
            
            # Chat with assistant
            response = assistant_service.chat_with_assistant(message, session_id, context)
            
            # Save message to session
            message_data = {
                'role': 'user',
                'content': message,
                'timestamp': datetime.utcnow().isoformat()
            }
            assistant_repo.add_message(session_id, message_data)
            
            # Save assistant response
            response_data = {
                'role': 'assistant',
                'content': response.get('response', ''),
                'timestamp': datetime.utcnow().isoformat()
            }
            assistant_repo.add_message(session_id, response_data)
            
            return jsonify(response), 200
            
        except Exception as e:
            logger.error(f"Error in assistant chat: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/assistant/calendar/auth', methods=['POST'])
    def calendar_auth():
        """Get Google Calendar authorization URL"""
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            
            if not user_id:
                return jsonify({'error': 'User ID is required'}), 400
            
            auth_url = assistant_service.get_auth_url(user_id)
            
            if not auth_url:
                return jsonify({'error': 'Failed to generate auth URL'}), 500
            
            return jsonify({
                'auth_url': auth_url,
                'user_id': user_id
            }), 200
            
        except Exception as e:
            logger.error(f"Error getting calendar auth: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/assistant/calendar/callback', methods=['GET'])
    def calendar_callback():
        """Handle Google Calendar OAuth callback"""
        try:
            code = request.args.get('code')
            user_id = request.args.get('state')  # We'll use state parameter for user_id
            
            if not code or not user_id:
                return jsonify({'error': 'Missing code or user_id'}), 400
            
            success = assistant_service.handle_auth_callback(user_id, code)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Calendar connected successfully'
                }), 200
            else:
                return jsonify({'error': 'Failed to connect calendar'}), 500
                
        except Exception as e:
            logger.error(f"Error in calendar callback: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/assistant/calendar/events', methods=['POST'])
    def create_calendar_event():
        """Create calendar event"""
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            event_data = data.get('event_data', {})
            
            if not user_id:
                return jsonify({'error': 'User ID is required'}), 400
            
            # Parse datetime strings
            if 'start_time' in event_data:
                event_data['start_time'] = datetime.fromisoformat(event_data['start_time'])
            if 'end_time' in event_data:
                event_data['end_time'] = datetime.fromisoformat(event_data['end_time'])
            
            result = assistant_service.create_calendar_event(user_id, event_data)
            
            if result['success']:
                # Save to database
                calendar_event_data = {
                    'user_id': user_id,
                    'title': event_data.get('title', 'New Event'),
                    'start_time': event_data['start_time'],
                    'end_time': event_data.get('end_time'),
                    'description': event_data.get('description', ''),
                    'location': event_data.get('location', ''),
                    'google_event_id': result['event_id'],
                    'status': 'created'
                }
                calendar_repo.create(calendar_event_data)
            
            return jsonify(result), 200 if result['success'] else 500
            
        except Exception as e:
            logger.error(f"Error creating calendar event: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/assistant/calendar/events/<user_id>', methods=['GET'])
    def get_calendar_events(user_id):
        """Get user's calendar events"""
        try:
            max_results = request.args.get('max_results', 10, type=int)
            result = assistant_service.get_upcoming_events(user_id, max_results)
            
            return jsonify(result), 200 if result['success'] else 500
            
        except Exception as e:
            logger.error(f"Error getting calendar events: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/voices', methods=['GET'])
    def get_voices():
        """Get available ElevenLabs voices"""
        try:
            voices = elevenlabs_service.get_available_voices()
            
            return jsonify({
                'voices': voices,
                'total': len(voices)
            }), 200
            
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app 