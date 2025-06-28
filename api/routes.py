import os
import logging
from flask import Flask, request, jsonify, send_file, current_app
from flask_cors import CORS
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

from database.connection import connect_db
from database.repository import (
    ChatSessionRepository, UserRepository, SummaryRepository, 
    AudioFileRepository, AssistantSessionRepository, CalendarEventRepository
)
from services.whatsapp_parser import WhatsAppParser
from services.summarizer import ChatSummarizer
from services.elevenlabs_service import ElevenLabsService
from services.assistant_service import AssistantService

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
    
    # Initialize repositories
    chat_repo = ChatSessionRepository()
    user_repo = UserRepository()
    summary_repo = SummaryRepository()
    audio_repo = AudioFileRepository()
    assistant_repo = AssistantSessionRepository()
    calendar_repo = CalendarEventRepository()
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'WhatsApp Summarizer API'
        })
    
    @app.route('/api/upload', methods=['POST'])
    def upload_chat():
        """Upload and parse WhatsApp chat file"""
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
            
            # Create chat session
            chat_session_data = {
                'group_name': request.form.get('group_name', 'Unknown Group'),
                'session_id': session_id,
                'messages': parsed_data['messages'],
                'participants': parsed_data['participants'],
                'status': 'uploaded',
                'file_path': file_path,
                'total_messages': parsed_data['total_messages'],
                'date_range': parsed_data['date_range']
            }
            
            chat_id = chat_repo.create(chat_session_data)
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'chat_id': chat_id,
                'participants': parsed_data['participants'],
                'total_messages': parsed_data['total_messages'],
                'date_range': parsed_data['date_range']
            }), 201
            
        except Exception as e:
            logger.error(f"Error uploading chat: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/summarize/<session_id>', methods=['POST'])
    def summarize_chat(session_id):
        """Generate summary for a chat session"""
        try:
            # Get chat session
            chat_session = chat_repo.find_by_session_id(session_id)
            if not chat_session:
                return jsonify({'error': 'Chat session not found'}), 404
            
            # Update status to processing
            chat_repo.update_status(session_id, 'processing')
            
            # Generate summary
            summary_data = summarizer.generate_summary(
                chat_session['messages'],
                chat_session['participants']
            )
            
            if 'error' in summary_data:
                chat_repo.update_status(session_id, 'failed')
                return jsonify({'error': summary_data['error']}), 500
            
            # Save summary
            summary_data['session_id'] = session_id
            summary_id = summary_repo.create(summary_data)
            
            # Update chat session status
            chat_repo.update_status(session_id, 'summarized')
            
            return jsonify({
                'success': True,
                'summary_id': summary_id,
                'summary_text': summary_data['summary_text'],
                'script_lines': summary_data['script_lines'],
                'participants': summary_data['participants']
            }), 200
            
        except Exception as e:
            logger.error(f"Error summarizing chat: {e}")
            chat_repo.update_status(session_id, 'failed')
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/generate-audio/<session_id>', methods=['POST'])
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
            
            # Generate audio files
            audio_results = elevenlabs_service.generate_batch_speech(script_lines, session_id)
            
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
                        'elevenlabs_generation_id': result.get('generation_id')
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
            
            # Update chat session status
            chat_repo.update_status(session_id, 'completed')
            
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
    
    @app.route('/api/sessions/<session_id>', methods=['GET'])
    def get_session(session_id):
        """Get chat session details"""
        try:
            # Get chat session
            chat_session = chat_repo.find_by_session_id(session_id)
            if not chat_session:
                return jsonify({'error': 'Session not found'}), 404
            
            # Get summary
            summary = summary_repo.find_by_session_id(session_id)
            
            # Get audio files
            audio_files = audio_repo.find_by_session_id(session_id)
            
            return jsonify({
                'session': chat_session,
                'summary': summary,
                'audio_files': audio_files
            }), 200
            
        except Exception as e:
            logger.error(f"Error getting session: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/sessions', methods=['GET'])
    def list_sessions():
        """List all chat sessions"""
        try:
            limit = request.args.get('limit', 10, type=int)
            sessions = chat_repo.find_recent_sessions(limit)
            
            return jsonify({
                'sessions': sessions,
                'total': len(sessions)
            }), 200
            
        except Exception as e:
            logger.error(f"Error listing sessions: {e}")
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
            
            # Get context (calendar events, etc.)
            context = {}
            if user_id != 'default_user':
                upcoming_events = assistant_service.get_upcoming_events(user_id, max_results=5)
                if upcoming_events.get('success'):
                    context['upcoming_events'] = upcoming_events['events']
            
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