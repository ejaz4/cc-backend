# Multi-Platform Conversation Summarizer API

A comprehensive **FastAPI** REST API backend for a Gen-Z-focused Android app that summarizes conversations from multiple platforms (WhatsApp, Instagram, Discord) and generates short voice message summaries using ElevenLabs TTS. The backend also integrates with ElevenLabs' conversational assistant and Google Calendar for event management.

## 🌟 Features

### Multi-Platform Support
- **WhatsApp**: Parse chat exports and extract conversations
- **Instagram**: Process direct messages and group chats
- **Discord**: Handle server conversations and DMs
- **Extensible**: Easy to add new platforms

### User Profile System
- **Personality Analysis**: Automatically analyze communication patterns
- **Voice Assignment**: Assign ElevenLabs voices based on personality traits
- **Relationship Context**: Track relationship types (family, friends, colleagues)
- **Trust Scoring**: Calculate trust levels based on interaction history
- **Interest Tracking**: Identify topics and interests from conversations

### AI-Powered Summarization
- **Context-Aware**: Uses user profiles for personalized summaries
- **Personality Preservation**: Maintains individual communication styles
- **Relationship Dynamics**: Highlights social interactions and dynamics
- **Tone Analysis**: Analyzes conversation mood and emotional context

### Voice Generation
- **Personality-Based Voices**: Automatically select voices based on user traits
- **Emotion Detection**: Adjust voice settings based on emotional content
- **Custom Voice Settings**: Stability, similarity boost, and style adjustments
- **Batch Processing**: Generate multiple audio files efficiently

### Assistant Integration
- **ElevenLabs Assistant**: Conversational AI with personality context
- **Calendar Management**: Create and manage events via Google Calendar
- **User Context**: Assistant uses conversation history and user profiles
- **Multi-Platform Context**: Access to conversations across all platforms

### Modern FastAPI Features
- **Automatic API Documentation**: Interactive Swagger UI at `/docs`
- **Type Safety**: Full type hints and Pydantic validation
- **Async Support**: High-performance async/await operations
- **Dependency Injection**: Clean service and repository injection
- **OpenAPI 3.0**: Standard API specification

## 🏗️ Architecture

### FastAPI Application Structure
```
cc-backend/
├── app.py                          # Main FastAPI application
├── main.py                         # Application entry point
├── config.py                       # Configuration management
├── api/
│   ├── models.py                   # Pydantic models for validation
│   ├── dependencies.py             # Dependency injection
│   └── routers/                    # Modular route organization
│       ├── conversations.py        # Conversation endpoints
│       ├── users.py               # User profile endpoints
│       ├── assistant.py           # AI assistant endpoints
│       ├── audio.py               # Audio file endpoints
│       └── voices.py              # ElevenLabs voice endpoints
├── database/                       # Supabase integration
├── services/                       # Business logic
└── requirements.txt               # Dependencies
```

### Database Models (PostgreSQL/Supabase)

#### Core Models
- **ConversationSession**: Multi-platform conversation sessions
- **PlatformMessage**: Generic message model for any platform
- **MainUser**: App owner with platform connections
- **UserProfile**: Profiles for people the main user talks to
- **Summary**: AI-generated summaries with personality context
- **AudioFile**: Generated TTS audio files with voice settings
- **AssistantSession**: Assistant conversation sessions
- **CalendarEvent**: Google Calendar events
- **PlatformIntegration**: Platform connection settings

#### User Profile Features
- Personality traits (friendly, professional, humorous, etc.)
- Communication style (emoji-heavy, formal, casual, etc.)
- Interests and preferred topics
- Relationship type and trust score
- Voice preferences and settings
- Interaction frequency and history

### Services

#### ConversationProcessor
- Multi-platform message parsing
- User profile creation and updates
- Personality analysis and trait extraction
- Relationship type detection
- Trust score calculation

#### ChatSummarizer
- Context-aware summarization using user profiles
- Personality-preserving dialogue generation
- Tone and emotion analysis
- Key update extraction
- Relationship dynamics analysis

#### ElevenLabsService
- Personality-based voice selection
- Emotion-aware voice settings
- Batch audio generation
- Voice cloning and management
- User voice preference management

