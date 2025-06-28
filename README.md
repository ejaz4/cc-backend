# Multi-Platform Conversation Summarizer API

A comprehensive Flask REST API backend for a Gen-Z-focused Android app that summarizes conversations from multiple platforms (WhatsApp, Instagram, Discord) and generates short voice message summaries using ElevenLabs TTS. The backend also integrates with ElevenLabs' conversational assistant and Google Calendar for event management.

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

## 🏗️ Architecture

### Database Models

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
- MongoDB
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

3. **Set up environment variables**
```bash
cp env.example .env
```

Edit `.env` with your API keys:
```env
# Database
MONGODB_URI=mongodb://localhost:27017/conversation_summarizer

# API Keys
ELEVENLABS_API_KEY=your_elevenlabs_api_key
OPENAI_API_KEY=your_openai_api_key

# Google Calendar (optional)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:5000/api/assistant/calendar/callback

# File Storage
UPLOAD_FOLDER=uploads
AUDIO_FOLDER=audio
```

4. **Run the application**
```bash
python main.py
```

The API will be available at `http://localhost:5000`

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
```

#### Generate Audio
```http
POST /api/conversations/{session_id}/generate-audio
```

#### Get Conversation Details
```http
GET /api/conversations/{session_id}
```

#### List Conversations
```http
GET /api/conversations?main_user=john_doe&platform=whatsapp&limit=10
```

### User Profile Management

#### Get User Profiles
```http
GET /api/users/profiles?main_user=john_doe&platform=whatsapp&relationship_type=family
```

#### Update User Profile
```http
PUT /api/users/profiles/{profile_id}
Content-Type: application/json

{
  "personality_traits": ["friendly", "helpful"],
  "interests": ["technology", "music"],
  "voice_id": "pNInz6obpgDQGcFmaJgB"
}
```

#### Get Frequent Contacts
```http
GET /api/users/profiles/frequent?main_user=john_doe&limit=10
```

### Assistant Integration

#### Chat with Assistant
```http
POST /api/assistant/chat
Content-Type: application/json

{
  "message": "What meetings do I have today?",
  "user_id": "john_doe",
  "session_id": "optional_session_id"
}
```

#### Calendar Authentication
```http
POST /api/assistant/calendar/auth
Content-Type: application/json

{
  "user_id": "john_doe"
}
```

#### Create Calendar Event
```http
POST /api/assistant/calendar/events
Content-Type: application/json

{
  "user_id": "john_doe",
  "event_data": {
    "title": "Team Meeting",
    "start_time": "2024-01-15T14:00:00Z",
    "end_time": "2024-01-15T15:00:00Z",
    "description": "Weekly team sync"
  }
}
```

### Audio Management

#### Serve Audio File
```http
GET /api/audio/{session_id}/{filename}
```

#### Get Available Voices
```http
GET /api/voices
```

## 🔧 Platform Integration Examples

### Instagram Integration
```json
{
  "platform": "instagram",
  "main_user": "john_doe",
  "group_name": "Close Friends",
  "conversation_type": "group",
  "messages": [
    {
      "username": "sarah",
      "content": "Just posted a new photo! 📸",
      "timestamp": "2024-01-15T10:30:00Z",
      "type": "text",
      "reactions": ["❤️", "🔥"],
      "reply_to": null
    }
  ],
  "platform_specific_data": {
    "instagram_data": {
      "is_dm": false,
      "has_media": false
    }
  }
}
```

### Discord Integration
```json
{
  "platform": "discord",
  "main_user": "john_doe",
  "group_name": "Gaming Server",
  "conversation_type": "channel",
  "messages": [
    {
      "username": "gamer123",
      "content": "Anyone up for a game tonight?",
      "timestamp": "2024-01-15T10:30:00Z",
      "type": "text",
      "reactions": ["👍"],
      "reply_to": null
    }
  ],
  "platform_specific_data": {
    "discord_data": {
      "channel_id": "123456789",
      "guild_id": "987654321",
      "is_bot": false,
      "attachments": []
    }
  }
}
```

## 🧠 Personality Analysis Features

### Automatic Trait Detection
- **Humorous**: Detects use of emojis, jokes, and playful language
- **Professional**: Identifies work-related vocabulary and formal language
- **Grateful**: Recognizes thank you messages and appreciation
- **Helpful**: Detects offers of assistance and support
- **Apologetic**: Identifies apologies and regretful language

### Communication Style Analysis
- **Emoji Usage**: Tracks frequency and types of emojis
- **Formality Level**: Analyzes language formality
- **Question Patterns**: Identifies question-heavy communication
- **Exclamation Usage**: Tracks enthusiasm and emphasis
- **Response Patterns**: Analyzes reply timing and engagement

### Relationship Context
- **Family**: Detects family-related vocabulary and dynamics
- **Friends**: Identifies casual, friendly interactions
- **Colleagues**: Recognizes work-related conversations
- **Close Friends**: Detects intimate, personal discussions

## 🎵 Voice Generation Features

### Personality-Based Voice Selection
- **Professional**: Adam voice for business-like communication
- **Friendly**: Josh voice for warm, casual interactions
- **Warm**: Bella voice for caring, supportive messages
- **Helpful**: Rachel voice for assistance and guidance

### Emotion-Aware Settings
- **Joy**: Lower stability for more expressive delivery
- **Urgency**: Reduced stability for urgent messages
- **Calmness**: Higher stability for peaceful content
- **Sadness**: Adjusted tone for empathetic delivery

### Custom Voice Settings
- **Stability**: Controls voice consistency (0.0-1.0)
- **Similarity Boost**: Enhances voice similarity (0.0-1.0)
- **Style**: Adjusts expressiveness (0.0-1.0)
- **Speaker Boost**: Enhances speaker clarity

## 🔒 Security & Privacy

### Data Protection
- Encrypted platform credentials
- Secure API key storage
- User data isolation
- Privacy settings per user

### Access Control
- User-specific data access
- Platform-specific permissions
- Relationship-based data sharing
- Audit logging

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "main.py"]
```

### Environment Variables
```env
# Production settings
FLASK_ENV=production
MONGODB_URI=mongodb://production-db:27017/conversation_summarizer
ELEVENLABS_API_KEY=your_production_key
OPENAI_API_KEY=your_production_key
```

### Scaling Considerations
- MongoDB clustering for high availability
- Redis for session management
- CDN for audio file delivery
- Load balancer for API distribution

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API examples

## 🔮 Future Enhancements

- **Real-time Processing**: WebSocket support for live conversations
- **Advanced Analytics**: Deep learning for better personality analysis
- **Voice Cloning**: Custom voice creation from user audio samples
- **Multi-language Support**: Internationalization and translation
- **Advanced Calendar**: Meeting scheduling and conflict resolution
- **Social Insights**: Relationship strength and network analysis