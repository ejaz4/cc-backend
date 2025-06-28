# WhatsApp Summarizer API 🗣️

A Flask REST API backend for a Gen-Z-focused Android app that summarizes WhatsApp group chats and generates voice message summaries using ElevenLabs TTS. The app also integrates with ElevenLabs' conversational assistant for calendar management.

## 🚀 Features

### Core Functionalities
- **📱 WhatsApp Chat Upload & Parsing**: Upload .txt chat exports and extract messages, timestamps, and usernames
- **🤖 AI-Powered Summarization**: Generate structured dialogue summaries using OpenAI GPT-4
- **🎵 TTS Audio Generation**: Convert script lines to speech using ElevenLabs voices
- **📁 Audio File Serving**: Serve generated audio files via REST API
- **🤖 Conversational Assistant**: ElevenLabs assistant integration with calendar management
- **📅 Google Calendar Integration**: Create, view, and manage calendar events

### Technical Features
- **🗄️ MongoDB Database**: Scalable NoSQL database with optimized indexes
- **🔧 Modular Architecture**: Clean separation of concerns with services and repositories
- **🛡️ Error Handling**: Comprehensive error handling and logging
- **📊 Data Validation**: Input validation and data integrity checks
- **🔌 RESTful API**: Standard REST endpoints with JSON responses

## 📋 Prerequisites

1. **Python 3.8+**
2. **MongoDB** (local or MongoDB Atlas)
3. **ElevenLabs API Key** ([Get one here](https://elevenlabs.io/))
4. **OpenAI API Key** ([Get one here](https://platform.openai.com/))
5. **Google Calendar API** (optional, for calendar features)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd cc-backend
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp env.example .env
```

Edit `.env` with your configuration:
```env
# Required
ELEVENLABS_API_KEY=your_elevenlabs_api_key
OPENAI_API_KEY=your_openai_api_key
MONGODB_URI=mongodb://localhost:27017/

# Optional (for calendar features)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

### 4. Start MongoDB
```bash
# Local MongoDB
mongod

# Or use MongoDB Atlas (cloud)
```

### 5. Run the Application
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## 📚 API Documentation

### Health Check
```http
GET /api/health
```

### Chat Upload & Processing

#### 1. Upload WhatsApp Chat
```http
POST /api/upload
Content-Type: multipart/form-data

file: chat_export.txt
group_name: "My Group Chat"
```

**Response:**
```json
{
  "success": true,
  "session_id": "uuid-session-id",
  "participants": ["Alice", "Bob", "Charlie"],
  "total_messages": 150,
  "date_range": {
    "start_date": "2023-12-01T10:00:00",
    "end_date": "2023-12-25T23:59:59"
  }
}
```

#### 2. Generate Summary
```http
POST /api/summarize/{session_id}
```

**Response:**
```json
{
  "success": true,
  "summary_text": "The group discussed weekend plans...",
  "script_lines": [
    {
      "username": "Alice",
      "line": "I'm going to Spain next week!",
      "line_number": 1
    },
    {
      "username": "Bob", 
      "line": "That sounds amazing!",
      "line_number": 2
    }
  ]
}
```

#### 3. Generate TTS Audio
```http
POST /api/generate-audio/{session_id}
```

**Response:**
```json
{
  "success": true,
  "audio_files": [
    {
      "username": "Alice",
      "filename": "alice_line1.mp3",
      "file_path": "/audio/session-id/alice_line1.mp3"
    }
  ],
  "total_generated": 3,
  "total_failed": 0
}
```

#### 4. Serve Audio Files
```http
GET /api/audio/{session_id}/{filename}
```

Returns the audio file as MP3.

### Session Management

#### Get Session Details
```http
GET /api/sessions/{session_id}
```

#### List All Sessions
```http
GET /api/sessions?limit=10
```

### Assistant Integration

#### Chat with Assistant
```http
POST /api/assistant/chat
Content-Type: application/json

{
  "message": "Create a meeting for tomorrow at 2 PM",
  "user_id": "user123",
  "session_id": "assistant-session-id"
}
```

#### Calendar Authentication
```http
POST /api/assistant/calendar/auth
Content-Type: application/json

{
  "user_id": "user123"
}
```

#### Create Calendar Event
```http
POST /api/assistant/calendar/events
Content-Type: application/json

{
  "user_id": "user123",
  "event_data": {
    "title": "Team Meeting",
    "start_time": "2023-12-26T14:00:00",
    "end_time": "2023-12-26T15:00:00",
    "description": "Weekly team sync",
    "location": "Conference Room A"
  }
}
```

### ElevenLabs Integration

#### Get Available Voices
```http
GET /api/voices
```

## 🗄️ Database Schema

### Collections

1. **chat_sessions**: WhatsApp chat sessions
2. **summaries**: Generated summaries and scripts
3. **audio_files**: TTS audio file metadata
4. **users**: User accounts and voice preferences
5. **assistant_sessions**: Assistant conversation sessions
6. **calendar_events**: Calendar event records

### Key Indexes
- Session ID lookups
- User-based queries
- Timestamp-based sorting
- Status-based filtering

## 🔧 Development

### Project Structure
```
cc-backend/
├── api/
│   ├── __init__.py
│   └── routes.py          # Flask API routes
├── database/
│   ├── __init__.py
│   ├── connection.py      # MongoDB connection
│   ├── models.py          # Data models
│   └── repository.py      # Database operations
├── services/
│   ├── __init__.py
│   ├── whatsapp_parser.py # Chat parsing
│   ├── summarizer.py      # AI summarization
│   ├── elevenlabs_service.py # TTS generation
│   └── assistant_service.py  # Assistant integration
├── app.py                 # Main application
├── config.py              # Configuration
├── requirements.txt       # Dependencies
└── README.md
```

### Running Tests
```bash
# Install test dependencies
pip install pytest

# Run tests
pytest
```

### Code Formatting
```bash
# Install formatting tools
pip install black flake8

# Format code
black .

# Check code style
flake8 .
```

## 🚀 Deployment

### Environment Variables
Set the following environment variables for production:

```env
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secure-secret-key
MONGODB_URI=your-production-mongodb-uri
ELEVENLABS_API_KEY=your-elevenlabs-key
OPENAI_API_KEY=your-openai-key
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

### Cloud Deployment
- **Heroku**: Use Procfile and environment variables
- **AWS**: Deploy to EC2 or use Elastic Beanstalk
- **Google Cloud**: Use App Engine or Cloud Run
- **Azure**: Use App Service

## 🔒 Security Considerations

- Use environment variables for sensitive data
- Implement proper authentication and authorization
- Validate all input data
- Use HTTPS in production
- Regular security updates
- Rate limiting for API endpoints

## 📈 Performance Optimization

- Database indexing for common queries
- Audio file caching
- Connection pooling
- Async processing for long-running tasks
- CDN for audio file delivery

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API examples

## 🔮 Future Enhancements

- Real-time chat processing
- Voice cloning for users
- Advanced calendar features
- Multi-language support
- Mobile app integration
- Analytics dashboard