#### AssistantService
- ElevenLabs conversational assistant
- Google Calendar integration
- User context integration
- Multi-platform conversation access

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Supabase account (PostgreSQL database)
- ElevenLabs API key
- OpenAI API key
- Google Calendar API (optional)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd cc-backend
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up Supabase**
   - Create a new project at [supabase.com](https://supabase.com)
   - Get your project URL and anon key from Settings > API
   - The database tables will be created automatically on first run

4. **Set up environment variables**
```bash
cp env.example .envpip uninstall Flask Flask-CORS Flask-RESTful
pip install fastapi uvicorn[standard] python-multipart httpx pydantic-settings
```

Edit `.env` with your configuration:
```env
# Database Configuration (Supabase PostgreSQL)
SUPABASE_URI=https://your-project-ref.supabase.co
SUPABASE_API_KEY=your-supabase-anon-key

# API Keys (Required)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Google Calendar (optional)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/assistant/calendar/callback

# File Storage
UPLOAD_FOLDER=uploads
AUDIO_FOLDER=audio

# FastAPI Configuration
FASTAPI_DEBUG=true
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
SECRET_KEY=your-secret-key-here

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CORS_ALLOW_CREDENTIALS=true
```

5. **Test the migration**
```bash
python test_fastapi_migration.py
```

6. **Run the application**
```bash
# Development
python main.py

# Or directly with uvicorn
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/health

## 📡 API Endpoints

### Conversation Management

#### Upload Conversation (Multi-Platform)
```http
POST /api/conversations/upload
Content-Type: application/json

{
  "platform": "whatsapp",
  "main_user": "john_doe",
  "group_name": "Family Group",
  "conversation_type": "group",
  "messages": [
    {
      "sender": "mom",
      "content": "Hey everyone! How's your day going?",
      "isGroup": true,
      "conversationName": "Family Group",
      "appId": "com.whatsapp.app",
      "timestamp": 1751167953
    }
  ]
}
```

**New JSON Format (Recommended):**
```json
{
  "platform": "whatsapp",
  "main_user": "john_doe",
  "group_name": "Keanu Czirjak",
  "conversation_type": "individual",
  "messages": [
    {
      "sender": "Keanu Czirjak",
      "content": "How are you",
      "isGroup": false,
      "conversationName": "Keanu Czirjak",
      "appId": "com.whatsapp.app",
      "timestamp": 1751167953
    },
    {
      "sender": "Keanu Czirjak",
      "content": "I am in london this week",
      "isGroup": false,
      "conversationName": "Keanu Czirjak",
      "appId": "com.whatsapp.app",
      "timestamp": 1751167980
    },
    {
      "sender": "Keanu Czirjak",
      "content": "let me know if i can see you soon",
      "isGroup": false,
      "conversationName": "Keanu Czirjak",
      "appId": "com.whatsapp.app",
      "timestamp": 1751167980
    }
  ]
}
```

**Message Format Fields:**
- `sender`: The name/username of the message sender
- `content`: The message text content
- `isGroup`: Boolean indicating if this is a group conversation
- `conversationName`: Name of the conversation/group
- `appId`: Platform-specific app identifier (e.g., "com.whatsapp.app")
- `timestamp`: Unix timestamp of the message (integer)

**Legacy Format (Still Supported):**
```json
{
  "platform": "whatsapp",
  "main_user": "john_doe",
  "group_name": "Family Group",
  "conversation_type": "group",
  "messages": [
    {
      "username": "mom",
      "content": "Hey everyone! How's your day going?",
      "timestamp": "2024-01-15T10:30:00Z",
      "type": "text"
    }
  ]
}
```

#### Upload WhatsApp File (Legacy)
```http
POST /api/conversations/upload-file
Content-Type: multipart/form-data

file: [WhatsApp chat export .txt file]
main_user: john_doe
group_name: Family Group
```

#### Generate Summary
```http
POST /api/conversations/{session_id}/summarize
Content-Type: application/json

{
  "include_personality": true,
  "include_relationships": true,
  "summary_length": "medium"
}
```

#### Generate Audio
```http
POST /api/conversations/{session_id}/generate-audio
Content-Type: application/json

{
  "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.75
  },
  "include_emotions": true
}
```

### User Profile Management

#### Get User Profiles
```http
GET /api/users/profiles?page=1&per_page=10&platform=whatsapp
```

#### Update User Profile
```http
PUT /api/users/profiles/{profile_id}
Content-Type: application/json

{
  "display_name": "Mom",
  "voice_id": "voice_id_here",
  "personality_traits": ["caring", "organized"],
  "relationship_type": "family",
  "trust_score": 0.9
}
```

### Audio Management

#### Get Session Audio Files
```http
GET /api/audio/{session_id}
```

#### Serve Audio File
```http
GET /api/audio/{session_id}/{filename}
```

### Assistant Integration

#### Chat with Assistant
```http
POST /api/assistant/chat
Content-Type: application/json

{
  "message": "What did my family talk about yesterday?",
  "include_calendar": true,
  "include_user_profiles": true
}
```

#### Create Calendar Event
```http
POST /api/assistant/calendar/events
Content-Type: application/json

{
  "main_user_id": 1,
  "title": "Family Dinner",
  "start_time": "2024-01-20T18:00:00Z",
  "end_time": "2024-01-20T20:00:00Z",
  "description": "Weekly family dinner",
  "location": "Home"
}
```

### Voice Management

#### Get Available Voices
```http
GET /api/voices/
```

## 🧪 Testing

### Run Migration Tests
```bash
python test_fastapi_migration.py
```

### Run Database Tests
```bash
python test_supabase_integration.py
```

### API Testing with curl
```bash
# Health check
curl http://localhost:8000/api/health

# List conversations
curl http://localhost:8000/api/conversations/

# Upload conversation
curl -X POST "http://localhost:8000/api/conversations/upload" \
  -H "Content-Type: application/json" \
  -d '{"platform": "whatsapp", "group_name": "Test Group", "main_user": "test_user", "messages": []}'
```

## 🚀 Deployment

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production
```bash
FASTAPI_DEBUG=false
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
CORS_ORIGINS=https://yourdomain.com
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com
```

## 📚 Documentation

- [FastAPI Migration Guide](FASTAPI_MIGRATION.md) - Detailed migration documentation
- [Database Migration Guide](DATABASE_MIGRATION.md) - Supabase integration details
- [API Documentation](http://localhost:8000/docs) - Interactive API docs

## 🔧 Development

### Code Style
```bash
# Format code
black .

# Lint code
flake8 .
```

### Adding New Endpoints
1. Create a new router in `api/routers/`
2. Add Pydantic models in `api/models.py`
3. Add dependencies in `api/dependencies.py`
4. Include the router in `app.py`

### Adding New Services
1. Create service class in `services/`
2. Add dependency injection in `api/dependencies.py`
3. Use in routers with dependency injection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues or questions:
1. Check the [FastAPI Migration Guide](FASTAPI_MIGRATION.md)
2. Review the API documentation at `/docs`
3. Check application logs
4. Verify environment configuration