import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the application"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database Configuration (Supabase PostgreSQL)
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    DATABASE_URL = os.getenv('DATABASE_URL')  # Direct PostgreSQL connection string
    
    # If DATABASE_URL is not provided, construct it from Supabase credentials
    if not DATABASE_URL and SUPABASE_URL and SUPABASE_KEY:
        # Extract host from Supabase URL and construct PostgreSQL connection
        # Supabase URL format: https://project-ref.supabase.co
        # PostgreSQL connection: postgresql://postgres:[password]@[host]:5432/postgres
        host = SUPABASE_URL.replace('https://', '').replace('.supabase.co', '')
        DATABASE_URL = f"postgresql://postgres:{SUPABASE_KEY}@{host}.supabase.co:5432/postgres"
    
    # API Keys
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Google Calendar Configuration (Optional)
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/api/assistant/calendar/callback')
    
    # File Storage Configuration
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    AUDIO_FOLDER = os.getenv('AUDIO_FOLDER', 'audio')
    
    # OpenAI Configuration
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    # ElevenLabs Configuration
    ELEVENLABS_BASE_URL = os.getenv('ELEVENLABS_BASE_URL', 'https://api.elevenlabs.io/v1')
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        required_vars = [
            'DATABASE_URL',
            'ELEVENLABS_API_KEY',
            'OPENAI_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_URL = 'test_whatsapp_summarizer'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 